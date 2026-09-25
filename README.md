# Fishing Macro

Macro de pesca para **Slayers 2, no Roblox**, com interface para Windows, calibração automática e histórico dos itens da sessão. O nome do aplicativo é genérico, mas o perfil disponível atualmente é específico para Slayers 2.

**[Baixar atualizador](https://github.com/ArieLindo993/Slayers2Macro/releases/latest/download/Atualizador.zip)** · **[Ver versões e downloads](https://github.com/ArieLindo993/Slayers2Macro/releases)** · **[Histórico de alterações](CHANGELOG.md)**

## Instalação rápida

Para utilizar o executável, você precisa de Windows e do Roblox. Não é necessário instalar Python, Git ou AutoHotkey. É preciso internet para baixar as atualizações e jogar Roblox.

1. Baixe **Atualizador.zip** pelo link acima. O botão verde “Code → Download ZIP” baixa o código-fonte, não o aplicativo pronto.
2. Clique com o botão direito no ZIP e escolha **Extrair tudo**. Use uma pasta fixa onde você possa salvar arquivos.
3. Abra a pasta extraída e dê dois cliques em **Atualizar.cmd**. Não execute os arquivos de dentro do ZIP.
4. Aguarde a consulta ao GitHub, o download, a verificação de integridade e a extração.
5. Quando aparecer “Abrir agora? (S/N)”, digite **S** e pressione Enter.

Mantenha os arquivos do atualizador juntos. Não mova apenas o executável nem apague a pasta oculta `.install`: ela guarda as versões instaladas.

### Qual arquivo baixar?

| Arquivo | Para que serve |
| --- | --- |
| **Atualizador.zip** | Opção recomendada: instala o macro e permite atualizar sem baixar o aplicativo manualmente a cada versão. |
| **Slayers2Macro.zip** | Aplicativo para instalação manual. Extraia todo o conteúdo e execute `Slayers2Macro.exe`, mantendo os demais arquivos ao lado dele. |
| **Slayers2Macro.zip.sha256** | Código de verificação da integridade do download. O atualizador o verifica automaticamente. |
| **Source code** | Código-fonte para desenvolvimento; não é o executável. |

## Primeira pesca

1. Abra o Roblox, entre no Slayers 2 e equipe a vara perto da água.
2. Com o Roblox em primeiro plano, aponte o mouse para um ponto válido na água e pressione **F8** para salvar o local do lançamento.
3. Mantenha a opção de calibração automática ativada e pressione **F4**.
4. O macro lança a vara, espera o minigame, controla o marcador e tenta coletar o resultado segurando **T**.
5. Acompanhe a primeira rodada pela prévia e pelo texto de status. Se precisar interromper, use **F10**.

A sequência considera tentativas sem recompensa e repete a coleta quando necessário. O texto de reconhecimento do item não é requisito para iniciar a tentativa de coleta. Há limites de até três lançamentos e cinco tentativas de coleta para cada sequência. A coleta termina antes desse limite ao reconhecer a recompensa ou validar o desaparecimento persistente de um item após T. Sem item identificado nas duas primeiras tentativas, volta a pescar após conferir a ausência. O desaparecimento isolado não é registrado como recompensa confirmada.

O Roblox precisa permanecer visível e em primeiro plano. Ao perder o foco, o macro pausa e libera as teclas e o mouse; volte ao jogo e pressione F4 para retomar. O macro usa o mouse e o teclado enquanto está ativo.

### Atalhos

| Tecla | Ação |
| --- | --- |
| **F8** | Salvar o ponto na água para lançar a vara. |
| **F4** | Iniciar ou pausar. |
| **F6** | Abrir a seleção manual da região da barra. |
| **F10** | Parar e liberar os comandos. |

## Calibração e acompanhamento

**Automática:** a barra é conferida a cada pesca. A localização precisa de três capturas consistentes para ser confirmada. Rodadas com leituras confiáveis refinam o perfil; isso não garante melhora em toda tentativa. A posição continua sendo conferida periodicamente mesmo após a confirmação. Quando a localização se perde, a busca passa pela região atual, seus arredores e a tela do jogo. Enquanto houver sinal de pesca ativa, tenta recuperar a leitura, respeitando o limite total de 120 segundos.

**Manual:** quando o minigame estiver visível, pressione F6. Na captura congelada, arraste para selecionar a barra inteira e salve. Isso ativa o modo manual. Volte ao Roblox e pressione F4. A opção automática pode ser reativada na interface.

Os perfis são separados pelo tamanho da janela, presença de bordas e escala de exibição do Windows (DPI). Cada perfil guarda sua região, aprendizado e escolha entre modo automático e manual.

Na prévia, **azul** marca a região analisada, **verde** indica o alvo e **rosa** indica o marcador. O indicador de tempo dentro da faixa considera apenas os intervalos com leitura válida: ele não representa a porcentagem de pescas vencidas.

## Ajustes de pesca

Abra as configurações, altere os valores e clique em **Salvar e fechar**.

| Ajuste | Padrão atual | Intervalo permitido |
| --- | --- | --- |
| Duração do clique | 0,25 segundo | 0,08 a 1 segundo |
| Segurar T | **3 segundos** | 0,2 a 5 segundos |
| Esperar a pesca antes de repetir | 20 segundos | 10 a 60 segundos |
| Esperar item depois da pesca | 12 segundos | 5 a 20 segundos |

**Atualizações preservam configurações salvas.** Se você usava 1,5 segundo para T, altere “Segurar T (s)” para 3 manualmente. O novo padrão se aplica a configurações novas ou sem esse valor salvo.

O modo **Só observar** permite acompanhar a leitura sem enviar comandos ao jogo.

## Histórico e diagnósticos

O botão **Itens obtidos** mostra os registros da sessão. O reconhecimento de nomes usa leitura de texto da tela e pode falhar: “Nome não identificado” não deve ser interpretado como um nome de item confirmado. Histórico e exportações usam JSON e CSV; métricas de acompanhamento por ciclo ficam no JSON.

Os diagnósticos de perda de leitura são locais e limitados a até 20 pares de imagem e registro. A interface permite desativá-los. Eles ajudam a investigar quando e onde a leitura falhou.

## Atualizar ou voltar de versão

Feche o macro antes de iniciar uma atualização ou trocar de versão.

| Atalho | Ação |
| --- | --- |
| **Iniciar.cmd** | Abre a versão já instalada sem consultar o GitHub. O Roblox ainda precisa de sua conexão normal. |
| **Atualizar.cmd** | Consulta o GitHub, instala a versão mais recente e pergunta se deseja abri-la. |
| **Voltar-versao.cmd** | Alterna para a versão anterior disponível na mesma instalação, preservando os dados locais. |

Para atualizar os próprios atalhos e o script do atualizador, baixe um novo **Atualizador.zip** e extraia na mesma pasta, substituindo os arquivos e preservando `.install`.

O retorno exige uma versão anterior instalada pelo atualizador. Instalações manuais em outras pastas não são localizadas automaticamente. Depois de voltar, use **Iniciar.cmd**; executar Atualizar novamente procura a versão mais recente.

## Solução de problemas

| Situação | O que verificar |
| --- | --- |
| A janela do atualizador parece parada | Aguarde o download e a extração. O pacote atualizado mostra cada etapa; a transferência pode levar alguns minutos. |
| O atualizador informa que o macro está aberto | Feche o aplicativo e tente novamente. Não abra várias atualizações ao mesmo tempo. |
| O arquivo `.cmd` não encontra o script | Extraia o ZIP inteiro e mantenha `Atualizar.ps1` junto dos atalhos. |
| Falha de rede ou de integridade | Confira a conexão e tente novamente. Não use um download incompleto. |
| F4 não inicia a pesca | Coloque o Roblox em primeiro plano, equipe a vara e marque a água com F8. |
| A barra não é acompanhada | Observe a prévia, confira o modo de calibração e use F6 se precisar selecionar a região manualmente. |
| T ainda é segurado por 1,5 segundo | A preferência anterior foi preservada. Salve 3 em “Segurar T (s)”. |
| Não há versão anterior para restaurar | O retorno só fica disponível após ter outra versão instalada pelo mesmo atualizador. |

Para relatar uma falha, informe a versão, o texto do status, o que ocorreu e os passos para reproduzir. Revise qualquer imagem antes de compartilhá-la; não envie a pasta inteira de dados pessoais.

## Dados e privacidade

Configurações, perfis, histórico e diagnósticos ficam em `%LOCALAPPDATA%\FishingMacro`, separados da instalação. Não há telemetria nem envio automático desses dados. O atualizador acessa o GitHub para consultar e baixar versões.

O diagnóstico salva apenas o recorte da região configurada, não uma captura inteira do desktop. Uma seleção incorreta pode incluir outros elementos visíveis. Seus registros usam campos limitados, sem caminhos pessoais, tokens ou mensagens de exceção.

Vídeos pessoais, configurações, históricos e diagnósticos não são incluídos no repositório nem nos pacotes. Os recursos visuais distribuídos são pequenos recortes de indicadores do jogo. A migração de dados antigos é local e aditiva.

O repositório e os downloads são públicos. O aplicativo ainda não inclui pagamentos, ativação por chave, autenticação de clientes ou restrições de cópia.

## Desenvolvimento e validação

Use Windows e Python 3.12. Em um ambiente virtual, execute:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python audit.py
python src/macro.py
```

Feche qualquer instância do macro antes dos testes: o teste do retorno de versão respeita o bloqueio de aplicativo aberto. Para gerar os pacotes, execute `python build.py`.

A marca e a versão ficam em `src/product.py`. Uma tag `v*` aciona o GitHub Actions para executar testes, auditar os arquivos, compilar no Windows, testar a inicialização do executável e publicar os pacotes. Mantenha a tag alinhada com `VERSION` e registre as mudanças no [CHANGELOG.md](CHANGELOG.md).

Os testes cobrem métricas, perfis, recuperação da leitura, registros, prévia e retorno de versão. Também foram usados quadros de gravações no desenvolvimento, sem publicar os arquivos pessoais de origem. Esses testes não substituem uma sessão prolongada no jogo ao vivo. Mudanças na interface do jogo podem exigir novos ajustes.

Os pacotes compilados incluem informações disponíveis das bibliotecas usadas na pasta `THIRD_PARTY`.
