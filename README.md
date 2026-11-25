# Estrela Negra · site

Site do canal de astronomia Estrela Negra: https://estrela-negra.github.io/

Publicado pelo GitHub Pages a partir da pasta `docs/` da branch `main`. Qualquer mudança enviada para essa pasta entra no ar em um ou dois minutos.

## Editar à mão
- **Pelo navegador:** abra o arquivo em github.com (por exemplo `docs/index.html` ou `docs/estilo.css`), clique no lápis, edite e clique em "Commit changes".
- **Cores, fontes e espaçamentos:** ficam em `docs/estilo.css` (as cores estão no começo, em `:root`).
- **Imagens:** ficam em `docs/img/`. Para trocar uma, envie um arquivo com o mesmo nome ("Add file" → "Upload files" dentro da pasta).

Atenção: as páginas são geradas pelo `gera_site.py`. Quando o site é gerado de novo (a tarefa automática faz isso quando sai vídeo novo), mudanças feitas direto nos `.html` de `docs/` são sobrescritas. Para uma mudança que deve ficar, altere o modelo dentro do `gera_site.py` (os textos e o HTML estão lá) ou peça a mudança ao Claude.

## Gerar o site no Mac
```
python3 arte_site.py      # artes de luz, grão e retrato (só quando mudar a identidade)
python3 gera_site.py      # gera docs/ com os vídeos já públicos no YouTube
```
`python3 gera_site.py --todos` gera uma prévia com todos os vídeos, inclusive os programados: nunca publique essa versão.

## De onde vêm os dados
- Vídeos: `motion/reels_NN/05_YOUTUBE/METADADOS_YOUTUBE.md`, narração em `scripts/motion/tempos/tts/rNN.txt`, miniaturas em `motion/THUMBS_LUZ/`.
- Fotos do céu: `motion/INSTAGRAM/FOTO_DO_CEU/foto_do_ceu.json`.
- IDs de vídeos novos: `ids_extra.json` (número da pasta → ID do vídeo 16:9 no YouTube).
