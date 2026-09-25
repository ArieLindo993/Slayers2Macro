# Histórico de versões

Alterações verificadas nas tags e no código do repositório. A versão mais recente pode ser instalada pelo atualizador.

## [7.0.2](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.2)

### Alterações

- Tempo padrão de coleta com **T aumentado de 1,5 para 3 segundos**.
- Configurações já salvas continuam preservadas. Para aplicar o novo tempo a uma instalação existente, salve 3 em “Segurar T (s)”.
- Atualizador passou a mostrar mensagens ao preparar, consultar o GitHub, baixar, verificar a integridade e extrair os arquivos.
- Consulta da versão mais recente passou a ter limite de espera de 30 segundos.

## [7.0.1](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.1)

### Correções

- Prévia visual reduzida para caber melhor no painel lateral.
- Cada perfil de tela passou a preservar e restaurar sua escolha entre calibração automática e manual.
- Trocar de perfil passou a atualizar também a opção correspondente na interface.

## [7.0.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.0)

### Novidades

- Nome de interface **Fishing Macro**, mantendo o perfil de Slayers 2 e o nome do executável para compatibilidade com o atualizador.
- Prévia da leitura com região, faixa alvo e marcador destacados.
- Métricas de qualidade: leituras válidas e tempo do marcador dentro da faixa, com registros por ciclo.
- Recuperação gradual da barra: região atual, arredores e tela do jogo.
- Perfis de calibração separados por tamanho da janela, bordas e DPI.
- Diagnósticos locais de perda de leitura, com recortes e limite de 20 pares de arquivos.
- Atalhos **Iniciar.cmd** e **Voltar-versao.cmd**, com suporte a abrir a instalação existente ou retornar à anterior.

### Dados e distribuição

- Configurações, perfis, histórico e diagnósticos separados dos executáveis em `%LOCALAPPDATA%\FishingMacro`.
- Migração aditiva dos dados antigos e preservação de dados na troca de versão.
- Auditoria de arquivos versionados para evitar a inclusão de dados de execução e caminhos pessoais.
- Inclusão de informações das dependências de terceiros na distribuição.
- Testes para métricas, perfis, recuperação, diagnósticos, prévia e retorno de versão.

## [6.1.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v6.1.0)

Primeira versão registrada neste repositório. Os recursos abaixo já estavam presentes nessa base; não é possível atribuir cada um a uma versão anterior usando o histórico Git disponível.

### Recursos da base

- Lançamento por clique no ponto salvo com F8 e controle de início/pausa com F4.
- Parada com F10 e seleção manual da barra com F6, por arraste sobre uma captura congelada.
- Localização automática da barra e aprendizado entre rodadas confiáveis.
- Controle do minigame e coleta segurando T, inclusive sem depender da identificação visual do item para tentar coletá-lo.
- Tentativas limitadas de lançamento e coleta, tratamento de falta de recompensa e pausa ao perder o foco.
- Histórico da sessão com leitura de nomes de itens e arquivos JSON/CSV.
- Executável Windows, compilação automatizada e atualizador apontando para este repositório, com verificação SHA-256 do pacote.

### Distribuição após a tag 6.1.0

- O empacotamento de `Atualizador.zip` foi acrescentado no commit `bd78a01`, entre as tags 6.1.0 e 7.0.0. Ele não representa uma nova versão do motor de pesca.

## Protótipos anteriores

Antes da primeira tag, o desenvolvimento passou por ajustes de clique para lançar, duração do T, tentativas de coleta quando o item girava fora do alcance, interface, identificação de itens e calibração. Esses pedidos fazem parte do contexto do projeto, mas não há tags anteriores neste repositório para comprovar uma lista exata de mudanças por versão. Por isso, não são apresentados como releases numeradas ou correções verificadas.
