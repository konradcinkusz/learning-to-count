# «Poznaję liczby» — el cuaderno en polaco

*Aprendo los números* en polaco, **página a página**, como *First
Numbers* en inglés: el mismo número, las mismas cosas dibujadas y la
misma actividad cada día, así que una niña o un niño puede hacer el que
quiera, o más de uno. Es para una familia que hable polaco en casa, o
para quien lo aprende, y es de la misma familia que *Poznaję ekonomię*,
el *Aprendo economía* en polaco
(https://github.com/konradcinkusz/learning-economics).

## El motor, en tres lenguas

El de *First Numbers*, sin una segunda copia de los días:
`content/polish/q*.json` solo trae el texto de cada uno -- la `frase`
de la historia, que lee el adulto, y el `prompt`, la `checklist` y el
`texto` de "Dibuja", "Repasa" y "Problema" --, y `cargar_traduccion`
(en `tools/gen_numeros.py`) lo pone encima del día de `content/q*.json`
y lo comprueba todo, como en inglés. Ver "Qué se mantiene y qué cambia"
en [`02-english.md`](02-english.md). La actividad de cada día es la de
*Aprendo los números*, siempre: el polaco no tiene actividades propias
(`Polaco.solo_aqui` está vacío), porque *trzynaście* y *trzydzieści* no
se confunden como *thirteen* y *thirty*.

Lo que cambia en el motor para que quepa una tercera lengua:

- `tools/gen_numeros.py` genera cada cuaderno de un `Cuaderno`: su
  nombre, su lengua (`ESPANOL`, `INGLES`, `POLACO`, de
  `tools/idiomas.py`), su carpeta, su `lang/*.tex` y cuántos días están
  escritos (`DIAS_ESCRITOS_POLACO`, mientras se escribe). `APRENDO` es
  el español; `TRADUCCIONES`, *First Numbers* y *Poznaję liczby*.
- `preamble.tex`: `\booklang{polish}` lee `lang/pl.tex` y carga
  `babel` en polaco (con `\shorthandoff{"}`, como el español).
- `lang/pl.tex`, `polish.tex`, `polish-bw.tex`, `body-polish.tex`, y
  `frontmatter/polish/` y `backmatter/polish/` (las páginas para el
  adulto, la clave y el diploma).

Lo generado para *Aprendo los números* y *First Numbers* es, letra por
letra, lo que era antes.

## El polaco

**El número cambia de forma.** Con lo que cuenta ("jeden pies", "jedna
piłka", "jedno jabłko"), con el caso ("Lucía ma jednego psa", "bawi się
dwiema piłkami", "z sześcioma samochodzikami") y con quién ("dwaj
chłopcy", "troje dzieci"). Así que la frase del día no se busca en una
lista: `Polaco._valores` lee los números que dice, con todas sus formas
(`_FORMAS`), y la frase tiene que decir el del día. "Dwadzieścia jeden"
es el 21, y no dice ni el 20 ni el 1; "ani jeden" dice el 1, y no vale
para el 0, que se dice *zero*, *żaden*, *nic* o *nikt*.

**Y la cosa, con el número.** El 1 lleva el singular (*1 piłka*); el 2,
el 3 y el 4 (y el 22, el 23, el 24..., pero no el 12, el 13 ni el 14),
el nominativo plural (*2 piłki*); y los demás, el genitivo plural (*5
piłek*, *12 piłek*). Cada cosa trae sus cuatro formas y su género
(`objetos`: *piłka, piłkę, piłki, piłek*), también en acusativo cuando
se colorea o se tacha (*Pokoloruj 1 piłkę*, *Skreśl 3 psy*). Lo que el
número no deja escribir bien, porque todavía no se sabe cuál es, se
dice sin concordancia: *Liczba kostek: [ ]*, *dziesiątki: [ ]
jedności: [ ]*.

**La hora.** En polaco, las tres y media es *wpół do czwartej*: la
media hora se dice con la hora que llega. La hora en punto se completa
con la hora ("Jest godzina [3]"), y la media con la siguiente ("Jest
wpół do [4]"); la instrucción lo explica, y la clave da las dos cosas:
*wpół do 4 (3:30)*.

Lo demás, como en *Poznaję ekonomię*: los personajes y lo que es de
aquí se quedan (Lucía, Dani, Toby, babcia Rosa, pani Marta, pan Pedro,
el turrón, los churros, los Reyes); el dinero son euros, que no se
declinan (*1 euro*, *5 euro*); lo que dice la niña o el niño no tiene
género (*Wiem...*, *Umiem...*, *napisz samodzielnie*); y las decenas y
las unidades son *D* y *J*, como en los colegios polacos.

## Las comprobaciones

Las mismas en los tres cuadernos: `python3 tools/gen_numeros.py --check`
valida y genera los tres; `make polish` compila y comprueba el cuaderno
en polaco, y `make all-formats`, los seis PDF (color y blanco y negro de
cada uno): el log, que cada día ocupa una página, y el día 1 la página
5. El CI hace lo mismo, con un job por PDF.

## Las fases

Como *First Numbers*, un PR por fase, cada uno en verde antes de
fusionarse. `DIAS_ESCRITOS_POLACO`, en `tools/gen_numeros.py`, dice
cuántos días están escritos.

1. **El motor en tres lenguas y el otoño** (días 1--65): `POLACO` en
   `tools/idiomas.py`, `Cuaderno` y `cargar_traduccion`, `lang/pl.tex`,
   `polish.tex`, las páginas para el adulto y el texto de los 65 días.
   Además, un cuaderno de prueba con los 260 días (con frases de
   relleno) para ver cómo quedan en polaco todas las actividades,
   también las que llegan después. **Hecho.**
2. **El invierno y la primavera** (días 66--195). **Hecho.**
3. **El verano** (días 196--260), y publicarlo: la página de descarga y
   Pages con los seis PDF.
