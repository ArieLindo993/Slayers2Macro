# Fishing Macro

**Português** · [English](docs/README.en.md) · [Español](docs/README.es.md)

Macro visual de pesca para **Slayers 2 no Roblox**, para Windows. **Beta 0.0.49** integra a mecânica circular de novembro: lançamento, splash, controle dos dois botões do mouse, pedidos A/D e coleta com T.

**[Baixar atualizador](https://github.com/ArieLindo993/Slayers2Macro/releases/latest/download/Atualizador.zip)** · **[Versões e downloads](https://github.com/ArieLindo993/Slayers2Macro/releases)** · **[Alterações por versão](CHANGELOG.md)**

## Instalar e atualizar

Você precisa de Windows e Roblox. O pacote pronto inclui as dependências: não é necessário instalar Python, Git ou AutoHotkey.

1. Baixe **Atualizador.zip**. O botão verde **Code → Download ZIP** baixa os fontes, não o aplicativo pronto.
2. Clique com o botão direito no ZIP e escolha **Extrair tudo**. Guarde a pasta extraída em um local fixo onde você possa salvar arquivos.
3. Abra **Atualizar.cmd** na pasta extraída. Aguarde o download, a verificação de integridade e a extração.
4. Quando aparecer **Abrir agora? (S/N)**, digite **S** e pressione Enter.
5. Depois, **Iniciar.cmd** abre a instalação local; **Atualizar.cmd** busca atualizações e **Voltar-versao.cmd** restaura a versão anterior disponível.

Mantenha `Atualizar.ps1` junto dos atalhos `.cmd` e preserve a pasta oculta `.install`. Se aparecer que o script não foi encontrado, extraia o ZIP inteiro novamente. Se ele desaparecer após extrair, confira a quarentena do antivírus e a origem do pacote. Não execute os atalhos de dentro do ZIP.

| Arquivo | Uso |
| --- | --- |
| Atualizador.zip | Instalação e futuras atualizações. |
| Slayers2Macro.zip | Instalação manual: extraia tudo e abra Slayers2Macro.exe com os arquivos acompanhantes. |
| Slayers2Macro.zip.sha256 | Verificação de integridade; o atualizador confere automaticamente. |
| Source code | Fontes para desenvolvimento. |

## Primeira pesca com a mecânica nova

1. Entre no jogo, equipe a vara e fique perto da água.
2. Mantenha a câmera fixa. Aponte para **onde a linha vai cair e o splash vai aparecer** e pressione **F8**.
3. Mantenha a calibração automática ligada e pressione **F4** com o Roblox em primeiro plano.
4. O macro lança e aguarda a linha assentar. A proteção padrão é de **3 segundos**, com verificação de estabilização. Ao identificar o splash, espera **0,18 segundo (180 ms)** antes do clique. Ajuste **Proteção após lançar (s)** e **Atraso da fisgada (s)** em Configurar, conforme a posição e a resposta do jogo.
5. O objetivo é **manter a agulha no arco verde**. Conforme o [guia do minigame](https://www.youtube.com/watch?v=BO6waB_XXhY&t=90s), **seta verde para a direita = segurar o botão direito; seta vermelha para a esquerda = segurar o botão esquerdo**. O macro solta o botão anterior antes de trocar. Ao se aproximar da borda do verde no sentido da pressão, alivia os dois botões e retoma dentro de uma margem segura. A/D continua independente. O alívio específico de saltos ainda depende de um sinal visual confirmado; não é confundido com essa proteção de borda.
6. Quando um cartão lateral fica ativo, o macro propõe um ou dois toques de A/D conforme os pontos. O mouse continua sendo controlado durante esses pedidos.
7. Após o resultado, tenta coletar segurando **T por três segundos**, lê Claim/nome/peso e volta a pescar. A coleta pode terminar antes do limite de tentativas.

Acompanhe as primeiras rodadas pela prévia e pelo status. O splash é buscado perto do ponto marcado: se mudar câmera ou posição, marque novamente com F8. A interface exige que o Roblox permaneça visível e em primeiro plano. Ao perder foco, o macro pausa e libera os comandos; volte ao jogo e retome com F4.

Se a agulha deixar de ser reconhecida, o macro solta os botões e continua relendo enquanto o anel estiver visível. Uma falha de leitura não inicia coleta nem move a mira. Sem resultado concluído ou Claim, não tenta T às cegas. Os comandos de cor expiram quando deixam de ser lidos; a posição volta a orientar o controle.

## Atalhos, idiomas e calibração

| Padrão | Ação |
| --- | --- |
| F4 | Iniciar / pausar. |
| F8 | Marcar a água e a região de busca do splash. |
| F6 | Selecionar manualmente o círculo inteiro numa imagem congelada. |
| F7 | Alternativa para a mesma seleção. |
| F10 | Parar e liberar os comandos. |

Em **Configurar → Idioma e atalhos**, escolha **Português**, **English** ou **Español** e as teclas desejadas. A, D e T ficam reservados ao jogo. Atalhos antigos que usavam essas teclas voltam aos padrões para evitar conflito. Salvar aplica as opções sem apagar o histórico. As instruções na interface mostram as teclas configuradas.

**Automático:** localiza o anel segmentado em cada pesca e procura novamente quando a leitura some. A posição do marcador fora do arco verde não impede localizar o círculo. A resolução do Roblox aparece na lateral.

**Manual:** com o círculo visível, pressione F6, arraste ao redor dele inteiro e salve com Enter; Esc cancela. Os cartões A/D são lidos nas laterais da posição reconhecida. A opção automática pode ser reativada a qualquer momento. Os perfis circulares são separados por tamanho da janela, bordas e DPI; as seleções da antiga barra vertical não são usadas.

**Só observar**, nas configurações, permite inspecionar as leituras sem enviar comandos. Tempos de lançamento, espera, resultado e T continuam ajustáveis.

## Histórico e registros

O inventário reúne quantidades por nome e o histórico de cada coleta, com horário, peso quando lido e ícones quando disponíveis na notificação. Nomes conhecidos são normalizados; nomes novos precisam de duas imagens distintas com confiança alta antes de entrar na listagem. A exportação CSV mantém o histórico; o JSON local também guarda peso e origem da confirmação.

Ver um nome em Claim identifica o item, mas não conta como aquisição. Uma notificação confirma a recompensa; sem ela, o desaparecimento persistente de Claim depois do período de T permite **inferir** a coleta. Essa origem fica registrada como `claim_after_hold`, separada de `reward_notification`. Física e alterações da interface ainda podem afetar essa inferência. Nenhum item identificado nas primeiras tentativas permite voltar a pescar após conferir a ausência.

Os logs de texto registram data, hora, início, pausa, splash, mudanças de etapa, mouse, A/D, T, leituras e resultados. Ficam em `%LOCALAPPDATA%/FishingMacro/logs`; **Ajuda e suporte → Abrir logs** abre a pasta. O resumo de suporte inclui versão, Windows, resolução e modo de calibração, sem usuário, caminhos, imagens ou conteúdo dos logs.

Os dados ficam no computador e não são enviados automaticamente. Vídeos, históricos, configurações e capturas pessoais não fazem parte do GitHub nem dos downloads. A interface pode ser redimensionada. A troca de idioma não muda o idioma do Roblox; nomes de itens ficam como no jogo.

## Validação e limites desta beta

A integração tem testes do ciclo de pesca, perda de leitura, comandos concorrentes, liberação das teclas, perfis, identificação e histórico. Os vídeos enviados foram reproduzidos localmente para conferir as decisões, inclusive o A com dois pontos. Essa reprodução não altera as ações do jogador gravadas e não comprova vitória numa rodada ao vivo. Sessões longas e janelas compactas reais com a nova interface ainda precisam de validação em jogo; mudanças de escala também são verificadas com quadros redimensionados.

[Detalhes da integração circular](docs/NOVO_MINIGAME.md) · [Diagnóstico de estabilidade](docs/ESTABILIDADE.md) · [Numeração beta e versões anteriores](docs/VERSIONAMENTO.md)

## Desenvolvimento

Use Python 3.12 e as dependências fixadas em requirements.txt. A integração contínua executa os testes, a auditoria e build.py; o empacotador também executa a verificação do aplicativo compilado. tools/replay_circular.py e tools/replay_fishing.py reproduzem vídeos locais sem entradas ao jogo; precisam adicionalmente de imageio-ffmpeg. Relatórios e gravações não são versionados.

O nome do aplicativo é genérico; o perfil disponível é específico para Slayers 2. O repositório e os pacotes são públicos. Não há pagamentos, ativação por chave, autenticação de clientes ou restrições de cópia implementadas.
