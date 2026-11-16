# Minigame circular — Beta 0.0.49

O aplicativo usa `CircularEngine` como motor padrão nesta beta. Os leitores do
círculo, splash e Claim estão ligados ao ciclo de pesca. A interface permite
seleção circular manual e exibe a resolução ativa. A distribuição é identificada
como Beta 0.0.49; consulte a página de releases para a disponibilidade publicada.

## Mecânica atual — esclarecimentos de 15 de novembro de 2026

1. Clicar na água para lançar a linha.
2. Esperar o splash e dar outro clique esquerdo. Esse segundo clique pode ser em
   qualquer lugar da janela do jogo.
3. No círculo, o chevron verde para a direita pede segurar o botão direito; o vermelho para a esquerda pede segurar o botão esquerdo. Ambos giram com o marcador. A interpretação anterior de segurar/soltar o mesmo botão foi corrigida pelo usuário e pelo guia.
4. Alguns peixes lendários ou itens de raridade superior também pedem um ou dois
   toques rápidos em A ou D. Um pedido de tecla pode coincidir com o mouse.
   A e D nunca são pedidos simultaneamente.
5. Depois do resultado, coletar segurando T. O aviso agora contém `Claim`, nome
   e peso. O padrão de segurar T por três segundos deve ser preservado.

## Evidências e implementação preparada

Dez trechos locais, gravados em 1920 × 1072, mostram splash, círculo, instruções
do mouse e resultado. A localização usa os segmentos laterais do anel e exige
o arco verde para validar a interface. A posição do marcador não é condição
para localizar o anel: sair da faixa verde não interrompe essa localização.

O objetivo é manter a agulha no arco verde. Desde a Beta 0.0.47,
`CircularReading.mouse_button` indica explicitamente `right`, `left` ou `None`.
`CircularCommand` usa as setas para escolher o botão. A posição permite aliviar
ao alcançar 75% da distância do centro à borda, no sentido da pressão aplicada;
retoma ao voltar para 35%. Essa diferença de margens evita oscilações. A última
direção é conservada entre leituras e um alívio por borda não retoma sem posição
válida. Não pressupõe que soltar provoque inércia para atravessar o centro.

O motor libera o botão oposto antes de pressionar o escolhido. A aplicação
também impõe exclusão entre os dois no envio ao Windows. Término ou ausência do
círculo por pelo menos 150 ms libera ambos. Pausa, foco, resize, erro e fechamento
tentam liberar cada entrada separadamente. As setas brancas superiores não são
interpretadas como M1/M2. Ainda falta identificar visualmente o salto para um
alívio preventivo dedicado; o controle de borda não é um detector de salto.

O leitor foi exercitado em 275 quadros amostrados dos dez vídeos. Foram obtidas
leituras do anel, de ambas as instruções e do resultado dourado. A amostragem
não mede taxa de acerto nem substitui uma sessão real. Testes adicionais
cobrem ambas as setas, mudança de escala/localização, fundos verdes sem anel e
liberação do comando ao perder a interface. A redução a 800 × 599 nesses testes
é sintética; ainda falta uma gravação real nessa resolução.

## Pedidos de A/D encontrados

A revisão mais detalhada encontrou o A ativo à esquerda do círculo, com dois
pontos amarelos abaixo, cerca de 14 segundos após o início do último trecho.
O D permanece desenhado em cinza à direita, mas não está ativo. O recorte
inicial centrado no anel excluía parte desse aviso lateral; portanto, a ausência
de A/D na análise inicial não significava ausência no vídeo.

O leitor agora verifica os dois lados. Exige cartão claro, contorno dourado e
um ou dois pontos para propor a tecla correspondente. Cartões apagados e duas
solicitações conflitantes não geram comandos. O controlador de teclas é
independente do mouse e limita os toques por solicitação, impedindo que o mesmo
aviso gere novos toques a cada quadro. A leitura real encontrada é A com dois
pontos; os casos de um ponto e da outra posição também têm verificação sintética.

Na reprodução do último trecho a intervalos de 100 ms, a leitura reconheceu
o aviso de A com dois pontos entre aproximadamente 14,0 e 14,5 segundos. O
controlador propôs exatamente dois toques, sem repetir em cada quadro. Nenhuma
entrada foi enviada ao jogo nessa verificação.

## Integração e validação

O motor de pesca agora usa os leitores descritos acima. Lançamento e fisgada
têm cliques separados. Mouse e A/D são independentes; as liberações são
programadas sem bloquear a captura. Pausa, perda de foco e mudanças de resolução
liberam entradas. A recuperação não exige reiniciar o programa.

Claim é localizado junto do botão T e lido em tarefa separada. Um nome novo
precisa de duas capturas distintas. O peso fica no histórico e no JSON. O
texto Claim identifica o item; ele não é tratado como aquisição. Sem uma
notificação, a coleta pode ser inferida após segurar T e observar ausência
persistente do aviso. A origem fica no campo confirmation_source.

Os testes exercitam o fluxo completo com entradas simuladas e observações
sintéticas, além dos quadros reais. O executável tem uma verificação própria
de inicialização e tarefas isoladas sem entradas no jogo. A reprodução dos
vídeos mantém as ações gravadas do jogador: não comprova uma vitória causada
pelo macro. D ativo, janelas compactas reais e sessões longas ainda exigem
validação durante o uso. O splash depende de F8 perto de onde a linha cai.

Os vídeos e relatórios ficam locais; apenas recortes de interface sem nomes
de jogadores e caminhos pessoais entram nas referências de teste.

## Correção de splash em zonas de pesca — Beta 0.0.43

O vídeo de 15/11 mostra um efeito contínuo com peixes, arcos brancos e névoa.
A soma global do brilho usada na Beta 0.0.42 podia aumentar com essa animação
ou manter uma referência alta demais para perceber a fisgada. O log também
mostrava cliques sem círculo subsequente e processamento demorado entre leituras.

O leitor agora busca grupos compactos de partículas ciano e sua concentração,
com referência temporal própria. Não depende de um aumento do brilho total da
área. Aprende mesmo antes de armar, preserva o intervalo entre eventos e expira
candidatos não confirmados. O clique e a liberação têm prioridade sobre análises
mais lentas. Os logs incluem os sinais usados para distinguir os eventos.

As regressões usam apenas máscaras binárias ciano anônimas. O trecho de fundo
não gerou acionamentos; os exemplos de fisgada anteriores continuam detectados
com e sem uma zona de pesca. Isso não comprova funcionamento ao vivo na nova
posição ou em outras animações ainda não gravadas.

## Impacto inicial e chevrons coloridos — Beta 0.0.44

O log de 15/11 mostrou uma fisgada cerca de 0,95 segundo após a liberação do
lançamento, compatível com o impacto inicial relatado. A antiga proteção de
0,9 segundo não cobria esse caso. A nova etapa de assentamento tem proteção
padrão de 1,8 segundo e uma breve verificação de estabilização; pode ser
ajustada para voos maiores. Há limite de espera para não bloquear a pesca em
uma área com animação contínua. Um minigame já visível pode retomar de imediato.

A instrução anterior baseada em ↑↑/↓↓ estava incorreta. O comando vem dos
chevrons coloridos junto ao marcador. O leitor normaliza sua rotação e confere
cor e formato. Não usa os avisos brancos nem a posição como substitutos de uma
ordem. Entre leituras válidas, mantém o comando anterior; perder o círculo o
libera. As novas referências contêm apenas setas binárias e recortes do círculo,
sem imagens de personagens, nomes de jogadores ou caminhos locais.

## Estouro azul pequeno — Beta 0.0.45

A gravação posterior contém três estouros que o usuário confirmou como
fisgadas, perto de 1,7, 3,8 e 5,6 segundos. A Beta 0.0.44 não os reconhecia:
o filtro ciano exigia brilho, cor e área incompatíveis com essas gotas menores.
O novo caminho complementar procura núcleos azuis compactos, próximos ao
ponto marcado, com direções distintas. A orientação radial e a predominância
das gotas sobre a máscara da área evitam depender do brilho geral. Em imagens
menores, a intensidade mínima e o tratamento de núcleos com poucos pixels
consideram a mistura de cores causada pela redução. Grupos mais afastados
exigem alinhamento e predominância mais fortes.

O replay original reconheceu os três eventos a 10, 15, 20 e 30 quadros por
segundo; também passaram os exemplos reduzidos a 1280, 960 e 800 pixels de
largura. O vídeo da área sem fisgada continuou negativo nessas verificações.
O replay a 5 quadros por segundo perdeu os eventos: a captura precisa ser
frequente, e o intervalo é registrado no log. Durante a espera, buscas completas
do círculo ocorrem a cada 400 ms, mantendo capturas de splash entre elas. Após
fisgar, a busca mantém seu intervalo anterior. Isso reduz trechos sem leitura,
mas não comprova o desempenho em cada computador ou uma vitória ao vivo.

## Impacto tardio e momento de fisgar — Beta 0.0.46

O novo trecho e o log mostram a queda inicial sendo clicada cerca de 2,57 s após
o lançamento. O usuário confirmou que a puxada perto de 32 s é esse impacto.
A proteção padrão passa a 3 s e monitora a duração do sinal elevado, incluindo
a cauda da animação. Ao chegar ao limite com sinal ainda ativo, não aceita uma
nova fisgada até observar estabilização. O antigo padrão salvo de 1,8 s é migrado
uma vez; outros ajustes, e escolhas posteriores à migração, são mantidos.

Um splash aceito agenda a fisgada para 180 ms depois, por padrão. A espera usa
um estado com prazo, sem bloquear os atalhos. O botão é pressionado por cerca
de 90 ms. Pausa, perda de foco ou círculo já reconhecido cancelam a ação pendente;
mais de 250 ms de atraso além do prazo também cancela o clique. Sem círculo após
quatro segundos, tenta novo lançamento dentro do limite existente, em vez de
puxar novamente a cada emissão de partículas. Os tempos dependem da resposta do
jogo: o atraso é configurável entre 80 e 400 ms e a proteção também é ajustável.
Uma proteção longa pode ignorar a primeira fisgada se ela vier muito cedo.

No replay desse trecho, o impacto perto de 32 s ficou sem clique. O próximo
evento foi lido por volta de 34 s e gerou uma proposta de clique perto de 34,2 s.
No minigame, todos os 87 quadros reconhecidos com aviso vermelho resultaram em
soltar, inclusive com diferença entre a posição e o centro do arco. A regressão
inclui um recorte anônimo desse caso. A gravação não muda com as entradas
propostas; portanto ainda falta validar sua aceitação pelo jogo ao vivo.

## Esclarecimento dos dois botões — Beta 0.0.47

O usuário confirmou que verde/direita significa botão direito e vermelho/esquerda
significa botão esquerdo. Isso também aparece entre 1:30 e 1:40 no
[guia de Ashira RBX](https://www.youtube.com/watch?v=BO6waB_XXhY&t=90s), cuja
legenda e trecho visual foram consultados localmente. O antigo booleano `hold`
misturava duas ações diferentes e foi substituído por um nome de botão.

Os atalhos A/D seguem independentes. A proteção de lançamento e o atraso de
fisgada não mudam nesta correção. Os registros indicam o botão efetivamente
pressionado/liberado e a razão de alívio. Os testes verificam os códigos nativos
Windows de M1/M2, a ordem das trocas e liberação mesmo quando outra entrada
falha. O autoteste do executável também verifica o fluxo dos dois botões,
sem enviar entradas ao jogo. A reprodução de vídeo não demonstra uma vitória
ao vivo nem identifica automaticamente todos os estados de movimento do peixe.

## Perda de leitura e animação da área — Beta 0.0.48

- Corrige a passagem indevida de pesca para coleta após apenas 850 ms sem leitura. Presença do anel e leitura dos controles agora são evidências separadas: com o círculo visível, continua procurando a agulha a cada captura, libera os botões durante a dúvida e não move a mira nem inicia T.
- Uma ausência real exige capturas distintas e persistentes. Se não houver resultado dourado nem Claim, a falha não dispara as tentativas cegas de T herdadas do minigame antigo. Claim e notificações continuam permitindo concluir a rodada; um anel reencontrado interrompe um resultado ainda não confirmado.
- O marcador passa a ser uma componente branca alongada e radial, em vez da mediana de todos os pixels brancos do anel. Os chevrons também podem fornecer sua posição quando o núcleo branco some. A última instrução tem validade curta; depois disso, relê a posição em vez de manter indefinidamente o mesmo botão.
- O splash exige partículas que apareçam fora da máscara colorida do quadro anterior. A tolerância ao movimento considera escala e intervalo entre capturas. Isso rejeita peixes/efeitos da área que apenas mudam de brilho. A memória da água é renovada a cada lançamento; a leitura de splash não disputa processamento com o minigame.
- Aplica a mudança de botão antes de desenhar a prévia ou agendar análises. Reduz a frequência da análise auxiliar durante a luta e impede a fila de OCR de ser preenchida apenas porque a agulha sumiu. Referências do anel redimensionadas são reutilizadas.
- Ativa os recortes locais de diagnóstico também no caminho circular, com limite de quantidade e frequência. O log passa a incluir pontuação/posição do anel, posição e origem da agulha, alvo, faixa, pontuações das setas e motivo da rejeição. Não publica gravações ou registros pessoais.
- Verificação: regressões de perda prolongada/releitura, comandos vencidos, prioridade do controle, ausência persistente, OCR e diagnóstico; replay preserva as três fisgadas azuis confirmadas pelo usuário em diferentes taxas e tamanhos e rejeita um trecho adicional de oito segundos só com animação da área. O executável verifica perda de leitura e retomada no autoteste. Esses testes não comprovam vitória ou uma sessão longa ao vivo.

## Beta 0.0.49 — fisgada em áreas com efeitos intensos

- A sessão analisada da Beta 0.0.48 lançou a vara, ficou esperando e não registrou nenhuma fisgada nem entrada no círculo. A gravação correspondente mostra clarões da boia descartados pelo filtro de predominância das gotas sobre toda a área. A pausa final foi precedida por redimensionamento e perda de foco, não por um encerramento interno do aplicativo.
- Acrescenta uma leitura rápida do clarão ciano perto da boia, comparando intensidade, núcleo muito brilhante e crescimento em relação a cerca de 200 ms antes. Não divide esse sinal pela animação inteira da área. A leitura de gotas azuis pequenas permanece disponível; a proteção após lançar e o atraso configurável antes do clique são preservados.
- Durante a espera, a busca pesada do círculo passa para o processo de calibração. O resultado só fornece uma indicação de localização: a captura atual precisa confirmar os controles antes de qualquer entrada. Resultados antigos ou de outra sessão não movimentam o mouse. A espera usa agendamento mais frequente, sem prometer uma taxa de captura independente do computador.
- A prévia mostra a água marcada enquanto aguarda a fisgada. Logs incluem brilho local, núcleo, referência, crescimento e intervalo entre capturas. Com diagnósticos ativados, uma espera prolongada também salva um recorte local da água e indicadores limitados, em vez de depender de entrar no minigame para produzir evidências.
- Regressões usam somente máscaras de cinco limiares de cor da gravação, sem intensidades RGB originais, nomes, personagens, caminhos ou áudio. Incluem os três splashes completos e o começo de outro no último quadro nativo. Os controles negativos e os exemplos anteriores de gotas pequenas permanecem cobertos. Uma luz ciano estática não é fisgada.
- Os 220 testes gerais passaram antes da alteração da numeração. As verificações específicas são repetidas com os novos dados; o executável verifica também a localização circular em processo separado. Replay mede reconhecimento e propostas de entrada: não confirma aceitação do clique, vitória no círculo ou estabilidade de uma partida longa. Essa sessão não contém um minigame circular para validar seu controle.
