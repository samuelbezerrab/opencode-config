# Cante app

## Lojas e assinaturas

- Identificadores: Android `cante.praise.app`; iOS `cante.praise.ios.app`. Confirme-os na configuração do projeto antes de operar.
- Google Play Developer API: a conta de serviço está em `android/google-play-key.json`. Use o escopo `https://www.googleapis.com/auth/androidpublisher` e a API `monetization.subscriptions`; consulte a documentação atual para criação, atualização e ativação de planos. Nunca exponha o conteúdo da chave ou tokens.
- App Store Connect API: chave em `ios/api_key.p8`; obtenha Key ID e Issuer ID em `ios/fastlane/Fastfile`. Se a API retornar `FORBIDDEN.REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED`, peça a regularização do contrato no App Store Connect e teste novamente.
- Adapty: use o CLI `adapty` autenticado para consultar o app Cante e seus produtos (`adapty apps list`, `adapty products list --app <id>`). O preço retornado em USD ou zero não comprova o preço local da Apple; confirme valores regionais antes de configurar a loja.
- Antes de alterar assinaturas, consulte produtos e preços existentes, apresente as mudanças e obtenha confirmação. A atualização do preço-base no Google afeta novas compras; migrar assinantes existentes é uma operação separada e exige confirmação específica. Confirme o estado após cada alteração.
- Criar produtos no Google Play não os vincula automaticamente ao Adapty nem garante sua disponibilidade no paywall. Verifique essas integrações quando estiverem no escopo solicitado.
