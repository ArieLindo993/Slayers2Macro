# Minigame circular — Beta 0.0.42

O aplicativo usa `CircularEngine` como motor padrão nesta beta. Os leitores do
círculo, splash e Claim estão ligados ao ciclo de pesca. A interface permite
seleção circular manual e exibe a resolução ativa. A distribuição é identificada
como Beta 0.0.42; consulte a página de releases para a disponibilidade publicada.

## Mecânica confirmada pelo usuário em 14 de novembro de 2026

1. Clicar na água para lançar a linha.
2. Esperar o splash e dar outro clique esquerdo. Esse segundo clique pode ser em
   qualquer lugar da janela do jogo.
3. Correção de 15/11: no círculo, o chevron verde para a direita pede segurar o botão esquerdo; o vermelho para a esquerda pede soltar. Ambos giram com o marcador.
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

Desde a Beta 0.0.44, os chevrons coloridos junto ao marcador são lidos como os
comandos do mouse; as setas brancas superiores não têm essa função. Um sinal
ausente não é interpretado como ordem para soltar. `CircularCommand` preserva a última ordem enquanto
há interface ativa, e libera o comando quando o círculo termina ou fica ausente
por pelo menos 150 ms. O componente apenas propõe um estado; não envia entradas.

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
