#!/usr/bin/env python3
"""Genera "Aprendo los números" (main.tex) a partir de content/q*.json:
content/generated-days.tex (una página por día) y
content/generated-clave.tex (la clave de respuestas).

Es el generador de "Aprendo a leer" (tools/gen_palabras.py, en
https://github.com/konradcinkusz/learning-to-read) para contar en vez de
leer: el mismo calendario (260 días, 52 semanas, cuatro trimestres que
son las cuatro estaciones, medalla al final de los tres primeros), los
mismos temas semana a semana y la misma familia -- y, como allí, una
escalera que NO es una disciplina editorial: está en ESCALERA, más abajo,
y este script falla si un día usa un número que todavía no ha llegado.

Cada día tiene una caja de arriba, "El número de hoy" (el número, su
nombre, el marco de diez, esas cosas dibujadas y una frase de la
historia, que lee el adulto), y una actividad que llena el resto de la
página. Las actividades y lo que se comprueba de cada una están en
render_actividad; el porqué, en notes/01-plan.md.

No editar content/generated-*.tex a mano -- se sobrescriben cada vez que
se ejecuta este script.

Uso:
    python3 tools/gen_numeros.py            # regenera content/generated-*.tex
    python3 tools/gen_numeros.py --check    # solo valida; exit 1 si algo no
                                            # cuadra o si lo generado está
                                            # desactualizado
"""

import json
import random
import re
import sys
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
SALIDA_DIAS = CONTENT_DIR / "generated-days.tex"
SALIDA_CLAVE = CONTENT_DIR / "generated-clave.tex"
TRAZO_FILE = CONTENT_DIR / "numeros-trazo.json"
LANG_FILE = ROOT / "lang" / "es.tex"

# --------------------------------------------------------------------
# El calendario
# --------------------------------------------------------------------
TOTAL_DIAS = 260
DIAS_POR_SEMANA = 5
SEMANAS_POR_TRIMESTRE = 13
# Mientras el cuaderno se escribe por partes (un PR por trimestre, cada
# uno en verde antes de fusionarse), cuántos días tiene ya escritos: se
# exigen exactamente esos, del 1 en adelante y sin huecos. None = el
# cuaderno está entero, con sus 260 días.
DIAS_ESCRITOS = 130

NOMBRE_MEDALLA = {1: "Otoño", 2: "Invierno", 3: "Primavera"}
ULTIMO_DIA_TRIMESTRE = {1: 65, 2: 130, 3: 195, 4: 260}

# Los temas de cada semana: los de "Aprendo a leer" (el cuaderno de
# frases y el de primeras palabras cuentan el mismo año con los mismos
# temas), para que quien lleve los dos cuadernos cuente esa semana lo
# que lee. El tema de cada día tiene que ser el de su semana.
TEMAS = [
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
assert len(TEMAS) == TOTAL_DIAS // DIAS_POR_SEMANA

# --------------------------------------------------------------------
# La escalera
# --------------------------------------------------------------------
# Semana a semana: qué números llegan (se trazan el lunes y son el
# número de toda la semana) -- ver notes/01-plan.md para el año entero.
# En otoño, uno por semana, del 1 al 10 y el 0, con dos semanas de
# repaso; lo que se cuenta, se traza y se busca un día solo puede ser un
# número que ya haya llegado.
ESCALERA = {
    1: [1], 2: [2], 3: [3], 4: [4], 5: [5],
    6: [],    # repaso del 1 al 5, con las hojas del otoño
    7: [6],
    8: [0],   # las castañas: la cesta vacía, cero
    9: [7],   # el cumpleaños de Lucía: siete velas
    10: [8],  # los animales del barrio: las ocho patas de la araña
    11: [9],
    12: [10], # el mercado: diez huevos
    13: [],   # repaso del 0 al 10, en Nochebuena
    # Invierno: del 11 al 20, dos por semana -- "diez y uno, diez y
    # dos..." --, y después, sin números nuevos, comparar, antes y
    # después, la recta, ordenar y juntar (DESDE_SEMANA, más abajo).
    14: [11, 12], 15: [13, 14], 16: [15, 16], 17: [17, 18], 18: [19, 20],
}
# El día de la semana (0 = lunes) en que llega cada número nuevo: el
# primero, el lunes; el segundo, si lo hay, el miércoles. Hasta ese día,
# el número todavía no ha llegado.
LLEGADA = [0, 2]
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes"]

# Las actividades que llegan con el invierno, y la semana en que llegan:
# como con los números, ninguna se usa antes.
DESDE_SEMANA = {
    "decena": 14,   # diez y más: 10 y 3 son 13
    "compara": 19,  # más, menos, igual
    "vecinos": 20,  # el de antes y el de después
    "recta": 21,    # la recta numérica
    "ordena": 22,   # de menor a mayor
    "junta": 23,    # la suma, con dibujos y sin signos: 3 y 2 son 5
}

# Un grupo de cosas va como los puntos de un dado hasta el 6 -- así se ve
# de un vistazo cuántas son --, del 7 al 10 como en el marco de diez (una
# fila de cinco y lo que falta debajo), y del 11 al 20 como dos marcos de
# diez, uno encima de otro: el primero, lleno. Más de 20, no cabe.
MAX_GRUPO = 20


def conocidos(semana, dia_semana=DIAS_POR_SEMANA - 1):
    """Los números que ya han llegado ese día de esa semana (sin día, al
    terminarla)."""
    previos = {n for s in range(1, semana) for n in ESCALERA.get(s, [])}
    nuevos = ESCALERA.get(semana, [])
    return previos | {n for i, n in enumerate(nuevos) if LLEGADA[i] <= dia_semana}


def trimestre_de(semana):
    return (semana - 1) // SEMANAS_POR_TRIMESTRE + 1


# Cómo se llama cada número, y cómo puede aparecer en la frase del día
# (la frase de un día con el 1 dice "un perro" o "una manzana"; con el 21,
# "veintiún globos" o "veintiuna velas").
_HASTA_29 = [
    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis",
    "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidós",
    "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete",
    "veintiocho", "veintinueve",
]
_DECENAS = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta",
            7: "setenta", 8: "ochenta", 9: "noventa"}


def nombre_numero(n):
    if n < 30:
        return _HASTA_29[n]
    if n == 100:
        return "cien"
    d, u = divmod(n, 10)
    return _DECENAS[d] + (f" y {_HASTA_29[u]}" if u else "")


NOMBRES = {n: nombre_numero(n) for n in range(101)}


def formas(n):
    if n == 0:
        return {"cero", "ningún", "ninguna", "ninguno", "nada"}
    nombre = NOMBRES[n]
    if n % 10 == 1 and n != 11:
        raiz = nombre[:-3]    # "uno" -> "un", "una"; "veintiuno" -> "veintiún"
        return {nombre, raiz + ("ún" if n == 21 else "un"), raiz + "una"}
    return {nombre}


# --------------------------------------------------------------------
# Las cosas que se cuentan (diagrams/objetos.tex)
# --------------------------------------------------------------------
# macro, singular, plural, género -- el enunciado se compone con ellos
# ("Colorea 1 manzana.", "Colorea 2 pelotas.", "¿Cuántos huesos hay?").
OBJETOS = {
    "manzana": (r"\objManzana", "manzana", "manzanas", "f"),
    "pelota": (r"\objPelota", "pelota", "pelotas", "f"),
    "hueso": (r"\objHueso", "hueso", "huesos", "m"),
    "sol": (r"\objSol", "sol", "soles", "m"),
    "huella": (r"\objHuella", "huella", "huellas", "f"),
    "toby": (r"\objToby", "perro", "perros", "m"),
    "globo": (r"\objGlobo", "globo", "globos", "m"),
    "estrella": (r"\objEstrella", "estrella", "estrellas", "f"),
    "hoja": (r"\objHoja", "hoja", "hojas", "f"),
    "corazon": (r"\objCorazon", "corazón", "corazones", "m"),
    "caramelo": (r"\objCaramelo", "caramelo", "caramelos", "m"),
    "pez": (r"\objPez", "pez", "peces", "m"),
    "lapiz": (r"\objLapiz", "lápiz", "lápices", "m"),
    "libro": (r"\objLibro", "libro", "libros", "m"),
    "galleta": (r"\objGalleta", "galleta", "galletas", "f"),
    "seta": (r"\objSeta", "seta", "setas", "f"),
    "castana": (r"\objCastana", "castaña", "castañas", "f"),
    "cesta": (r"\objCesta", "cesta", "cestas", "f"),
    "vela": (r"\objVela", "vela", "velas", "f"),
    "regalo": (r"\objRegalo", "regalo", "regalos", "m"),
    "arana": (r"\objArana", "araña", "arañas", "f"),
    "paraguas": (r"\objParaguas", "paraguas", "paraguas", "m"),
    "bola": (r"\objBola", "bola", "bolas", "f"),
    "arbol": (r"\objArbol", "árbol", "árboles", "m"),
    "pato": (r"\objPato", "pato", "patos", "m"),
    "coche": (r"\objCoche", "coche", "coches", "m"),
    "trex": (r"\objTrex", "dinosaurio", "dinosaurios", "m"),
    "mariposa": (r"\objMariposa", "mariposa", "mariposas", "f"),
    "gota": (r"\objGota", "gota", "gotas", "f"),
    "nube": (r"\objNube", "nube", "nubes", "f"),
    "huevo": (r"\objHuevo", "huevo", "huevos", "m"),
    "pajaro": (r"\objPajaro", "pájaro", "pájaros", "m"),
    "gato": (r"\objGato", "gato", "gatos", "m"),
    "mochila": (r"\objMochila", "mochila", "mochilas", "f"),
    "ardilla": (r"\objArdilla", "ardilla", "ardillas", "f"),
    "plato": (r"\objPlato", "plato", "platos", "m"),
    "mandarina": (r"\objMandarina", "mandarina", "mandarinas", "f"),
    "copo": (r"\objCopo", "copo", "copos", "m"),
    "muneco": (r"\objMuneco", "muñeco de nieve", "muñecos de nieve", "m"),
    "gorrofiesta": (r"\objGorroFiesta", "gorro de fiesta", "gorros de fiesta", "m"),
    "nota": (r"\objNota", "nota", "notas", "f"),
    "osito": (r"\objOsito", "osito", "ositos", "m"),
    "flor": (r"\objFlor", "flor", "flores", "f"),
    "corona": (r"\objCorona", "corona", "coronas", "f"),
    "cometa": (r"\objCometa", "cometa", "cometas", "f"),
    "alubia": (r"\objAlubia", "semilla", "semillas", "f"),
    "boton": (r"\objBoton", "botón", "botones", "m"),
    "tronco": (r"\objTronco", "tronco", "troncos", "m"),
    "fresa": (r"\objFresa", "fresa", "fresas", "f"),
    "piruleta": (r"\objPiruleta", "piruleta", "piruletas", "f"),
    "paloma": (r"\objPaloma", "paloma", "palomas", "f"),
    "ovillo": (r"\objOvillo", "ovillo", "ovillos", "m"),
    "bufanda": (r"\objBufanda", "bufanda", "bufandas", "f"),
    "gorro": (r"\objGorro", "gorro", "gorros", "m"),
    "maceta": (r"\objMaceta", "maceta", "macetas", "f"),
    "brote": (r"\objBrote", "brote", "brotes", "m"),
    "pipa": (r"\objPipa", "pipa", "pipas", "f"),
}

# Lo que se dibuja vacío en "El número de hoy" el día que el número es el
# 0: la cesta en la que no queda ninguna castaña, el plato en el que no
# queda nada.
CONTENEDORES = {"cesta", "plato"}


def nombre_objeto(objeto, n):
    _, singular, plural, _ = OBJETOS[objeto]
    return singular if n == 1 else plural


def genero(objeto):
    return OBJETOS[objeto][3]


class ErrorDeContenido(Exception):
    pass


def escapar(texto):
    """Lo mínimo para que un texto del JSON se pueda poner tal cual en
    LaTeX."""
    return (
        texto.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
        .replace("#", r"\#").replace("_", r"\_")
    )


def campos(dia, actividad, requeridos):
    faltan = [c for c in requeridos if c not in actividad]
    if faltan:
        raise ErrorDeContenido(
            f"día {dia}: a la actividad '{actividad.get('tipo')}' le falta "
            + ", ".join(repr(c) for c in faltan)
        )


# --------------------------------------------------------------------
# Dibujar cosas: en fila, en grupos (como los puntos de un dado)
# --------------------------------------------------------------------
# Cada cosa ocupa la caja de -1 a 1 (diagrams/objetos.tex); aquí se
# colocan en unidades de esa caja, y el tikzpicture entero se escala.
POSICIONES_DADO = {
    1: [(0, 0)],
    2: [(-1, 1), (1, -1)],
    3: [(-1, 1), (0, 0), (1, -1)],
    4: [(-1, 1), (1, 1), (-1, -1), (1, -1)],
    5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
    6: [(-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)],
}


def _cosa(macro, x, y):
    return f"\\begin{{scope}}[shift={{({x:.2f},{y:.2f})}}]{macro}\\end{{scope}}"


def escala_para(n, ancho_cm, paso, maxima, por_fila=5):
    """La escala a la que caben n cosas en filas de `por_fila` dentro de
    `ancho_cm`, sin pasar de `maxima`: pocas cosas, grandes; muchas, más
    pequeñas, pero siempre en el mismo ancho."""
    return round(min(maxima, ancho_cm / (max(1, min(n, por_fila)) * paso)), 3)


def fila(objeto, n, escala, por_fila=5, paso=2.5):
    """n cosas en filas de `por_fila`, centradas: la última fila, si no
    está llena, también centrada. De 11 en adelante, las diez primeras
    (dos filas) van un poco separadas de las demás, como en los dos
    marcos de diez."""
    macro = OBJETOS[objeto][0]
    piezas = []
    filas = [min(por_fila, n - i) for i in range(0, n, por_fila)]
    for f, cuantas in enumerate(filas):
        for i in range(cuantas):
            x = (i - (cuantas - 1) / 2) * paso
            y = -f * paso - (SEPARACION_DECENA * paso if n > 10 and f >= 2 else 0)
            piezas.append(_cosa(macro, x, y))
    return (
        f"\\begin{{tikzpicture}}[objeto, scale={escala}, baseline=(current bounding box.center)]"
        + "".join(piezas) + "\\end{tikzpicture}"
    )


# Del 11 al 20, lo que se separan las diez primeras de las demás, en
# pasos: se ven los dos marcos de diez.
SEPARACION_DECENA = 0.4


def posiciones(n, paso):
    """Dónde va cada cosa de un grupo de n, en unidades de la caja de una
    cosa, y el ancho y el alto de lo que ocupan: hasta 6, los puntos de un
    dado; del 7 al 10, el marco de diez (una fila de cinco, y debajo el
    resto, desde la izquierda); del 11 al 20, dos marcos de diez, uno
    encima de otro (el primero, lleno). El grupo de 0 no tiene nada, pero
    ocupa lo mismo que uno de 6: su marco se ve vacío."""
    if n <= 6:
        return [(x * paso, y * paso) for x, y in POSICIONES_DADO.get(n, [])], 2 * paso + 2, 2 * paso + 2
    filas = -(-n // 5)
    separacion = SEPARACION_DECENA * paso if n > 10 else 0
    alto = (filas - 1) * paso + separacion
    sitios = [((i % 5 - 2) * paso, alto / 2 - (i // 5) * paso - (separacion if i >= 10 else 0))
              for i in range(n)]
    return sitios, 4 * paso + 2, alto + 2


def posiciones_en_filas(n, paso, sitios_fila=5):
    """Como en el marco de diez, para todos: filas de cinco desde la
    izquierda (hasta 5, una fila; del 6 al 10, dos), y el mismo ancho
    siempre -- el de `sitios_fila` cosas --, para que todos los grupos de
    "une" se alineen."""
    filas = max(1, -(-n // 5))
    x0 = (sitios_fila - 1) / 2
    sitios = [((i % 5 - x0) * paso, ((filas - 1) / 2 - i // 5) * paso) for i in range(n)]
    return sitios, (sitios_fila - 1) * paso + 2, (filas - 1) * paso + 2


# Entre las cosas de un grupo y su marco a trazos.
MARGEN_GRUPO = 0.2


def grupo(objeto, n, paso=2.3, colocar=posiciones):
    """Un grupo de n cosas (n <= MAX_GRUPO) dentro de su marco a trazos,
    centrado en el origen: (tikz, ancho, alto), con el marco."""
    macro = OBJETOS[objeto][0]
    sitios, ancho, alto = colocar(n, paso)
    ancho, alto = ancho + 2 * MARGEN_GRUPO, alto + 2 * MARGEN_GRUPO
    return marco(ancho, alto) + "".join(_cosa(macro, x, y) for x, y in sitios), ancho, alto


def marco(ancho, alto, x=0.0, y=0.0):
    """El borde a trazos de un grupo (o de la bandeja de "cuenta")."""
    return (
        f"\\draw[dashed, line width=0.8pt, rounded corners=4mm, colorGris] "
        f"({x - ancho / 2:.2f},{y - alto / 2:.2f}) rectangle ({x + ancho / 2:.2f},{y + alto / 2:.2f});"
    )


def disponer(bloques, ancho_cm, alto_cm, hueco, maxima):
    """Coloca bloques [(tikz, ancho, alto)], centrados, en una fila -- o en
    dos, si así salen más grandes --, y devuelve (tikz, escala): lo de
    dentro de un tikzpicture a esa escala, con los bloques en orden de
    lectura (de izquierda a derecha, y de arriba abajo)."""
    opciones = [[bloques]]
    if len(bloques) >= 3:
        mitad = (len(bloques) + 1) // 2
        opciones.append([bloques[:mitad], bloques[mitad:]])
    mejor = None
    for filas in opciones:
        ancho = max(sum(b[1] for b in f) + hueco * (len(f) - 1) for f in filas)
        alto = sum(max(b[2] for b in f) for f in filas) + hueco * (len(filas) - 1)
        escala = min(maxima, ancho_cm / ancho, alto_cm / alto)
        # Dos filas, solo si así las cosas salen bastante más grandes: en
        # una fila, los grupos se comparan mejor.
        if mejor is None or escala > mejor[0] * 1.15:
            mejor = (escala, filas, alto)
    escala, filas, alto = mejor
    piezas, y = [], alto / 2
    for f in filas:
        alto_fila = max(b[2] for b in f)
        x = -(sum(b[1] for b in f) + hueco * (len(f) - 1)) / 2
        for tikz, ancho_b, _ in f:
            piezas.append(
                f"\\begin{{scope}}[shift={{({x + ancho_b / 2:.2f},{y - alto_fila / 2:.2f})}}]{tikz}\\end{{scope}}"
            )
            x += ancho_b + hueco
        y -= alto_fila + hueco
    return "\n".join(piezas), round(escala, 3)


# --------------------------------------------------------------------
# Traza: el contorno de puntos de cada número
# --------------------------------------------------------------------
# El mismo tamaño y los mismos puntos que las letras de "Aprendo a
# leer" (ESCALA_TRAZO_CM, RADIO_PUNTO_TRAZO_CM en su tools/gen_days.py).
ESCALA_TRAZO_CM = 7.0
RADIO_PUNTO_TRAZO_CM = "0.08"
HUECO_CIFRAS_EM = 0.06   # entre las dos cifras del 10
HUECO_COPIAS_CM = 1.2    # entre una copia y la siguiente
ANCHO_TRAZO_CM = 15.0    # lo que cabe dentro de la caja

_trazo = None


def datos_trazo():
    global _trazo
    if _trazo is None:
        datos = json.loads(TRAZO_FILE.read_text(encoding="utf-8"))
        datos.pop("_comentario", None)
        _trazo = datos
    return _trazo


def puntos_numero(n, x0):
    """Los puntos de n (una o dos cifras) en cm, empezando en x0, y el
    ancho que ocupa."""
    datos = datos_trazo()
    piezas, x = [], 0.0
    for i, cifra in enumerate(str(n)):
        if cifra not in datos:
            raise ErrorDeContenido(f"no hay contorno para la cifra {cifra} en {TRAZO_FILE.name}")
        entrada = datos[cifra]
        bx0, _, bx1, _ = entrada["bbox"]
        if i:
            x += HUECO_CIFRAS_EM
        for contorno in entrada["contornos"]:
            for px, py in contorno:
                cx = x0 + (x + px - bx0) * ESCALA_TRAZO_CM
                cy = py * ESCALA_TRAZO_CM
                piezas.append(f"({cx:.3f},{cy:.3f}) circle ({RADIO_PUNTO_TRAZO_CM})")
        x += bx1 - bx0
    return piezas, x * ESCALA_TRAZO_CM


def trazo(n):
    """Tantas copias de n como quepan (hasta tres), en fila."""
    _, ancho = puntos_numero(n, 0)
    copias = max(1, min(3, int((ANCHO_TRAZO_CM + HUECO_COPIAS_CM) // (ancho + HUECO_COPIAS_CM))))
    piezas = []
    for c in range(copias):
        p, _ = puntos_numero(n, c * (ancho + HUECO_COPIAS_CM))
        piezas += p
    return r"\begin{tikzpicture}\fill[colorPunto] " + " ".join(piezas) + r";\end{tikzpicture}"


# --------------------------------------------------------------------
# Las plantillas
# --------------------------------------------------------------------
PLANTILLA_DIA = Template(r"""\begin{diapagina}{$dia}{$semana}{$trimestre}{$tema}
\numeroDeHoy{$numero}{$nombre}{$cosas}{$frase}
$actividad
\end{diapagina}
""")

PLANTILLA_TRAZA = Template(r"""\begin{cajaTraza}[abajo]
\begin{center}
$trazo
\end{center}
\tcblower
\instruccion{\lblInstruccionTraza}
\vspace{8mm}
$renglones
\end{cajaTraza}""")

PLANTILLA_COLOREA = Template(r"""\begin{cajaColorea}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$resto}
\tcblower
\begin{center}
$cosas
\end{center}
\end{cajaColorea}""")

PLANTILLA_RODEA = Template(r"""\begin{cajaRodea}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
\begin{tikzpicture}[objeto, scale=$escala]
$grupos
\end{tikzpicture}
\end{center}
\end{cajaRodea}""")

PLANTILLA_CUENTA = Template(r"""\begin{cajaCuenta}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
\begin{tikzpicture}[objeto, scale=$escala]
$grupo
\end{tikzpicture}

\vspace{14mm}
{\fontsize{44}{48}\selectfont\bfseries $opciones}
\end{center}
\end{cajaCuenta}""")

PLANTILLA_BUSCA = Template(r"""\begin{cajaBusca}[centrado abajo]
\enunciado{$enunciado}
\instruccion{\lblInstruccionBusca}
\tcblower
\begin{center}
{\renewcommand{\arraystretch}{2.1}\fontsize{34}{38}\selectfont\bfseries
\begin{tabular}{*{$columnas}{>{\centering\arraybackslash}p{17mm}}}
$filas
\end{tabular}}
\end{center}
\end{cajaBusca}""")

PLANTILLA_UNE = Template(r"""\begin{cajaUne}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
\begin{tikzpicture}[objeto]
$dibujo
\end{tikzpicture}
\end{center}
\end{cajaUne}""")

PLANTILLA_SERIE = Template(r"""\begin{cajaCompleta}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
\begin{tikzpicture}[objeto]
$tren
\end{tikzpicture}
\end{center}
\end{cajaCompleta}""")

# "Diez y más" y "Junta": los dos grupos con una "y" en medio y, debajo,
# lo que se escribe: "10 y 3 son [ ]".
PLANTILLA_DOS_GRUPOS = Template(r"""\begin{$caja}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
\begin{tikzpicture}[objeto, scale=$escala]
$dibujo
\end{tikzpicture}

\vspace{12mm}
{\fontsize{40}{44}\selectfont\bfseries $a y $b son \huecoRespuesta}
\end{center}
\end{$caja}""")

# Las demás actividades del invierno: un enunciado, la instrucción y un
# dibujo, centrado en el hueco.
PLANTILLA_CAJA = Template(r"""\begin{$caja}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
$dibujo
\end{center}
\end{$caja}""")

PLANTILLA_DIBUJA = Template(r"""\begin{cajaDibuja}
\enunciado{$enunciado}
\end{cajaDibuja}""")

PLANTILLA_REPASA = Template(r"""\begin{cajaRepasa}[abajo]
\begin{listaRepaso}
$items
\end{listaRepaso}
\vspace{2mm}
\enunciado{$prompt}
\tcblower
$cartel
\end{cajaRepasa}""")

PLANTILLA_MEDALLA = Template(r"""\begin{center}
\vspace*{3cm}
\medalla{$dia}

\vspace{10mm}
{\fontsize{34}{40}\selectfont\bfseries\color{colorLectura}\lblMedalla{$estacion}}\\[8mm]
{\Large $dia\ días, $dia\ páginas.}\\[12mm]
{\Large \lblMedallaAnimo}
\end{center}
\vspace*{\fill}
\newpage
""")

# Las formas que acompañan a los números en "busca": se ven distintas a
# primera vista, así que lo que hay que mirar son los números. La
# primera es el círculo, que el día que se busca el 0 no sale.
FORMAS_BUSCA = [
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt] (0,0) circle (3.8mm);",
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt, line join=round] (-4mm,-3.4mm) -- (4mm,-3.4mm) -- (0,3.8mm) -- cycle;",
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt] (-3.4mm,-3.4mm) rectangle (3.4mm,3.4mm);",
]

ORDINALES = {1: "el primero", 2: "el segundo", 3: "el tercero", 4: "el cuarto"}

# "Une": los grupos a la izquierda, uno debajo de otro, cada uno con un
# punto a su derecha; los números a la derecha, desordenados, cada uno
# con su punto -- de punto a punto se traza la línea. En cm.
ANCHO_GRUPOS_UNE_CM = 8.6
ALTO_UNE_CM = 11.0
HUECO_UNE_CM = 3.8        # lo que recorre la línea, como poco
FUENTE_NUMERO = r"\fontsize{40}{40}\selectfont\bfseries"
# "Junta", en invierno: sumas con dibujos, hasta 10.
MAX_JUNTA = 10


def bloque_puntos(n, dos):
    """El marco de diez con sus n puntos -- dos marcos, uno al lado del
    otro, si `dos` (del 11 al 20) --, en las unidades de las cosas y con su
    marco a trazos: (tikz, ancho, alto), centrado en el origen."""
    marcos, celda, hueco = (2 if dos else 1), 1.0, 0.6
    ancho = marcos * 5 * celda + (marcos - 1) * hueco
    piezas = []
    for m in range(marcos):
        x0 = -ancho / 2 + m * (5 * celda + hueco)
        for i in range(10):
            cx, cy = x0 + (i % 5) * celda, (0 if i < 5 else -celda)
            piezas.append(f"\\draw ({cx:.2f},{cy:.2f}) rectangle ++({celda},{celda});")
            if m * 10 + i < n:
                piezas.append(f"\\fill[colorLectura] ({cx + celda / 2:.2f},{cy + celda / 2:.2f}) circle (0.32);")
    ancho, alto = ancho + 0.8, 2 * celda + 0.8
    return marco(ancho, alto) + "".join(piezas), ancho, alto


def dibujo_une(objeto, grupos, orden):
    """Los grupos (en filas de cinco, como en el marco de diez: así se
    alinean) y, frente a cada uno, un número de `orden`. Con el objeto
    "puntos", cada grupo es un marco de diez (dos, del 11 al 20)."""
    paso, hueco = 2.3, 1.0
    sitios_fila = min(5, max(grupos))

    def colocar(n, paso):
        return posiciones_en_filas(n, paso, sitios_fila)

    if objeto == "puntos":
        bloques = [bloque_puntos(g, max(grupos) > 10) for g in grupos]
    else:
        bloques = [grupo(objeto, g, paso, colocar=colocar) for g in grupos]
    ancho = max(b[1] for b in bloques)
    alto = sum(b[2] for b in bloques) + hueco * (len(bloques) - 1)
    s = min(1.0, ANCHO_GRUPOS_UNE_CM / ancho, ALTO_UNE_CM / alto)
    x_punto = ancho * s + 0.3
    x_numero = x_punto + HUECO_UNE_CM
    piezas, y = [], 0.0
    for (tikz, _, alto_b), numero in zip(bloques, orden):
        yc = y - alto_b * s / 2
        piezas.append(
            f"\\begin{{scope}}[shift={{({ancho * s / 2:.2f},{yc:.2f})}}, scale={s:.3f}]{tikz}\\end{{scope}}"
            f"\\fill ({x_punto:.2f},{yc:.2f}) circle (1.3mm);"
            f"\\fill ({x_numero:.2f},{yc:.2f}) circle (1.3mm);"
            f"\\node[anchor=west, font={FUENTE_NUMERO}] at ({x_numero + 0.3:.2f},{yc:.2f}) {{{numero}}};"
        )
        y -= (alto_b + hueco) * s
    return "\n".join(piezas)


# La locomotora de "serie", en unidades del vagón (un vagón de 2,4 cm
# mide 2,4 x 2,4): las ruedas antes que la caldera, que las tapa por
# arriba; el humo va hacia atrás, porque el tren va hacia la izquierda.
LOCOMOTORA = (
    r"\filldraw[fill=white] (0.7,0) circle (0.3); \filldraw[fill=white] (1.5,0) circle (0.3);"
    r"\filldraw[fill=white] (2.6,0.15) circle (0.45);"
    r"\filldraw[fill=white] (0,0.12) rectangle (0.2,0.6);"
    r"\filldraw[fill=white, rounded corners=1mm] (0.2,0.12) rectangle (2.0,1.35);"
    r"\filldraw[fill=white] (2.0,0.12) rectangle (3.2,2.3);"
    r"\filldraw[fill=white] (2.3,1.3) rectangle (2.9,1.9);"
    r"\filldraw[fill=white] (1.85,2.3) rectangle (3.35,2.5);"
    r"\filldraw[fill=white] (0.45,1.35) rectangle (0.85,2.0);"
    r"\filldraw[fill=white] (0.35,2.0) rectangle (0.95,2.2);"
    r"\draw (1.05,2.55) circle (0.17); \draw (1.45,2.82) circle (0.22); \draw (1.97,3.0) circle (0.26);"
)
ANCHO_LOCOMOTORA = 3.35
ANCHO_TREN_CM = 14.8


def dibujo_serie(valores):
    """Un tren: la locomotora y un vagón por número, vacíos los que faltan
    (None). Si son muchos vagones, sin locomotora, para que quepan."""
    k, hueco = len(valores), 0.45
    con_locomotora = k <= 5
    if con_locomotora:
        ancho = (ANCHO_TREN_CM - k * hueco) / (ANCHO_LOCOMOTORA / 2.4 + k)
    else:
        ancho = (ANCHO_TREN_CM + hueco) / k - hueco
    ancho = min(2.6, ancho)
    u = ancho / 2.4
    tam = 44 if ancho >= 2.2 else 38 if ancho >= 1.8 else 32
    fuente = f"\\fontsize{{{tam}}}{{{tam}}}\\selectfont\\bfseries"
    piezas, x = [], 0.0
    if con_locomotora:
        piezas.append(f"\\begin{{scope}}[scale={u:.3f}]{LOCOMOTORA}\\end{{scope}}")
        x = ANCHO_LOCOMOTORA * u + hueco
        piezas.append(f"\\draw ({3.2 * u:.2f},{0.45 * u:.2f}) -- ({x:.2f},{0.45 * u:.2f});")
    total = x + k * ancho + (k - 1) * hueco
    piezas.insert(0, f"\\draw (-0.3,{-0.3 * u:.2f}) -- ({total + 0.3:.2f},{-0.3 * u:.2f});")
    for i, v in enumerate(valores):
        if i:
            piezas.append(f"\\draw ({x - hueco:.2f},{0.45 * u:.2f}) -- ({x:.2f},{0.45 * u:.2f});")
        for rueda in (0.27, 0.73):
            piezas.append(f"\\filldraw[fill=white] ({x + rueda * ancho:.2f},0) circle ({0.3 * u:.2f});")
        piezas.append(
            f"\\filldraw[fill=white, rounded corners=2mm] ({x:.2f},{0.12 * u:.2f}) "
            f"rectangle ({x + ancho:.2f},{0.12 * u + ancho:.2f});"
        )
        if v is not None:
            piezas.append(f"\\node[font={fuente}] at ({x + ancho / 2:.2f},{0.12 * u + ancho / 2:.2f}) {{{v}}};")
        x += ancho + hueco
    return "\n".join(piezas)


def dibujo_dos_grupos(objeto, a, b):
    """Dos grupos, uno al lado del otro, con una "y" en medio ("Diez y
    más", "Junta"): (tikz, escala)."""
    ga, gb = grupo(objeto, a), grupo(objeto, b)
    hueco = 3.0
    ancho = ga[1] + hueco + gb[1]
    escala = round(min(0.75, 14.0 / ancho, 7.0 / max(ga[2], gb[2])), 3)
    xa, xb = -ancho / 2 + ga[1] / 2, ancho / 2 - gb[1] / 2
    return (
        f"\\begin{{scope}}[shift={{({xa:.2f},0)}}]{ga[0]}\\end{{scope}}"
        f"\\begin{{scope}}[shift={{({xb:.2f},0)}}]{gb[0]}\\end{{scope}}"
        f"\\node[font={FUENTE_NUMERO}] at ({-ancho / 2 + ga[1] + hueco / 2:.2f},0) {{y}};"
    ), escala


def dibujo_vecinos(numeros):
    """Una fila de tres casas por número: en la de en medio vive el
    número; la de la izquierda, la de antes, y la de la derecha, la de
    después, se quedan vacías para escribir. En cm."""
    ancho, alto, tejado, sep, hueco = 2.6, 2.2, 1.1, 3.5, 0.9
    s = round(min(1.0, 11.0 / (len(numeros) * (alto + tejado + hueco))), 3)
    piezas = [
        f"\\node[font=\\small, text=colorGris] at ({-sep:.2f},{alto + tejado + 0.45:.2f}) {{antes}};",
        f"\\node[font=\\small, text=colorGris] at ({sep:.2f},{alto + tejado + 0.45:.2f}) {{después}};",
    ]
    for f, n in enumerate(numeros):
        y = -f * (alto + tejado + hueco)
        for i, x in enumerate((-sep, 0, sep)):
            piezas.append(
                f"\\filldraw[fill=white] ({x - ancho / 2:.2f},{y:.2f}) rectangle ({x + ancho / 2:.2f},{y + alto:.2f});"
                f"\\filldraw[fill=white] ({x - ancho / 2 - 0.25:.2f},{y + alto:.2f}) -- ({x:.2f},{y + alto + tejado:.2f})"
                f" -- ({x + ancho / 2 + 0.25:.2f},{y + alto:.2f}) -- cycle;"
            )
            if i == 1:
                piezas.append(f"\\node[font={FUENTE_NUMERO}] at ({x:.2f},{y + alto / 2:.2f}) {{{n}}};")
    return f"\\begin{{tikzpicture}}[objeto, scale={s}]\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_recta(desde, hasta, faltan):
    """La recta numérica de `desde` a `hasta`: una raya por número, y
    debajo el número -- o, si falta, un hueco para escribirlo. En cm."""
    paso = min(1.6, 13.2 / (hasta - desde))
    largo = (hasta - desde) * paso
    # Con dos números de dos cifras seguidos, más pequeños: si no, se tocan.
    tam = 22 if sum(v >= 10 for v in range(desde, hasta + 1)) >= 2 else 28
    fuente = f"\\fontsize{{{tam}}}{{{tam}}}\\selectfont\\bfseries"
    medio = min(0.62, (paso - 0.2) / 2)    # medio hueco
    piezas = [f"\\draw[-{{Stealth[length=3mm]}}, line width=1.4pt] (-0.5,0) -- ({largo + 0.8:.2f},0);"]
    for i, v in enumerate(range(desde, hasta + 1)):
        x = i * paso
        piezas.append(f"\\draw[line width=1.4pt] ({x:.2f},-0.3) -- ({x:.2f},0.3);")
        if v in faltan:
            piezas.append(f"\\draw[dashed, line width=0.9pt, rounded corners=1mm] ({x - medio:.2f},-2.1) rectangle ({x + medio:.2f},-0.75);")
        else:
            piezas.append(f"\\node[font={fuente}] at ({x:.2f},-1.3) {{{v}}};")
    return "\\begin{tikzpicture}[objeto]\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_ordena(numeros):
    """Arriba, los números en tarjetas, desordenados (tal como vienen);
    abajo, tantos huecos como números, en fila, para escribirlos en
    orden. En cm."""
    k, lado, sep = len(numeros), 2.3, 3.1
    x0 = -(k - 1) * sep / 2
    giros = [-7, 5, -4, 8, -6]
    piezas = []
    for i, n in enumerate(numeros):
        piezas.append(
            f"\\begin{{scope}}[shift={{({x0 + i * sep:.2f},3.6)}}, rotate={giros[i % len(giros)]}]"
            f"\\filldraw[fill=white, rounded corners=2mm] ({-lado / 2},{-lado / 2}) rectangle ({lado / 2},{lado / 2});"
            f"\\node[font={FUENTE_NUMERO}, transform shape] at (0,0) {{{n}}};\\end{{scope}}"
        )
    for i in range(k):
        x = x0 + i * sep
        piezas.append(f"\\draw[line width=1.1pt, rounded corners=2mm] ({x - lado / 2:.2f},{-lado / 2:.2f}) rectangle ({x + lado / 2:.2f},{lado / 2:.2f});")
        if i:
            piezas.append(f"\\draw[-{{Stealth[length=2.5mm]}}, line width=1.1pt] ({x - sep + lado / 2 + 0.12:.2f},0) -- ({x - lado / 2 - 0.12:.2f},0);")
    return "\\begin{tikzpicture}[objeto]\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_numeros(numeros):
    """Unos números sueltos, grandes, para rodear uno ("Compara")."""
    fuente = r"\fontsize{72}{72}\selectfont\bfseries"
    return (f"{{{fuente}" + r"\hspace{26mm}".join(str(n) for n in numeros) + "}")


# --------------------------------------------------------------------
# Actividades
# --------------------------------------------------------------------
def comprobar_numero(dia, n, semana, que):
    dia_semana = (dia - 1) % DIAS_POR_SEMANA
    if n not in conocidos(semana, dia_semana):
        raise ErrorDeContenido(
            f"día {dia}: {que} es {n}, que todavía no ha llegado el "
            f"{DIAS_SEMANA[dia_semana]} de la semana {semana} (ver ESCALERA y "
            f"LLEGADA: hasta ahora, {sorted(conocidos(semana, dia_semana))})"
        )


def comprobar_objeto(dia, objeto):
    if objeto not in OBJETOS:
        raise ErrorDeContenido(
            f"día {dia}: no hay dibujo para «{objeto}» (ver OBJETOS y "
            "diagrams/objetos.tex)"
        )


def render_actividad(d):
    """(tex, clave): la caja de la actividad del día, y su entrada de la
    clave de respuestas (None si no tiene nada que comprobar)."""
    num, semana, a = d["dia"], d["semana"], d["actividad"]
    tipo = a.get("tipo")
    n = d["numero"]
    if tipo in DESDE_SEMANA and semana < DESDE_SEMANA[tipo]:
        raise ErrorDeContenido(
            f"día {num}: '{tipo}' no llega hasta la semana {DESDE_SEMANA[tipo]} (ver DESDE_SEMANA)"
        )

    if tipo == "traza":
        cifra = a.get("numero", n)
        comprobar_numero(num, cifra, semana, "el número que se traza")
        # Del 11 en adelante, la caja de arriba es más alta (dos marcos de
        # diez): dos renglones, en vez de tres.
        renglones = "\n".join([f"\\renglonTraza{{{cifra}}}"] * (3 if n <= 10 else 2))
        return PLANTILLA_TRAZA.substitute(trazo=trazo(cifra), renglones=renglones), None

    if tipo == "colorea":
        campos(num, a, ["objeto", "total"])
        comprobar_objeto(num, a["objeto"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "lo que se colorea")
        total = a["total"]
        if not 1 <= cuantas < total <= 20:
            raise ErrorDeContenido(
                f"día {num}: 'colorea' tiene que tener más cosas que las que se "
                f"colorean (al menos una), y como mucho 20 (colorea {cuantas} de {total})"
            )
        resto = ("Las demás, déjalas en blanco." if genero(a["objeto"]) == "f"
                 else "Los demás, déjalos en blanco.")
        return PLANTILLA_COLOREA.substitute(
            enunciado=f"Colorea {cuantas} {nombre_objeto(a['objeto'], cuantas)}.",
            resto=resto,
            # En filas de cinco, a lo ancho de la caja, y sin pasar de
            # 10 cm de alto (de 11 en adelante, cuatro filas).
            cosas=fila(a["objeto"], total, escala=min(
                escala_para(total, 15.0, 2.5, 1.3), round(10.0 / (-(-total // 5) * 2.5), 3))),
        ), None

    if tipo == "rodea":
        campos(num, a, ["objeto", "grupos"])
        comprobar_objeto(num, a["objeto"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "el grupo que se rodea")
        grupos = a["grupos"]
        if not 2 <= len(grupos) <= 4 or len(set(grupos)) != len(grupos):
            raise ErrorDeContenido(
                f"día {num}: 'rodea' lleva de 2 a 4 grupos, todos distintos ({grupos})"
            )
        if grupos.count(cuantas) != 1:
            raise ErrorDeContenido(
                f"día {num}: en 'rodea' tiene que haber exactamente un grupo de "
                f"{cuantas} ({grupos})"
            )
        if max(grupos) > MAX_GRUPO or min(grupos) < 0:
            raise ErrorDeContenido(
                f"día {num}: un grupo de 'rodea' va de 1 a {MAX_GRUPO} cosas, o ninguna "
                f"el día que se rodea el 0 ({grupos})"
            )
        # Un grupo vacío solo tiene sentido si es el que se busca: "Rodea
        # donde no hay ninguna castaña."
        if 0 in grupos and cuantas != 0:
            raise ErrorDeContenido(
                f"día {num}: en 'rodea', el grupo vacío solo puede ser el que se rodea ({grupos})"
            )
        dibujo, escala = disponer(
            [grupo(a["objeto"], g, paso=2.2) for g in grupos],
            ancho_cm=15.0, alto_cm=10.0, hueco=1.6, maxima=0.7,
        )
        cosa = nombre_objeto(a["objeto"], cuantas)
        femenino = genero(a["objeto"]) == "f"
        if cuantas == 0:
            ninguna = f"{'ninguna' if femenino else 'ningún'} {nombre_objeto(a['objeto'], 1)}"
            enunciado, respuesta = f"Rodea donde no hay {ninguna}.", ninguna
        elif cuantas == 1:
            enunciado = f"Rodea donde hay 1 {cosa} {'sola' if femenino else 'solo'}."
            respuesta = f"1 {cosa}"
        else:
            enunciado, respuesta = f"Rodea donde hay {cuantas} {cosa}.", f"{cuantas} {cosa}"
        posicion = grupos.index(cuantas) + 1
        return PLANTILLA_RODEA.substitute(
            enunciado=enunciado,
            instruccion="Un adulto lee la pregunta. Rodea con el lápiz todo el grupo.",
            escala=escala,
            grupos=dibujo,
        ), ("rodea", f"{ORDINALES[posicion]} ({respuesta})")

    if tipo == "cuenta":
        campos(num, a, ["objeto", "opciones"])
        comprobar_objeto(num, a["objeto"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "lo que se cuenta")
        opciones = a["opciones"]
        for o in opciones:
            comprobar_numero(num, o, semana, "una de las opciones")
        if cuantas not in opciones or len(set(opciones)) != len(opciones) or not 2 <= len(opciones) <= 4:
            raise ErrorDeContenido(
                f"día {num}: 'cuenta' lleva de 2 a 4 opciones distintas, y una es "
                f"{cuantas} ({opciones})"
            )
        if cuantas > MAX_GRUPO:
            raise ErrorDeContenido(f"día {num}: 'cuenta' dibuja como mucho {MAX_GRUPO} cosas")
        plural = nombre_objeto(a["objeto"], 2)
        cuantos = "Cuántas" if genero(a["objeto"]) == "f" else "Cuántos"
        # La bandeja (el marco del grupo) se dibuja siempre: el día del 0,
        # es lo único que hay.
        dibujo, ancho, alto = grupo(a["objeto"], cuantas)
        return PLANTILLA_CUENTA.substitute(
            enunciado=f"¿{cuantos} {plural} hay?",
            instruccion=("Un adulto lee la pregunta. Cuenta señalando cada una con "
                         "el dedo, y rodea el número." if genero(a["objeto"]) == "f" else
                         "Un adulto lee la pregunta. Cuenta señalando cada uno con "
                         "el dedo, y rodea el número."),
            escala=round(min(1.0, 13.0 / ancho, 8.0 / alto), 3),
            grupo=dibujo,
            opciones=r"\hspace{14mm}".join(str(o) for o in opciones),
        ), ("cuenta", str(cuantas))

    if tipo == "busca":
        campos(num, a, ["veces", "otros"])
        buscar = a.get("buscar", n)
        comprobar_numero(num, buscar, semana, "el número que se busca")
        for o in a["otros"]:
            comprobar_numero(num, o, semana, "uno de los otros números")
            if o == buscar:
                raise ErrorDeContenido(f"día {num}: en 'busca', 'otros' no puede llevar el {buscar}")
        filas_n, columnas = 4, 6
        casillas = filas_n * columnas
        veces = a["veces"]
        if not 3 <= veces <= casillas // 2:
            raise ErrorDeContenido(
                f"día {num}: en 'busca', el número sale de 3 a {casillas // 2} veces"
            )
        # El orden lo decide el número del día: el mismo JSON da siempre
        # la misma cuadrícula.
        rng = random.Random(num)
        # El círculo se confunde con el 0: el día que se busca el 0, fuera.
        formas_busca = FORMAS_BUSCA[1:] if buscar == 0 else FORMAS_BUSCA
        relleno = [str(o) for o in a["otros"]] + formas_busca
        cuadricula = [str(buscar)] * veces + [
            relleno[i % len(relleno)] for i in range(casillas - veces)
        ]
        rng.shuffle(cuadricula)
        filas = " \\\\\n".join(
            " & ".join(cuadricula[f * columnas:(f + 1) * columnas]) for f in range(filas_n)
        )
        return PLANTILLA_BUSCA.substitute(
            enunciado=f"Busca todos los {buscar}.",
            columnas=columnas, filas=filas,
        ), ("busca", f"el {buscar} sale {veces} veces")

    if tipo == "une":
        campos(num, a, ["objeto", "grupos"])
        if a["objeto"] != "puntos":    # "puntos": marcos de diez, en vez de cosas
            comprobar_objeto(num, a["objeto"])
        grupos = a["grupos"]
        for g in grupos:
            comprobar_numero(num, g, semana, "uno de los grupos")
        if not 2 <= len(grupos) <= 4 or len(set(grupos)) != len(grupos) or max(grupos) > MAX_GRUPO:
            raise ErrorDeContenido(
                f"día {num}: 'une' lleva de 2 a 4 grupos, todos distintos y de "
                f"hasta {MAX_GRUPO} cosas ({grupos})"
            )
        if n not in grupos:
            raise ErrorDeContenido(f"día {num}: en 'une', uno de los grupos es el número del día ({n})")
        # Los números, desordenados: ninguno enfrente de su grupo. Los
        # baraja el número del día, así que siempre salen igual.
        rng, orden = random.Random(num), list(grupos)
        while any(o == g for o, g in zip(orden, grupos)):
            rng.shuffle(orden)
        return PLANTILLA_UNE.substitute(
            enunciado="Une cada grupo con su número.",
            instruccion=("Un adulto lee la pregunta. Cuenta cada grupo, y traza una "
                         "línea desde su punto hasta el punto de su número."),
            dibujo=dibujo_une(a["objeto"], grupos, orden),
        ), ("une", "de arriba abajo: " + ", ".join(str(g) for g in grupos))

    if tipo == "serie":
        campos(num, a, ["serie"])
        serie = a["serie"]
        huecos = [i for i, v in enumerate(serie) if v is None]
        dados = [(i, v) for i, v in enumerate(serie) if v is not None]
        if not 4 <= len(serie) <= 7 or not 1 <= len(huecos) <= 2 or len(dados) < 2:
            raise ErrorDeContenido(
                f"día {num}: 'serie' lleva de 4 a 7 números, y faltan 1 o 2 ({serie})"
            )
        # De uno en uno, hacia arriba o hacia atrás: lo dicen los que se ven.
        (i0, v0), (i1, v1) = dados[0], dados[1]
        paso = (v1 - v0) / (i1 - i0)
        completa = [v0 + paso * (i - i0) for i in range(len(serie))]
        if paso not in (1, -1) or any(serie[i] != completa[i] for i, _ in dados):
            raise ErrorDeContenido(
                f"día {num}: 'serie' va de uno en uno, hacia arriba o hacia atrás ({serie})"
            )
        completa = [int(v) for v in completa]
        for v in completa:
            if v < 0:
                raise ErrorDeContenido(f"día {num}: 'serie' no baja del 0 ({serie})")
            comprobar_numero(num, v, semana, "un número de la serie")
        if n not in completa:
            raise ErrorDeContenido(f"día {num}: la serie tiene que pasar por el número del día ({n})")
        faltan = [completa[i] for i in huecos]
        uno = len(faltan) == 1
        hacia = "" if paso == 1 else ", hacia atrás"
        return PLANTILLA_SERIE.substitute(
            enunciado="¿Qué número falta?" if uno else "¿Qué números faltan?",
            instruccion=(f"Un adulto lee la pregunta. Di los números del tren uno a uno{hacia}, "
                         + ("y escribe en el vagón vacío el que falta." if uno
                            else "y escribe en los vagones vacíos los que faltan.")),
            tren=dibujo_serie(serie),
        ), ("completa", ("falta el " if uno else "faltan el ")
            + " y el ".join(str(v) for v in faltan))

    if tipo in ("decena", "junta"):
        campos(num, a, ["objeto"] + (["grupos"] if tipo == "junta" else []))
        comprobar_objeto(num, a["objeto"])
        femenino = genero(a["objeto"]) == "f"
        plural = nombre_objeto(a["objeto"], 2)
        cuantas = "cuántas" if femenino else "cuántos"
        if tipo == "decena":
            # Diez y algo más: la bandeja llena y la otra.
            total = a.get("total", n)
            comprobar_numero(num, total, semana, "lo que se cuenta")
            if not 11 <= total <= 20:
                raise ErrorDeContenido(f"día {num}: 'decena' es diez y algo más, del 11 al 20 ({total})")
            grupos = [10, total - 10]
            enunciado = f"¿{cuantas.capitalize()} {plural} hay?"
            instruccion = (f"Un adulto lee la pregunta. En la bandeja llena hay 10: sigue contando "
                           f"desde el 10 {'las' if femenino else 'los'} de la otra, y escribe {cuantas} hay.")
        else:
            grupos = a["grupos"]
            if len(grupos) != 2 or min(grupos) < 1:
                raise ErrorDeContenido(f"día {num}: 'junta' junta dos grupos, de una cosa o más ({grupos})")
            for g in grupos:
                comprobar_numero(num, g, semana, "uno de los grupos")
            total = sum(grupos)
            if total > MAX_JUNTA:
                raise ErrorDeContenido(f"día {num}: 'junta' suma como mucho {MAX_JUNTA} ({grupos})")
            enunciado = f"¿{cuantas.capitalize()} {plural} hay en total?"
            instruccion = (f"Un adulto lee la pregunta. Junta los dos grupos: cuenta "
                           f"{'todas' if femenino else 'todos'}, y escribe {cuantas} son.")
        if total != n:
            raise ErrorDeContenido(f"día {num}: en '{tipo}', el total es el número del día ({n}), no {total}")
        dibujo, escala = dibujo_dos_grupos(a["objeto"], *grupos)
        return PLANTILLA_DOS_GRUPOS.substitute(
            caja="cajaDecena" if tipo == "decena" else "cajaJunta",
            enunciado=enunciado, instruccion=instruccion, escala=escala, dibujo=dibujo,
            a=grupos[0], b=grupos[1],
        ), (tipo, f"{grupos[0]} y {grupos[1]} son {total}")

    if tipo == "compara":
        que = a.get("que")
        if que not in ("mas", "menos", "igual"):
            raise ErrorDeContenido(f"día {num}: 'compara' busca 'mas', 'menos' o 'igual' ({que!r})")
        if "numeros" in a:
            # Solo números: el más grande o el más pequeño.
            numeros = a["numeros"]
            if que == "igual" or not 2 <= len(numeros) <= 3 or len(set(numeros)) != len(numeros):
                raise ErrorDeContenido(
                    f"día {num}: 'compara' con números lleva 2 o 3, distintos, y busca 'mas' o 'menos' ({numeros})"
                )
            for x in numeros:
                comprobar_numero(num, x, semana, "uno de los números")
            if n not in numeros:
                raise ErrorDeContenido(f"día {num}: en 'compara', uno de los números es el del día ({n})")
            elegido = max(numeros) if que == "mas" else min(numeros)
            return PLANTILLA_CAJA.substitute(
                caja="cajaCompara",
                enunciado=f"Rodea el número más {'grande' if que == 'mas' else 'pequeño'}.",
                instruccion=("Un adulto lee la pregunta. Si hace falta, contad juntos: "
                             "el más pequeño es el que se dice antes al contar."),
                dibujo=dibujo_numeros(numeros),
            ), ("compara", f"el {elegido}")
        campos(num, a, ["objeto", "grupos"])
        comprobar_objeto(num, a["objeto"])
        grupos = a["grupos"]
        for x in grupos:
            comprobar_numero(num, x, semana, "uno de los grupos")
        if n not in grupos:
            raise ErrorDeContenido(f"día {num}: en 'compara', uno de los grupos es el número del día ({n})")
        if min(grupos) < 1 or max(grupos) > MAX_GRUPO:
            raise ErrorDeContenido(f"día {num}: un grupo de 'compara' va de 1 a {MAX_GRUPO} cosas ({grupos})")
        femenino = genero(a["objeto"]) == "f"
        plural = nombre_objeto(a["objeto"], 2)
        if que == "igual":
            if len(grupos) != 3 or len(set(grupos)) != 2:
                raise ErrorDeContenido(f"día {num}: 'compara' con 'igual' lleva tres grupos, y dos iguales ({grupos})")
            igual = next(x for x in grupos if grupos.count(x) == 2)
            p1, p2 = [i + 1 for i, x in enumerate(grupos) if x == igual]
            enunciado = f"Rodea los dos grupos que tienen {'las mismas' if femenino else 'los mismos'} {plural}."
            clave = f"{ORDINALES[p1]} y {ORDINALES[p2]} ({igual} y {igual})"
        else:
            if not 2 <= len(grupos) <= 3 or len(set(grupos)) != len(grupos):
                raise ErrorDeContenido(f"día {num}: 'compara' lleva 2 o 3 grupos, distintos ({grupos})")
            elegido = max(grupos) if que == "mas" else min(grupos)
            enunciado = f"Rodea donde hay {'más' if que == 'mas' else 'menos'} {plural}."
            clave = f"{ORDINALES[grupos.index(elegido) + 1]} ({elegido} {nombre_objeto(a['objeto'], elegido)})"
        dibujo, escala = disponer(
            [grupo(a["objeto"], x, paso=2.2) for x in grupos],
            ancho_cm=15.0, alto_cm=10.0, hueco=1.6, maxima=0.7,
        )
        return PLANTILLA_CAJA.substitute(
            caja="cajaCompara", enunciado=enunciado,
            instruccion="Un adulto lee la pregunta. Cuenta cada grupo, y rodea con el lápiz el que dice.",
            dibujo=f"\\begin{{tikzpicture}}[objeto, scale={escala}]\n{dibujo}\n\\end{{tikzpicture}}",
        ), ("compara", clave)

    if tipo == "vecinos":
        numeros = a.get("numeros", [n])
        if not 1 <= len(numeros) <= 3 or len(set(numeros)) != len(numeros):
            raise ErrorDeContenido(f"día {num}: 'vecinos' lleva de 1 a 3 números, distintos ({numeros})")
        for x in numeros:
            if x < 1:
                raise ErrorDeContenido(f"día {num}: en 'vecinos', el 0 no tiene número de antes")
            for v in (x - 1, x, x + 1):
                comprobar_numero(num, v, semana, "un número de 'vecinos'")
        if n not in numeros:
            raise ErrorDeContenido(f"día {num}: en 'vecinos', uno de los números es el del día ({n})")
        uno = len(numeros) == 1
        return PLANTILLA_CAJA.substitute(
            caja="cajaVecinos",
            enunciado="¿Qué número va antes, y cuál va después?" if uno
            else "¿Qué números van antes, y cuáles van después?",
            instruccion=("Un adulto lee la pregunta. En la casa de la izquierda, escribe el "
                         "número de antes; en la de la derecha, el de después."),
            dibujo=dibujo_vecinos(numeros),
        ), ("vecinos", "; ".join(f"{x}: {x - 1} y {x + 1}" for x in numeros))

    if tipo == "recta":
        campos(num, a, ["desde", "hasta", "faltan"])
        desde, hasta, faltan = a["desde"], a["hasta"], a["faltan"]
        if not 4 <= hasta - desde <= 10:
            raise ErrorDeContenido(f"día {num}: 'recta' lleva de 5 a 11 números ({desde}-{hasta})")
        if (not 1 <= len(faltan) <= 3 or len(set(faltan)) != len(faltan)
                or any(not desde < f <= hasta for f in faltan)):
            raise ErrorDeContenido(
                f"día {num}: en 'recta' faltan de 1 a 3 números de la recta, y el primero se ve ({faltan})"
            )
        for v in range(desde, hasta + 1):
            comprobar_numero(num, v, semana, "un número de la recta")
        if not desde <= n <= hasta:
            raise ErrorDeContenido(f"día {num}: la recta tiene que pasar por el número del día ({n})")
        faltan = sorted(faltan)
        uno = len(faltan) == 1
        return PLANTILLA_CAJA.substitute(
            caja="cajaRecta",
            enunciado="¿Qué número falta en la recta?" if uno else "¿Qué números faltan en la recta?",
            instruccion=("Un adulto lee la pregunta. Di los números de la recta uno a uno, de "
                         "izquierda a derecha, y escribe en cada hueco el que falta."),
            dibujo=dibujo_recta(desde, hasta, faltan),
        ), ("recta", ("falta el " if uno else "faltan el ") + " y el ".join(str(v) for v in faltan))

    if tipo == "ordena":
        campos(num, a, ["numeros"])
        numeros, orden = a["numeros"], a.get("orden", "menor")
        if orden not in ("menor", "mayor"):
            raise ErrorDeContenido(f"día {num}: 'ordena' va de 'menor' a mayor, o de 'mayor' a menor ({orden!r})")
        if not 3 <= len(numeros) <= 5 or len(set(numeros)) != len(numeros):
            raise ErrorDeContenido(f"día {num}: 'ordena' lleva de 3 a 5 números, distintos ({numeros})")
        for x in numeros:
            comprobar_numero(num, x, semana, "uno de los números")
        if n not in numeros:
            raise ErrorDeContenido(f"día {num}: en 'ordena', uno de los números es el del día ({n})")
        ordenados = sorted(numeros, reverse=(orden == "mayor"))
        if numeros == ordenados:
            raise ErrorDeContenido(f"día {num}: en 'ordena', los números ya vienen en orden ({numeros})")
        de, a_ = ("pequeño", "grande") if orden == "menor" else ("grande", "pequeño")
        return PLANTILLA_CAJA.substitute(
            caja="cajaOrdena",
            enunciado=f"Ordena los números, del más {de} al más {a_}.",
            instruccion=(f"Un adulto lee la pregunta. Escribe abajo los números en orden, "
                         f"siguiendo las flechas: primero, el más {de}."),
            dibujo=dibujo_ordena(numeros),
        ), ("ordena", ", ".join(str(x) for x in ordenados))

    if tipo == "dibuja":
        campos(num, a, ["prompt"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "lo que se dibuja")
        if cuantas < 1:
            raise ErrorDeContenido(f"día {num}: 'dibuja' dibuja al menos una cosa")
        if not re.search(rf"\b({cuantas}|{'|'.join(formas(cuantas))})\b", a["prompt"].lower()):
            raise ErrorDeContenido(
                f"día {num}: el enunciado de 'dibuja' tiene que decir cuántas cosas se "
                f"dibujan ({cuantas}): «{a['prompt']}»"
            )
        return PLANTILLA_DIBUJA.substitute(enunciado=escapar(a["prompt"])), None

    if tipo == "repasa":
        campos(num, a, ["checklist", "prompt"])
        items = "\n".join(f"\\item {escapar(i)}" for i in a["checklist"])
        cartel = ""
        if num % 10 == 0:
            cartel = f"\\cartel{{\\lblPaginasHechas{{{num}}}}}"
        return PLANTILLA_REPASA.substitute(
            items=items, prompt=escapar(a["prompt"]), cartel=cartel
        ), None

    raise ErrorDeContenido(f"día {num}: tipo de actividad desconocido: {tipo!r}")


# --------------------------------------------------------------------
# Cargar y validar
# --------------------------------------------------------------------
def cargar_dias():
    dias = []
    for ruta in sorted(CONTENT_DIR.glob("q*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        dias += datos["dias"]
    return sorted(dias, key=lambda d: d["dia"])


def validar_dias(dias):
    total = DIAS_ESCRITOS or TOTAL_DIAS
    numeros = [d["dia"] for d in dias]
    if numeros != list(range(1, total + 1)):
        raise ErrorDeContenido(
            f"tienen que estar los días del 1 al {total}, sin huecos ni repetidos"
            + (" (en obras: DIAS_ESCRITOS)" if DIAS_ESCRITOS else "")
        )
    for d in dias:
        num = d["dia"]
        semana = (num - 1) // DIAS_POR_SEMANA + 1
        if d.get("semana") != semana:
            raise ErrorDeContenido(f"día {num}: es de la semana {semana}, no {d.get('semana')}")
        if d.get("tema") != TEMAS[semana - 1]:
            raise ErrorDeContenido(
                f"día {num}: el tema de la semana {semana} es «{TEMAS[semana - 1]}», "
                f"no «{d.get('tema')}»"
            )
        for c in ("numero", "objeto", "frase", "actividad"):
            if c not in d:
                raise ErrorDeContenido(f"día {num}: falta '{c}'")
        n = d["numero"]
        comprobar_numero(num, n, semana, "el número del día")
        comprobar_objeto(num, d["objeto"])
        if n == 0 and d["objeto"] not in CONTENEDORES:
            raise ErrorDeContenido(
                f"día {num}: el día del 0, «El número de hoy» dibuja un recipiente "
                f"vacío (uno de {sorted(CONTENEDORES)}), no «{d['objeto']}»"
            )
        if not any(re.search(rf"\b{re.escape(f)}\b", d["frase"].lower()) for f in formas(n)):
            raise ErrorDeContenido(
                f"día {num}: la frase tiene que decir el número del día "
                f"({' / '.join(sorted(formas(n)))}): «{d['frase']}»"
            )
        # En una semana con números nuevos, el día que llega uno se traza
        # (el lunes, el primero; el miércoles, el segundo), y el número del
        # día es el último que ha llegado -- el viernes, cualquiera de los
        # de la semana. El viernes, además, se repasa.
        nuevos = ESCALERA.get(semana, [])
        dia_semana = (num - 1) % DIAS_POR_SEMANA
        tipo = d["actividad"].get("tipo")
        if nuevos:
            llegados = [x for i, x in enumerate(nuevos) if LLEGADA[i] <= dia_semana]
            if dia_semana == DIAS_POR_SEMANA - 1:
                if n not in nuevos:
                    raise ErrorDeContenido(
                        f"día {num}: el número del viernes es uno de los de la semana {semana} "
                        f"({' o '.join(map(str, nuevos))}), no el {n}"
                    )
            elif n != llegados[-1]:
                raise ErrorDeContenido(
                    f"día {num}: el número de este día de la semana {semana} es el "
                    f"{llegados[-1]}, no el {n}"
                )
            for i, x in enumerate(nuevos):
                if dia_semana == LLEGADA[i] and (tipo != "traza" or d["actividad"].get("numero", n) != x):
                    raise ErrorDeContenido(
                        f"día {num}: el {DIAS_SEMANA[LLEGADA[i]]} que llega el {x}, se traza el {x}"
                    )
        if (dia_semana == DIAS_POR_SEMANA - 1) != (tipo == "repasa"):
            raise ErrorDeContenido(
                f"día {num}: 'repasa' es la actividad de los viernes, y solo de los viernes"
            )


# --------------------------------------------------------------------
# Generar
# --------------------------------------------------------------------
CABECERA = (
    "% {nombre}\n"
    "% GENERADO por tools/gen_numeros.py a partir de content/q*.json.\n"
    "% NO EDITAR A MANO -- los cambios se perderán en la siguiente\n"
    "% ejecución de `make generate`. Edita content/q*.json en su lugar.\n\n"
)


def generar(dias):
    piezas = [CABECERA.format(nombre="content/generated-days.tex")]
    claves = [CABECERA.format(nombre="content/generated-clave.tex")]
    for d in dias:
        num, semana = d["dia"], d["semana"]
        trimestre = trimestre_de(semana)
        n = d["numero"]
        actividad, clave = render_actividad(d)
        # Las cosas del número de hoy, tantas como el número -- el 0 es el
        # recipiente vacío --, en el sitio que deja el número (el 10 ocupa
        # más que una cifra: ver \numeroDeHoy).
        ancho = 7.2 if n < 10 else 6.4
        escala = escala_para(max(n, 1), ancho, 2.4, 0.85)
        if n > 10:
            # Del 11 al 20, no más altas que los dos marcos de diez.
            filas = -(-n // 5)
            escala = min(escala, round(4.4 / ((filas - 1 + SEPARACION_DECENA) * 2.4 + 2), 3))
        cosas = fila(d["objeto"], max(n, 1), escala=escala, paso=2.4)
        piezas.append(PLANTILLA_DIA.substitute(
            dia=num, semana=semana, trimestre=trimestre,
            tema=escapar(d["tema"]),
            numero=n, nombre=NOMBRES[n],
            cosas=cosas,
            frase=escapar(d["frase"]),
            actividad=actividad,
        ))
        if clave:
            etiqueta, texto = clave
            claves.append(f"\\claveEntrada{{{num}}}{{\\lbl{etiqueta.capitalize()}}}{{{escapar(texto)}}}\n")
        if num == ULTIMO_DIA_TRIMESTRE.get(trimestre) and trimestre in NOMBRE_MEDALLA:
            piezas.append(PLANTILLA_MEDALLA.substitute(dia=num, estacion=NOMBRE_MEDALLA[trimestre]))
    return "\n".join(piezas), "".join(claves)


def comprobar_totaldias():
    """lang/es.tex promete los mismos 260 días que este script."""
    m = re.search(r"\\newcommand\{\\totaldias\}\{(\d+)\}", LANG_FILE.read_text(encoding="utf-8"))
    if not m or int(m.group(1)) != TOTAL_DIAS:
        raise ErrorDeContenido(f"\\totaldias en lang/es.tex tiene que ser {TOTAL_DIAS}")


def main():
    check_only = "--check" in sys.argv
    try:
        comprobar_totaldias()
        dias = cargar_dias()
        validar_dias(dias)
        tex, clave = generar(dias)
    except ErrorDeContenido as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    salidas = [(SALIDA_DIAS, tex), (SALIDA_CLAVE, clave)]
    if check_only:
        for ruta, contenido in salidas:
            actual = ruta.read_text(encoding="utf-8") if ruta.exists() else None
            if actual != contenido:
                print(
                    f"DESACTUALIZADO: {ruta.relative_to(ROOT)} no coincide con "
                    "content/q*.json -- ejecuta `make generate`.",
                    file=sys.stderr,
                )
                return 1
        obras = f" (en obras: {len(dias)} de {TOTAL_DIAS} días escritos)" if DIAS_ESCRITOS else ""
        print(f"OK: {len(dias)} días validados{obras}, generated-days.tex y generated-clave.tex al día.")
        return 0

    for ruta, contenido in salidas:
        ruta.write_text(contenido, encoding="utf-8")
    print(f"Escrito {SALIDA_DIAS.relative_to(ROOT)} con {len(dias)} días, y {SALIDA_CLAVE.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
