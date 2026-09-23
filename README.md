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
completar el tren de números, dibujar N cosas, y los viernes, repasar.

- **Otoño**: del 1 al 10, y el 0 -- un número nuevo cada semana.
- **Invierno**: hasta el 20, más y menos, el anterior y el siguiente,
  las primeras sumas con dibujos.
- **Primavera**: sumar y restar hasta 10, contar de 2 en 2, de 5 en 5 y
  de 10 en 10, hasta el 50.
- **Verano**: hasta el 100, sumas y restas hasta 20, el dinero, la hora
  y medir.

El plan completo, semana a semana, está en
[`notes/01-plan.md`](notes/01-plan.md).

## Descargar el PDF sin instalar nada

**[⬇ PDF (color)](https://konradcinkusz.github.io/learning-to-count/aprendo-los-numeros.pdf)**
· **[⬇ PDF (blanco y negro)](https://konradcinkusz.github.io/learning-to-count/aprendo-los-numeros-bn.pdf)**

Enlaces fijos, publicados por GitHub Pages en cada push a `main` (ver
`.github/workflows/pages.yml`). Las dos versiones tienen exactamente el
mismo contenido y la misma paginación: nada en el cuaderno se distingue
solo por el color. Mientras Pages no esté activado, los mismos PDF están
en la pestaña *Actions* → el último run de *Build* → artefactos
`pdf-color` / `pdf-bw`.

## Construir el PDF a mano

Necesita una distribución de TeX con **LuaLaTeX** (la letra es Andika,
cargada con `fontspec` desde `fonts/andika/`) + `latexmk`, con `babel`,
`tcolorbox` y `tikz`, y Python 3.

```sh
make              # genera, compila el cuaderno en color y comprueba
make all-formats  # los dos PDF, color Y blanco-y-negro -- lo que corre el CI
make generate     # solo regenera los .tex desde el JSON
make build        # solo compila en color (asume que ya está generado)
make build-bw     # solo compila en blanco y negro
make check        # lee main.log + 1 día = 1 página (main.aux) + valida el JSON
make clean
```

## Estructura

```
main.tex, main-bw.tex          -- el cuaderno, color y blanco-y-negro; solo fijan \bookcolor
preamble.tex, lang/es.tex      -- el motor LaTeX y todas las cadenas de texto
body.tex                       -- el orden del documento
frontmatter/, backmatter/      -- portada, instrucciones, mapa del curso; clave de respuestas y diploma
content/q1.json ...            -- los días, uno por trimestre, editados a mano
content/numeros-trazo.json     -- el contorno de cada número (Andika), generado por tools/gen_numeros_puntos.py
content/generated-*.tex        -- GENERADO por tools/gen_numeros.py, no editar
diagrams/kit.tex               -- las piezas de los dibujos de «First Words» (de Aprendo a leer)
diagrams/objetos.tex           -- las cosas que se cuentan, cada una en la misma caja
tools/gen_numeros.py           -- JSON -> LaTeX, la escalera, las comprobaciones de cada actividad, la clave
tools/gen_numeros_puntos.py    -- letra -> contorno de cada número (matplotlib; no forma parte de `make`)
tools/checklog.py              -- lee el .log de LuaLaTeX correctamente (de Aprendo a leer)
tools/check_pages.py           -- comprueba que cada día ocupa una sola página (de Aprendo a leer)
docs/index.html                -- la página que publica .github/workflows/pages.yml
notes/01-plan.md               -- el plan: la escalera, las actividades, las comprobaciones y las fases
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

**En obras.** Fase 2 de 5: el otoño entero (días 1–65: del 1 al 10, y
el 0) y su medalla, en color y en blanco y negro, con las mismas
comprobaciones que tendrá el cuaderno entero -- 1 día = 1 página, log
limpio, cada día dentro de la escalera. Ver "Las fases" en
[`notes/01-plan.md`](notes/01-plan.md).
