# Numeração beta

[Português](VERSIONAMENTO.md) · [English](VERSIONING.en.md) · [Español](VERSIONING.es.md)

Toda a trajetória do produto é classificada como beta, desde os protótipos anteriores ao Git. A sequência abaixo começa em zero e inclui os pacotes intermediários disponíveis. Esta classificação retrospectiva não afirma que todos os protótipos funcionavam ou foram publicados. A ordem pré-Git usa os arquivos disponíveis e seus registros locais; não reconstrói tentativas sem artefato preservado.

| Versão beta | Identificação anterior | Registro |
| --- | --- | --- |
| Beta 0.0.0 | MacroPesca-Slayers2.zip | Arquivo local anterior ao Git |
| Beta 0.0.1 | MacroPesca-Slayers2-v2.zip | Arquivo local anterior ao Git |
| Beta 0.0.2 | MacroPesca-Slayers2-v3.zip | Arquivo local anterior ao Git |
| Beta 0.0.3 | MacroPesca-Slayers2-v4.zip | Arquivo local anterior ao Git |
| Beta 0.0.4 | MacroPesca-Slayers2-v4-correcao.zip | Arquivo local anterior ao Git |
| Beta 0.0.5 | MacroPesca-Slayers2-sem-validacao.zip | Arquivo local anterior ao Git |
| Beta 0.0.6 | MacroPesca-Slayers2-ajustada.zip | Arquivo local anterior ao Git |
| Beta 0.0.7 | MacroPesca-Slayers2-fonte-corrigida.zip | Arquivo local anterior ao Git |
| Beta 0.0.8 | MacroPescaSlayers2.ahk | Arquivo local anterior ao Git |
| Beta 0.0.9 | MacroPesca-Slayers2-v5.zip | Arquivo local anterior ao Git |
| Beta 0.0.10 | MacroPesca-Slayers2-v6.zip | Arquivo local anterior ao Git |
| Beta 0.0.11 | MacroPesca-Slayers2-v6-1.zip | Arquivo local anterior ao Git |
| Beta 0.0.12 | [v6.1.0](https://github.com/ArieLindo993/Slayers2Macro/tree/v6.1.0) | Tag Git |
| Beta 0.0.13 | [v7.0.0](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.0) | Tag Git |
| Beta 0.0.14 | [v7.0.1](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.1) | Tag Git |
| Beta 0.0.15 | [v7.0.2](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.2) | Tag Git |
| Beta 0.0.16 | [v7.0.3](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.3) | Tag Git |
| Beta 0.0.17 | [v7.0.4](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.4) | Tag Git |
| Beta 0.0.18 | [v7.0.5](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.5) | Tag Git |
| Beta 0.0.19 | [v7.0.6](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.6) | Tag Git |
| Beta 0.0.20 | [v7.0.7](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.7) | Tag Git |
| Beta 0.0.21 | [v7.0.8](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.8) | Tag Git |
| Beta 0.0.22 | [v7.0.9](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.0.9) | Tag Git |
| Beta 0.0.23 | [v7.1.0](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.1.0) | Tag Git |
| Beta 0.0.24 | [v7.1.1](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.1.1) | Tag Git |
| Beta 0.0.25 | [v7.2.0](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.2.0) | Tag Git — sem executável publicado |
| Beta 0.0.26 | [v7.2.1](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.2.1) | Tag Git — sem executável publicado |
| Beta 0.0.27 | [v7.2.2](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.2.2) | Tag Git |
| Beta 0.0.28 | [v7.3.0](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.3.0) | Tag Git |
| Beta 0.0.29 | [v7.3.1](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.3.1) | Tag Git |
| Beta 0.0.30 | [v7.4.0](https://github.com/ArieLindo993/Slayers2Macro/tree/v7.4.0) | Tag Git |
| Beta 0.0.31 | [beta numbering](https://github.com/ArieLindo993/Slayers2Macro/tree/v0.0.31-beta) | Nova nomenclatura |
| Beta 0.0.32 | [v0.0.32-beta](https://github.com/ArieLindo993/Slayers2Macro/tree/v0.0.32-beta) | Ícones e recompensas diretas |

As tags, commits, checksums e pacotes antigos são preservados. Os executáveis antigos podem continuar mostrando a numeração com a qual foram compilados; a nova interface exibe **Beta 0.0.32**. O inventário não publica arquivos pessoais nem recompila protótipos. As variantes “ajustada” e “fonte-corrigida” têm o mesmo código Python listado, mas pacotes com hashes diferentes; são registradas como pacotes distintos, sem atribuir uma correção inexistente.

**Compatibilidade:** “Beta” indica o estágio do produto. As releases continuam publicadas no canal usado por `/releases/latest`, preservando os atualizadores instalados e os links de download. Não são convertidas para o filtro técnico de prerelease do GitHub, que [fica fora desse canal](https://docs.github.com/en/rest/releases/releases#get-the-latest-release). O atualizador identifica instalações pelo ID da release, e não pela comparação entre 7.x e 0.x. Não há reset das configurações ou dos dados.
