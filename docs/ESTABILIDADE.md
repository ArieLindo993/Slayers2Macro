# Investigação de estabilidade — 7.2.1

## Falha confirmada

A sessão analisada continuava com `ativo=True`, mas permaneceu em `RECUPERANDO` por mais de quatro minutos depois de anunciar nova tentativa em 15 segundos. A pausa por perda de foco ocorreu depois. Não foi encontrado um erro interno que explicasse esse intervalo.

O motor exigia duas capturas recentes para relançar, mas zerava a contagem em todo tick no qual a última captura tivesse envelhecido. Com análises de aproximadamente 0,7 segundo, a captura anterior frequentemente passava do limite antigo de um segundo antes de chegar a próxima. Assim, cada confirmação apagava-se antes de formar um par. A correção anterior da coleta tratava um problema semelhante, mas a recuperação de lançamentos ainda continha esse defeito.

A reprodução com o motor anterior, 400 capturas distintas e intervalos sem leitura manteve o estado preso por 281 segundos. A regressão agora exige saída da recuperação após o prazo e duas evidências válidas. Nenhum log, vídeo, configuração ou caminho pessoal foi incluído neste repositório.

## Áreas revisadas

| Área | Resultado e tratamento |
| --- | --- |
| Motor e prazos | Corrigida a contagem da recuperação; retirado o encerramento definitivo por 120 segundos; confirmação de pesca distingue capturas de ticks. |
| Sinais e calibração | Resultados úteis eram descartados após um segundo; calibração consultava um sinal de outra captura. Corrigidos idade limitada e vínculo com a mesma imagem. |
| Trabalho em segundo plano | Threads travadas não podiam ser encerradas; OCR podia acumular confirmações. Processos com prazo e fila limitada permitem reinício e encerramento previsíveis. |
| Captura e janela | Falha temporária de captura agora recupera. Mudança de geometria da mesma janela é distinta de perda de foco. |
| Detector e controlador | Mantidos os critérios geométricos e o controle do marcador; regressões cobrem alvo translúcido, marcador fora da faixa e distrações de texto/branco. |
| Coleta e histórico | Mantidos T por três segundos, confirmação de recompensa, ausência persistente e saída após duas tentativas sem item. Capturas inválidas não são novas evidências. |
| Armazenamento e interface | Histórico e tabela crescem com o número de registros, mas o custo medido no volume da sessão não explica a parada. Journal e recortes têm limites. Falhas de gravação são tratadas. |
| Instalação | Encontrado problema independente: um executável extraído parcialmente podia fazer uma instalação parecer completa. Adicionada validação da extração antes da substituição. |

## Limites usados

- Análises da cena são aceitas por até 2,5 segundos. A leitura que movimenta o marcador vem de uma captura atual separada.
- A recuperação conserva evidências por até três segundos; imagens antigas, repetidas e fora de ordem não avançam a decisão.
- Sem leitura atual da barra nem cena utilizável por cinco segundos, solta comandos e entra em recuperação.
- Tarefas de sinais, calibração e recortes têm prazo de dez segundos. OCR tem trinta segundos, incluindo espera e carregamento inicial.
- No máximo uma tarefa pendente por serviço visual/diagnóstico e três tarefas de OCR. Um timeout encerra o processo e invalida suas tarefas; a próxima solicitação inicia outro.
- A espera entre rodadas de lançamento continua sendo 15, 30, 45 e até 60 segundos. Pausas manuais e perda real de foco não são retomadas automaticamente.

## Verificação reproduzível

Execute `python -m unittest discover -s tests -v` no Windows com as dependências instaladas. A suíte contém 70 testes. Os novos grupos cobrem integração da interface (`test_app_recovery.py`), duração e evidências (`test_engine_endurance.py`), processos (`test_background.py`) e integridade do atualizador (`test_update_integrity.py`).

A simulação de oito horas percorre os estados reais de lançamento, espera e recuperação com leituras atrasadas e intervalos inválidos. Não altera artificialmente o estado para desbloquear uma rodada. Testes separados cobrem retorno ao acompanhamento, coleta, expiração do marcador, pausas manuais e falta de foco.

A revisão também verificou análises de 1,2, 1,6 e 2,4 segundos. A expiração entre entregas usa o horário de recebimento, enquanto a distância entre capturas usa seus carimbos próprios; misturar esses dois relógios contava o processamento duas vezes e recriava o travamento. Os testes incluem pesca ativa sem marcador e recuperação antes de relançar.

Na validação local com material fornecido foram conferidos 28 quadros de pesca/coleta/recompensa e o reconhecimento de duas recompensas reais. A verificação rápida durante uma pesca reconhecida levou cerca de 11 ms, contra 362 ms da busca completa nessa medição; a busca completa continua necessária periodicamente e na coleta. São medidas locais, não uma garantia para outros computadores.

Os testes dos processos provocam travamento, encerramento inesperado, erro de análise, fila cheia e interrupção durante transmissão de uma imagem grande. O fechamento tem espera limitada. A geração do executável exige um autoteste que inicia os processos de visão, calibração e OCR usando imagens artificiais, sem comandos ao jogo.

O histórico permanece inteiro; os registros resumidos continuam limitados a 200 eventos e os recortes a 20 pares. A investigação não encontrou evidência de que apagar o histórico resolveria o incidente.

## Limites da conclusão

A falha registrada foi reproduzida e coberta por regressões. Os testes não demonstram uma noite completa de execução no Roblox ao vivo, nem permitem garantir ausência de qualquer falha futura. Mudanças no jogo, desconexão e perda de foco precisam ser distinguidas de defeitos do macro. Os novos campos do log permitem identificar se uma próxima ocorrência está no motor, no processamento, na captura ou em uma pausa explícita.
