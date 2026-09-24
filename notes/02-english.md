# «First Numbers» — el cuaderno en inglés

*Aprendo los números* en inglés, **página a página**: el mismo número,
las mismas cosas dibujadas y la misma actividad cada día, así que una
niña o un niño puede hacer uno, el otro o los dos. Es para quien
aprende inglés en el colegio, como Lucía en *Read and Draw* y *First
Words* (de *Aprendo a leer*), y también para una familia que hable
inglés en casa.

## Qué se mantiene y qué cambia

Se mantiene todo lo que no es lengua: el calendario, la escalera
(`ESCALERA`), las actividades y cuándo llega cada una (`DESDE_SEMANA`),
los dibujos, lo que se comprueba de cada actividad y la clave, que la
calcula el script. No hay una segunda copia de los días:
`content/english/q*.json` solo trae el texto de cada uno, y
`cargar_ingles` (en `tools/gen_numeros.py`) lo pone encima del día de
`content/q*.json`:

- `frase`: la frase de la historia, que lee el adulto;
- `prompt`, en "Dibuja" y en "Repasa" (lo que se dibuja);
- `checklist`, en "Repasa" (las mismas cosas que en español: tres);
- `texto`, en "Problema".

Lo demás que se lee en la página sale de `tools/idiomas.py` (los
nombres de los números y de las cosas, los temas de cada semana, el
enunciado, la instrucción y la clave de cada actividad), de
`lang/en.tex` (los títulos de las cajas, la cabecera, la portada) y de
`frontmatter/english/` y `backmatter/english/` (las páginas para el
adulto, la clave y el diploma). El español es `ESPANOL`, en el mismo
fichero, y lo que genera es, letra por letra, lo que generaba el script
antes de que hubiera un cuaderno en inglés.

## El inglés

**Británico**, como *Read and Draw* y *First Words*: colour, Mum,
biscuits, sweets, pudding, wellies, a rubber para borrar, a woolly hat.

Lo que es de aquí se queda como en esos dos cuadernos: los nombres
(Lucía, Dani, Toby, Grandma Rosa, Marta, Sofía, Pedro y su gata Luna;
en verano, Andrés, su gato Bigotes y Martín), el turrón, los churros,
las torrijas, la fiesta del pueblo, los Reyes (*the Three Kings*). Y el
dinero son **euros**: Lucía vive en España, y las monedas y los billetes
del cuaderno son los de verdad.

**La frase del día dice el número del día, con letra**, como en
español -- y en inglés el 1 tiene que ser *one*: "Lucía has one dog"
dice un número, "Lucía has a dog" no. El 0 puede ser *zero*, *no*,
*none*, *nothing* o *nobody*. Los nombres de dos palabras llevan guion
(*twenty-one*), y *twenty* no vale por *twenty-one*: el script busca la
palabra entera, guion incluido.

## Lo único que tiene de más: "Number names"

En inglés, *thirteen* y *thirty*, *fourteen* y *forty*... suenan casi
igual; en español, *trece* y *treinta* no se parecen. Así que cuando
llegan las decenas, dos días cambian su actividad por **Number names**:
unir cada número con su nombre, que lee el adulto marcando el final
(thir**teen**, **thir**ty).

- el día 174 (semana 35, cuando llegan el 30, el 40 y el 50): 13, 30,
  14, 40, 15 y 50;
- el día 198 (semana 40, cuando llegan del 60 al 100): 16, 60, 17, 70,
  18 y 80.

Son los únicos días en que la actividad no es la de *Aprendo los
números*: `cargar_ingles` solo deja cambiarla por una de las que el
cuaderno en español no tiene (`Ingles.solo_aqui`), y "Number names"
pasa por las mismas comprobaciones que las demás (de 4 a 6 números, ya
llegados, uno de ellos el del día, y desde la semana 35).

## Las comprobaciones

Las mismas, en los dos cuadernos: `python3 tools/gen_numeros.py --check`
valida y genera los dos; `make all-formats` compila los cuatro PDF
(color y blanco y negro de cada uno) y comprueba el log y que cada día
ocupa una página, y el día 1 la página 5 (también en inglés: las páginas
para el adulto tienen que seguir cabiendo en una cada una). El CI hace
lo mismo, con un job por PDF.

## Las fases

Como *Aprendo los números*, un PR por fase, cada uno en verde antes de
fusionarse. `DIAS_ESCRITOS_INGLES`, en `tools/gen_numeros.py`, dice
cuántos días están escritos.

1. **El motor en dos lenguas y el otoño** (días 1--65): `tools/idiomas.py`,
   `lang/en.tex`, `english.tex`, las páginas para el adulto y el
   texto de los 65 días. Además, un cuaderno de prueba con los 260 días
   (con frases de relleno) para ver cómo quedan en inglés todas las
   actividades, también las que llegan después. **Hecho.**
2. **El invierno y la primavera** (días 66--195), con el primer día de
   "Number names".
3. **El verano** (días 196--260), con el segundo, y publicarlo: la
   página de descarga y Pages con los cuatro PDF.
