# Cómo contribuir

Este repositorio es un cuaderno de 260 días en tres lenguas (español,
inglés y polaco), página a página. Antes de tocar nada, lee
[`notes/01-plan.md`](notes/01-plan.md) (el porqué) y el README (cómo se
construye).

## Qué hace falta

Para las comprobaciones, solo Python 3 y `make`; no hace falta TeX.
Compilar los PDF necesita LuaLaTeX y `latexmk` (ver el README).
`requirements.txt` solo hace falta para regenerar
`content/numeros-trazo.json` con `tools/gen_numeros_puntos.py`.

```sh
make generate                              # escribe los generated-*.tex (no están en git)
python3 tools/gen_numeros.py --check       # valida el JSON y que lo generado esté al día
python3 -m pip install pytest && python3 -m pytest tests   # tests de los validadores
```

Un `--check` sobre un checkout limpio dice `FALTA` (los `.tex` generados
no existen): ejecuta `make generate`. `DESACTUALIZADO` significa que
existen pero ya no coinciden con el JSON.

## Cómo añadir o cambiar un día

La fuente de verdad es el JSON; los `.tex` de `content/**/generated-*.tex`
se generan y **no se editan a mano**.

1. Edita el día en `content/q1.json` ... `content/q4.json` (cuaderno en
   español, el que manda). Cada día lleva `dia`, `semana`, `tema`,
   `numero`, `objeto`, `frase` y `actividad` (con su `tipo` y los campos
   que ese tipo necesite: ver la tabla de actividades en
   `notes/01-plan.md` y `render_actividad` en `tools/gen_numeros.py`).
2. Respeta la escalera: un día solo puede usar números que ya han llegado
   (`ESCALERA` y `LLEGADA` en `tools/gen_numeros.py`) y actividades que ya
   han llegado (`DESDE_SEMANA`). El script falla si no.
3. Haz el mismo cambio en `content/english/q*.json` y
   `content/polish/q*.json` (ver la regla siguiente).
4. `make generate`, `python3 tools/gen_numeros.py --check` y
   `python3 -m pytest tests`. Si tienes TeX, `make all-formats` comprueba
   además que cada día cabe en una página.

## Regla de paridad (`cargar_traduccion`)

Las traducciones no tienen días propios: cada día de inglés y de polaco
es el de español, con su texto en su lengua. Por eso
`content/<lengua>/q*.json` solo trae, por día:

- `dia` y `frase` (siempre);
- `prompt` en *Dibuja* y *Repasa*, `checklist` en *Repasa* (con el mismo
  número de ítems que en español) y `texto` en *Problema*, y ningún otro
  campo (`TEXTOS_ACTIVIDAD`).

`cargar_traduccion` rechaza un día repetido, un hueco, un campo que
sobra o falta, y una `checklist` de otra longitud. Número, objeto,
semana, actividad y clave **no se traducen**: se cambian en español y
valen para las tres lenguas. La única excepción es una actividad que
solo existe en un cuaderno (`solo_aqui` en `tools/idiomas.py`, hoy
*Number names* en inglés). Los temas de cada semana y las cadenas del
motor están en `tools/idiomas.py` y `lang/*.tex`, no en el JSON.

## Política de personajes sintéticos

Todos los personajes, nombres, lugares y situaciones son inventados:
Lucía, Dani, Toby, Mamá, Papá, la abuela Rosa y el resto de la familia y
los vecinos. Para mantenerlo así:

- No uses nombres, fotos, dibujos ni historias de niñas, niños o
  familias reales, ni de clientes, colegios o documentos reales, en el
  contenido, en los fixtures de los tests ni en los mensajes de commit.
- Los fixtures de `tests/` se construyen en memoria o con ficheros
  sintéticos; no se copian documentos reales.
- No subas secretos, claves ni datos personales a ningún fichero.
- Si un personaje nuevo hace falta, que sea inventado y se use igual en
  las tres lenguas.

## Lo que no se toca sin hablarlo antes

- La prosa del cuaderno (`content/**/*.json`): ortografía, nombres,
  orden de las lecciones y nombres de semana son decisiones del
  propietario.
- `frontmatter/` y `backmatter/`: `tools/check_pages.py` tiene fijado
  dónde cae el día 1 (`PAGINA_DIA_1`) y los saltos de las medallas
  (`SALTOS_ESPERADOS`); añadir o quitar una página de adulto los rompe, y
  sin TeX no se puede comprobar.
- Las comprobaciones: no se debilitan ni se quitan; si una falla, se
  arregla el contenido.

Commits pequeños, uno por cambio lógico; el código y los comentarios, en
inglés o español como el resto del fichero que tocas.
