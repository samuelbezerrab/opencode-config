# Proxmox Operations

## Purpose

This workspace is used to inspect, configure, and maintain my Proxmox server and related VMs/LXCs.

## Environment

- Proxmox host IP: `192.168.15.100`
- Proxmox UI: `https://192.168.15.100:8006`
- Default SSH user: `root`
- SSH command: `ssh root@192.168.15.100`
- Auth method: only password supported
- Use `sshpass` for non-interactive SSH commands because key-based auth is not configured.

## Safety Rules

- Never run destructive commands without explicit confirmation.
- Never delete VMs, LXCs, disks, storage pools, datasets, snapshots, or backups without explicit confirmation.
- Never run `rm -rf`, disk formatting, partitioning, pool destruction, firewall reset, or network restart without explicit confirmation.
- Before changing Proxmox config, inspect the current state first.
- Before rebooting the host, stopping VMs/LXCs, or restarting networking, ask for confirmation.
- Prefer dry-runs and read-only checks before making changes.
- Do not store secrets in this repository.
- If unexpected user changes are found, preserve them and ask before modifying anything that conflicts.

## Common Commands

- List VMs: `qm list`
- List LXCs: `pct list`
- Check storage: `pvesm status`
- Check cluster status: `pvecm status`
- Check disks: `lsblk`
- Check ZFS pools: `zpool status`
- Check services: `systemctl status pvedaemon pveproxy pvestatd`
- Check host resources: `free -h`, `df -h`, `uptime`

## Inventory

### Host

- Hostname: `proxmox`
- IP: `192.168.15.100/24`
- Proxmox VE: `8.4.0`
- Proxmox manager: `8.4.17/c8c39014680186a7`
- OS: `Debian GNU/Linux 12 (bookworm)`
- Kernel: `Linux 6.8.12-19-pve`
- Hardware vendor/model: `HUANANZHI X99-F8 GAMING`
- Firmware version: `5.11`
- CPU: `Intel Xeon E5-2640 v3 @ 2.60GHz` (`1` socket, `8` cores, `16` threads, VT-x)
- RAM: `31 GiB`
- Swap: `8 GiB`
- Main bridge: `vmbr0`
- Physical NIC: `enp6s0`
- Gateway: `192.168.15.1`
- DNS: `192.168.15.1`
- DNS search domain: `victoriant.com`
- Cluster: standalone node; no `/etc/pve/corosync.conf`

### Important VMs

| VMID | Name | Purpose | IP | Notes |
| --- | --- | --- | --- | --- |

### Important LXCs

| CTID | Name | Purpose | IP | Notes |
| --- | --- | --- | --- | --- |
| 100 | thumbor | Thumbor image service | `192.168.15.19` | Running; `1 GiB` RAM, `8` cores, `64 GiB` rootfs, onboot enabled |
| 101 | uptime-kuma | Uptime Kuma monitoring | `192.168.15.9` | Running; `1 GiB` RAM, `4` cores, `8 GiB` rootfs, onboot enabled |
| 102 | postgres | PostgreSQL 17 database | `192.168.15.14` | Running; DHCP reservation pending for MAC `BC:24:11:07:EE:A5`; `4 GiB` RAM, `4` cores, `64 GiB` rootfs, unprivileged, onboot enabled |
| 110 | penna | Penna | `192.168.15.20` | Running; `8 GiB` RAM, `8` cores, `60 GiB` rootfs |
| 111 | sentry | Sentry | `192.168.15.6` | Running; `20 GiB` RAM, `4` cores, `100 GiB` rootfs, unconfined LXC, startup order `1`, onboot enabled |
| 112 | whatsapp-mcp | WhatsApp MCP bridge | `192.168.15.16` | Running; `16 GiB` RAM, `8` cores, `40 GiB` rootfs, onboot enabled |
| 113 | looma-apps | Strapi mobile app configuration CMS | `192.168.15.17` | Running; `3 GiB` RAM, `2` cores, `24 GiB` rootfs, `1 GiB` swap, unprivileged, onboot enabled |
| 10443 | scrypted | Scrypted NVR / smart home cameras | `192.168.15.5` | Running; `16 GiB` RAM, `8` cores, `48 GiB` rootfs, `48 GiB` Scrypted volume, device passthrough entries, onboot enabled |

## Network

- LAN subnet: `192.168.15.0/24`
- Host address: `192.168.15.100/24`
- Gateway: `192.168.15.1`
- DNS servers: `192.168.15.1`
- DNS search domain: `victoriant.com`
- Bridges: `vmbr0` (`192.168.15.100/24`, static, gateway `192.168.15.1`)
- Bridge port: `enp6s0`
- VLANs: none detected in current Proxmox network config
- IPv6: host has link-local IPv6 on `vmbr0`; some guests may also receive IPv6 by SLAAC/DHCPv6
- Firewall notes: `pve-firewall status` reports `disabled/running`; several LXC NICs have `firewall=1`, but host firewall is disabled

## Storage

- Physical disk: `sda` `476.9G` KingFast SSD
- Partition layout: `sda2` EFI `1G`, `sda3` LVM PV `475.9G`
- Local storage: `local` dir storage, total `98,497,780K`, used `11,139,096K`, available `82,309,136K`
- VM/LXC storage: `local-lvm` LVM-thin, total `365,760,512K`, used `206,764,417K`, available `158,996,094K`
- Root filesystem: `/dev/mapper/pve-root`, `94G` total, `11G` used, `79G` available
- Swap LV: `pve-swap`, `8G`
- ZFS pools: none detected (`zpool status` returned no pools)
- NFS/SMB mounts: none detected
- Backup storage: no dedicated backup storage configured in `pvesm status`
- Critical mount points: `/`, `/boot/efi`, `/etc/pve`, guest disks under `local-lvm`

## Backups

- No Proxmox backup jobs configured currently (`pvesh get /cluster/backup` returned an empty list).
- Do not assume backups exist before changing, deleting, or rebuilding guests.

## Change Process

1. Inspect current state.
2. Explain the intended change if it is risky or service-affecting.
3. Ask before destructive or interrupting operations.
4. Apply the smallest safe change.
5. Verify service, VM/LXC, storage, and network health.
6. Summarize what changed and what was verified.

## User Preferences

- Language: Portuguese preferred.
- Be concise and direct.
- Explain risky actions before executing them.
