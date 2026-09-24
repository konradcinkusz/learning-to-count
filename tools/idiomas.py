"""Las tres lenguas de los cuadernos de números.

tools/gen_numeros.py genera tres cuadernos que son, página a página, el
mismo: "Aprendo los números" (main.tex), en español; "First Numbers"
(english.tex), en inglés británico, como "Read and Draw" y "First Words"
de "Aprendo a leer"; y "Poznaję liczby" (polish.tex), en polaco.
Comparten todo lo que no es lengua -- el calendario, la escalera, los
dibujos, las actividades y lo que se comprueba de cada una --, y lo que
cambia de uno a otro está aquí, en un solo sitio:

  - cómo se llama cada número, y cómo puede aparecer en la frase del día
    (en español, "un perro", "una manzana", "ninguna castaña"; en
    inglés, "one dog", "no chestnuts"; en polaco, "jednego psa", "dwie
    piłki", "żadnego kasztana");
  - cómo se llaman las cosas que se cuentan (el dibujo es el mismo:
    OBJETOS, en tools/gen_numeros.py);
  - el tema de cada semana y el nombre de cada medalla;
  - y el enunciado, la instrucción y la entrada de la clave de cada
    actividad, que tools/gen_numeros.py compone con los números y las
    cosas de cada día ("Colorea 2 pelotas.", "Colour 2 balls.").

Lo que la página dice siempre igual (los títulos de las cajas, la
cabecera de cada día, la portada) no está aquí, sino en lang/es.tex,
lang/en.tex y lang/pl.tex.

Cada lengua es un objeto con los mismos métodos: ESPANOL, INGLES y
POLACO, más abajo. Los métodos de ESPANOL devuelven, letra por letra, lo
que escribía tools/gen_numeros.py antes de que hubiera un cuaderno en
inglés.
"""

import re
from string import Template


# La página de medalla del final de cada trimestre (T1-T3): de una lengua
# a otra solo cambian "días" y "páginas" (el título y el ánimo están en
# lang/es.tex y lang/en.tex).
_MEDALLA = r"""\begin{center}
\vspace*{3cm}
\medalla{$dia}

\vspace{10mm}
{\fontsize{34}{40}\selectfont\bfseries\color{colorLectura}\lblMedalla{$estacion}}\\[8mm]
{\Large $dia\ %s, $dia\ %s.}\\[12mm]
{\Large \lblMedallaAnimo}
\end{center}
\vspace*{\fill}
\newpage
"""


class Espanol:
    codigo = "es"

    # Los temas de cada semana: los de "Aprendo a leer" (el cuaderno de
    # frases y el de primeras palabras cuentan el mismo año con los mismos
    # temas), para que quien lleve los dos cuadernos cuente esa semana lo
    # que lee. El tema de cada día tiene que ser el de su semana.
    temas = [
        "La familia de Lucía", "Toby, el perro juguetón", "El colegio de Lucía",
        "El barrio y el parque", "La comida en casa", "Llega el otoño",
        "Los juguetes de Dani", "Castañas y Todos los Santos",
        "El cumpleaños de Lucía", "Los animales del barrio", "Un día de lluvia",
        "Ir al mercado con Mamá", "Nochebuena",
        "El frío de enero", "El cumpleaños de Papá", "El disfraz de Carnaval",
        "El Día de la Paz", "Lucía se pone mala",
        "Un domingo de manualidades con la abuela", "La biblioteca del barrio",
        "El cumpleaños de Toby", "Un día de mucho viento",
        "El proyecto de plantas de Marta", "Dani rompe el dinosaurio de Lucía",
        "Huele a primavera", "Despedida del segundo trimestre",
        "Toby se pierde en el parque", "A Dani se le cae un diente",
        "El Día del Libro", "Empieza la Semana Santa", "El huerto del colegio",
        "Lucía aprende a montar en bici", "Lucía se apunta a natación",
        "El día de la madre", "Dani ya reconoce casi todas las letras",
        "Se acerca el fin de curso", "La oruga se convierte en mariposa",
        "La feria del libro de fin de curso", "Último día de colegio",
        "Empieza el verano", "Llegada al pueblo de la abuela Rosa",
        "Andrés, el vecino, y su gato Bigotes", "Un día en el río del pueblo",
        "El huerto de la abuela", "Una tormenta de verano",
        "La excursión a la playa", "La verbena del pueblo",
        "Dani se hace amigo de Martín", "Vuelta a la ciudad",
        "Preparativos para la vuelta al cole",
        "Dani practica para leer en voz alta", "Vuelta al cole",
    ]

    nombre_medalla = {1: "Otoño", 2: "Invierno", 3: "Primavera"}
    plantilla_medalla = Template(_MEDALLA % ("días", "páginas"))

    # Las actividades que solo tiene uno de los dos cuadernos: ninguna.
    solo_aqui = frozenset()

    # Cómo se llama cada número, y cómo puede aparecer en la frase del día
    # (la frase de un día con el 1 dice "un perro" o "una manzana"; con el
    # 21, "veintiún globos" o "veintiuna velas").
    _HASTA_29 = [
        "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
        "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis",
        "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidós",
        "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete",
        "veintiocho", "veintinueve",
    ]
    _DECENAS = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta",
                7: "setenta", 8: "ochenta", 9: "noventa"}

    def __init__(self):
        self.nombres = {n: self._nombre(n) for n in range(101)}

    def _nombre(self, n):
        if n < 30:
            return self._HASTA_29[n]
        if n == 100:
            return "cien"
        d, u = divmod(n, 10)
        return self._DECENAS[d] + (f" y {self._HASTA_29[u]}" if u else "")

    def formas(self, n):
        if n == 0:
            return {"cero", "ningún", "ninguna", "ninguno", "nada"}
        nombre = self.nombres[n]
        if n % 10 == 1 and n != 11:
            raiz = nombre[:-3]    # "uno" -> "un", "una"; "veintiuno" -> "veintiún"
            return {nombre, raiz + ("ún" if n == 21 else "un"), raiz + "una"}
        return {nombre}

    def dice(self, texto, n):
        """¿Dice `texto` el número n, con letra? (La frase del día.)"""
        return any(re.search(rf"\b{re.escape(f)}\b", texto.lower()) for f in self.formas(n))

    def dice_cuantas(self, texto, n):
        """¿Dice `texto` cuántas cosas son, con cifras o con letra? ("Dibuja".)"""
        return bool(re.search(rf"\b({n}|{'|'.join(self.formas(n))})\b", texto.lower()))

    def en_texto(self, texto, n):
        """¿Dice `texto` el número n, con cifras o con letra? ("Problema".)"""
        t = texto.lower()
        return bool(re.search(rf"(?<!\d){n}(?!\d)", t)) or any(
            re.search(rf"\b{re.escape(f)}\b", t) for f in self.formas(n))

    # ----------------------------------------------------------------
    # Las cosas que se cuentan: singular, plural y género -- el
    # enunciado se compone con ellos ("Colorea 1 manzana.", "Colorea 2
    # pelotas.", "¿Cuántos huesos hay?").
    # ----------------------------------------------------------------
    objetos = {
        "manzana": ("manzana", "manzanas", "f"),
        "pelota": ("pelota", "pelotas", "f"),
        "hueso": ("hueso", "huesos", "m"),
        "sol": ("sol", "soles", "m"),
        "huella": ("huella", "huellas", "f"),
        "toby": ("perro", "perros", "m"),
        "globo": ("globo", "globos", "m"),
        "estrella": ("estrella", "estrellas", "f"),
        "hoja": ("hoja", "hojas", "f"),
        "corazon": ("corazón", "corazones", "m"),
        "caramelo": ("caramelo", "caramelos", "m"),
        "pez": ("pez", "peces", "m"),
        "lapiz": ("lápiz", "lápices", "m"),
        "libro": ("libro", "libros", "m"),
        "galleta": ("galleta", "galletas", "f"),
        "seta": ("seta", "setas", "f"),
        "castana": ("castaña", "castañas", "f"),
        "cesta": ("cesta", "cestas", "f"),
        "vela": ("vela", "velas", "f"),
        "regalo": ("regalo", "regalos", "m"),
        "arana": ("araña", "arañas", "f"),
        "paraguas": ("paraguas", "paraguas", "m"),
        "bola": ("bola", "bolas", "f"),
        "arbol": ("árbol", "árboles", "m"),
        "pato": ("pato", "patos", "m"),
        "coche": ("coche", "coches", "m"),
        "trex": ("dinosaurio", "dinosaurios", "m"),
        "mariposa": ("mariposa", "mariposas", "f"),
        "gota": ("gota", "gotas", "f"),
        "nube": ("nube", "nubes", "f"),
        "huevo": ("huevo", "huevos", "m"),
        "pajaro": ("pájaro", "pájaros", "m"),
        "gato": ("gato", "gatos", "m"),
        "mochila": ("mochila", "mochilas", "f"),
        "ardilla": ("ardilla", "ardillas", "f"),
        "plato": ("plato", "platos", "m"),
        "mandarina": ("mandarina", "mandarinas", "f"),
        "copo": ("copo", "copos", "m"),
        "muneco": ("muñeco de nieve", "muñecos de nieve", "m"),
        "gorrofiesta": ("gorro de fiesta", "gorros de fiesta", "m"),
        "nota": ("nota", "notas", "f"),
        "osito": ("osito", "ositos", "m"),
        "flor": ("flor", "flores", "f"),
        "corona": ("corona", "coronas", "f"),
        "cometa": ("cometa", "cometas", "f"),
        "alubia": ("semilla", "semillas", "f"),
        "boton": ("botón", "botones", "m"),
        "tronco": ("tronco", "troncos", "m"),
        "fresa": ("fresa", "fresas", "f"),
        "piruleta": ("piruleta", "piruletas", "f"),
        "paloma": ("paloma", "palomas", "f"),
        "ovillo": ("ovillo", "ovillos", "m"),
        "bufanda": ("bufanda", "bufandas", "f"),
        "gorro": ("gorro", "gorros", "m"),
        "maceta": ("maceta", "macetas", "f"),
        "brote": ("brote", "brotes", "m"),
        "pipa": ("pipa", "pipas", "f"),
        "rueda": ("rueda", "ruedas", "f"),
        "bici": ("bici", "bicis", "f"),
        "oruga": ("oruga", "orugas", "f"),
        "gafas": ("gafas de nadar", "gafas de nadar", "f"),
        "arbusto": ("matorral", "matorrales", "m"),
        "tarta": ("tarta", "tartas", "f"),
        "rosa": ("rosa", "rosas", "f"),
        "abeja": ("abeja", "abejas", "f"),
        "pollito": ("pollito", "pollitos", "m"),
        "diente": ("diente", "dientes", "m"),
        "moneda": ("moneda", "monedas", "f"),
        "mano": ("mano", "manos", "f"),
        "torrija": ("torrija", "torrijas", "f"),
        "zanahoria": ("zanahoria", "zanahorias", "f"),
        "tomate": ("tomate", "tomates", "m"),
        "regadera": ("regadera", "regaderas", "f"),
        "tarjeta": ("tarjeta", "tarjetas", "f"),
        "pan": ("pan", "panes", "m"),
        "rayo": ("rayo", "rayos", "m"),
        "lechuga": ("lechuga", "lechugas", "f"),
        "maleta": ("maleta", "maletas", "f"),
        "helado": ("helado", "helados", "m"),
        "concha": ("concha", "conchas", "f"),
        "cubo": ("cubo", "cubos", "m"),
        "churro": ("churro", "churros", "m"),
        "caracol": ("caracol", "caracoles", "m"),
        "reloj": ("reloj", "relojes", "m"),
    }

    # Lo que se cuenta de 2 en 2 o de 5 en 5 en "Cuenta": las ruedas de
    # las bicis y los dedos de las manos (cuántas, en CONTAR_DE, en
    # tools/gen_numeros.py).
    contar_de = {"bici": ("ruedas", "f"), "mano": ("dedos", "m")}

    _PASO = {1: "uno", 2: "dos", 5: "cinco", 10: "diez"}
    _ORDINALES = {1: "el primero", 2: "el segundo", 3: "el tercero", 4: "el cuarto"}

    # Los dos rótulos de "Antes y después", encima de las casas.
    antes, despues = "antes", "después"
    # Lo que va entre los dos grupos de "Diez y más" y de "Junta".
    signo_junta = "y"

    def cosa(self, objeto, n):
        singular, plural, _ = self.objetos[objeto]
        return singular if n == 1 else plural

    def femenino(self, objeto):
        return self.objetos[objeto][2] == "f"

    def _de(self, paso):
        return "uno a uno" if paso == 1 else f"de {self._PASO[paso]} en {self._PASO[paso]}"

    # ----------------------------------------------------------------
    # Las actividades: lo que se lee en cada una. Devuelven el enunciado
    # (lo grande), la instrucción (lo que lee el adulto), la respuesta
    # (lo que se completa, con \huecoRespuesta) y el texto de la clave,
    # según lo que lleve cada actividad.
    # ----------------------------------------------------------------
    def colorea(self, cuantas, objeto):
        resto = "Las demás, déjalas en blanco." if self.femenino(objeto) else "Los demás, déjalos en blanco."
        return f"Colorea {cuantas} {self.cosa(objeto, cuantas)}.", resto

    def rodea(self, cuantas, objeto, posicion):
        cosa, femenino = self.cosa(objeto, cuantas), self.femenino(objeto)
        if cuantas == 0:
            ninguna = f"{'ninguna' if femenino else 'ningún'} {self.cosa(objeto, 1)}"
            enunciado, respuesta = f"Rodea donde no hay {ninguna}.", ninguna
        elif cuantas == 1:
            enunciado = f"Rodea donde hay 1 {cosa} {'sola' if femenino else 'solo'}."
            respuesta = f"1 {cosa}"
        else:
            enunciado, respuesta = f"Rodea donde hay {cuantas} {cosa}.", f"{cuantas} {cosa}"
        return (enunciado, "Un adulto lee la pregunta. Rodea con el lápiz todo el grupo.",
                f"{self._ORDINALES[posicion]} ({respuesta})")

    def cuenta(self, objeto, de):
        if de == 1:
            plural, femenino = self.cosa(objeto, 2), self.femenino(objeto)
            instruccion = (f"Un adulto lee la pregunta. Cuenta señalando {'cada una' if femenino else 'cada uno'} "
                           "con el dedo, y rodea el número.")
        else:
            plural, g = self.contar_de[objeto]
            femenino = g == "f"
            instruccion = (f"Un adulto lee la pregunta. Cada {self.cosa(objeto, 1)} tiene "
                           f"{self._PASO[de]} {plural}: cuenta de {self._PASO[de]} en {self._PASO[de]}, "
                           f"señalando {'cada una' if self.femenino(objeto) else 'cada uno'}, y rodea el número.")
        cuantos = "Cuántas" if femenino else "Cuántos"
        return f"¿{cuantos} {plural} hay?", instruccion

    def busca(self, buscar, veces):
        return f"Busca todos los {buscar}.", f"el {buscar} sale {veces} veces"

    def une(self, grupos):
        return ("Une cada grupo con su número.",
                "Un adulto lee la pregunta. Cuenta cada grupo, y traza una "
                "línea desde su punto hasta el punto de su número.",
                "de arriba abajo: " + ", ".join(str(g) for g in grupos))

    def serie(self, paso, faltan):
        uno = len(faltan) == 1
        hacia = "" if paso > 0 else ", hacia atrás"
        return ("¿Qué número falta?" if uno else "¿Qué números faltan?",
                f"Un adulto lee la pregunta. Di los números del tren {self._de(abs(paso))}{hacia}, "
                + ("y escribe en el vagón vacío el que falta." if uno
                   else "y escribe en los vagones vacíos los que faltan."),
                ("falta el " if uno else "faltan el ") + " y el ".join(str(v) for v in faltan))

    def decena(self, objeto):
        femenino, plural = self.femenino(objeto), self.cosa(objeto, 2)
        cuantas = "cuántas" if femenino else "cuántos"
        return (f"¿{cuantas.capitalize()} {plural} hay?",
                f"Un adulto lee la pregunta. En la bandeja llena hay 10: sigue contando "
                f"desde el 10 {'las' if femenino else 'los'} de la otra, y escribe {cuantas} hay.")

    def junta(self, objeto):
        femenino, plural = self.femenino(objeto), self.cosa(objeto, 2)
        cuantas = "cuántas" if femenino else "cuántos"
        return (f"¿{cuantas.capitalize()} {plural} hay en total?",
                f"Un adulto lee la pregunta. Junta los dos grupos: cuenta "
                f"{'todas' if femenino else 'todos'}, y escribe {cuantas} son.")

    def son(self, a, b, total):
        """"10 y 3 son 13": lo que se completa en "Diez y más" y "Junta"
        (con total = \\huecoRespuesta), y su clave."""
        return f"{a} y {b} son {total}"

    def compara_numeros(self, que, numeros, elegido):
        return (f"Rodea el número más {'grande' if que == 'mas' else 'pequeño'}.",
                "Un adulto lee la pregunta. Si hace falta, contad juntos: "
                "el más pequeño es el que se dice antes al contar.",
                f"el {elegido}")

    def compara_grupos(self, que, objeto, grupos):
        femenino, plural = self.femenino(objeto), self.cosa(objeto, 2)
        if que == "igual":
            igual = next(x for x in grupos if grupos.count(x) == 2)
            p1, p2 = [i + 1 for i, x in enumerate(grupos) if x == igual]
            enunciado = f"Rodea los dos grupos que tienen {'las mismas' if femenino else 'los mismos'} {plural}."
            clave = f"{self._ORDINALES[p1]} y {self._ORDINALES[p2]} ({igual} y {igual})"
        else:
            elegido = max(grupos) if que == "mas" else min(grupos)
            enunciado = f"Rodea donde hay {'más' if que == 'mas' else 'menos'} {plural}."
            clave = f"{self._ORDINALES[grupos.index(elegido) + 1]} ({elegido} {self.cosa(objeto, elegido)})"
        return enunciado, "Un adulto lee la pregunta. Cuenta cada grupo, y rodea con el lápiz el que dice.", clave

    def vecinos(self, numeros):
        uno = len(numeros) == 1
        return ("¿Qué número va antes, y cuál va después?" if uno
                else "¿Qué números van antes, y cuáles van después?",
                "Un adulto lee la pregunta. En la casa de la izquierda, escribe el "
                "número de antes; en la de la derecha, el de después.",
                "; ".join(f"{x}: {x - 1} y {x + 1}" for x in numeros))

    def recta(self, paso, faltan):
        uno = len(faltan) == 1
        return ("¿Qué número falta en la recta?" if uno else "¿Qué números faltan en la recta?",
                f"Un adulto lee la pregunta. Di los números de la recta {self._de(paso)}, de "
                "izquierda a derecha, y escribe en cada hueco el que falta.",
                ("falta el " if uno else "faltan el ") + " y el ".join(str(v) for v in faltan))

    def ordena(self, orden, ordenados):
        de, a = ("pequeño", "grande") if orden == "menor" else ("grande", "pequeño")
        return (f"Ordena los números, del más {de} al más {a}.",
                f"Un adulto lee la pregunta. Escribe abajo los números en orden, "
                f"siguiendo las flechas: primero, el más {de}.",
                ", ".join(str(x) for x in ordenados))

    def suma(self, objeto):
        return (f"¿{'Cuántas' if self.femenino(objeto) else 'Cuántos'} {self.cosa(objeto, 2)} hay en total?",
                "Un adulto lee la pregunta. El signo + quiere decir que se juntan: "
                "cuenta todo, y escribe el resultado.")

    def resta(self, quita, objeto):
        femenino = self.femenino(objeto)
        return (f"Tacha {quita} {self.cosa(objeto, quita)}. "
                f"¿{'Cuántas' if femenino else 'Cuántos'} quedan?",
                f"Un adulto lee la pregunta. Tacha con una raya {'las' if femenino else 'los'} "
                f"que se quitan, cuenta {'las' if femenino else 'los'} que quedan, y escribe el resultado.")

    def parte(self, total, parte, objeto):
        femenino = self.femenino(objeto)
        return (f"{total} son {parte} y... ¿{'cuántas' if femenino else 'cuántos'} más?",
                f"Un adulto lee la pregunta. La raya parte el grupo en dos: a un lado hay "
                f"{parte}; cuenta {'las' if femenino else 'los'} del otro lado, y escribe "
                f"{'cuántas' if femenino else 'cuántos'} son.",
                f"{total} son {parte} y \\huecoRespuesta",
                f"{total} son {parte} y {total - parte}")

    def diez(self):
        return ("¿Cuántos faltan para llegar a 10?",
                "Un adulto lee la pregunta. Dibuja en el marco los puntos que faltan para "
                "llenarlo, cuenta los que has dibujado, y escribe el número.")

    def problema(self):
        return ("Un adulto lee el problema, despacio. Dibújalo en el recuadro, si ayuda, "
                "y escribe la cuenta y el resultado.")

    def bloques(self, numero):
        decenas, unidades = divmod(numero, 10)
        return ("¿Qué número es?",
                "Un adulto lee la pregunta. Cada barra es una decena: diez cubitos. Cuenta las "
                "barras y los cubitos sueltos, y escribe cuántos hay de cada, y el número.",
                r"{\fontsize{30}{36}\selectfont \huecoRespuesta[18mm]\ decenas y "
                r"\huecoRespuesta[18mm]\ unidades}\\[5mm] son \huecoRespuesta",
                f"{decenas} {'decena' if decenas == 1 else 'decenas'} y {unidades} "
                f"{'unidad' if unidades == 1 else 'unidades'} son {numero}")

    def tabla(self, faltan):
        return ("¿Qué números faltan en la tabla?",
                "Un adulto lee la pregunta. Cada fila es una decena: di los números fila a "
                "fila, y escribe en cada casilla vacía el que falta.",
                "faltan el " + ", el ".join(str(v) for v in faltan[:-1]) + f" y el {faltan[-1]}")

    def dinero(self, total):
        return ("¿Cuánto dinero hay?",
                "Un adulto lee la pregunta. Cuenta primero los billetes y después las "
                "monedas, y escribe cuántos euros hay en total.",
                "Hay \\huecoRespuesta\\ euros",
                f"{total} euros")

    def hora(self, hora, minutos):
        la = "Es la" if hora == 1 else "Son las"
        cola = "en punto" if minutos == 0 else "y media"
        return ("¿Qué hora es?",
                "Un adulto lee la pregunta. La aguja corta dice la hora; la larga, arriba del "
                "todo, quiere decir «en punto», y abajo del todo, «y media».",
                f"{la} \\huecoRespuesta[20mm]\\ {cola}",
                f"{la.split()[1]} {hora} {cola}")

    def mide(self, largos):
        if len(largos) == 1:
            return ("¿Cuántos cubitos mide el lápiz?",
                    "Un adulto lee la pregunta. Cuenta los cubitos que hay debajo del lápiz, "
                    "desde la goma hasta la punta.",
                    "Mide \\huecoRespuesta\\ cubitos",
                    f"{largos[0]} cubitos")
        largo = "el de arriba" if largos[0] > largos[1] else "el de abajo"
        return ("¿Cuántos cubitos mide cada lápiz? ¿Cuál es más largo?",
                "Un adulto lee la pregunta. Cuenta los cubitos que hay debajo de cada lápiz, "
                "desde la goma hasta la punta, y rodea el más largo.",
                r"{\fontsize{28}{34}\selectfont El de arriba mide \huecoRespuesta\ cubitos.\\[4mm]"
                r"El de abajo mide \huecoRespuesta\ cubitos.}",
                f"{largos[0]} y {largos[1]} cubitos: {largo} es más largo")


class Ingles(Espanol):
    """"First Numbers": el mismo cuaderno, en inglés británico -- como
    "Read and Draw" y "First Words" (colour, Mum, biscuits, a rubber
    para borrar). Los personajes y lo que es de aquí se quedan como en
    esos dos cuadernos: Lucía, Grandma Rosa, Andrés y su gato Bigotes,
    los churros, las torrijas, el turrón, los euros."""

    codigo = "en"

    temas = [
        "Lucía's family", "Toby, the playful dog", "Lucía's school",
        "The neighbourhood and the park", "Food at home", "Autumn is here",
        "Dani's toys", "Chestnuts and All Saints' Day",
        "Lucía's birthday", "Animals in the neighbourhood", "A rainy day",
        "Going to the market with Mum", "Christmas Eve",
        "Cold January", "Dad's birthday", "The Carnival costume",
        "Peace Day", "Lucía is poorly",
        "A Sunday of crafts with Grandma", "The local library",
        "Toby's birthday", "A very windy day",
        "Marta's plant project", "Dani breaks Lucía's dinosaur",
        "Spring is in the air", "The end of the second term",
        "Toby gets lost in the park", "Dani loses a tooth",
        "World Book Day", "Easter week begins", "The school vegetable garden",
        "Lucía learns to ride a bike", "Lucía starts swimming lessons",
        "Mother's Day", "Dani knows nearly all his letters",
        "The end of the school year is coming", "The caterpillar becomes a butterfly",
        "The end-of-year book fair", "The last day of school",
        "Summer begins", "Arriving at Grandma Rosa's village",
        "Andrés next door, and his cat Bigotes", "A day at the village river",
        "Grandma's vegetable garden", "A summer storm",
        "A trip to the beach", "The village fiesta",
        "Dani makes friends with Martín", "Back to the city",
        "Getting ready for school",
        "Dani practises reading aloud", "Back to school",
    ]

    nombre_medalla = {1: "Autumn", 2: "Winter", 3: "Spring"}
    plantilla_medalla = Template(_MEDALLA % ("days", "pages"))

    # En inglés, 13 y 30, 14 y 40... suenan casi igual (thirTEEN,
    # THIRty); en español no (trece, treinta). Cuando llegan las decenas,
    # "Number names" los pone juntos: ver tools/gen_numeros.py.
    solo_aqui = frozenset({"nombres"})

    _HASTA_19 = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
    ]
    _DECENAS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty",
                7: "seventy", 8: "eighty", 9: "ninety"}

    def _nombre(self, n):
        if n < 20:
            return self._HASTA_19[n]
        if n == 100:
            return "one hundred"
        d, u = divmod(n, 10)
        return self._DECENAS[d] + (f"-{self._HASTA_19[u]}" if u else "")

    def formas(self, n):
        # El 1 tiene que ser "one": "a dog" no dice ningún número.
        if n == 0:
            return {"zero", "no", "none", "nothing", "nobody"}
        if n == 100:
            return {"one hundred", "a hundred"}
        return {self.nombres[n]}

    @staticmethod
    def _palabra(forma):
        # Una palabra entera: "twenty" no está en "twenty-one".
        return rf"(?<![\w-]){re.escape(forma)}(?![\w-])"

    def dice(self, texto, n):
        return any(re.search(self._palabra(f), texto.lower()) for f in self.formas(n))

    def en_texto(self, texto, n):
        return bool(re.search(rf"(?<!\d){n}(?!\d)", texto)) or self.dice(texto, n)

    dice_cuantas = en_texto

    # Singular y plural (el género no hace falta).
    objetos = {
        "manzana": ("apple", "apples"),
        "pelota": ("ball", "balls"),
        "hueso": ("bone", "bones"),
        "sol": ("sun", "suns"),
        "huella": ("paw print", "paw prints"),
        "toby": ("dog", "dogs"),
        "globo": ("balloon", "balloons"),
        "estrella": ("star", "stars"),
        "hoja": ("leaf", "leaves"),
        "corazon": ("heart", "hearts"),
        "caramelo": ("sweet", "sweets"),
        "pez": ("fish", "fish"),
        "lapiz": ("pencil", "pencils"),
        "libro": ("book", "books"),
        "galleta": ("biscuit", "biscuits"),
        "seta": ("mushroom", "mushrooms"),
        "castana": ("chestnut", "chestnuts"),
        "cesta": ("basket", "baskets"),
        "vela": ("candle", "candles"),
        "regalo": ("present", "presents"),
        "arana": ("spider", "spiders"),
        "paraguas": ("umbrella", "umbrellas"),
        "bola": ("bauble", "baubles"),
        "arbol": ("tree", "trees"),
        "pato": ("duck", "ducks"),
        "coche": ("car", "cars"),
        "trex": ("dinosaur", "dinosaurs"),
        "mariposa": ("butterfly", "butterflies"),
        "gota": ("raindrop", "raindrops"),
        "nube": ("cloud", "clouds"),
        "huevo": ("egg", "eggs"),
        "pajaro": ("bird", "birds"),
        "gato": ("cat", "cats"),
        "mochila": ("school bag", "school bags"),
        "ardilla": ("squirrel", "squirrels"),
        "plato": ("plate", "plates"),
        "mandarina": ("tangerine", "tangerines"),
        "copo": ("snowflake", "snowflakes"),
        "muneco": ("snowman", "snowmen"),
        "gorrofiesta": ("party hat", "party hats"),
        "nota": ("musical note", "musical notes"),
        "osito": ("teddy bear", "teddy bears"),
        "flor": ("flower", "flowers"),
        "corona": ("crown", "crowns"),
        "cometa": ("kite", "kites"),
        "alubia": ("seed", "seeds"),
        "boton": ("button", "buttons"),
        "tronco": ("log", "logs"),
        "fresa": ("strawberry", "strawberries"),
        "piruleta": ("lollipop", "lollipops"),
        "paloma": ("dove", "doves"),
        "ovillo": ("ball of wool", "balls of wool"),
        "bufanda": ("scarf", "scarves"),
        "gorro": ("woolly hat", "woolly hats"),
        "maceta": ("flowerpot", "flowerpots"),
        "brote": ("shoot", "shoots"),
        "pipa": ("sunflower seed", "sunflower seeds"),
        "rueda": ("wheel", "wheels"),
        "bici": ("bike", "bikes"),
        "oruga": ("caterpillar", "caterpillars"),
        "gafas": ("pair of goggles", "pairs of goggles"),
        "arbusto": ("bush", "bushes"),
        "tarta": ("cake", "cakes"),
        "rosa": ("rose", "roses"),
        "abeja": ("bee", "bees"),
        "pollito": ("chick", "chicks"),
        "diente": ("tooth", "teeth"),
        "moneda": ("coin", "coins"),
        "mano": ("hand", "hands"),
        "torrija": ("torrija", "torrijas"),
        "zanahoria": ("carrot", "carrots"),
        "tomate": ("tomato", "tomatoes"),
        "regadera": ("watering can", "watering cans"),
        "tarjeta": ("letter card", "letter cards"),
        "pan": ("loaf", "loaves"),
        "rayo": ("lightning bolt", "lightning bolts"),
        "lechuga": ("lettuce", "lettuces"),
        "maleta": ("suitcase", "suitcases"),
        "helado": ("ice cream", "ice creams"),
        "concha": ("shell", "shells"),
        "cubo": ("bucket", "buckets"),
        "churro": ("churro", "churros"),
        "caracol": ("snail", "snails"),
        "reloj": ("clock", "clocks"),
    }

    contar_de = {"bici": "wheels", "mano": "fingers"}

    _DE = {1: "one by one", 2: "in twos", 5: "in fives", 10: "in tens"}
    _ORDINALES = {1: "the first", 2: "the second", 3: "the third", 4: "the fourth"}

    antes, despues = "before", "after"
    signo_junta = "and"

    # La instrucción de casi todas las actividades empieza igual.
    LEE = "A grown-up reads out the question. "

    def cosa(self, objeto, n):
        singular, plural = self.objetos[objeto]
        return singular if n == 1 else plural

    def femenino(self, objeto):
        return False

    def _de(self, paso):
        return self._DE[paso]

    @staticmethod
    def _y(numeros):
        """"5", "5 and 7", "5, 7 and 9"."""
        numeros = [str(v) for v in numeros]
        return numeros[0] if len(numeros) == 1 else ", ".join(numeros[:-1]) + " and " + numeros[-1]

    def colorea(self, cuantas, objeto):
        return f"Colour {cuantas} {self.cosa(objeto, cuantas)}.", "Leave the rest white."

    def rodea(self, cuantas, objeto, posicion):
        if cuantas == 0:
            respuesta = f"no {self.cosa(objeto, 0)}"
        elif cuantas == 1:
            respuesta = f"just 1 {self.cosa(objeto, 1)}"
        else:
            respuesta = f"{cuantas} {self.cosa(objeto, cuantas)}"
        return (f"Circle the group with {respuesta}.",
                self.LEE + "Draw a circle round the whole group with your pencil.",
                f"{self._ORDINALES[posicion]} ({respuesta})")

    def cuenta(self, objeto, de):
        if de == 1:
            return (f"How many {self.cosa(objeto, 2)} are there?",
                    self.LEE + "Point to each one with your finger as you count, and circle the number.")
        partes = self.contar_de[objeto]
        return (f"How many {partes} are there?",
                self.LEE + f"Each {self.cosa(objeto, 1)} has {self.nombres[de]} {partes}: count "
                f"{self._de(de)}, pointing to each one, and circle the number.")

    def busca(self, buscar, veces):
        return f"Find all the {buscar}s.", f"{buscar} appears {veces} times"

    def une(self, grupos):
        return ("Match each group to its number.",
                self.LEE + "Count each group, and draw a line from its dot to the dot next to its number.",
                "top to bottom: " + ", ".join(str(g) for g in grupos))

    def serie(self, paso, faltan):
        uno = len(faltan) == 1
        hacia = "" if paso > 0 else ", backwards"
        return ("Which number is missing?" if uno else "Which numbers are missing?",
                self.LEE + f"Say the numbers on the train {self._de(abs(paso))}{hacia}, "
                + ("and write the missing one in the empty carriage." if uno
                   else "and write the missing ones in the empty carriages."),
                "missing: " + self._y(faltan))

    def decena(self, objeto):
        return (f"How many {self.cosa(objeto, 2)} are there?",
                self.LEE + "The full tray has 10: count on from 10 with the ones in the "
                "other tray, and write how many there are.")

    def junta(self, objeto):
        return (f"How many {self.cosa(objeto, 2)} are there altogether?",
                self.LEE + "Put the two groups together: count them all, and write how many there are.")

    def son(self, a, b, total):
        return f"{a} and {b} make {total}"

    def compara_numeros(self, que, numeros, elegido):
        dos = len(numeros) == 2
        cual = {("mas", True): "bigger", ("mas", False): "biggest",
                ("menos", True): "smaller", ("menos", False): "smallest"}[que, dos]
        return (f"Circle the {cual} number.",
                self.LEE + "If it helps, count together: the smaller number is the one you "
                "say first when you count.",
                str(elegido))

    def compara_grupos(self, que, objeto, grupos):
        plural = self.cosa(objeto, 2)
        if que == "igual":
            igual = next(x for x in grupos if grupos.count(x) == 2)
            p1, p2 = [i + 1 for i, x in enumerate(grupos) if x == igual]
            enunciado = f"Circle the two groups with the same number of {plural}."
            clave = f"{self._ORDINALES[p1]} and {self._ORDINALES[p2]} ({igual} and {igual})"
        else:
            elegido = max(grupos) if que == "mas" else min(grupos)
            dos = len(grupos) == 2
            cuanto = {("mas", True): "more", ("mas", False): "the most",
                      ("menos", True): "fewer", ("menos", False): "the fewest"}[que, dos]
            enunciado = f"Circle the group with {cuanto} {plural}."
            clave = f"{self._ORDINALES[grupos.index(elegido) + 1]} ({elegido} {self.cosa(objeto, elegido)})"
        return enunciado, self.LEE + "Count each group, and circle the one it asks for with your pencil.", clave

    def vecinos(self, numeros):
        uno = len(numeros) == 1
        return ("Which number comes before, and which comes after?" if uno
                else "Which numbers come before, and which come after?",
                self.LEE + "In the house on the left, write the number that comes before; in "
                "the house on the right, the one that comes after.",
                "; ".join(f"{x}: {x - 1} and {x + 1}" for x in numeros))

    def recta(self, paso, faltan):
        uno = len(faltan) == 1
        return ("Which number is missing on the number line?" if uno
                else "Which numbers are missing on the number line?",
                self.LEE + f"Say the numbers on the line {self._de(paso)}, from left to right, "
                "and write the missing one in each gap.",
                "missing: " + self._y(faltan))

    def ordena(self, orden, ordenados):
        de, a = ("smallest", "biggest") if orden == "menor" else ("biggest", "smallest")
        return (f"Put the numbers in order, from {de} to {a}.",
                self.LEE + f"Write the numbers in order below, following the arrows: the {de} first.",
                ", ".join(str(x) for x in ordenados))

    def suma(self, objeto):
        return (f"How many {self.cosa(objeto, 2)} are there altogether?",
                self.LEE + "The + sign means put together: count them all, and write the answer.")

    def resta(self, quita, objeto):
        return (f"Cross out {quita} {self.cosa(objeto, quita)}. How many are left?",
                self.LEE + "Cross out the ones taken away with a line, count the ones that "
                "are left, and write the answer.")

    def parte(self, total, parte, objeto):
        return (f"{total} is {parte} and... how many more?",
                self.LEE + f"The line splits the group in two: on one side there are {parte}; "
                "count the ones on the other side, and write how many there are.",
                f"{total} is {parte} and \\huecoRespuesta",
                f"{total} is {parte} and {total - parte}")

    def diez(self):
        return ("How many more to make 10?",
                self.LEE + "Draw the missing dots in the frame to fill it, count the ones you "
                "have drawn, and write the number.")

    def problema(self):
        return ("A grown-up reads out the problem, slowly. Draw it in the box if it helps, "
                "and write the calculation and the answer.")

    def bloques(self, numero):
        decenas, unidades = divmod(numero, 10)
        return ("What number is it?",
                self.LEE + "Each bar is a ten: ten cubes. Count the bars and the loose cubes, "
                "write how many of each there are, and then the number.",
                r"{\fontsize{30}{36}\selectfont \huecoRespuesta[18mm]\ tens and "
                r"\huecoRespuesta[18mm]\ ones}\\[5mm] make \huecoRespuesta",
                f"{decenas} {'ten' if decenas == 1 else 'tens'} and {unidades} "
                f"{'one' if unidades == 1 else 'ones'} make {numero}")

    def tabla(self, faltan):
        return ("Which numbers are missing from the hundred square?",
                self.LEE + "Each row is a ten: say the numbers row by row, and write the "
                "missing one in each empty square.",
                "missing: " + self._y(faltan))

    def dinero(self, total):
        return ("How much money is there?",
                self.LEE + "Count the notes first and then the coins, and write how many "
                "euros there are altogether.",
                "\\huecoRespuesta\\ euros",
                f"{total} euros")

    def hora(self, hora, minutos):
        return ("What time is it?",
                self.LEE + "The short hand shows the hour. When the long hand points straight "
                "up, it is “o'clock”; when it points straight down, it is “half past”.",
                "It's \\huecoRespuesta[20mm]\\ o'clock" if minutos == 0
                else "It's half past \\huecoRespuesta[20mm]",
                f"{hora} o'clock" if minutos == 0 else f"half past {hora}")

    def mide(self, largos):
        if len(largos) == 1:
            return ("How many cubes long is the pencil?",
                    self.LEE + "Count the cubes under the pencil, from the rubber to the tip.",
                    "It is \\huecoRespuesta\\ cubes long",
                    f"{largos[0]} cubes")
        largo = "the top one" if largos[0] > largos[1] else "the bottom one"
        return ("How long is each pencil? Which one is longer?",
                self.LEE + "Count the cubes under each pencil, from the rubber to the tip, "
                "and circle the longer one.",
                r"{\fontsize{26}{32}\selectfont Top pencil: \huecoRespuesta\ cubes.\\[4mm]"
                r"Bottom pencil: \huecoRespuesta\ cubes.}",
                f"{largos[0]} and {largos[1]} cubes: {largo} is longer")

    def nombres_numeros(self, numeros):
        """"Number names": cada número con su nombre."""
        return ("Match each number to its name.",
                "A grown-up reads out each name, saying the end clearly: thirTEEN, THIRty. "
                "Draw a line from each number to its name.",
                ", ".join(f"{x} {self.nombres[x]}" for x in numeros))


class Polaco(Espanol):
    """"Poznaję liczby": el mismo cuaderno, en polaco. Los personajes y lo
    que es de aquí se quedan como en español (Lucía, Dani, Toby, babcia
    Rosa, pani Marta, el turrón, los churros, las torrijas), y el dinero
    son euros -- que en polaco no se declina: 1 euro, 2 euro, 5 euro.

    Lo difícil del polaco es el número. La cosa va en singular con el 1
    (1 piłka), en nominativo plural con el 2, el 3 y el 4 (y el 22, el
    23, el 24..., pero no el 12, el 13 ni el 14: 2 piłki) y en genitivo
    plural con los demás (5 piłek, 12 piłek); y el propio número cambia
    con el caso y con lo que cuenta: "jeden pies", "jednego psa", "dwie
    piłki", "dwóch chłopców", "troje dzieci". Por eso la frase del día no
    se busca en una lista de formas: se leen sus números (_valores), y
    "dwadzieścia jeden" es el 21, no el 20 y el 1."""

    codigo = "pl"

    temas = [
        "Rodzina Lucíi", "Toby, wesoły piesek", "Szkoła Lucíi",
        "Okolica i park", "Jedzenie w domu", "Przychodzi jesień",
        "Zabawki Daniego", "Kasztany i Wszystkich Świętych",
        "Urodziny Lucíi", "Zwierzęta z okolicy", "Deszczowy dzień",
        "Z mamą na targ", "Wigilia",
        "Styczniowy mróz", "Urodziny taty", "Karnawałowy strój",
        "Dzień Pokoju", "Lucía jest chora",
        "Niedziela z babcią i robótkami", "Osiedlowa biblioteka",
        "Urodziny Toby'ego", "Bardzo wietrzny dzień",
        "Roślinny projekt pani Marty", "Dani psuje dinozaura Lucíi",
        "Pachnie wiosną", "Koniec drugiej części roku",
        "Toby gubi się w parku", "Daniemu wypada ząbek",
        "Dzień Książki", "Zaczyna się Wielki Tydzień", "Szkolny ogródek",
        "Lucía uczy się jeździć na rowerze", "Lucía zapisuje się na basen",
        "Dzień Matki", "Dani zna już prawie wszystkie litery",
        "Zbliża się koniec roku szkolnego", "Gąsienica zmienia się w motyla",
        "Kiermasz książek na koniec roku", "Ostatni dzień szkoły",
        "Zaczyna się lato", "Przyjazd na wieś babci Rosy",
        "Sąsiad Andrés i jego kot Bigotes", "Dzień nad rzeką",
        "Ogródek babci", "Letnia burza",
        "Wycieczka na plażę", "Wiejski festyn",
        "Dani zaprzyjaźnia się z Martínem", "Powrót do miasta",
        "Przygotowania do szkoły",
        "Dani ćwiczy czytanie na głos", "Znowu do szkoły",
    ]

    # "Medal za jesień!": \lblMedalla{#1}, en lang/pl.tex, pide el
    # acusativo. "65 dni, 65 stron": 65, 130 y 195 piden el genitivo.
    nombre_medalla = {1: "jesień", 2: "zimę", 3: "wiosnę"}
    plantilla_medalla = Template(_MEDALLA % ("dni", "stron"))

    # Los nombres de los números, en nominativo (los de la caja de
    # arriba).
    _HASTA_19 = [
        "zero", "jeden", "dwa", "trzy", "cztery", "pięć", "sześć", "siedem", "osiem",
        "dziewięć", "dziesięć", "jedenaście", "dwanaście", "trzynaście", "czternaście",
        "piętnaście", "szesnaście", "siedemnaście", "osiemnaście", "dziewiętnaście",
    ]
    _DECENAS = {2: "dwadzieścia", 3: "trzydzieści", 4: "czterdzieści", 5: "pięćdziesiąt",
                6: "sześćdziesiąt", 7: "siedemdziesiąt", 8: "osiemdziesiąt",
                9: "dziewięćdziesiąt"}

    # Y todas sus formas: los casos, el masculino de persona ("dwaj",
    # "dwóch") y los colectivos ("dwoje dzieci"). El 0 también se dice
    # "żaden", "nic" o "nikt".
    _FORMAS = {
        0: ("zero", "żaden", "żadna", "żadne", "żadnego", "żadnej", "żadnych", "żadnym",
            "nic", "niczego", "nikt", "nikogo"),
        1: ("jeden", "jedna", "jedno", "jednego", "jednej", "jednemu", "jednym", "jedną"),
        2: ("dwa", "dwie", "dwaj", "dwóch", "dwu", "dwom", "dwóm", "dwoma", "dwiema",
            "dwoje", "dwojga", "dwojgu", "dwojgiem"),
        3: ("trzy", "trzej", "trzech", "trzem", "trzema", "troje", "trojga", "trojgu", "trojgiem"),
        4: ("cztery", "czterej", "czterech", "czterem", "czterema", "czworo", "czworga",
            "czworgu", "czworgiem"),
        5: ("pięć", "pięciu", "pięcioma", "pięcioro", "pięciorga"),
        6: ("sześć", "sześciu", "sześcioma", "sześcioro", "sześciorga"),
        7: ("siedem", "siedmiu", "siedmioma", "siedmioro", "siedmiorga"),
        8: ("osiem", "ośmiu", "ośmioma", "ośmioro", "ośmiorga"),
        9: ("dziewięć", "dziewięciu", "dziewięcioma", "dziewięcioro", "dziewięciorga"),
        10: ("dziesięć", "dziesięciu", "dziesięcioma", "dziesięcioro", "dziesięciorga"),
        11: ("jedenaście", "jedenastu", "jedenastoma", "jedenaścioro"),
        12: ("dwanaście", "dwunastu", "dwunastoma", "dwanaścioro"),
        13: ("trzynaście", "trzynastu", "trzynastoma", "trzynaścioro"),
        14: ("czternaście", "czternastu", "czternastoma", "czternaścioro"),
        15: ("piętnaście", "piętnastu", "piętnastoma", "piętnaścioro"),
        16: ("szesnaście", "szesnastu", "szesnastoma", "szesnaścioro"),
        17: ("siedemnaście", "siedemnastu", "siedemnastoma", "siedemnaścioro"),
        18: ("osiemnaście", "osiemnastu", "osiemnastoma", "osiemnaścioro"),
        19: ("dziewiętnaście", "dziewiętnastu", "dziewiętnastoma", "dziewiętnaścioro"),
        20: ("dwadzieścia", "dwudziestu", "dwudziestoma", "dwadzieścioro"),
        30: ("trzydzieści", "trzydziestu", "trzydziestoma"),
        40: ("czterdzieści", "czterdziestu", "czterdziestoma"),
        50: ("pięćdziesiąt", "pięćdziesięciu", "pięćdziesięcioma"),
        60: ("sześćdziesiąt", "sześćdziesięciu", "sześćdziesięcioma"),
        70: ("siedemdziesiąt", "siedemdziesięciu", "siedemdziesięcioma"),
        80: ("osiemdziesiąt", "osiemdziesięciu", "osiemdziesięcioma"),
        90: ("dziewięćdziesiąt", "dziewięćdziesięciu", "dziewięćdziesięcioma"),
        100: ("sto", "stu", "stoma"),
    }
    # Qué vale cada palabra, y qué puede ir detrás de una decena: del 2 al
    # 9, cualquiera de sus formas; el 1, solo "jeden" ("dwadzieścia
    # jeden", "dwudziestu jeden").
    _VALOR = {f: n for n, formas in _FORMAS.items() for f in formas}
    _TRAS_DECENA = dict({f: n for n, formas in _FORMAS.items() if 2 <= n <= 9 for f in formas}, jeden=1)

    def _nombre(self, n):
        if n < 20:
            return self._HASTA_19[n]
        if n == 100:
            return "sto"
        d, u = divmod(n, 10)
        return self._DECENAS[d] + (f" {self._HASTA_19[u]}" if u else "")

    def formas(self, n):
        """Algunas de las formas del número n (para decir, si falla, qué
        tiene que decir la frase)."""
        if n in self._FORMAS:
            return set(self._FORMAS[n])
        d, u = divmod(n, 10)
        unidades = ("jeden",) if u == 1 else self._FORMAS[u][:4]
        return {f"{t} {x}" for t in self._FORMAS[d * 10][:2] for x in unidades}

    def _valores(self, texto):
        """Los números que dice `texto` con letra: "dwadzieścia jeden" es
        el 21 (y no el 20 y el 1), y "dwudziestu trzech", el 23."""
        palabras = re.findall(r"[^\W\d_]+", texto.lower())
        valores, i = [], 0
        while i < len(palabras):
            v = self._VALOR.get(palabras[i])
            if v is None:
                i += 1
                continue
            if 20 <= v <= 90 and v % 10 == 0 and i + 1 < len(palabras) and palabras[i + 1] in self._TRAS_DECENA:
                valores.append(v + self._TRAS_DECENA[palabras[i + 1]])
                i += 2
                continue
            valores.append(v)
            i += 1
        return valores

    def dice(self, texto, n):
        return n in self._valores(texto)

    def en_texto(self, texto, n):
        return bool(re.search(rf"(?<!\d){n}(?!\d)", texto)) or self.dice(texto, n)

    dice_cuantas = en_texto

    # ----------------------------------------------------------------
    # Las cosas que se cuentan: nominativo y acusativo singular,
    # nominativo y genitivo plural, y género. "Pokoloruj 1 piłkę",
    # "Pokoloruj 2 piłki", "Pokoloruj 5 piłek"; "Ile jest piłek?".
    # ----------------------------------------------------------------
    objetos = {
        "manzana": ("jabłko", "jabłko", "jabłka", "jabłek", "n"),
        "pelota": ("piłka", "piłkę", "piłki", "piłek", "f"),
        "hueso": ("kość", "kość", "kości", "kości", "f"),
        "sol": ("słońce", "słońce", "słońca", "słońc", "n"),
        "huella": ("ślad łapy", "ślad łapy", "ślady łap", "śladów łap", "m"),
        "toby": ("pies", "psa", "psy", "psów", "m"),
        "globo": ("balonik", "balonik", "baloniki", "baloników", "m"),
        "estrella": ("gwiazdka", "gwiazdkę", "gwiazdki", "gwiazdek", "f"),
        "hoja": ("liść", "liść", "liście", "liści", "m"),
        "corazon": ("serduszko", "serduszko", "serduszka", "serduszek", "n"),
        "caramelo": ("cukierek", "cukierka", "cukierki", "cukierków", "m"),
        "pez": ("rybka", "rybkę", "rybki", "rybek", "f"),
        "lapiz": ("ołówek", "ołówek", "ołówki", "ołówków", "m"),
        "libro": ("książka", "książkę", "książki", "książek", "f"),
        "galleta": ("ciastko", "ciastko", "ciastka", "ciastek", "n"),
        "seta": ("grzyb", "grzyba", "grzyby", "grzybów", "m"),
        "castana": ("kasztan", "kasztan", "kasztany", "kasztanów", "m"),
        "cesta": ("koszyk", "koszyk", "koszyki", "koszyków", "m"),
        "vela": ("świeczka", "świeczkę", "świeczki", "świeczek", "f"),
        "regalo": ("prezent", "prezent", "prezenty", "prezentów", "m"),
        "arana": ("pająk", "pająka", "pająki", "pająków", "m"),
        "paraguas": ("parasol", "parasol", "parasole", "parasoli", "m"),
        "bola": ("bombka", "bombkę", "bombki", "bombek", "f"),
        "arbol": ("drzewo", "drzewo", "drzewa", "drzew", "n"),
        "pato": ("kaczka", "kaczkę", "kaczki", "kaczek", "f"),
        "coche": ("samochodzik", "samochodzik", "samochodziki", "samochodzików", "m"),
        "trex": ("dinozaur", "dinozaura", "dinozaury", "dinozaurów", "m"),
        "mariposa": ("motyl", "motyla", "motyle", "motyli", "m"),
        "gota": ("kropla", "kroplę", "krople", "kropli", "f"),
        "nube": ("chmurka", "chmurkę", "chmurki", "chmurek", "f"),
        "huevo": ("jajko", "jajko", "jajka", "jajek", "n"),
        "pajaro": ("ptaszek", "ptaszka", "ptaszki", "ptaszków", "m"),
        "gato": ("kot", "kota", "koty", "kotów", "m"),
        "mochila": ("plecak", "plecak", "plecaki", "plecaków", "m"),
        "ardilla": ("wiewiórka", "wiewiórkę", "wiewiórki", "wiewiórek", "f"),
        "plato": ("talerz", "talerz", "talerze", "talerzy", "m"),
        "mandarina": ("mandarynka", "mandarynkę", "mandarynki", "mandarynek", "f"),
        "copo": ("płatek śniegu", "płatek śniegu", "płatki śniegu", "płatków śniegu", "m"),
        "muneco": ("bałwan", "bałwana", "bałwany", "bałwanów", "m"),
        "gorrofiesta": ("czapeczka", "czapeczkę", "czapeczki", "czapeczek", "f"),
        "nota": ("nutka", "nutkę", "nutki", "nutek", "f"),
        "osito": ("miś", "misia", "misie", "misiów", "m"),
        "flor": ("kwiatek", "kwiatek", "kwiatki", "kwiatków", "m"),
        "corona": ("korona", "koronę", "korony", "koron", "f"),
        "cometa": ("latawiec", "latawiec", "latawce", "latawców", "m"),
        "alubia": ("nasionko", "nasionko", "nasionka", "nasionek", "n"),
        "boton": ("guzik", "guzik", "guziki", "guzików", "m"),
        "tronco": ("polano", "polano", "polana", "polan", "n"),
        "fresa": ("truskawka", "truskawkę", "truskawki", "truskawek", "f"),
        "piruleta": ("lizak", "lizaka", "lizaki", "lizaków", "m"),
        "paloma": ("gołąb", "gołębia", "gołębie", "gołębi", "m"),
        "ovillo": ("kłębek włóczki", "kłębek włóczki", "kłębki włóczki", "kłębków włóczki", "m"),
        "bufanda": ("szalik", "szalik", "szaliki", "szalików", "m"),
        "gorro": ("czapka", "czapkę", "czapki", "czapek", "f"),
        "maceta": ("doniczka", "doniczkę", "doniczki", "doniczek", "f"),
        "brote": ("kiełek", "kiełek", "kiełki", "kiełków", "m"),
        "pipa": ("pestka", "pestkę", "pestki", "pestek", "f"),
        "rueda": ("koło", "koło", "koła", "kół", "n"),
        "bici": ("rower", "rower", "rowery", "rowerów", "m"),
        "oruga": ("gąsienica", "gąsienicę", "gąsienice", "gąsienic", "f"),
        "gafas": ("para okularków", "parę okularków", "pary okularków", "par okularków", "f"),
        "arbusto": ("krzak", "krzak", "krzaki", "krzaków", "m"),
        "tarta": ("tort", "tort", "torty", "tortów", "m"),
        "rosa": ("róża", "różę", "róże", "róż", "f"),
        "abeja": ("pszczoła", "pszczołę", "pszczoły", "pszczół", "f"),
        "pollito": ("kurczątko", "kurczątko", "kurczątka", "kurczątek", "n"),
        "diente": ("ząbek", "ząbek", "ząbki", "ząbków", "m"),
        "moneda": ("moneta", "monetę", "monety", "monet", "f"),
        "mano": ("ręka", "rękę", "ręce", "rąk", "f"),
        "torrija": ("grzanka", "grzankę", "grzanki", "grzanek", "f"),
        "zanahoria": ("marchewka", "marchewkę", "marchewki", "marchewek", "f"),
        "tomate": ("pomidor", "pomidor", "pomidory", "pomidorów", "m"),
        "regadera": ("konewka", "konewkę", "konewki", "konewek", "f"),
        "tarjeta": ("kartonik", "kartonik", "kartoniki", "kartoników", "m"),
        "pan": ("bochenek", "bochenek", "bochenki", "bochenków", "m"),
        "rayo": ("błyskawica", "błyskawicę", "błyskawice", "błyskawic", "f"),
        "lechuga": ("sałata", "sałatę", "sałaty", "sałat", "f"),
        "maleta": ("walizka", "walizkę", "walizki", "walizek", "f"),
        "helado": ("rożek lodów", "rożek lodów", "rożki lodów", "rożków lodów", "m"),
        "concha": ("muszelka", "muszelkę", "muszelki", "muszelek", "f"),
        "cubo": ("wiaderko", "wiaderko", "wiaderka", "wiaderek", "n"),
        "churro": ("churros", "churrosa", "churrosy", "churrosów", "m"),
        "caracol": ("ślimak", "ślimaka", "ślimaki", "ślimaków", "m"),
        "reloj": ("zegar", "zegar", "zegary", "zegarów", "m"),
    }

    # Lo que se cuenta de 2 en 2 o de 5 en 5 en "Cuenta": las ruedas de
    # las bicis y los dedos de las manos (nominativo y genitivo plural).
    contar_de = {"bici": ("koła", "kół"), "mano": ("palce", "palców")}

    _DE = {1: "po kolei", 2: "dwójkami", 5: "piątkami", 10: "dziesiątkami"}
    _ORDINALES = {1: "pierwsza", 2: "druga", 3: "trzecia", 4: "czwarta"}

    antes, despues = "przed", "po"
    signo_junta = "i"

    # La instrucción de casi todas las actividades empieza igual.
    LEE = "Dorosły czyta polecenie. "

    @staticmethod
    def _grupo(n):
        """1: el singular; 2, 3 y 4 (y 22, 23, 24..., no 12, 13 y 14): el
        nominativo plural; los demás, el genitivo plural."""
        if n == 1:
            return 1
        if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
            return 2
        return 5

    def _con(self, n, uno, dos, cinco):
        return {1: uno, 2: dos, 5: cinco}[self._grupo(n)]

    def cosa(self, objeto, n):
        """Detrás del número n, en nominativo: "1 piłka", "2 piłki", "5 piłek"."""
        nom, _, plural, genitivo, _ = self.objetos[objeto]
        return self._con(n, nom, plural, genitivo)

    def acusativo(self, objeto, n):
        """Lo mismo, en acusativo: "Pokoloruj 1 piłkę", "Skreśl 2 psy"."""
        _, acu, plural, genitivo, _ = self.objetos[objeto]
        return self._con(n, acu, plural, genitivo)

    def genitivo_plural(self, objeto):
        """"Ile jest piłek?"."""
        return self.objetos[objeto][3]

    def femenino(self, objeto):
        return self.objetos[objeto][4] == "f"

    def _de(self, paso):
        return self._DE[paso]

    @staticmethod
    def _y(numeros):
        """"5", "5 i 7", "5, 7 i 9"."""
        numeros = [str(v) for v in numeros]
        return numeros[0] if len(numeros) == 1 else ", ".join(numeros[:-1]) + " i " + numeros[-1]

    def _cuantas_hay(self, objeto, n):
        """"jest 1 piłka", "są 2 piłki", "jest 5 piłek"."""
        return f"{'są' if self._grupo(n) == 2 else 'jest'} {n} {self.cosa(objeto, n)}"

    def colorea(self, cuantas, objeto):
        return f"Pokoloruj {cuantas} {self.acusativo(objeto, cuantas)}.", "Resztę zostaw bez koloru."

    def rodea(self, cuantas, objeto, posicion):
        if cuantas == 0:
            enunciado = f"Zakreśl grupę, w której nie ma żadnych {self.genitivo_plural(objeto)}."
            respuesta = f"0 {self.genitivo_plural(objeto)}"
        elif cuantas == 1:
            enunciado = f"Zakreśl grupę, w której jest tylko 1 {self.cosa(objeto, 1)}."
            respuesta = f"1 {self.cosa(objeto, 1)}"
        else:
            enunciado = f"Zakreśl grupę, w której {self._cuantas_hay(objeto, cuantas)}."
            respuesta = f"{cuantas} {self.cosa(objeto, cuantas)}"
        return (enunciado, self.LEE + "Zakreśl ołówkiem całą grupę.",
                f"{self._ORDINALES[posicion]} grupa ({respuesta})")

    def cuenta(self, objeto, de):
        if de == 1:
            return (f"Ile jest {self.genitivo_plural(objeto)}?",
                    self.LEE + "Licz, wskazując palcem każdą rzecz po kolei, i zakreśl liczbę.")
        plural, genitivo = self.contar_de[objeto]
        cada = "Każda" if self.femenino(objeto) else "Każdy"
        return (f"Ile jest {genitivo}?",
                self.LEE + f"{cada} {self.cosa(objeto, 1)} ma {de} {self._con(de, plural, plural, genitivo)}: "
                f"licz {self._de(de)}, wskazując je po kolei, i zakreśl liczbę.")

    def busca(self, buscar, veces):
        return f"Znajdź wszystkie liczby {buscar}.", f"liczba {buscar} występuje {veces} razy"

    def une(self, grupos):
        return ("Połącz każdą grupę z jej liczbą.",
                self.LEE + "Policz każdą grupę i poprowadź linię od jej kropki do kropki przy jej liczbie.",
                "od góry: " + ", ".join(str(g) for g in grupos))

    def serie(self, paso, faltan):
        uno = len(faltan) == 1
        hacia = "" if paso > 0 else " od końca"
        return ("Jakiej liczby brakuje?" if uno else "Jakich liczb brakuje?",
                self.LEE + f"Powiedz liczby z pociągu {self._de(abs(paso))}{hacia} "
                + ("i wpisz do pustego wagonu tę, której brakuje." if uno
                   else "i wpisz do pustych wagonów te, których brakuje."),
                "brakuje " + self._y(faltan))

    def decena(self, objeto):
        return (f"Ile jest {self.genitivo_plural(objeto)}?",
                self.LEE + "Na pełnej tacy jest 10: licz dalej od 10 te z drugiej tacy "
                "i wpisz, ile ich jest.")

    def junta(self, objeto):
        return (f"Ile jest razem {self.genitivo_plural(objeto)}?",
                self.LEE + "Połącz obie grupy: policz wszystko i wpisz, ile ich jest.")

    def son(self, a, b, total):
        return f"{a} i {b} to {total}"

    def compara_numeros(self, que, numeros, elegido):
        dos = len(numeros) == 2
        cual = {("mas", True): "większą", ("mas", False): "największą",
                ("menos", True): "mniejszą", ("menos", False): "najmniejszą"}[que, dos]
        return (f"Zakreśl {cual} liczbę.",
                self.LEE + "Jeśli trzeba, policzcie razem: mniejsza liczba to ta, którą "
                "mówi się wcześniej przy liczeniu.",
                str(elegido))

    def compara_grupos(self, que, objeto, grupos):
        genitivo = self.genitivo_plural(objeto)
        if que == "igual":
            igual = next(x for x in grupos if grupos.count(x) == 2)
            p1, p2 = [i + 1 for i, x in enumerate(grupos) if x == igual]
            enunciado = f"Zakreśl dwie grupy, w których jest tyle samo {genitivo}."
            clave = f"{self._ORDINALES[p1]} i {self._ORDINALES[p2]} grupa ({igual} i {igual})"
        else:
            elegido = max(grupos) if que == "mas" else min(grupos)
            dos = len(grupos) == 2
            cuanto = {("mas", True): "więcej", ("mas", False): "najwięcej",
                      ("menos", True): "mniej", ("menos", False): "najmniej"}[que, dos]
            enunciado = f"Zakreśl grupę, w której jest {cuanto} {genitivo}."
            clave = (f"{self._ORDINALES[grupos.index(elegido) + 1]} grupa "
                     f"({elegido} {self.cosa(objeto, elegido)})")
        return enunciado, self.LEE + "Policz każdą grupę i zakreśl ołówkiem tę, o którą chodzi.", clave

    def vecinos(self, numeros):
        uno = len(numeros) == 1
        return ("Jaka liczba jest przed, a jaka po?" if uno
                else "Jakie liczby są przed, a jakie po?",
                self.LEE + "W domku po lewej wpisz liczbę, która jest przed; w domku po "
                "prawej tę, która jest po.",
                "; ".join(f"{x}: {x - 1} i {x + 1}" for x in numeros))

    def recta(self, paso, faltan):
        uno = len(faltan) == 1
        return ("Jakiej liczby brakuje na osi liczbowej?" if uno
                else "Jakich liczb brakuje na osi liczbowej?",
                self.LEE + f"Powiedz liczby z osi {self._de(paso)}, od lewej do prawej, "
                "i wpisz w każdą lukę tę, której brakuje.",
                "brakuje " + self._y(faltan))

    def ordena(self, orden, ordenados):
        de, a = ("najmniejszej", "największej") if orden == "menor" else ("największej", "najmniejszej")
        primero = "najmniejszą" if orden == "menor" else "największą"
        return (f"Ułóż liczby od {de} do {a}.",
                self.LEE + f"Wpisz liczby na dole po kolei, zgodnie ze strzałkami: najpierw {primero}.",
                ", ".join(str(x) for x in ordenados))

    def suma(self, objeto):
        return (f"Ile jest razem {self.genitivo_plural(objeto)}?",
                self.LEE + "Znak + oznacza, że łączymy: policz wszystko i wpisz wynik.")

    def resta(self, quita, objeto):
        return (f"Skreśl {quita} {self.acusativo(objeto, quita)}. Ile zostało?",
                self.LEE + "Skreśl kreską te, które zabieramy, policz te, które zostały, "
                "i wpisz wynik.")

    def parte(self, total, parte, objeto):
        return (f"{total} to {parte} i... ile jeszcze?",
                self.LEE + f"Kreska dzieli grupę na dwie części. Po jednej stronie policzono już "
                f"{parte}; policz te po drugiej stronie i wpisz, ile ich jest.",
                f"{total} to {parte} i \\huecoRespuesta",
                f"{total} to {parte} i {total - parte}")

    def diez(self):
        return ("Ile brakuje do 10?",
                self.LEE + "Dorysuj w ramce brakujące kropki, żeby ją wypełnić, policz "
                "dorysowane kropki i wpisz liczbę.")

    def problema(self):
        return ("Dorosły czyta zadanie, powoli. Jeśli to pomaga, narysuj je w ramce, "
                "a potem wpisz działanie i wynik.")

    def bloques(self, numero):
        decenas, unidades = divmod(numero, 10)
        return ("Jaka to liczba?",
                self.LEE + "Każdy słupek to dziesiątka: dziesięć kostek. Policz słupki i pojedyncze "
                "kostki, wpisz, ile jest jednych i drugich, a potem liczbę.",
                r"{\fontsize{30}{36}\selectfont dziesiątki: \huecoRespuesta[18mm]\quad "
                r"jedności: \huecoRespuesta[18mm]}\\[5mm] liczba: \huecoRespuesta",
                f"{decenas} {self._con(decenas, 'dziesiątka', 'dziesiątki', 'dziesiątek')} i "
                f"{unidades} {self._con(unidades, 'jedność', 'jedności', 'jedności')} to {numero}")

    def tabla(self, faltan):
        return ("Jakich liczb brakuje w tabeli?",
                self.LEE + "Każdy rząd to jedna dziesiątka: mów liczby rząd po rzędzie i wpisz "
                "w każdą pustą kratkę tę, której brakuje.",
                "brakuje " + self._y(faltan))

    def dinero(self, total):
        return ("Ile jest pieniędzy?",
                self.LEE + "Policz najpierw banknoty, a potem monety, i wpisz, ile jest "
                "razem euro.",
                "Razem: \\huecoRespuesta\\ euro",
                f"{total} euro")

    def hora(self, hora, minutos):
        # "Jest godzina 3" (la trzecia) y "wpół do 4", que en polaco es
        # las tres y media: la media hora se dice con la hora que llega.
        siguiente = hora % 12 + 1
        return ("Która godzina?",
                self.LEE + "Krótka wskazówka pokazuje godzinę. Kiedy długa wskazówka jest na "
                "samej górze, jest pełna godzina; kiedy na samym dole, jest wpół do następnej.",
                "Jest godzina \\huecoRespuesta[20mm]" if minutos == 0
                else "Jest wpół do \\huecoRespuesta[20mm]",
                f"godzina {hora}" if minutos == 0 else f"wpół do {siguiente} ({hora}:30)")

    def mide(self, largos):
        kostek = lambda n: f"{n} {self._con(n, 'kostka', 'kostki', 'kostek')}"
        if len(largos) == 1:
            return ("Ile kostek ma ołówek?",
                    self.LEE + "Policz kostki pod ołówkiem, od gumki do czubka.",
                    "Liczba kostek: \\huecoRespuesta",
                    kostek(largos[0]))
        largo = "górny" if largos[0] > largos[1] else "dolny"
        return ("Ile kostek ma każdy ołówek? Który jest dłuższy?",
                self.LEE + "Policz kostki pod każdym ołówkiem, od gumki do czubka, i zakreśl "
                "dłuższy.",
                r"{\fontsize{28}{34}\selectfont Górny ołówek: \huecoRespuesta\\[4mm]"
                r"Dolny ołówek: \huecoRespuesta}",
                f"{kostek(largos[0])} i {kostek(largos[1])}: dłuższy jest {largo}")


ESPANOL = Espanol()
INGLES = Ingles()
POLACO = Polaco()
