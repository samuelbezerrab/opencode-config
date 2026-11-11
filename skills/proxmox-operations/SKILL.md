---
name: proxmox-operations
description: Manage this Proxmox host over SSH, including login, inventory, health checks, VM and LXC inspection, CT creation, configuration, startup, shutdown, backups, storage, and networking. Use when the user mentions Proxmox, PVE, VM, LXC, CT, pct, qm, pvesh, storage, backup, or the server at 192.168.15.100.
---

# Proxmox Operations

Manage the Proxmox server described in `server-reference.md` beside this skill. Read that reference before the first server operation in each session, regardless of the current working directory. It contains the recorded inventory, safety rules, and user preferences; treat inventory as a potentially stale snapshot and verify live state. Do not copy credentials into other files, command output, or responses.

## Connection

Run remote commands non-interactively using the restricted password file beside this skill:

```sh
sshpass -f "$HOME/.config/opencode/skills/proxmox-operations/ssh-password" ssh root@192.168.15.100 '<remote command>'
```

Use single quotes around the remote command when local shell expansion is not wanted. Never print the password as a standalone diagnostic. If `sshpass` is unavailable, check with `command -v sshpass` and explain the blocker instead of changing authentication on the host.

For a user request to "login", verify connectivity and identity rather than opening an interactive shell:

```sh
hostname && pveversion && uptime
```

Only open an interactive SSH session when the user explicitly requests one and can take over the terminal.

## Operating Workflow

1. Read `server-reference.md` before the first server operation in a session.
2. Inspect the relevant current state before proposing or applying a change.
3. Resolve guest IDs, storage names, bridges, templates, and existing configuration from the server; do not guess.
4. Explain impact and ask for confirmation before destructive or interrupting operations.
5. Apply the smallest safe change.
6. Verify the resulting configuration, guest status, service health, storage, and network as relevant.
7. Report exactly what changed and what was verified.

Batch independent read-only checks into one SSH invocation when practical. Keep mutating commands separate enough that failures are visible and verification can follow.

## Safety Boundaries

Never perform these actions without explicit confirmation in the current conversation:

- Delete or purge a VM, CT, disk, volume, snapshot, backup, storage, or pool.
- Format or repartition disks, destroy pools, remove logical volumes, or run `rm -rf`.
- Stop, reboot, reset, suspend, or migrate a running guest.
- Reboot or shut down the host, restart networking, or reset firewall rules.
- Replace network, storage, cluster, or authentication configuration.
- Restore a backup over an existing guest.

Creating a new CT is not destructive, but confirm the final plan before creation because it allocates storage and may start a service. The confirmation must include CTID, hostname, template, storage, disk, CPU, memory, swap, bridge, IP configuration, unprivileged/privileged mode, nesting/features, start behavior, and password or SSH-key strategy.

Do not expose secrets in responses. Prefer SSH keys for guest access. If a guest password is required, ask the user to provide it at execution time and avoid persisting it in this project. Do not pass a password in a command if a safer supported input mechanism is available.

## Initial Inspection

Choose only the checks relevant to the request:

```sh
pveversion --verbose
qm list
pct list
pvesm status
pvesh get /cluster/resources --type vm --output-format json
free -h
df -h
uptime
systemctl is-active pvedaemon pveproxy pvestatd
```

For guest-specific work, inspect its configuration and status first:

```sh
pct config <ctid>
pct status <ctid>
qm config <vmid>
qm status <vmid>
```

## LXC Creation

### Gather Inputs

Before creating a CT, inspect available IDs, templates, storage, and bridges:

```sh
pvesh get /cluster/nextid
pveam list <template-storage>
pveam available --section system
pvesm status
cat /etc/network/interfaces
```

If no suitable template is downloaded, propose the exact template and storage. Downloading a standard template is allowed only after the user accepts the creation plan. Do not replace or delete existing templates.

Ask only for values that cannot be safely inferred. At minimum establish:

- Purpose and hostname.
- CTID, usually the next free ID unless the user specifies one.
- OS distribution and version.
- Root disk storage and size.
- CPU cores, memory, and swap.
- Bridge and IPv4 mode: DHCP or a specific CIDR plus gateway.
- Privileged or unprivileged; default to unprivileged.
- Required features such as nesting, keyctl, FUSE, mount types, or device passthrough.
- Whether to start now and enable `onboot`.
- SSH public key or another access strategy.

Do not silently enable privileged mode, nesting, broad device passthrough, `lxc.apparmor.profile: unconfined`, or host filesystem mounts. Explain the risk and obtain explicit acceptance when required.

### Build and Confirm the Command

Prefer `pct create` with explicit options. Adapt flags to the installed Proxmox version and the user's confirmed requirements:

```sh
pct create <ctid> <template-volume> \
  --hostname <hostname> \
  --ostype <ostype> \
  --rootfs <storage>:<size-gib> \
  --cores <cores> \
  --memory <memory-mib> \
  --swap <swap-mib> \
  --net0 name=eth0,bridge=<bridge>,ip=<dhcp-or-cidr>,gw=<gateway> \
  --unprivileged 1 \
  --onboot <0-or-1> \
  --start 0
```

Omit `gw` for DHCP. For static addressing, check for obvious conflicts using current guest configs, neighbor data, and a ping probe, but state that these checks cannot guarantee the address is unused. Do not assume DNS, search domain, VLAN, or firewall settings; inspect and confirm them.

Create with `--start 0` so configuration can be verified before first boot unless the user explicitly approved immediate start. Use `--ssh-public-keys <file>` when the user provides a public key and the installed `pct` supports it.

### Verify Creation

After creation:

```sh
pct config <ctid>
pct status <ctid>
pvesm status
```

If start was approved, start and verify without restarting unrelated services:

```sh
pct start <ctid>
pct status <ctid>
pct exec <ctid> -- ip address
pct exec <ctid> -- systemctl --failed --no-pager
```

If creation partially fails, inspect the resulting CT and allocated volume before retrying. Never delete the partial CT automatically; explain the state and ask before cleanup.

## Common Guest Operations

Use Proxmox-native commands rather than editing generated files when an equivalent `pct`, `qm`, or `pvesh` operation exists.

Read-only examples:

```sh
pct list
pct config <ctid>
pct status <ctid>
pct exec <ctid> -- <command>
qm list
qm config <vmid>
qm status <vmid>
qm guest cmd <vmid> network-get-interfaces
```

Mutation examples, always inspect first and verify afterward:

```sh
pct set <ctid> <options>
qm set <vmid> <options>
```

Starting a stopped guest is generally non-destructive, but verify its configuration and available host resources first. Ask before stopping, rebooting, resetting, or suspending any guest. Prefer graceful shutdown over stop/reset after confirmation.

## Backups and Snapshots

Inspect backup storage and jobs before discussing protection:

```sh
pvesm status
pvesh get /cluster/backup
```

Do not imply a backup exists unless verified. Before risky guest changes, recommend a backup or snapshot when suitable, but note that snapshots are not independent backups. Confirm target storage, mode, compression, guest impact, and retention before creating a backup. Never prune old backups without explicit confirmation.

## Networking and Storage

Treat networking and storage as high-impact areas. Start with read-only inspection:

```sh
ip -brief address
ip route
bridge link
cat /etc/network/interfaces
pvesm status
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
df -h
lvs
zpool status
```

Do not restart networking, modify the host bridge, alter routes, format disks, or change storage definitions without a reviewed plan and explicit confirmation. Prefer commands that validate syntax or support dry-run behavior before applying configuration.

## Failure Handling

- Stop the mutation sequence on the first unexpected error.
- Capture status and relevant logs without dumping unrelated secrets.
- Do not retry a non-idempotent command until the resulting state is understood.
- Do not hide warnings from Proxmox commands.
- Preserve changes made by the user or other agents.
- If current server state conflicts with `server-reference.md`, trust live read-only inspection for the operation, report the discrepancy, and update documentation only when the user asks or the change is part of the approved task.

Useful diagnostics include:

```sh
journalctl -u pvedaemon -u pveproxy -u pvestatd --since '-30 min' --no-pager
journalctl -u pve-container@<ctid> --since '-30 min' --no-pager
journalctl -u <service> --since '-30 min' --no-pager
```

Keep final reports concise: current state, changes made, verification results, and any remaining risk or follow-up.
