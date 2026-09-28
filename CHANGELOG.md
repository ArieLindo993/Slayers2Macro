# Histórico de versões

Alterações verificadas nas tags e no código do repositório. A versão mais recente pode ser instalada pelo atualizador.

## [7.1.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.0)

### Renovação visual

- Tema noturno em azul-escuro e verde-jade, com detalhes dourados, símbolo de anzol e xadrez discreto inspirado no universo de Demon Slayer.
- Tela principal organizada em status da pescaria, preparação, inventário da sessão e painel de reconhecimento/registros.
- Botões com estados de foco e interação; destaque para iniciar e parar.
- Tema consistente nas configurações, tabelas do histórico e seleção manual da barra.
- Janela principal de 900 × 720 e ações do histórico em uma faixa inferior reservada para permanecerem acessíveis.

### Compatibilidade

- Alteração somente de apresentação: algoritmos, tempos, recuperação, coleta, calibração, atalhos, histórico, logs e configurações mantidos.
- Nenhuma nova dependência, download de imagens ou migração de dados.
- Verificação dos callbacks dos controles, testes existentes e inspeção das janelas com dados fictícios.

## [7.0.9](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.9)

### Verificação de coleta mais rápida

- Espera padrão pelo item após o minigame reduzida de 12 para 2 segundos. O antigo valor padrão salvo de 12 segundos é migrado uma vez; outros valores personalizados são preservados.
- Ajuste manual dessa espera agora aceita valores de 0,5 a 20 segundos.
- Após soltar T, a ausência pode ser validada por duas capturas distintas ao longo de pelo menos 0,6 segundo, substituindo três capturas e 1,2 segundo.
- Intervalo mínimo para repetir a coleta quando o indicador continua visível reduzido de 1,8 para 0,6 segundo.
- Preservados T por 3 segundos, checagem de capturas recentes, confirmação por recompensa e tratamento de item que reaparece. A latência real depende do processamento das capturas.
- Testes da validação rápida, capturas repetidas e migração única do padrão, além dos testes existentes.

## [7.0.8](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.8)

### Validação após a coleta

- Corrigida a contagem de ausência do indicador Collect: intervalos em que uma captura envelhece enquanto a próxima é processada não apagam mais as evidências já obtidas.
- Somente capturas válidas, distintas e em ordem avançam a contagem. Reaparecimento do indicador, minigame ativo ou lacuna superior a três segundos entre observações reiniciam a verificação.
- Sem evidência suficiente, aguarda novas capturas em vez de gastar automaticamente outra tentativa de T; o limite total de coleta continua valendo.
- Mantida a saída após duas tentativas sem item, desde que a ausência seja validada. Recompensa reconhecida continua encerrando a coleta imediatamente.
- Novo evento `VERIFICACAO_ITEM_APOS_T` no log: visibilidade do indicador/recompensa/minigame, idade e validade da captura, contagem de ausências, tentativa e decisão.

A identificação usa o indicador visual Collect. A ausência desse indicador não comprova, sozinha, a coleta do objeto; esses resultados permanecem separados das recompensas confirmadas.

### Validação

- Testes com processamento lento entre capturas, duas tentativas sem item, item que reaparece, lacuna longa e falta de novas observações. Ainda é necessária validação no jogo ao vivo.

## [7.0.7](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.7)

### Recuperação de lançamentos

- Três lançamentos sem confirmação deixam de provocar pausa definitiva. O macro libera T/mouse e entra em recuperação automática.
- As rodadas de recuperação aguardam 15, 30, 45 e depois até 60 segundos antes de uma nova série de lançamentos, evitando cliques contínuos.
- Antes de relançar, exige leituras recentes e distintas. Se detectar pesca ou item para coletar, trata esse estado antes de lançar novamente.
- Reinicia a busca automática da barra e registra os sinais de pesca, item, região e idade da captura no log da recuperação.
- Preserva contadores/histórico. Pausas manuais, perda de foco e demais paradas explícitas continuam exigindo retomada pelo usuário; não há reconexão automática ao Roblox.

### Validação

- Testes reproduzem o limite de três lançamentos observado em uma sessão longa, retorno da pesca, presença de item, capturas antigas, pausa manual e cem recuperações sucessivas em tempo simulado.
- A correção trata a pausa definitiva identificada no log; os registros não determinam por que o jogo deixou de confirmar os lançamentos. Testes simulados não equivalem a uma noite de execução no Roblox.

## [7.0.6](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.6)

### Log de texto por execução

- Arquivo `.txt` independente a cada abertura do aplicativo, com data, hora, milissegundos e fuso local em cada linha.
- Registro de início, pausa e motivo, fechamento, lançamento, início/fim de minigame, perda/recuperação de leitura, calibração e alterações de ajustes.
- Registro das tentativas de coleta, comandos T, presença do item, recompensa confirmada, item/quantidade reconhecidos e identificação posterior pelo OCR.
- Ciclos sem recompensa ou com coleta não confirmada ficam explicitamente separados de coletas confirmadas.
- Estado periódico a cada 30 segundos e erros internos/reconhecimento por classe de erro, sem mensagens contendo caminhos pessoais.
- Logs locais em `%LOCALAPPDATA%\FishingMacro\logs`, acessíveis por **Abrir logs de texto**. Sessões anteriores são preservadas; o limite de 200 eventos do `runtime.json` não se aplica aos arquivos de texto.
- Cada evento é acrescentado ao arquivo e o arquivo é fechado imediatamente. A interface sinaliza falha de gravação. Uma queda de energia ou encerramento forçado pode impedir o registro do evento final.
- Testes de horários, persistência, sessões distintas, identificação tardia, falha de escrita e integração com início/pausa.

## [7.0.5](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.5)

### Calibração e sessões prolongadas

- Corrigida uma condição em que a calibração podia aceitar texto de uma lista como marcador e salvar uma região incorreta.
- Candidatos de calibração agora precisam de um marcador compacto, preenchido e centralizado, além da geometria do trilho.
- Uma nova região só é confirmada com um sinal independente e recente de minigame ativo.
- Perfis automáticos anteriores são invalidados para aprender novamente com os critérios corrigidos. Seleções manuais, ponto de lançamento, tempo de T e histórico são preservados.
- A validação geométrica também protege leituras automáticas enquanto a região ainda não foi confirmada.

### Registros locais

- Novo `runtime.json`: registra inícios, pausas, perda de foco, limites de tempo e falhas internas tratadas, com até 200 eventos e um estado recente atualizado a cada cinco segundos.
- Ao reabrir, identifica uma sessão anterior que ficou marcada como ativa sem encerramento registrado. Isso é evidência de uma interrupção, não prova da causa.
- Botão **Abrir registros** abre a pasta de dados locais. A opção **Salvar recortes** controla as imagens; o registro textual de execução permanece local e não inclui capturas ou mensagens de exceção.
- Arquivos de execução são ignorados pelo Git e bloqueados pela auditoria de publicação.

### Validação

- Testes de rejeição de texto, migração de perfis, sinal independente de pesca e persistência dos registros.
- Comparação com quadros reais do minigame. Ainda é necessária validação em uma sessão longa no Roblox; não há garantia de execução ininterrupta.

## [7.0.4](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.4)

### Correção de detecção no minigame

- Corrigida a perda de leitura quando o marcador fica fora do alvo e a faixa passa a ficar amarelada/translúcida sobre o cenário azul.
- O detector reconstrói o interior da faixa a partir das bordas coloridas, exigindo continuidade lateral para não unir linhas desconectadas.
- Ajustada a identificação do marcador branco quando ele fica azul-acinzentado com brilho reduzido.
- Mantidos o acompanhamento periódico e a recuperação de localização introduzidos na 7.0.3.

### Validação

- Correção comparada com a versão 7.0.3 no mesmo trecho de uma gravação de reprodução da falha, com aumento de 154 para 275 leituras válidas em 310 quadros analisados. O trecho inclui o desaparecimento do minigame; a contagem não é uma taxa de vitória.
- Adicionados testes sintéticos da faixa translúcida, marcador escurecido e rejeição de linhas coloridas desconectadas. A gravação pessoal não faz parte do repositório ou da distribuição.
- A reprodução em vídeo e os testes automatizados não equivalem a validar uma sessão ao vivo no Roblox.

## [7.0.3](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.3)

### Minigame

- Conferência periódica da posição da barra mesmo após confirmar a calibração automática.
- Recuperação da localização começa após 0,2 segundo sem leitura; a busca continua enquanto há sinal de pesca ativa, respeitando o limite total de 120 segundos.
- Conferências de uma região estável não reiniciam o controlador.
- Detecção trata a sobreposição branca que divide a faixa colorida e descarta regiões brancas grandes antes de selecionar o marcador.

### Coleta

- Recompensa reconhecida encerra a coleta imediatamente, sem gastar as tentativas restantes.
- Quando um item antes identificado deixa de aparecer após T, a sequência pode terminar com três capturas distintas e ao menos 1,2 segundo de ausência persistente. O histórico indica que a recompensa não foi confirmada se não houve aviso de recompensa.
- Sem item identificado nas duas primeiras tentativas, volta a pescar após validar a ausência. As cinco tentativas permanecem como limite para casos ainda não resolvidos.
- Reaparecimento do item reinicia a verificação; capturas repetidas ou antigas não contam como novas evidências de ausência.
- A verificação aguarda capturas mais lentas antes de gastar outra tentativa.

### Validação

- Testes de sobreposição, relocalização, retomada do controle, coleta antecipada, item girando e observações antigas. A validação automatizada não substitui uma sessão no jogo ao vivo.

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
