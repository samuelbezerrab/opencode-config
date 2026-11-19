# Índice de perfis pessoais

## Identificação

1. Identifique o projeto ativo e, se for um repositório Git, consulte a URL de fetch do remote `origin`. Para comparar URLs GitHub, normalize SSH no formato `git@github.com:owner/repo.git`, SSH em formato URL e HTTPS para `github.com/owner/repo`: remova usuário, protocolo, barra final e sufixo `.git`; compare host, owner e repositório sem diferenciar maiúsculas de minúsculas. Preserve owner e nome completos: forks são repositórios distintos.
2. Se o remote corresponder a exatamente um perfil na tabela, leia-o e aplique-o à tarefa. Isso inclui clones, subdiretórios e worktrees do mesmo repositório.
3. Um caminho local absoluto explicitamente cadastrado na tabela também pode identificar um projeto sem remote; aplique-o à raiz cadastrada e seus subdiretórios. Se houver caminhos sobrepostos, conflito com um remote ou mais de uma correspondência possível, pergunte ao usuário; não deduza equivalência por nome de pasta ou similaridade. Um remote diferente não passa a ser equivalente por compartilhar um caminho.
4. Se não houver correspondência, prossiga sem perfil, a menos que instruções pessoais sejam necessárias ou o usuário peça para registrar um aprendizado. Nesses casos, siga o cadastro abaixo ou peça esclarecimento se a identidade for ambígua.

| Remote normalizado | Perfil |
| --- | --- |
| `github.com/ACParticipacoes/bipfut.app` | `~/.config/opencode/projects/bipfut.md` |
| `github.com/App2Sales/cante_app` | `~/.config/opencode/projects/cante-app.md` |
| `github.com/App2Sales/cante-cms` | `~/.config/opencode/projects/cante-cms.md` |

## Registrar aprendizado

Quando o usuário pedir para aprender, lembrar, registrar ou acrescentar algo para um projeto:

1. Identifique o projeto seguindo o procedimento acima e leia o perfil existente, se houver. Se houver ambiguidade sobre o projeto ou sobre o aprendizado, pergunte antes de alterar arquivos.
2. Se ainda não houver perfil e houver um `origin` inequívoco, crie um arquivo Markdown com nome distinto neste diretório e cadastre na tabela o remote normalizado e o caminho do perfil. Para projeto sem `origin`, peça ao usuário confirmação da raiz local absoluta antes de cadastrá-la como identificador na tabela. Não sobrescreva perfis existentes nem associe forks automaticamente.
3. Acrescente ou atualize no perfil a instrução reutilizável solicitada, preservando as demais. Se ela conflitar com uma instrução existente e o pedido não esclarecer que é uma correção ou substituição, pergunte antes de alterá-la. Separe fatos sujeitos a mudança de instruções permanentes e oriente a verificação quando necessário.
4. Não salve senhas, chaves privadas, tokens ou conteúdo de credenciais; registre apenas referências necessárias, como caminhos, sem expor segredos. Não inclua credenciais nas URLs. Não modifique o repositório do projeto para armazenar o aprendizado.
5. Informe ao usuário o que foi registrado e o caminho do perfil.

## Associar projetos

Quando o usuário pedir para associar projetos distintos:

1. Identifique cada projeto separadamente pelo remote ou por raiz local confirmada, conforme o procedimento de identificação. Reutilize perfis existentes e cadastre os que faltarem seguindo as regras de registro; pergunte se a identidade, a relação ou o papel de algum projeto for ambíguo.
2. Acrescente uma entrada na tabela de associações abaixo com os caminhos dos perfis e o papel de cada projeto, por exemplo backend e frontend. Uma associação pode conter dois ou mais projetos, e um projeto pode participar de mais de uma associação. Atualize a entrada existente ao acrescentar membros, sem duplicar ou substituir perfis.
3. Ao identificar o projeto ativo, consulte suas associações. Leia o perfil de outro projeto associado apenas quando relevante para a tarefa. A associação indica uma relação, não que sejam o mesmo repositório: aplique as instruções específicas somente ao projeto a que pertencem e não presuma autorização para modificar ou executar operações nos outros projetos.
4. Informe os projetos, seus papéis e os arquivos de perfil cadastrados ou atualizados. Mantenha os dados e credenciais sob as mesmas regras de segurança do registro de aprendizado.

| Associação | Perfis e papéis |
| --- | --- |
| Cante | Backend: `~/.config/opencode/projects/cante-cms.md`; frontend: `~/.config/opencode/projects/cante-app.md` |
