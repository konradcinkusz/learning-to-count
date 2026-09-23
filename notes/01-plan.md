# «Aprendo los números» — el plan

Un cuaderno diario de números, de la misma familia que *Aprendo a leer*
(https://github.com/konradcinkusz/learning-to-read): el mismo motor
(JSON → LaTeX, LuaLaTeX, la letra Andika, color y blanco y negro, un día
por página, comprobado a máquina), el mismo calendario, la misma familia
y los mismos temas semana a semana. Nació del issue C de aquel
repositorio (#15, "Inna umiejętność — silnik Traza"): el mismo mecanismo
de trazo que las letras — el contorno real del glifo de la letra del
cuaderno, convertido en puntos —, aplicado a los números, y alrededor
un cuaderno de contar.

## Para quién

Para una niña o un niño de cinco o seis años (el último curso de
Infantil o el principio de 1.º de Primaria) que empieza con los
números: reconocerlos, contarlos y escribirlos, y a lo largo del año
compararlos, sumar y restar. No hace falta que sepa leer: lo que se lee
(la frase de la historia, las instrucciones) lo lee un adulto, y lo que
hace la niña o el niño va siempre grande — el número, las cosas que se
cuentan, el enunciado de una línea.

## Lo que se mantiene igual que en *Aprendo a leer*

- **260 días, 52 semanas, cuatro trimestres = cuatro estaciones**, con
  vacaciones incluidas, y una medalla al final de otoño, invierno y
  primavera; un diploma al final.
- **Los mismos temas semana a semana** (`TEMAS` en `tools/gen_numeros.py`,
  copiados del cuaderno de frases): quien lleve los dos cuadernos
  cuenta esa semana lo que lee. La semana del cumpleaños de Lucía, el
  número es el 7: las siete velas.
- **La página**: la cabecera de siempre (día, semana, trimestre, tema;
  fecha, *Hecho: sola / con ayuda / con dificultad*, notas), una caja de
  arriba igual todos los días y una caja de actividad que llena lo que
  queda de página. El pie, "Día N / 260".
- **La escalera no es una disciplina editorial**: está en el script
  (`ESCALERA`, `conocidos()`), y el script falla si un día usa un número
  que todavía no ha llegado.
- **La letra**: Andika, y los números que se trazan salen de su propio
  glifo (`tools/gen_numeros_puntos.py` → `content/numeros-trazo.json`),
  como las letras de *Aprendo a leer*: el 4 que se traza es el mismo 4
  que se lee en el resto del cuaderno. En Andika, el 6 y el 9 son un
  solo contorno que se cruza consigo mismo; el script quita los puntos
  que quedan dentro del trazo relleno, que no son borde de nada.
- **Los dibujos**: las cosas que se cuentan son, casi todas, dibujos de
  *First Words* (`diagrams/kit.tex`, copiado de *Aprendo a leer*), cada
  uno metido en la misma caja (`diagrams/objetos.tex`), para colorear.

## La caja de arriba: "El número de hoy"

El número, grande; su nombre; el **marco de diez** (dos filas de cinco
casillas, con un punto en las N primeras: el 5 es una fila entera, el 7
una fila y dos más — la manera de ver de un vistazo cuánto es un número
hasta el 10); esas cosas dibujadas, tantas como el número, y debajo una
**frase de la historia** que lee el adulto: *Lucía tiene un perro, y se
llama Toby.* La frase tiene que decir el número del día (con letra: *un,
una, uno, dos...*; el 0, *cero, ningún, ninguna, ninguno* o *nada*): el
script lo comprueba.

El día del **0**, lo dibujado es un recipiente vacío — la cesta en la
que no queda ninguna castaña, el plato en el que no queda nada
(`CONTENEDORES` en el script) —, y el marco de diez, sin ningún punto.
El **10** es el primer número de dos cifras: su columna se ensancha lo
que haga falta (`\numeroDeHoy`), y sus cosas se dibujan un poco más
pequeñas para que quepan.

## La escalera, semana a semana

### Otoño (semanas 1–13, días 1–65): del 1 al 10, y el 0

Un número nuevo por semana. El lunes se traza; el resto de la semana es
el número de todos los días.

| Semana | Tema | Número |
|---|---|---|
| 1 | La familia de Lucía | 1 |
| 2 | Toby, el perro juguetón | 2 |
| 3 | El colegio de Lucía | 3 |
| 4 | El barrio y el parque | 4 |
| 5 | La comida en casa | 5 |
| 6 | Llega el otoño | repaso del 1 al 5 (las hojas) |
| 7 | Los juguetes de Dani | 6 |
| 8 | Castañas y Todos los Santos | 0 (la cesta vacía) |
| 9 | El cumpleaños de Lucía | 7 (las velas) |
| 10 | Los animales del barrio | 8 (las patas de la araña) |
| 11 | Un día de lluvia | 9 |
| 12 | Ir al mercado con Mamá | 10 (los huevos) |
| 13 | Nochebuena | repaso del 0 al 10 |

### Invierno (semanas 14–26, días 66–130): hasta el 20, comparar, las primeras sumas

La decena (10 = una fila entera del marco de diez, dos veces) y los
números del 11 al 20, dos por semana (semanas 14–18); más, menos e igual
(19); el anterior y el siguiente, la recta numérica (20–21); ordenar
(22); juntar: la suma con dibujos, hasta 5 y hasta 10 (23–25); repaso
(26).

### Primavera (semanas 27–39, días 131–195): sumar y restar hasta 10, hasta el 50

Sumas hasta 10, ya con los signos + e =; partir un número en dos (5 = 2
+ 3) y las parejas que suman 10; quitar: la resta, hasta 10; problemas
que lee el adulto; contar de 2 en 2, de 5 en 5 y de 10 en 10; las
decenas hasta el 50.

### Verano (semanas 40–52, días 196–260): hasta el 100, y los números de verdad

Las decenas hasta el 100 y la tabla del 100; sumas y restas hasta 20; el
dinero (euros), la hora (en punto, y media), medir (más largo, más
corto, con palmos), en el pueblo de la abuela Rosa; repaso y diploma.

Lo de invierno en adelante es el plan: cada fase lo concreta semana a
semana (y lo lleva a `ESCALERA` y a las actividades nuevas) antes de
escribir sus días.

## Las actividades (otoño)

El ciclo de una semana con número nuevo: el **lunes, Traza**; el
**viernes, Repasa**; en medio, una de las demás. El script exige que el
lunes de una semana con número nuevo sea *Traza* y que *Repasa* sea la
de los viernes, y solo de los viernes.

| Actividad | Qué se hace | Qué comprueba el script |
|---|---|---|
| **Traza** | Repasar el número con el dedo por los puntos, luego con un lápiz, y escribirlo en tres renglones con un número de muestra | que el número haya llegado; que haya contorno para cada cifra (el 10 son dos) |
| **Colorea** | Colorear exactamente N de las cosas; las demás, en blanco | que N haya llegado; que haya más cosas que N, y como mucho 10 |
| **Rodea** | Entre 2–4 grupos, rodear el que tiene N | que haya exactamente un grupo de N, todos distintos, de 1 a 10 cosas; hasta el 6 van como los puntos de un dado, y del 7 al 10 como en el marco de diez (así se ven de un vistazo); el grupo vacío, solo el día que se rodea el 0 |
| **Cuenta** | Contar un grupo, señalando cada cosa, y rodear su número entre 2–4 | que la respuesta esté entre las opciones, y que todas hayan llegado; el grupo va en una bandeja, que el día del 0 está vacía |
| **Busca** | Rodear el número cada vez que sale, en una cuadrícula con otros números y formas | que los otros números hayan llegado; la cuadrícula la baraja el script con el número del día (siempre la misma); el día del 0, sin círculos, que se confunden con él |
| **Une** | Contar cada grupo (2–4, uno debajo de otro) y trazar una línea hasta su número | que los grupos sean distintos, de hasta 10, que hayan llegado y que uno sea el número del día; los números los desordena el script — ninguno enfrente de su grupo —, con el número del día |
| **Completa** | Un tren de 4–7 vagones con números seguidos, de uno en uno, hacia arriba o hacia atrás: escribir los 1–2 que faltan | que la serie vaya de uno en uno, que todos sus números hayan llegado y que pase por el número del día |
| **Dibuja** | Dibujar N cosas | que el enunciado diga N (y N, al menos 1) |
| **Repasa** | Lo que ya sabe hacer esa semana, para marcarlo, y un dibujo; cada diez páginas, el cartel "¡N páginas hechas!" | el cartel lo pone el script |

Los enunciados de *Colorea*, *Rodea*, *Cuenta*, *Busca*, *Une* y
*Completa* los compone el script con el número y las cosas del día
("Colorea 2 pelotas.", "¿Cuántos huesos hay?", "Rodea donde no hay
ninguna castaña."), con su género y su número: no se escriben a mano.
Las respuestas de la clave, igual: *Rodea* (qué grupo), *Cuenta* (el
número), *Busca* (cuántas veces sale), *Une* (el número de cada grupo,
de arriba abajo) y *Completa* (los que faltan), calculadas.

En el otoño, las semanas con número nuevo tienen, entre el lunes y el
viernes, tres de las demás; las dos de repaso (la 6, del 1 al 5, y la
13, del 0 al 10) no tienen *Traza*, y el número de cada día es uno de
los que ya han llegado.

## Cómo se comprueba

- `make generate` escribe `content/generated-days.tex` y
  `content/generated-clave.tex`; `python3 tools/gen_numeros.py --check`
  valida el JSON (calendario, temas, escalera, actividades) y que lo
  generado esté al día.
- `tools/checklog.py` lee el log de LuaLaTeX (errores, cajas overfull) y
  `tools/check_pages.py` comprueba en el `.aux` que cada día ocupa
  exactamente una página — los dos, de *Aprendo a leer*, sin cambios.
- El CI (`.github/workflows/build.yml`) hace las dos cosas en cada push y
  cada PR, en color y en blanco y negro; Pages publica los dos PDF en
  cada push a `main`.

## Las fases

Como *Aprendo a leer*: un PR por fase, cada uno en verde antes de
fusionarse, y `DIAS_ESCRITOS` dice cuántos días hay ya.

1. **El motor, el diseño y las semanas 1–2** (el 1 y el 2). Hecho.
2. **El otoño** (días 11–65): del 3 al 10 y el 0, con las cosas nuevas
   que había que dibujar (castañas, la cesta, velas, una araña, huevos
   en su huevera — solos, se confundían con el 0 —...) y dos
   actividades nuevas, *Une* y *Completa*. Hecho.
3. **El invierno** (días 66–130): la decena, hasta el 20, comparar, las
   primeras sumas — con sus actividades nuevas.
4. **La primavera** (días 131–195).
5. **El verano** (días 196–260), el diploma, y el cuaderno completo.
