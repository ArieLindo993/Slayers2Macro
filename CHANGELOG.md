# Histórico de versões

**Português** · [English](docs/CHANGELOG.en.md) · [Español](docs/CHANGELOG.es.md)

Alterações verificadas nas tags e no código do repositório. A versão mais recente pode ser instalada pelo atualizador.

## [Beta 0.0.41](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.41-beta)

### Captura contínua, primeira recompensa e calibração completa

- Corrige um bloqueio no agendamento: a captura de notificações e a recalibração agora continuam enquanto a análise anterior da cena está ocupada. Uma fila limitada guarda as imagens com o horário e o ciclo originais; resultados atrasados atualizam a coleta certa, sem duplicar a contagem.
- O OCR amplia pequenas regiões de texto, em vez de ampliar todo o cenário quatro vezes. Encerra a busca quando reconhece nome e recompensa válidos. Nos quadros compactos testados, Metal Scraps, Crustadon, Krathulon e OuwFish foram reconhecidos; o tempo varia conforme o quadro e a carga do computador.
- A primeira aquisição pode mostrar um selo amarelo NEW! em vez de ×1. O leitor aceita esse selo somente junto de um nome conhecido e alinhado. Collect e nomes isolados continuam sem confirmar uma coleta.
- A calibração rejeita alvos cortados pela borda do recorte e prefere o trilho completo aos contornos internos. Com a pesca confirmada pelo indicador independente, a sobreposição do marcador com o cenário não aciona o filtro mais restrito usado para localizar uma nova barra.
- Acrescenta uma referência nativa do texto Collect compacto, mantendo o limite de aceitação em 0,80. A revisão do detector passa a 5 e renova perfis automáticos antigos; configurações manuais são preservadas.
- O log passa a registrar cada resultado do OCR, incluindo idade da imagem, tamanho da fila, caixas e quantidades encontradas. Nova sessão descarta imagens pendentes da anterior.
- Validação: testes automatizados, replay de quadros locais em 800×599 e teste do executável compilado. O replay verifica as imagens gravadas; não equivale a uma sessão longa controlando o Roblox ao vivo. `tools/replay_video.py` permite repetir a análise com gravações locais, sem publicá-las.

## [Beta 0.0.40](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.40-beta)

### Rastreamento compacto e leitura da recompensa sobre o personagem

- A gravação em 800×599 revelou que o botão “Exit” do minigame marcava 0,823, abaixo do limite 0,83. O detector agora aceita o sinal a partir de 0,78, preservando a confirmação por quadros distintos do fluxo existente.
- Sobre a ilha verde, o contorno do alvo fica verde-limão em alguns quadros, e não amarelo. O detector agora pareia os dois contornos saturados (amarelo ou verde-limão), sem confundir a grande área verde do mapa com a faixa.
- O item obtido aparece como uma etiqueta pequena sobre o personagem. Na captura real, o OCR leu “OuwFish” e “X” porque o `1` de `x1` é pequeno. O leitor agora aceita esse caso apenas quando o X está alinhado junto a um nome conhecido; um X solto não confirma item.
- Os quadros reais enviados agora recuperam leituras da barra em cinco momentos consecutivos sobre a ilha, e o OCR lê “OuwFish × 1” no quadro compacto. Testes também verificam a margem de detecção do botão e rejeitam falsos positivos sem faixa ou sem nome alinhado.

## [Beta 0.0.39](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.39-beta)

### Resolução compacta, coleta e rastreamento em fundos verdes

- O log de 800×599 concluiu 16 ciclos sem uma coleta confirmada. A varredura encontrou um erro geométrico: o selo era localizado em coordenadas do cliente Roblox, mas o recorte de OCR usava uma imagem centralizada em 1920×1080; a conversão anterior deslocava o recorte, especialmente na vertical. Agora a posição do OCR inclui a moldura da janela e a posição usada para o ícone fica separada.
- Uma correspondência fraca do selo pode orientar uma tentativa adicional de OCR a partir de 0,50. Ela não confirma uma recompensa: nome e quantidade continuam passando pela validação existente. O recorte alternativo compacto agora parte do centro da imagem do jogo.
- Os modelos de aviso de coleta e de pesca são comparados em escalas proporcionais ao tamanho atual do Roblox. A lateral da interface mostra explicitamente a resolução ativa.
- O alvo verde agora é localizado primeiro por suas duas bordas amarelas, independente da cor do preenchimento. Isso recupera a barra quando uma área verde do mapa se funde com o alvo, inclusive em recortes estreitos de janela pequena. A revisão do detector é atualizada para reiniciar apenas perfis automáticos antigos.
- Os 129 testes automatizados cobrem aviso e pesca em 800×599/1280×720, coordenadas do recorte centralizado, ausência de falsos avisos e alvo amarelo sobre mapa verde. As capturas diagnósticas que falhavam agora produzem leituras válidas; uma sessão nova no Roblox ainda precisa confirmar o comportamento ao vivo.

## [Beta 0.0.38](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.38-beta)

### Leitura de recompensa em janela pequena

- No ciclo compacto do log enviado, o macro detectou o minigame, detectou o item na vara, pressionou T e viu o aviso desaparecer, mas o OCR não encontrou nome nem quantidade. A sessão passou para tela cheia depois desse único ciclo compacto; ela não comprova uma falha em todos os ciclos pequenos.
- As capturas compactas agora mantêm a escala original em vez de esticar a imagem até 1920×1080 antes do OCR. O reconhecimento tenta também um segundo recorte independente na região central superior, mesmo que a detecção fraca do selo tenha apontado para outro lugar.
- A validação continua exigindo texto de nome e quantidade. O desaparecimento do item sozinho não vira uma coleta confirmada.
- 125 testes automatizados cobrem geometria compacta, recorte alternativo, atribuição de ciclo e recuperação. Eles confirmam a lógica com imagens e OCR simulados; falta uma nova sessão real em 800×599 para validar o resultado dentro do Roblox.

## [Beta 0.0.37](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.37-beta)

### Varredura do OCR e estabilização da janela

- O log mais recente mostrou seis ciclos concluídos sem recompensa lida; as melhores correspondências do selo ficaram em 0,71–0,77, abaixo do limite de confirmação de 0,91. A busca ampliada da Beta 0.0.36 não cobria a diferença de escala do selo em janelas compactas.
- Compara o selo em várias escalas que preservam sua proporção. Uma correspondência fraca pode orientar o recorte do OCR, mas não confirma a recompensa nem reduz a validação visual.
- O mesmo log registrou cerca de 35 recuperações em sequência enquanto a geometria reportada continuava 800×599. Mudanças de posição ou identificador com o mesmo tamanho agora atualizam a janela sem reiniciar o ciclo; uma mudança de resolução precisa permanecer estável por 250 ms e gera uma recuperação única.
- Os logs de OCR agora registram dimensões do recorte, quantidade de caixas encontradas, melhores confianças numéricas e dados de escala/posição da janela, sem salvar imagens nem o texto bruto do OCR.
- Testes automatizados cobrem avisos pequenos e fracos, além de oscilações de HWND/posição. Uma nova sessão real ainda é necessária para confirmar a leitura do aviso no Roblox.

## [Beta 0.0.36](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.36-beta)

### Detecção de avisos em posições variáveis

- O último log mostrou que a busca começava abaixo do aviso nas janelas 800×599: 0/10 avisos pequenos e 8/10 em tela cheia foram detectados, apesar dos 20 ciclos concluídos.
- Amplia a região de busca do aviso tanto na geometria fixa quanto na interface escalada.
- Aumenta a altura do recorte de OCR para alcançar notificações posicionadas acima da referência de tela cheia.
- Inclui regressão que reproduz a notificação acima da antiga faixa de busca.
- Ainda precisa de confirmação em uma sessão real com as duas resoluções; a correção de geometria não permite afirmar funcionamento perfeito.

## [Beta 0.0.35](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.35-beta)

### Correção da coleta em janela pequena

- Amplia o recorte da notificação para incluir o aviso inteiro em janelas menores e quando o nome e a quantidade aparecem na mesma linha.
- Um OCR que termina antes de o ciclo entrar no histórico fica guardado e é associado à coleta correta assim que ela for registrada.
- Avisos que ainda estão na tela durante a espera pela próxima fisgada não são atribuídos ao ciclo novo.
- Diagnóstico do último log: 10/10 coletas na janela de 800×599 não tiveram aviso reconhecido; em tela cheia, 8/10 tiveram. Os nomes foram lidos nos avisos detectados, mas as demais coletas foram registradas como não confirmadas. A alteração trata as falhas como problema de leitura e de associação de ciclo.
- Mantém a validação de nomes e a contagem de possíveis pescas vazias.

## [Beta 0.0.34](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.34-beta)

### Recuperação de notificações e OCR

- Detecta avisos de recompensa tanto com a interface fixa quanto com a interface que escala com a janela. Escolhe o recorte correspondente à geometria detectada.
- Se a leitura normal não separar bem o texto pequeno ou parcialmente apagado, tenta também uma imagem com contraste local reforçado. A quantidade e o nome continuam sujeitos à validação existente.
- Diagnóstico no log mostra a geometria usada, a semelhança visual do aviso e se o OCR encontrou algum texto de recompensa.
- Evidência local: o log anterior registrou 9 ciclos sem indicador ou aviso de item, depois identificou Crustadon x1 quando a notificação apareceu; outra notificação foi detectada, mas o Roblox perdeu o foco antes da leitura terminar.
- Validação: 112 testes e auditoria de empacotamento passaram, incluindo 5 verificações de geometria. Ainda precisa de confirmação em uma sessão real contínua.

## [Beta 0.0.33](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.33-beta)

### Validação rigorosa dos nomes

- Catálogo de nomes observados e correções explícitas para variantes de Golden Fish, Clown Fish, Crustadon, Coral, Sea Horse e outros. Itens diferentes como OuwFish/OuwFwesh e Refinement Ore/Mythic Refinement Ore permanecem separados.
- Fragmentos como “Fish”, “a Fish” e “Ore”, palavras cortadas na borda e possíveis erros próximos de nomes conhecidos ficam como **Nome não identificado**, preservando a quantidade da recompensa.
- Nomes novos exigem duas imagens diferentes com leitura concordante e confiança alta. Reprocessar a mesma imagem não confirma um nome novo; erros parecidos com nomes conhecidos não são aprendidos como espécies novas.
- Uma leitura posterior conflitante não substitui um nome já validado. A identificação pode ser concluída depois sem duplicar a coleta. Pendências de confirmação têm memória limitada.
- Eventos de nomes pendentes e conflitos ficam no log. Arquivos antigos são preservados; a validação se aplica aos novos registros.
- Mantém as correções de miniaturas e recompensas diretas da Beta 0.0.32.
- Validação: 107 testes, reprodução local dos nomes de um histórico real com quantidades preservadas e leitura de OuwFish/Metal Scraps em capturas reais. Dados pessoais não publicados.

## [Beta 0.0.32](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.32-beta)

### Ícones nítidos e itens enviados ao inventário

- Notificações de recompensa verificadas também durante a leitura rápida do minigame. Um aviso novo pode confirmar um item enviado direto ao inventário, sem indicador Collect e sem exigir T.
- Se o aviso surge no último quadro do minigame, a evidência fica guardada até a pesca encerrar. Aviso já visível ao iniciar ou persistente da rodada anterior não é contado novamente.
- OCR recebe o recorte da mesma captura que detectou a notificação, associado ao ciclo original. O caminho de leitura de texto também começa quando a barra desaparece.
- Miniaturas escolhidas entre capturas distintas, usando contraste da notificação e detalhes do ícone. Quadros muito esmaecidos não são salvos; uma imagem melhor pode substituir a anterior, sem trocar por outra pior durante o desaparecimento.
- A miniatura melhor é reutilizada nas entradas do mesmo item desta sessão. Registros antigos em disco não são reprocessados; quando não houver quadro adequado, permanece o traço.
- Eventos de notificação e atualização de ícone registrados no log.
- Verificação: 99 testes automatizados e seleção do quadro mais nítido em uma sequência real fornecida. A entrada direta no inventário foi testada por simulação; ainda precisa ser acompanhada no jogo.

## [Beta 0.0.31](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.31-beta)

### Numeração beta desde o início

- Todas as versões são classificadas como beta, de Beta 0.0.0 até a atual Beta 0.0.31. Inclui pacotes pré-Git, variantes intermediárias e o protótipo AutoHotkey.
- [Tabela de correspondência](docs/VERSIONAMENTO.md) registra identificadores antigos, hashes dos pacotes locais e tags preservadas. Tentativas sem artefato não recebem uma versão inventada.
- Interface e título exibem Beta 0.0.31; logs identificam 0.0.31-beta. Nomes e descrições das releases anteriores atualizados no GitHub. Os pacotes históricos permanecem originais.
- Atualizador mostra o nome público da release e continua instalando por ID. Canal de download preservado; sem reset de dados, atalhos ou idioma.
- Mudança de nomenclatura, documentação e distribuição; mecânicas de pesca mantidas.

## [Beta 0.0.30](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.4.0)

### Idiomas e atalhos

- Interface em português (padrão), inglês e espanhol, selecionável em **Configurar → Idioma e atalhos**. Aplicação imediata ao salvar, sem perder histórico ou contadores.
- Tradução da tela principal, mensagens da pesca, configurações, histórico, seleção manual e CSV exportado pelo botão. Nomes dos itens permanecem os do jogo; logs e dados automáticos mantêm seu formato técnico estável.
- Atalhos configuráveis para iniciar/pausar, marcar água, selecionar barra (principal e alternativo) e parar. Padrões preservados: F4, F8, F6, F7 e F10, respectivamente.
- Teclas F1–F12, letras e números, com T reservado à coleta. Validação contra duplicação e botão para restaurar padrões. Textos da interface acompanham as teclas escolhidas.
- Configurações pausam a pesca e bloqueiam os atalhos enquanto são editadas. Na seleção manual, a tecla personalizada de parada cancela a seleção; Enter e Esc permanecem disponíveis.
- Preferências salvas localmente, independentes dos perfis de calibração. Configurações antigas ou inválidas usam os padrões. Nenhuma alteração no controlador, nos tempos ou na tecla T enviada ao jogo.
- Guias e históricos de versões em três idiomas, com links de escolha no GitHub e nos pacotes. Scripts do atualizador permanecem em português.

### Verificação

- 88 testes automatizados, incluindo traduções, parâmetros das mensagens, atalhos personalizados, rejeição de conflitos, persistência, exportação e preservação do histórico.
- Testes anteriores de pesca e estabilidade mantidos; inspeção visual das janelas traduzidas.

## [Beta 0.0.29](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.1)

### Contagem e nomes dos itens

- Uma recompensa lida depois do encerramento da coleta agora corrige a linha original e o contador de coletas confirmadas, uma única vez. A demora de inicialização do OCR não invalida mais uma leitura apenas por ultrapassar quatro segundos.
- Novas tentativas de leitura durante a preparação da próxima pesca também atendem coletas ainda não confirmadas. O desaparecimento do item, sozinho, continua sem ser prova de recompensa.
- Área de leitura ampliada para evitar cortes no aviso; palavras separadas pelo OCR na mesma linha são reunidas.
- “Clown”, “Clown F”, “Clown Fi”, “Clown Fis” e “Clown Fish” usam o nome “Clown Fish”, inclusive nos totais e na associação de ícones. Diferenças de maiúsculas também reutilizam a grafia já registrada na sessão. Espécies diferentes não são fundidas por semelhança de nome.
- Históricos de sessões antigas permanecem preservados; a correção se aplica aos novos registros.

### Verificação

- 81 testes automatizados, incluindo primeira recompensa atrasada, contador sem duplicação, vínculo ao ciclo original, nomes fragmentados e espécies distintas.
- OCR conferido em quadros reais de OuwFish e Metal Scraps. A notificação específica da primeira descoberta ainda precisa ser conferida no jogo; nenhuma coleta é inventada quando não há evidência legível.

## [Beta 0.0.28](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.0)

### Ícones dos itens

- Miniaturas reais do aviso de recompensa nas abas Resumo e Histórico, ao lado do nome do item.
- Recorte associado à mesma captura que reconheceu a recompensa e ao ciclo de origem, inclusive quando a análise termina depois da coleta.
- Reutilização da miniatura por nome reconhecido e associação posterior quando o OCR identifica o item; coletas não confirmadas não recebem imagem.
- Ícones persistidos no JSON local do histórico. Exportação CSV permanece compatível e somente textual.
- Até 256 miniaturas distintas por sessão; ausência de imagem ou limite atingido não impede registrar itens nem pescar.
- Mantidos controlador do minigame, tempos, atalhos e recuperação da Beta 0.0.27.

### Verificação

- 77 testes automatizados, incluindo recorte em resoluções diferentes, identificação tardia, deduplicação, limite de memória, descarte de análise antiga e exibição nas duas tabelas.
- Inspeção da interface com miniaturas de OuwFish e Metal Scraps extraídas de gravações reais fornecidas. Imagens e históricos pessoais não integram a distribuição.

## [Beta 0.0.27](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.2.2)

### Recuperação em sessões longas

- Corrigido o travamento em `RECUPERANDO`: intervalos curtos sem leitura não apagam mais a primeira confirmação necessária para relançar. Capturas repetidas, fora de ordem ou anteriores à recuperação não contam como novas evidências.
- Confirmar pesca pelo indicador visual agora exige capturas independentes; reutilizar uma imagem em dois ticks não equivale a duas confirmações.
- Removida a pausa definitiva de 120 segundos. Esse prazo agora conta a ausência do marcador e inicia recuperação; o acompanhamento válido continua normalmente.
- Resultados de análise entre 1 e 2,5 segundos deixam de ser descartados prematuramente. Capturas mais antigas continuam inválidas; o controle da barra usa sua própria captura atual.
- Calibração valida o candidato e o indicador de pesca na mesma imagem, eliminando a dependência de uma análise anterior atrasada.
- Visão, calibração, OCR e diagnóstico passam a usar processos reiniciáveis e filas limitadas. Travamento ou falha de um deles não encerra automaticamente a sessão nem acumula tarefas indefinidamente.
- Perda temporária da captura inicia recuperação e recria o capturador. Alterar a posição/tamanho da mesma janela ajusta as coordenadas; pausa manual e perda real de foco continuam exigindo F4.
- Durante o controle válido da barra, verificações rápidas evitam buscas completas desnecessárias. Uma verificação completa continua sendo solicitada periodicamente, e o desaparecimento do indicador aciona a busca de coleta/recompensa.

### Diagnóstico e instalação

- Logs passam a registrar atraso de análise, descartes, duração máxima de atualização, contagem de evidências e prazo de recuperação, filas e reinícios dos processos. Erros internos incluem etapa e origem sem caminhos pessoais.
- Corrigida a instalação incompleta após interrupção da extração: arquivos são verificados em uma pasta temporária antes de substituir a versão instalada.
- A verificação SHA-256 usa diretamente o .NET do Windows, evitando falhas quando o ambiente não disponibiliza o comando Get-FileHash.
- Preservados F8/F4/F6/F10, duração padrão de T, calibração manual, configurações, histórico e arquivos locais.

### Validação

- 72 testes automatizados, incluindo oito horas simuladas com capturas lentas, atrasos de até 2,4 segundos, tarefas travadas/encerradas, transmissão interrompida de imagens, falhas de captura, coleta, pausas, calibração e instalação interrompida.
- Verificação local de 28 quadros de gravações fornecidas, reconhecimento de duas recompensas reais e controle simulado; esses arquivos pessoais não integram o pacote.
- Autoteste também exercita visão, calibração e OCR em processos separados no executável empacotado.
- [Relatório da investigação](docs/ESTABILIDADE.md). Simulação e reprodução de falhas não equivalem a uma noite de validação no Roblox ao vivo.

## [Beta 0.0.24](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.1)

### Cabeçalho

- Ícone de anzol substituído pelo ícone da página de Slayers 2 no Roblox indicada pelo usuário.
- Removido o padrão de quadrados verdes.
- Imagem incluída no pacote; não exige conexão para exibir o cabeçalho.
- Alteração exclusivamente visual, sem mudanças nas mecânicas ou configurações.

## [Beta 0.0.23](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.0)

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

## [Beta 0.0.22](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.9)

### Verificação de coleta mais rápida

- Espera padrão pelo item após o minigame reduzida de 12 para 2 segundos. O antigo valor padrão salvo de 12 segundos é migrado uma vez; outros valores personalizados são preservados.
- Ajuste manual dessa espera agora aceita valores de 0,5 a 20 segundos.
- Após soltar T, a ausência pode ser validada por duas capturas distintas ao longo de pelo menos 0,6 segundo, substituindo três capturas e 1,2 segundo.
- Intervalo mínimo para repetir a coleta quando o indicador continua visível reduzido de 1,8 para 0,6 segundo.
- Preservados T por 3 segundos, checagem de capturas recentes, confirmação por recompensa e tratamento de item que reaparece. A latência real depende do processamento das capturas.
- Testes da validação rápida, capturas repetidas e migração única do padrão, além dos testes existentes.

## [Beta 0.0.21](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.8)

### Validação após a coleta

- Corrigida a contagem de ausência do indicador Collect: intervalos em que uma captura envelhece enquanto a próxima é processada não apagam mais as evidências já obtidas.
- Somente capturas válidas, distintas e em ordem avançam a contagem. Reaparecimento do indicador, minigame ativo ou lacuna superior a três segundos entre observações reiniciam a verificação.
- Sem evidência suficiente, aguarda novas capturas em vez de gastar automaticamente outra tentativa de T; o limite total de coleta continua valendo.
- Mantida a saída após duas tentativas sem item, desde que a ausência seja validada. Recompensa reconhecida continua encerrando a coleta imediatamente.
- Novo evento `VERIFICACAO_ITEM_APOS_T` no log: visibilidade do indicador/recompensa/minigame, idade e validade da captura, contagem de ausências, tentativa e decisão.

A identificação usa o indicador visual Collect. A ausência desse indicador não comprova, sozinha, a coleta do objeto; esses resultados permanecem separados das recompensas confirmadas.

### Validação

- Testes com processamento lento entre capturas, duas tentativas sem item, item que reaparece, lacuna longa e falta de novas observações. Ainda é necessária validação no jogo ao vivo.

## [Beta 0.0.20](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.7)

### Recuperação de lançamentos

- Três lançamentos sem confirmação deixam de provocar pausa definitiva. O macro libera T/mouse e entra em recuperação automática.
- As rodadas de recuperação aguardam 15, 30, 45 e depois até 60 segundos antes de uma nova série de lançamentos, evitando cliques contínuos.
- Antes de relançar, exige leituras recentes e distintas. Se detectar pesca ou item para coletar, trata esse estado antes de lançar novamente.
- Reinicia a busca automática da barra e registra os sinais de pesca, item, região e idade da captura no log da recuperação.
- Preserva contadores/histórico. Pausas manuais, perda de foco e demais paradas explícitas continuam exigindo retomada pelo usuário; não há reconexão automática ao Roblox.

### Validação

- Testes reproduzem o limite de três lançamentos observado em uma sessão longa, retorno da pesca, presença de item, capturas antigas, pausa manual e cem recuperações sucessivas em tempo simulado.
- A correção trata a pausa definitiva identificada no log; os registros não determinam por que o jogo deixou de confirmar os lançamentos. Testes simulados não equivalem a uma noite de execução no Roblox.

## [Beta 0.0.19](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.6)

### Log de texto por execução

- Arquivo `.txt` independente a cada abertura do aplicativo, com data, hora, milissegundos e fuso local em cada linha.
- Registro de início, pausa e motivo, fechamento, lançamento, início/fim de minigame, perda/recuperação de leitura, calibração e alterações de ajustes.
- Registro das tentativas de coleta, comandos T, presença do item, recompensa confirmada, item/quantidade reconhecidos e identificação posterior pelo OCR.
- Ciclos sem recompensa ou com coleta não confirmada ficam explicitamente separados de coletas confirmadas.
- Estado periódico a cada 30 segundos e erros internos/reconhecimento por classe de erro, sem mensagens contendo caminhos pessoais.
- Logs locais em `%LOCALAPPDATA%\FishingMacro\logs`, acessíveis por **Abrir logs de texto**. Sessões anteriores são preservadas; o limite de 200 eventos do `runtime.json` não se aplica aos arquivos de texto.
- Cada evento é acrescentado ao arquivo e o arquivo é fechado imediatamente. A interface sinaliza falha de gravação. Uma queda de energia ou encerramento forçado pode impedir o registro do evento final.
- Testes de horários, persistência, sessões distintas, identificação tardia, falha de escrita e integração com início/pausa.

## [Beta 0.0.18](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.5)

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

## [Beta 0.0.17](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.4)

### Correção de detecção no minigame

- Corrigida a perda de leitura quando o marcador fica fora do alvo e a faixa passa a ficar amarelada/translúcida sobre o cenário azul.
- O detector reconstrói o interior da faixa a partir das bordas coloridas, exigindo continuidade lateral para não unir linhas desconectadas.
- Ajustada a identificação do marcador branco quando ele fica azul-acinzentado com brilho reduzido.
- Mantidos o acompanhamento periódico e a recuperação de localização introduzidos na Beta 0.0.16.

### Validação

- Correção comparada com a versão Beta 0.0.16 no mesmo trecho de uma gravação de reprodução da falha, com aumento de 154 para 275 leituras válidas em 310 quadros analisados. O trecho inclui o desaparecimento do minigame; a contagem não é uma taxa de vitória.
- Adicionados testes sintéticos da faixa translúcida, marcador escurecido e rejeição de linhas coloridas desconectadas. A gravação pessoal não faz parte do repositório ou da distribuição.
- A reprodução em vídeo e os testes automatizados não equivalem a validar uma sessão ao vivo no Roblox.

## [Beta 0.0.16](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.3)

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

## [Beta 0.0.15](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.2)

### Alterações

- Tempo padrão de coleta com **T aumentado de 1,5 para 3 segundos**.
- Configurações já salvas continuam preservadas. Para aplicar o novo tempo a uma instalação existente, salve 3 em “Segurar T (s)”.
- Atualizador passou a mostrar mensagens ao preparar, consultar o GitHub, baixar, verificar a integridade e extrair os arquivos.
- Consulta da versão mais recente passou a ter limite de espera de 30 segundos.

## [Beta 0.0.14](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.1)

### Correções

- Prévia visual reduzida para caber melhor no painel lateral.
- Cada perfil de tela passou a preservar e restaurar sua escolha entre calibração automática e manual.
- Trocar de perfil passou a atualizar também a opção correspondente na interface.

## [Beta 0.0.13](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.0)

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

## [Beta 0.0.12](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v6.1.0)

Primeira versão registrada neste repositório. Os recursos abaixo já estavam presentes nessa base; não é possível atribuir cada um a uma versão anterior usando o histórico Git disponível.

### Recursos da base

- Lançamento por clique no ponto salvo com F8 e controle de início/pausa com F4.
- Parada com F10 e seleção manual da barra com F6, por arraste sobre uma captura congelada.
- Localização automática da barra e aprendizado entre rodadas confiáveis.
- Controle do minigame e coleta segurando T, inclusive sem depender da identificação visual do item para tentar coletá-lo.
- Tentativas limitadas de lançamento e coleta, tratamento de falta de recompensa e pausa ao perder o foco.
- Histórico da sessão com leitura de nomes de itens e arquivos JSON/CSV.
- Executável Windows, compilação automatizada e atualizador apontando para este repositório, com verificação SHA-256 do pacote.

### Distribuição após a tag Beta 0.0.12

- O empacotamento de `Atualizador.zip` foi acrescentado no commit `bd78a01`, entre as tags Beta 0.0.12 e Beta 0.0.13. Ele não representa uma nova versão do motor de pesca.

## Protótipos anteriores

Antes da primeira tag, o desenvolvimento passou por ajustes de clique para lançar, duração do T, tentativas de coleta quando o item girava fora do alcance, interface, identificação de itens e calibração. Esses pedidos fazem parte do contexto do projeto, mas não há tags anteriores neste repositório para comprovar uma lista exata de mudanças por versão. Por isso, não são apresentados como releases numeradas ou correções verificadas.
