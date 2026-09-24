"""Las dos lenguas de los cuadernos de números.

tools/gen_numeros.py genera dos cuadernos que son, página a página, el
mismo: "Aprendo los números" (main.tex), en español, y "First Numbers"
(english.tex), en inglés británico, como "Read and Draw" y "First Words"
de "Aprendo a leer". Comparten todo lo que no es lengua -- el calendario,
la escalera, los dibujos, las actividades y lo que se comprueba de cada
una --, y lo que cambia de uno a otro está aquí, en un solo sitio:

  - cómo se llama cada número, y cómo puede aparecer en la frase del día
    (en español, "un perro", "una manzana", "ninguna castaña"; en
    inglés, "one dog", "no chestnuts");
  - cómo se llaman las cosas que se cuentan (el dibujo es el mismo:
    OBJETOS, en tools/gen_numeros.py);
  - el tema de cada semana y el nombre de cada medalla;
  - y el enunciado, la instrucción y la entrada de la clave de cada
    actividad, que tools/gen_numeros.py compone con los números y las
    cosas de cada día ("Colorea 2 pelotas.", "Colour 2 balls.").

Lo que la página dice siempre igual (los títulos de las cajas, la
cabecera de cada día, la portada) no está aquí, sino en lang/es.tex y
lang/en.tex.

Cada lengua es un objeto con los mismos métodos: ESPANOL e INGLES, más
abajo. Los métodos de ESPANOL devuelven, letra por letra, lo que
escribía tools/gen_numeros.py antes de que hubiera un cuaderno en
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


ESPANOL = Espanol()
INGLES = Ingles()
