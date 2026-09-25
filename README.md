# Slayers2Macro

Macro visual para Windows, baseado na versão 6.1.0. F8 marca a água; F4 inicia/pausa; F6 abre seleção manual; F10 para. Calibração automática, recuperação da barra durante a pesca, coleta com T e histórico JSON/CSV.

## Atualizar sem extrair ZIPs manualmente

Feche o macro e abra `Atualizar.cmd`. Na primeira execução, informe `usuario/repositorio` do GitHub. O atalho consulta a última Release, baixa o executável, confere o checksum e instala numa pasta separada. Nas próximas atualizações, o destino fica salvo. Os dados da instalação anterior feita pelo atalho são copiados; instalações antigas externas a ele não são migradas automaticamente.

Para repositório privado, o atualizador precisa do GitHub CLI (`gh`) autenticado com acesso ao repositório. Para público, não é necessário autenticar. Sem internet, ainda é possível abrir diretamente o executável já instalado em `.install`.

**Estado:** repositório preparado localmente. Publicação e download de Release ainda dependem de configurar o destino no GitHub. O atualizador não foi testado contra um repositório remoto real. Não confunda código preparado com publicação concluída.

## Desenvolvimento

Windows, Python 3.12. Instale `requirements.txt` em um ambiente virtual e rode `python src/macro.py`. Use `python build.py` para gerar o executável e um ZIP em `dist/`. As versões das dependências correspondem ao ambiente que compilou o macro; a instalação dessas versões no GitHub Actions ainda precisa ser verificada na primeira execução remota.

## Publicação

Depois de conectar este repositório ao GitHub, um push de tag como `v6.1.0` executa `.github/workflows/release.yml`, compila no Windows, testa a inicialização e publica o ZIP e seu checksum numa Release. A versão exibida é `VERSION` em `src/macro.py`: atualize-a junto com a tag.

O Git guarda somente código e recursos visuais. Executáveis vão em Releases. Configuração, histórico, dependências e gravações pessoais não são versionados.

## Limites de validação

A v6.1 passou por testes de recuperação, imagens do vídeo, OCR e interface simulada; não houve confirmação de uma sessão completa no jogo ao vivo. A CI executa um teste de inicialização; esse teste não comprova desempenho no jogo.
