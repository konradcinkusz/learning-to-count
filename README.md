# Aprendo los números

[![Build](https://github.com/konradcinkusz/learning-to-count/actions/workflows/build.yml/badge.svg)](https://github.com/konradcinkusz/learning-to-count/actions/workflows/build.yml)
[![Licencia](https://img.shields.io/github/license/konradcinkusz/learning-to-count)](LICENSE)
[![Hecho con](https://img.shields.io/badge/hecho%20con-LaTeX-2E7D32)](preamble.tex)

Un cuaderno diario de números en español, A4, una página por día
laborable del año: para una niña o un niño de cinco o seis años que
empieza con los números -- reconocerlos, contarlos y escribirlos -- y, a
lo largo del año, compararlos, sumar y restar.

Es de la misma familia que
[**Aprendo a leer**](https://github.com/konradcinkusz/learning-to-read):
el mismo motor, los mismos personajes (Lucía, su hermano Dani, su perro
Toby, Mamá, Papá y la abuela Rosa) y los mismos temas semana a semana,
así que quien lleve los dos cuadernos cuenta esa semana lo que lee. La
semana del cumpleaños de Lucía, el número es el 7: las siete velas.

Cada página tiene, arriba, **el número de hoy**: el número grande, su
nombre, el marco de diez (dos filas de cinco casillas con un punto por
cada uno) y esas cosas dibujadas, con una frase de la historia que lee
el adulto. Debajo, una **actividad** que llena el resto de la página:
trazar el número (el contorno de puntos sale del glifo real de la letra
del cuaderno, como las letras de *Aprendo a leer*), colorear
exactamente N cosas, rodear el grupo que tiene N, contar y rodear el
número, buscar el número entre otros, unir cada grupo con su número,
completar el tren de números, dibujar N cosas, y los viernes, repasar;
y desde el invierno, comparar, el número de antes y el de después, la
recta numérica, ordenar y juntar dos grupos -- las primeras sumas; en
primavera, sumar y restar con sus signos, partir un número en dos, las
parejas del 10, los problemas y las decenas y las unidades; y en
verano, la tabla del 100, el dinero, la hora y medir.

- **Otoño**: del 1 al 10, y el 0 -- un número nuevo cada semana.
- **Invierno**: hasta el 20, más y menos, el anterior y el siguiente,
  las primeras sumas con dibujos.
- **Primavera**: sumar y restar hasta 10, contar de 2 en 2, de 5 en 5 y
  de 10 en 10, hasta el 50.
- **Verano**: hasta el 100, sumas y restas hasta 20, el dinero, la hora
  y medir.

El plan completo, semana a semana, está en
[`notes/01-plan.md`](notes/01-plan.md).

## First Numbers (en inglés)

El mismo cuaderno en inglés (británico, como *Read and Draw* y *First
Words* de *Aprendo a leer*), **página a página**: el mismo número, las
mismas cosas dibujadas y la misma actividad cada día, así que se puede
hacer uno, el otro o los dos. Lo que cambia es la lengua: la frase de la
historia, los temas, los enunciados, las instrucciones, las páginas para
el adulto, la clave y el diploma. Los personajes y lo que es de aquí se
quedan como en esos dos cuadernos (Lucía, Grandma Rosa, Bigotes, los
churros, el turrón), y el dinero son euros: Lucía vive en España.

Lo único que tiene de más: cuando llegan las decenas, un par de días de
**Number names** -- unir 13, 30, 14, 40... con su nombre --, porque en
inglés *thirteen* y *thirty* suenan casi igual, y en español *trece* y
*treinta* no.

Está en `english.tex` (y `english-bw.tex`), con el texto de cada día en
`content/english/q*.json`; todo lo que se escribe en una lengua o en la
otra sale de `tools/idiomas.py`, y las comprobaciones son las mismas. El
plan, en [`notes/02-english.md`](notes/02-english.md).

## Poznaję liczby (en polaco)

El mismo cuaderno en polaco, **página a página**, como *First Numbers*:
el mismo número, las mismas cosas dibujadas y la misma actividad cada
día. Lo que cambia es la lengua: la frase de la historia, los temas, los
enunciados, con cada cosa en la forma que le toca con su número
(*Pokoloruj 1 piłkę*, *2 piłki*, *5 piłek*), las instrucciones, las
páginas para el adulto, la clave y el diploma. Y la frase del día dice
su número en cualquiera de sus formas, que en polaco cambian con el
caso y con lo que se cuenta (*jeden pies*, *jednego psa*, *dwie
piłki*, *troje dzieci*): el script las lee todas. Los personajes se
quedan (Lucía, babcia Rosa, pani Marta), y el dinero son euros.

Está en `polish.tex` (y `polish-bw.tex`), con el texto de cada día en
`content/polish/q*.json`, y las comprobaciones son las mismas. Se está
escribiendo: el otoño, días 1--65, ya está. El plan, en
[`notes/03-polish.md`](notes/03-polish.md).

## Descargar el PDF sin instalar nada

**[⬇ PDF (color)](https://konradcinkusz.github.io/learning-to-count/aprendo-los-numeros.pdf)**
· **[⬇ PDF (blanco y negro)](https://konradcinkusz.github.io/learning-to-count/aprendo-los-numeros-bn.pdf)**

*First Numbers*: **[⬇ PDF (colour)](https://konradcinkusz.github.io/learning-to-count/first-numbers.pdf)**
· **[⬇ PDF (black and white)](https://konradcinkusz.github.io/learning-to-count/first-numbers-bw.pdf)**

Enlaces fijos, publicados por GitHub Pages en cada push a `main` (ver
`.github/workflows/pages.yml`). Las dos versiones tienen exactamente el
mismo contenido y la misma paginación: nada en el cuaderno se distingue
solo por el color. Mientras Pages no esté activado, los mismos PDF están
en la pestaña *Actions* → el último run de *Build* → artefactos
`pdf-color` / `pdf-bw` -- y los de *First Numbers*, `pdf-english` /
`pdf-english-bw`; y los de *Poznaję liczby*, mientras se escribe,
`pdf-polish` / `pdf-polish-bw`.

## Construir el PDF a mano

Necesita una distribución de TeX con **LuaLaTeX** (la letra es Andika,
cargada con `fontspec` desde `fonts/andika/`) + `latexmk`, con `babel`,
`tcolorbox` y `tikz`, y Python 3.

```sh
make              # genera, compila el cuaderno en color y comprueba
make english      # lo mismo, "First Numbers" (english.tex)
make polish       # lo mismo, "Poznaję liczby" (polish.tex)
make all-formats  # los seis PDF, color Y blanco-y-negro de los tres -- lo que corre el CI
make generate     # solo regenera los .tex de los tres cuadernos desde el JSON
make build        # solo compila en color (asume que ya está generado)
make build-bw     # solo compila en blanco y negro
make check        # lee main.log + 1 día = 1 página (main.aux) + valida el JSON
make clean
```

## Estructura

```
main.tex, main-bw.tex          -- el cuaderno, color y blanco-y-negro; solo fijan \bookcolor
english.tex, english-bw.tex    -- "First Numbers": lo mismo, con \booklang{english}
polish.tex, polish-bw.tex      -- "Poznaję liczby": lo mismo, con \booklang{polish}
preamble.tex, lang/es.tex      -- el motor LaTeX y todas las cadenas de texto
lang/en.tex, lang/pl.tex       -- las mismas cadenas, en inglés y en polaco
body.tex, body-english.tex, body-polish.tex -- el orden del documento
frontmatter/, backmatter/      -- portada, instrucciones, mapa del curso; clave de respuestas y diploma
frontmatter/english/, backmatter/english/ -- lo mismo, en inglés (y frontmatter/polish/, backmatter/polish/, en polaco)
content/q1.json ...            -- los días, uno por trimestre, editados a mano
content/english/q1.json ...    -- el texto en inglés de cada día (lo demás es el de content/q*.json)
content/polish/q1.json ...     -- lo mismo, en polaco
content/numeros-trazo.json     -- el contorno de cada número (Andika), generado por tools/gen_numeros_puntos.py
content/generated-*.tex        -- GENERADO por tools/gen_numeros.py, no editar
diagrams/kit.tex               -- las piezas de los dibujos de «First Words» (de Aprendo a leer)
diagrams/objetos.tex           -- las cosas que se cuentan, cada una en la misma caja
tools/gen_numeros.py           -- JSON -> LaTeX, la escalera, las comprobaciones de cada actividad, la clave
tools/idiomas.py               -- lo que se escribe en la página, en español, en inglés y en polaco
tools/gen_numeros_puntos.py    -- letra -> contorno de cada número (matplotlib; no forma parte de `make`)
tools/checklog.py              -- lee el .log de LuaLaTeX correctamente (de Aprendo a leer)
tools/check_pages.py           -- comprueba que cada día ocupa una sola página (de Aprendo a leer)
docs/index.html                -- la página que publica .github/workflows/pages.yml
notes/01-plan.md               -- el plan: la escalera, las actividades, las comprobaciones y las fases
notes/02-english.md            -- el plan de "First Numbers"
notes/03-polish.md             -- el plan de "Poznaję liczby"
```

## Licencia

Como *Aprendo a leer*: el motor -- LaTeX, los dibujos, las herramientas,
el `Makefile` y el CI -- está bajo MIT ([`LICENSE-CODE`](LICENSE-CODE));
el contenido -- los días de `content/q*.json`, la historia y lo que se
genera de ahí -- bajo Creative Commons BY-NC-SA 4.0
([`LICENSE-CONTENT`](LICENSE-CONTENT)); la letra Andika, bajo la SIL Open
Font License 1.1 ([`fonts/andika/OFL.txt`](fonts/andika/OFL.txt)). Ver
[`LICENSE`](LICENSE).

## Estado

**Completo.** Los 260 días, del 0 al 100 -- contar, trazar, comparar,
ordenar, sumar y restar hasta 20, contar de 2 en 2, de 5 en 5 y de 10 en
10, las decenas y las unidades, la tabla del 100, el dinero, la hora y
medir --, con sus tres medallas, la clave de respuestas y el diploma, en
color y en blanco y negro. Cada push comprueba el cuaderno entero: 1 día
= 1 página, log limpio, cada día dentro de la escalera. Se escribió en
cinco fases, un PR cada una: ver "Las fases" en
[`notes/01-plan.md`](notes/01-plan.md).

**First Numbers**, también completo: los 260 días en inglés, con sus
medallas, sus respuestas y su diploma, en color y en blanco y negro,
publicado junto al español. Se escribió en tres fases: ver
[`notes/02-english.md`](notes/02-english.md).

**Poznaję liczby**, en obras: el otoño (días 1--65, del 0 al 10), con su
medalla, en color y en blanco y negro. Faltan el invierno, la primavera
y el verano: ver [`notes/03-polish.md`](notes/03-polish.md).
