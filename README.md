# Fishing Macro

Aplicativo local para Windows. O perfil disponível nesta versão é **Slayers 2**, no Roblox. A identidade do produto fica em `src/product.py`; o nome genérico não significa compatibilidade automática com outros jogos.

## Instalar e atualizar

Baixe `Atualizador.zip` na [última Release](https://github.com/ArieLindo993/Slayers2Macro/releases/latest), extraia em uma pasta fixa e execute `Atualizar.cmd`. O atalho baixa o executável e verifica o checksum. Não exige Python, Git ou AutoHotkey para uso.

- `Iniciar.cmd`: abre a versão instalada, inclusive sem internet.
- `Atualizar.cmd`: procura e instala a versão mais recente.
- `Voltar-versao.cmd`: restaura a instalação anterior, sem apagar o histórico. Feche o macro antes de trocar de versão. Depois de voltar, use Iniciar; Atualizar procura novamente a versão mais nova.

O retorno exige uma instalação anterior feita pelo atualizador. Versões extraídas manualmente em outras pastas não são localizadas automaticamente.

## Usar

Equipe a vara no Roblox, aponte para a água e pressione **F8**. **F4** inicia/pausa; **F10** para. A perda de foco pausa e libera as entradas.

A calibração automática confirma a barra em três capturas e refina o perfil nas rodadas confiáveis. Se a leitura falhar, tenta a região atual, os arredores e finalmente a tela do jogo. **F6** abre uma captura congelada para selecionar a barra inteira por arraste. Salvar ativa o modo manual; o automático pode ser reativado na interface.

## Recursos da versão 7

1. Diagnósticos locais de perda de leitura, com até 20 pares de imagem/registro.
2. Prévia anotada: azul = região, verde = alvo, rosa = marcador.
3. Recuperação gradual da localização, sem bloquear o controle do mouse.
4. Tempo dentro da faixa e percentual de leituras válidas. O percentual dentro da faixa considera apenas intervalos com leitura; não representa taxa de vitória. Métricas por ciclo ficam no JSON do histórico.
5. Perfis separados por tamanho da janela, presença de bordas e DPI. Cada perfil guarda a região e seu aprendizado.
6. Retorno à versão anterior por atalho, mantendo os dados locais.

## Dados e privacidade

Configurações, perfis, histórico e diagnósticos ficam em `%LOCALAPPDATA%\FishingMacro`, separados dos executáveis. Não há telemetria ou envio automático desses dados. O atualizador acessa o GitHub exclusivamente para baixar versões.

O diagnóstico salva apenas o recorte da região configurada, nunca uma captura inteira do desktop. Uma região mal selecionada pode conter outros elementos do jogo. Pode ser desativado na interface. Registros usam campos limitados e não contêm caminhos de arquivos, usuário do Windows, tokens ou mensagens de exceção.

Vídeos, configurações, históricos e diagnósticos não são incluídos no Git nem na distribuição. Os modelos visuais incluídos são pequenos recortes dos indicadores do jogo. A migração da versão anterior é local e aditiva.

## Desenvolvimento e publicação

Windows e Python 3.12. Crie um ambiente virtual e instale `requirements.txt`. Execute `python -m unittest discover -s tests -v`, depois `python build.py`. Para desenvolvimento, execute `python src/macro.py`.

Uma tag `v*` aciona a compilação Windows no GitHub Actions, executa os testes e publica o executável. Mantenha `VERSION` em `src/product.py` alinhada com a tag. O build inclui as informações de bibliotecas de terceiros disponíveis no ambiente de distribuição.

O repositório continua público. Esta organização facilita futuras alterações de marca e distribuição, mas não inclui pagamentos, ativação por chave, restrições de cópia ou autenticação de clientes.

## Validação

Os testes cobrem métricas, perfis, recuperação, privacidade dos registros, prévia e retorno offline. O build testa a inicialização do executável. Testes com gravações foram usados no desenvolvimento, mas os arquivos pessoais que os originaram não são publicados. Esses testes não substituem uma sessão completa no jogo ao vivo.
