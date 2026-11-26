# Endereços das matérias (CTA no fim dos vídeos)

Padrão: **https://estrela-negra.github.io/materias/<slug>/** — o slug é fixo (vem do campo `slug:` do arquivo `site/materias/<slug>.md`, não do título) e não muda depois de anunciado no vídeo.

Regra de publicação: a página da matéria só é gerada quando (1) existe `site/materias/<slug>.md` com `reels: NN` e (2) o vídeo 16:9 da pasta `reels_NN` está público no YouTube (ID em `motion/THUMBS_LUZ/TROCA_YOUTUBE.json` ou `site/ids_extra.json`). Antes disso o endereço dá 404. Por isso: escrever a matéria ANTES do vídeo ir ao ar e conferir o ID em `ids_extra.json`.

Formato do arquivo: cabeçalho `chave: valor` (reels, slug, chapeu, titulo, linha_fina, data, certeza), linha `---`, corpo com intertítulos `## ` e, no fim, `## Fontes` com itens `- nome: URL` (só URLs abertas e conferidas). O vídeo incorporado ("Assista ao vídeo") entra sozinho.

## No ar (vídeos públicos, 26/11/2026)
| Pasta | Vídeo | Endereço |
|---|---|---|
| reels_01 | A física tem um problema de 100 anos (gravidade pós-quântica) | https://estrela-negra.github.io/materias/gravidade-quantica/ |
| reels_02 | 3I/ATLAS: o cometa interestelar que pode ser mais velho que o Sol | https://estrela-negra.github.io/materias/3i-atlas/ |
| reels_03 | Ondas gravitacionais: como o LIGO mediu algo 400 vezes menor que um próton | https://estrela-negra.github.io/materias/ondas-gravitacionais/ |
| reels_04 | O buraco negro que nasceu antes da galáxia (QSO1) | https://estrela-negra.github.io/materias/buraco-negro-antes-da-galaxia/ |
| reels_10 | Voyager 1: um dia-luz de casa | https://estrela-negra.github.io/materias/voyager-1-dia-luz/ |
| reels_22 | A gente levou 8 anos pra chegar em Mercúrio. Por quê? (BepiColombo) | https://estrela-negra.github.io/materias/bepicolombo-mercurio/ |
| reels_23 | O asteroide que acompanha a Terra é um pedaço da Lua? (Kamoʻoalewa) | https://estrela-negra.github.io/materias/kamooalewa-quase-lua/ |

## Próximos vídeos (endereço reservado; matéria AINDA NÃO ESCRITA, página só publica quando o vídeo estiver público)
| Pasta | Vídeo | Endereço | Situação |
|---|---|---|---|
| reels_24 | Como se formam os buracos negros? | https://estrela-negra.github.io/materias/como-se-formam-os-buracos-negros/ | YouTube 16:9 `JXFqd-ejZnI` programado 27/11 18:00; falta a matéria |
| reels_25 | Por que a gente nunca mais pousou na Lua? | https://estrela-negra.github.io/materias/por-que-nunca-mais-pousamos-na-lua/ | YouTube 16:9 `NShn1KXhbGY` programado 14/12 18:00; falta a matéria |
| reels_26 | O que é o Paradoxo de Fermi? | https://estrela-negra.github.io/materias/paradoxo-de-fermi/ | YouTube 16:9 `1V5P94QCB2Q` programado 30/11 18:00 (ID ainda NÃO está em ids_extra.json); falta a matéria |
| reels_27 | Como nascem as estrelas? | https://estrela-negra.github.io/materias/como-nascem-as-estrelas/ | primeiro vídeo com o CTA no fim; matéria a escrever |

Os vídeos de reels_24 a reels_26 já foram renderizados sem o CTA; o CTA no fim do vídeo começa no reels_27.

## Vídeos com metadados mas não públicos no YouTube (oEmbed 403 em 26/11/2026; slug reservado caso sejam publicados)
| Pasta | Vídeo | Endereço |
|---|---|---|
| reels_05 | A estrela mais rápida da Galáxia | https://estrela-negra.github.io/materias/estrela-mais-rapida-da-galaxia/ |
| reels_06 | Betelgeuse não está sozinha | https://estrela-negra.github.io/materias/betelgeuse-companheira/ |
| reels_07 | Gaia DR4: o maior mapa da Via Láctea | https://estrela-negra.github.io/materias/gaia-dr4/ |
| reels_08 | Estrelas negras: o Webb achou uma? | https://estrela-negra.github.io/materias/estrelas-negras/ |
| reels_09 | Rajadas rápidas de rádio | https://estrela-negra.github.io/materias/rajadas-rapidas-de-radio/ |
| reels_11 | A tensão de Hubble | https://estrela-negra.github.io/materias/tensao-de-hubble/ |
| reels_12 | A energia escura está enfraquecendo? (DESI) | https://estrela-negra.github.io/materias/energia-escura-desi/ |
| reels_13 | Observatório Vera Rubin | https://estrela-negra.github.io/materias/observatorio-vera-rubin/ |
| reels_14 | TRAPPIST-1: esses planetas têm ar? | https://estrela-negra.github.io/materias/trappist-1/ |
| reels_15 | Eclipse do Carnaval: o anel de fogo | https://estrela-negra.github.io/materias/eclipse-anel-de-fogo/ |
| reels_16 | O universo zumbe: ondas gravitacionais medidas com pulsares | https://estrela-negra.github.io/materias/ondas-gravitacionais-pulsares/ |
| reels_17 | O asteroide que podia bater na Lua | https://estrela-negra.github.io/materias/asteroide-2024-yr4/ |
| reels_18 | A Hera foi ver o estrago do DART | https://estrela-negra.github.io/materias/hera-dart/ |
| reels_19 | A estrela que vai acender no céu (T Coronae Borealis) | https://estrela-negra.github.io/materias/t-coronae-borealis/ |
| reels_20 | 5 anos do James Webb | https://estrela-negra.github.io/materias/cinco-anos-do-james-webb/ |
| reels_21 | Artemis II: fomos até a Lua para olhar para trás | https://estrela-negra.github.io/materias/artemis-ii/ |
