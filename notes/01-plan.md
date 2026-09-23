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

Del 11 al 20, dos por semana: el primero llega el lunes y el segundo el
miércoles (`LLEGADA` en el script), y cada uno se traza el día que
llega; hasta entonces, no se puede usar. Son *diez y algo más*: en «El
número de hoy» van dos marcos de diez, uno encima de otro (el primero,
lleno), y las cosas, las diez primeras aparte. Después, sin números
nuevos, una semana para cada cosa que se aprende a hacer con ellos — y,
como con los números, el script no deja usar una actividad antes de su
semana (`DESDE_SEMANA`).

| Semana | Tema | Qué llega |
|---|---|---|
| 14 | El frío de enero | 11 y 12 |
| 15 | El cumpleaños de Papá | 13 y 14 |
| 16 | El disfraz de Carnaval | 15 y 16 |
| 17 | El Día de la Paz | 17 y 18 (las palomas de papel) |
| 18 | Lucía se pone mala | 19 y 20 |
| 19 | Un domingo de manualidades con la abuela | *Compara*: más, menos, los mismos |
| 20 | La biblioteca del barrio | *Antes y después* |
| 21 | El cumpleaños de Toby | *La recta* |
| 22 | Un día de mucho viento | *Ordena* |
| 23 | El proyecto de plantas de Marta | *Junta*: las primeras sumas, hasta 5 |
| 24 | Dani rompe el dinosaurio de Lucía | *Junta*, hasta 10 |
| 25 | Huele a primavera | *Junta*, hasta 10, y diez y diez |
| 26 | Despedida del segundo trimestre | repaso, y la medalla de invierno |

### Primavera (semanas 27–39, días 131–195): sumar y restar hasta 10, hasta el 50

Ocho semanas sin números nuevos, para las cuentas hasta 10 — ya con sus
signos, y cada día el resultado es el número del día —, y después las
decenas: el 30, el 40 y el 50 (de 10 en 10), y cada semana una decena
entera, que llega el lunes (una semana con más números nuevos que días
de `LLEGADA` los recibe todos el lunes). Del 21 en adelante, «El número
de hoy» ya no dibuja las cosas: dibuja sus decenas y sus unidades (una
barra de diez cubitos por decena), con la tabla D | U.

| Semana | Tema | Qué llega |
|---|---|---|
| 27 | Toby se pierde en el parque | *Suma*: 3 + 2 = [ ] |
| 28 | A Dani se le cae un diente | *Parte en dos*: 5 son 2 y [ ] |
| 29 | El Día del Libro | *Hasta el 10*: 7 + [ ] = 10 |
| 30 | Empieza la Semana Santa | *Resta*: 5 − 2 = [ ] (las torrijas de la abuela) |
| 31 | El huerto del colegio | *Problema*: los lee el adulto |
| 32 | Lucía aprende a montar en bici | de 2 en 2 (las ruedas) |
| 33 | Lucía se apunta a natación | de 5 en 5 (los dedos de las manos) |
| 34 | El día de la madre | repaso: sumar, restar, problemas |
| 35 | Dani ya reconoce casi todas las letras | 30, 40 y 50: de 10 en 10 |
| 36 | Se acerca el fin de curso | del 21 al 29; *Decenas y unidades* |
| 37 | La oruga se convierte en mariposa | del 31 al 39 |
| 38 | La feria del libro de fin de curso | del 41 al 49 |
| 39 | Último día de colegio | repaso, y la medalla de primavera |

### Verano (semanas 40–52, días 196–260): hasta el 100, y los números de verdad

Primero, de 10 en 10 hasta el 100 (el 60, el 70, el 80, el 90 y el
100, el lunes), y después las decenas que faltan: del 51 al 69, y del 71
al 99, cada grupo una semana. Luego, las cuentas hasta 20 (`MAX_CUENTA`
del cuarto trimestre) y los números de verdad, en el pueblo de la abuela
Rosa: el dinero, la hora y medir.

| Semana | Tema | Qué llega |
|---|---|---|
| 40 | Empieza el verano | 60, 70, 80, 90 y 100 |
| 41 | Llegada al pueblo de la abuela Rosa | del 51 al 69 |
| 42 | Andrés, el vecino, y su gato Bigotes | del 71 al 99; *La tabla del 100* |
| 43 | Un día en el río del pueblo | sumar hasta 20 |
| 44 | El huerto de la abuela | restar hasta 20 |
| 45 | Una tormenta de verano | problemas hasta 20 |
| 46 | La excursión a la playa | *El dinero* |
| 47 | La verbena del pueblo | *El dinero*, y problemas con euros |
| 48 | Dani se hace amigo de Martín | *La hora*: en punto |
| 49 | Vuelta a la ciudad | *La hora*: y media |
| 50 | Preparativos para la vuelta al cole | *Mide* |
| 51 | Dani practica para leer en voz alta | repaso |
| 52 | Vuelta al cole | repaso, y el diploma |

Cada estación se concretó semana a semana (en `ESCALERA` y en las
actividades nuevas) antes de escribir sus días: las tablas de arriba son
lo que hay en el cuaderno.

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

## Las actividades del invierno

Las de otoño siguen (*Rodea*, *Cuenta* y *Colorea* llegan al 20; *Une*
puede usar marcos de diez en vez de cosas: `"objeto": "puntos"`), y
llegan seis, cada una en su semana:

| Actividad | Desde | Qué se hace | Qué comprueba el script |
|---|---|---|---|
| **Diez y más** | 14 | Una bandeja llena (10) y otra con lo que falta: "10 y 3 son [ ]" | que el total, del 11 al 20, sea el número del día |
| **Compara** | 19 | Rodear el grupo con más, con menos, o los dos que tienen los mismos; o, solo con números, el más grande o el más pequeño | que haya una sola respuesta, y que el número del día esté entre los grupos o los números |
| **Antes y después** | 20 | Tres casas: en la de en medio vive el número; en las de los lados se escriben el de antes y el de después | que el de antes y el de después hayan llegado (el 0 no tiene de antes) |
| **La recta** | 21 | Una recta de 5 a 11 números, con 1–3 huecos | que el primero se vea y que la recta pase por el número del día |
| **Ordena** | 22 | Tarjetas desordenadas, y abajo, en fila, los huecos para escribirlas en orden (de menor a mayor, o al revés) | que no vengan ya en orden |
| **Junta** | 23 | Dos grupos con una "y" en medio: "3 y 2 son [ ]" — la suma, sin signos todavía | que sume el número del día, y como mucho 10 |

Los días con dos números nuevos, el lunes y el miércoles son *Traza*
(con dos renglones: la caja de arriba es más alta), el martes y el
jueves usan el último número que ha llegado, y el viernes, *Repasa*,
cualquiera de los dos.

## Las actividades de la primavera

Las cuentas llevan ya sus signos (el menos, `−`, es el de verdad, el de
Andika), llegan como mucho a 10 (`MAX_CUENTA`), y su resultado es
siempre el número del día. *Completa* y *La recta* pueden ir de 2 en 2
(desde la semana 32), de 5 en 5 (33) y de 10 en 10 (35) — `PASOS_DESDE`
—, y *Cuenta* puede contar las ruedas de las bicis de 2 en 2 o los dedos
de las manos de 5 en 5 (`CONTAR_DE`).

| Actividad | Desde | Qué se hace | Qué comprueba el script |
|---|---|---|---|
| **Suma** | 27 | Dos grupos con un + en medio: "3 + 2 = [ ]" | que el resultado sea el número del día, y como mucho 10 |
| **Parte en dos** | 28 | Una fila de cosas, partida por una raya: "5 son 2 y [ ]" | que las dos partes tengan una cosa o más |
| **Hasta el 10** | 29 | Un marco de diez grande, con puntos: se dibujan los que faltan, "7 + [ ] = 10" | que lo que falta sea el número del día |
| **Resta** | 30 | Se tachan las que se quitan: "5 − 2 = [ ]" | que no se quite más de lo que hay |
| **Problema** | 31 | Un problema corto, que lee el adulto; un recuadro para dibujarlo y "[ ] + [ ] = [ ]" | que el problema diga sus dos números, y que la cuenta dé el número del día |
| **Decenas y unidades** | 36 | Barras de diez cubitos y cubitos sueltos: "[ ] decenas y [ ] unidades son [ ]" | que sea el número del día, del 11 en adelante |

## Las actividades del verano

| Actividad | Desde | Qué se hace | Qué comprueba el script |
|---|---|---|---|
| **La tabla del 100** | 42 | Media tabla (cinco filas de diez) con 3–8 casillas vacías | que empiece en una decena (1, 11... 51), que todos sus números hayan llegado y que tenga el número del día |
| **El dinero** | 46 | Billetes (5, 10, 20 €) y monedas (1, 2 €): "Hay [ ] euros" | que sea el número del día, y como mucho 20 € |
| **La hora** | 48 | Un reloj de agujas: "Son las [ ] en punto" (o "y media", desde la semana 49: `MEDIA_DESDE`) | que la hora sea el número del día |
| **Mide** | 50 | Uno o dos lápices sobre una regla de cubitos: cuántos mide cada uno, y cuál es más largo | que midan de 2 a 14 cubitos, distintos, y uno, el número del día |

Las cuentas del verano (*Suma*, *Resta*, *Problema*) llegan hasta 20.
Del 100 se encoge un poco su número en «El número de hoy», y el tren de
*Completa* escribe sus números más pequeños, para que quepan.

## Cómo se comprueba

- `make generate` escribe `content/generated-days.tex` y
  `content/generated-clave.tex`; `python3 tools/gen_numeros.py --check`
  valida el JSON (calendario, temas, escalera, actividades) y que lo
  generado esté al día.
- `tools/checklog.py` lee el log de LuaLaTeX (errores, cajas overfull) y
  `tools/check_pages.py` comprueba en el `.aux` que cada día ocupa
  exactamente una página — los dos, de *Aprendo a leer* —, y además que
  el día 1 cae en la página 5: "Las actividades" (la página que las
  explica, una a una, para el adulto) crece con cada estación, y tiene
  que seguir cabiendo en una página.
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
3. **El invierno** (días 66–130): del 11 al 20, dos por semana;
   comparar, antes y después, la recta, ordenar y las primeras sumas,
   con seis actividades nuevas y 21 dibujos más (copos, un muñeco de
   nieve, palomas de papel, ovillos, semillas...). Hecho.
4. **La primavera** (días 131–195): las cuentas con sus signos hasta
   10, contar de 2 en 2, de 5 en 5 y de 10 en 10, y las decenas hasta
   el 50, con seis actividades nuevas y 18 dibujos más (el diente de
   Dani, las torrijas de la abuela, la bici, la mano...). Hecho.
5. **El verano** (días 196–260): hasta el 100, las cuentas hasta 20, la
   tabla del 100, el dinero, la hora y medir, con cuatro actividades
   nuevas y los dibujos del pueblo (el helado, la concha, el caracol,
   la maleta...); el diploma, y el cuaderno completo (`DIAS_ESCRITOS =
   None`). Hecho.
