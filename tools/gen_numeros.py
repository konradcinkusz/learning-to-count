#!/usr/bin/env python3
"""Genera "Aprendo los números" (main.tex) a partir de content/q*.json:
content/generated-days.tex (una página por día) y
content/generated-clave.tex (la clave de respuestas); y el mismo cuaderno
en otras lenguas, página a página: "First Numbers" (english.tex), en
inglés, en content/english/, y "Poznaję liczby" (polish.tex), en polaco,
en content/polish/ (los mismos dos ficheros).

Las traducciones no tienen días propios: cada uno es el de "Aprendo los
números" -- el mismo número, las mismas cosas, la misma actividad --, con
la frase, el tema y los textos de su actividad en su lengua, que están en
content/<lengua>/q*.json (cargar_traduccion, más abajo). Todo lo que se
escribe en la página en una lengua o en otra sale de tools/idiomas.py, y
las comprobaciones son las mismas para todos los cuadernos.

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

No editar content/generated-*.tex, content/english/generated-*.tex ni
content/polish/generated-*.tex a mano -- se sobrescriben cada vez que se
ejecuta este script.

Uso:
    python3 tools/gen_numeros.py            # regenera los tres cuadernos
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

from idiomas import ESPANOL, INGLES, POLACO

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
TRAZO_FILE = CONTENT_DIR / "numeros-trazo.json"

# --------------------------------------------------------------------
# El calendario
# --------------------------------------------------------------------
TOTAL_DIAS = 260
DIAS_POR_SEMANA = 5
SEMANAS_POR_TRIMESTRE = 13
# Mientras el cuaderno se escribe por partes (un PR por trimestre, cada
# uno en verde antes de fusionarse), cuántos días tiene ya escritos: se
# exigen exactamente esos, del 1 en adelante y sin huecos. None = el
# cuaderno está entero, con sus 260 días. DIAS_ESCRITOS_INGLES y
# DIAS_ESCRITOS_POLACO, lo mismo para "First Numbers" y "Poznaję
# liczby", que se escriben también por partes: sus días son los primeros
# de "Aprendo los números".
DIAS_ESCRITOS = None
DIAS_ESCRITOS_INGLES = None
DIAS_ESCRITOS_POLACO = 195


# Los cuadernos: su lengua, dónde están sus textos (y lo que generan), el
# fichero de sus cadenas de texto (que promete los mismos 260 días que
# este script) y cuántos días tienen escritos.
class Cuaderno:
    def __init__(self, nombre, lengua, carpeta, lang, escritos, constante):
        self.nombre, self.lengua, self.carpeta = nombre, lengua, carpeta
        self.escritos, self.constante = escritos, constante
        self.salida_dias = carpeta / "generated-days.tex"
        self.salida_clave = carpeta / "generated-clave.tex"
        self.lang = ROOT / "lang" / lang


APRENDO = Cuaderno("Aprendo los números", ESPANOL, CONTENT_DIR, "es.tex", DIAS_ESCRITOS, "DIAS_ESCRITOS")
# Las traducciones de "Aprendo los números", página a página.
TRADUCCIONES = (
    Cuaderno("First Numbers", INGLES, CONTENT_DIR / "english", "en.tex",
             DIAS_ESCRITOS_INGLES, "DIAS_ESCRITOS_INGLES"),
    Cuaderno("Poznaję liczby", POLACO, CONTENT_DIR / "polish", "pl.tex",
             DIAS_ESCRITOS_POLACO, "DIAS_ESCRITOS_POLACO"),
)
LENGUAS = (ESPANOL, INGLES, POLACO)

ULTIMO_DIA_TRIMESTRE = {1: 65, 2: 130, 3: 195, 4: 260}

# Los temas de cada semana y el nombre de cada medalla están en
# tools/idiomas.py, en todas las lenguas.
for _lengua in LENGUAS:
    assert len(_lengua.temas) == TOTAL_DIAS // DIAS_POR_SEMANA

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
    # Primavera: sumar, partir y restar hasta 10, sin números nuevos; y
    # después, de 10 en 10 hasta el 50 (las decenas), y cada semana, una
    # decena entera: los veinti-, los treinta y..., los cuarenta y...
    35: [30, 40, 50],
    36: list(range(21, 30)), 37: list(range(31, 40)), 38: list(range(41, 50)),
    # Verano: de 10 en 10 hasta el 100, y después, de dos decenas en dos
    # (del 51 al 69) y de tres en tres (del 71 al 99): ya se sabe cómo son.
    40: [60, 70, 80, 90, 100],
    41: list(range(51, 60)) + list(range(61, 70)),
    42: list(range(71, 80)) + list(range(81, 90)) + list(range(91, 100)),
}
# El día de la semana (0 = lunes) en que llega cada número nuevo: el
# primero, el lunes; el segundo, si lo hay, el miércoles. Hasta ese día,
# el número todavía no ha llegado. Una semana con más números nuevos que
# días de LLEGADA (una decena entera) los recibe todos el lunes.
LLEGADA = [0, 2]


def dia_de_llegada(nuevos, i):
    return LLEGADA[i] if len(nuevos) <= len(LLEGADA) else 0
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
    # Las de la primavera.
    "suma": 27,     # ya con los signos: 3 + 2 = [ ]
    "parte": 28,    # partir un número en dos: 5 son 2 y [ ]
    "diez": 29,     # las parejas que suman 10: 7 + [ ] = 10
    "resta": 30,    # quitar: 5 - 2 = [ ]
    "problema": 31, # un problema que lee el adulto
    "bloques": 36,  # decenas y unidades: 2 decenas y 3 unidades son 23
    # Solo en "First Numbers": cuando llegan las decenas, cada una con el
    # número de su "-teen" (thirTEEN, THIRty), que suenan casi igual.
    "nombres": 35,
    # Las del verano.
    "tabla": 42,    # la tabla del 100
    "dinero": 46,   # euros: monedas de 1 y 2, billetes de 5, 10 y 20
    "hora": 48,     # en punto (y, desde la semana 49, y media: MEDIA_DESDE)
    "mide": 50,     # cuántos cubitos mide, y cuál es más largo
}

# Lo que se cuenta de 2 en 2 o de 5 en 5 en "Cuenta" ("de"): las ruedas
# de las bicis y los dedos de las manos (cómo se llaman, en
# tools/idiomas.py).
CONTAR_DE = {"bici": 2, "mano": 5}

# De cuánto en cuánto pueden ir "Completa" (el tren) y "La recta", y desde
# qué semana: de uno en uno, siempre; de 2 en 2 (las ruedas de la bici),
# de 5 en 5 (los dedos de la mano) y de 10 en 10, en primavera.
PASOS_DESDE = {1: 1, 2: 32, 5: 33, 10: 35}

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
    return previos | {n for i, n in enumerate(nuevos) if dia_de_llegada(nuevos, i) <= dia_semana}


def trimestre_de(semana):
    return (semana - 1) // SEMANAS_POR_TRIMESTRE + 1


# --------------------------------------------------------------------
# Las cosas que se cuentan (diagrams/objetos.tex)
# --------------------------------------------------------------------
# El dibujo de cada una. Cómo se llaman, en singular y en plural (y, en
# español, su género, para "Colorea 1 manzana.", "¿Cuántos huesos
# hay?"), está en tools/idiomas.py: todas tienen nombre en las dos
# lenguas.
OBJETOS = {
    "manzana": r"\objManzana", "pelota": r"\objPelota", "hueso": r"\objHueso",
    "sol": r"\objSol", "huella": r"\objHuella", "toby": r"\objToby",
    "globo": r"\objGlobo", "estrella": r"\objEstrella", "hoja": r"\objHoja",
    "corazon": r"\objCorazon", "caramelo": r"\objCaramelo", "pez": r"\objPez",
    "lapiz": r"\objLapiz", "libro": r"\objLibro", "galleta": r"\objGalleta",
    "seta": r"\objSeta", "castana": r"\objCastana", "cesta": r"\objCesta",
    "vela": r"\objVela", "regalo": r"\objRegalo", "arana": r"\objArana",
    "paraguas": r"\objParaguas", "bola": r"\objBola", "arbol": r"\objArbol",
    "pato": r"\objPato", "coche": r"\objCoche", "trex": r"\objTrex",
    "mariposa": r"\objMariposa", "gota": r"\objGota", "nube": r"\objNube",
    "huevo": r"\objHuevo", "pajaro": r"\objPajaro", "gato": r"\objGato",
    "mochila": r"\objMochila", "ardilla": r"\objArdilla", "plato": r"\objPlato",
    "mandarina": r"\objMandarina", "copo": r"\objCopo", "muneco": r"\objMuneco",
    "gorrofiesta": r"\objGorroFiesta", "nota": r"\objNota", "osito": r"\objOsito",
    "flor": r"\objFlor", "corona": r"\objCorona", "cometa": r"\objCometa",
    "alubia": r"\objAlubia", "boton": r"\objBoton", "tronco": r"\objTronco",
    "fresa": r"\objFresa", "piruleta": r"\objPiruleta", "paloma": r"\objPaloma",
    "ovillo": r"\objOvillo", "bufanda": r"\objBufanda", "gorro": r"\objGorro",
    "maceta": r"\objMaceta", "brote": r"\objBrote", "pipa": r"\objPipa",
    "rueda": r"\objRueda", "bici": r"\objBici", "oruga": r"\objOruga",
    "gafas": r"\objGafas", "arbusto": r"\objArbusto", "tarta": r"\objTarta",
    "rosa": r"\objRosa", "abeja": r"\objAbeja", "pollito": r"\objPollito",
    "diente": r"\objDiente", "moneda": r"\objMoneda", "mano": r"\objMano",
    "torrija": r"\objTorrija", "zanahoria": r"\objZanahoria", "tomate": r"\objTomate",
    "regadera": r"\objRegadera", "tarjeta": r"\objTarjeta", "pan": r"\objPan",
    "rayo": r"\objRayo", "lechuga": r"\objLechuga", "maleta": r"\objMaleta",
    "helado": r"\objHelado", "concha": r"\objConcha", "cubo": r"\objCubo",
    "churro": r"\objChurro", "caracol": r"\objCaracol", "reloj": r"\objReloj",
}
for _lengua in LENGUAS:
    assert set(_lengua.objetos) == set(OBJETOS), set(_lengua.objetos) ^ set(OBJETOS)
    assert set(_lengua.contar_de) == set(CONTAR_DE)

# Lo que se dibuja vacío en "El número de hoy" el día que el número es el
# 0: la cesta en la que no queda ninguna castaña, el plato en el que no
# queda nada.
CONTENEDORES = {"cesta", "plato"}


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
    macro = OBJETOS[objeto]
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
    macro = OBJETOS[objeto]
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

# "Diez y más", "Junta", "Suma", "Resta", "Parte", "Diez", "Bloques" y
# "Problema": el dibujo y, debajo, lo que se completa ("10 y 3 son [ ]",
# "5 − 2 = [ ]"): \huecoRespuesta es el hueco.
PLANTILLA_CON_RESPUESTA = Template(r"""\begin{$caja}[centrado abajo]
\enunciado{$enunciado}
\instruccion{$instruccion}
\tcblower
\begin{center}
$dibujo

\vspace{12mm}
{\fontsize{40}{44}\selectfont\bfseries $respuesta}
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

# La página de medalla del final de cada trimestre (T1-T3) está en
# tools/idiomas.py (plantilla_medalla), en todas las lenguas.

# Las formas que acompañan a los números en "busca": se ven distintas a
# primera vista, así que lo que hay que mirar son los números. La
# primera es el círculo, que el día que se busca el 0 no sale.
FORMAS_BUSCA = [
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt] (0,0) circle (3.8mm);",
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt, line join=round] (-4mm,-3.4mm) -- (4mm,-3.4mm) -- (0,3.8mm) -- cycle;",
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt] (-3.4mm,-3.4mm) rectangle (3.4mm,3.4mm);",
]

# "Une":los grupos a la izquierda, uno debajo de otro, cada uno con un
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


# "Number names" (solo en "First Numbers"): los números a la izquierda,
# uno debajo de otro, cada uno con su punto; sus nombres a la derecha,
# desordenados, cada uno con el suyo -- de punto a punto se traza la
# línea, como en "Une". En cm.
FUENTE_NOMBRE = r"\fontsize{24}{24}\selectfont\bfseries"
ALTO_FILA_NOMBRES_CM = 1.85
HUECO_NOMBRES_CM = 4.6


def dibujo_nombres(numeros, orden, L):
    piezas = []
    x_punto = 2.6
    x_nombre = x_punto + HUECO_NOMBRES_CM
    for i, (numero, nombre) in enumerate(zip(numeros, orden)):
        y = -i * ALTO_FILA_NOMBRES_CM
        piezas.append(
            f"\\node[anchor=east, font={FUENTE_NUMERO}] at ({x_punto - 0.4:.2f},{y:.2f}) {{{numero}}};"
            f"\\fill ({x_punto:.2f},{y:.2f}) circle (1.3mm);"
            f"\\fill ({x_nombre:.2f},{y:.2f}) circle (1.3mm);"
            f"\\node[anchor=west, font={FUENTE_NOMBRE}] at ({x_nombre + 0.3:.2f},{y:.2f}) {{{L.nombres[nombre]}}};"
        )
    return "\\begin{tikzpicture}[objeto]\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


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
    if any(v is not None and v >= 100 for v in valores):
        tam = min(tam, 28)
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


def tikz(dibujo, escala):
    return f"\\begin{{tikzpicture}}[objeto, scale={escala}]\n{dibujo}\n\\end{{tikzpicture}}"


def dibujo_dos_grupos(objeto, a, b, signo):
    """Dos grupos, uno al lado del otro, con una "y" en medio ("Diez y
    más", "Junta") -- o un "+" ("Suma"): (tikz, escala). Un "and", con
    sus tres letras, más pequeño y con más sitio."""
    ga, gb = grupo(objeto, a), grupo(objeto, b)
    hueco, fuente = (3.0, FUENTE_NUMERO) if len(signo) == 1 else (4.4, FUENTE_SIGNO_LARGO)
    ancho = ga[1] + hueco + gb[1]
    escala = round(min(0.75, 14.0 / ancho, 7.0 / max(ga[2], gb[2])), 3)
    xa, xb = -ancho / 2 + ga[1] / 2, ancho / 2 - gb[1] / 2
    return (
        f"\\begin{{scope}}[shift={{({xa:.2f},0)}}]{ga[0]}\\end{{scope}}"
        f"\\begin{{scope}}[shift={{({xb:.2f},0)}}]{gb[0]}\\end{{scope}}"
        f"\\node[font={fuente}] at ({-ancho / 2 + ga[1] + hueco / 2:.2f},0) {{{signo}}};"
    ), escala


FUENTE_SIGNO_LARGO = r"\fontsize{26}{26}\selectfont\bfseries"


def dibujo_partido(objeto, total, parte):
    """"Parte": las cosas en una fila, y una raya a trazos que la parte en
    dos, después de las `parte` primeras: (tikz, escala)."""
    macro, paso = OBJETOS[objeto], 2.4
    ancho = (total - 1) * paso + 2 + 2 * MARGEN_GRUPO + 0.8
    x0 = -(total - 1) * paso / 2
    piezas = [marco(ancho, 2 + 2 * MARGEN_GRUPO + 0.4)]
    piezas += [_cosa(macro, x0 + i * paso + (0.8 if i >= parte else 0) - 0.4, 0) for i in range(total)]
    xr = x0 + (parte - 0.5) * paso
    piezas.append(f"\\draw[dashed, line width=1.4pt] ({xr:.2f},-1.6) -- ({xr:.2f},1.6);")
    return "".join(piezas), round(min(0.8, 14.5 / ancho), 3)


def dibujo_diez(puntos):
    """"Diez": un marco de diez grande, con sus puntos, para dibujar los
    que faltan. En cm."""
    celda = 2.2
    piezas = []
    for i in range(10):
        x, y = (i % 5) * celda, (0 if i < 5 else -celda)
        piezas.append(f"\\filldraw[fill=white, line width=1.4pt] ({x:.2f},{y:.2f}) rectangle ++({celda},{celda});")
        if i < puntos:
            piezas.append(f"\\fill[colorLectura] ({x + celda / 2:.2f},{y + celda / 2:.2f}) circle ({0.34 * celda:.2f});")
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_bloques(numero, celda):
    """Las decenas y las unidades: una barra de diez cubitos por decena, y
    los cubitos sueltos al lado, en columnas de cinco. En cm, centrado."""
    decenas, unidades = divmod(numero, 10)
    sep = celda * 0.7
    piezas = []
    for d in range(decenas):
        x = d * (celda + sep)
        for i in range(10):
            piezas.append(f"\\filldraw[fill=white] ({x:.2f},{i * celda:.2f}) rectangle ++({celda:.2f},{celda:.2f});")
    x0 = decenas * (celda + sep) + (sep if decenas else 0)
    for u in range(unidades):
        x = x0 + (u // 5) * (celda + sep * 0.5)
        piezas.append(f"\\filldraw[fill=white] ({x:.2f},{(u % 5) * celda:.2f}) rectangle ++({celda:.2f},{celda:.2f});")
    return ("\\begin{tikzpicture}[line width=0.9pt, baseline=(current bounding box.center)]"
            + "".join(piezas) + "\\end{tikzpicture}")


def dibujo_vecinos(numeros, L):
    """Una fila de tres casas por número: en la de en medio vive el
    número; la de la izquierda, la de antes, y la de la derecha, la de
    después, se quedan vacías para escribir. En cm."""
    ancho, alto, tejado, sep, hueco = 2.6, 2.2, 1.1, 3.5, 0.9
    s = round(min(1.0, 11.0 / (len(numeros) * (alto + tejado + hueco))), 3)
    piezas = [
        f"\\node[font=\\small, text=colorGris] at ({-sep:.2f},{alto + tejado + 0.45:.2f}) {{{L.antes}}};",
        f"\\node[font=\\small, text=colorGris] at ({sep:.2f},{alto + tejado + 0.45:.2f}) {{{L.despues}}};",
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


def dibujo_recta(marcas, faltan):
    """La recta numérica: una raya por cada número de `marcas`, y debajo
    el número -- o, si falta, un hueco para escribirlo. En cm."""
    # Con pocas marcas (de 5 en 5, de 10 en 10), más separadas.
    paso = min(1.6 if len(marcas) > 9 else 2.4, 13.2 / (len(marcas) - 1))
    largo = (len(marcas) - 1) * paso
    # Con dos números de dos cifras seguidos, más pequeños: si no, se tocan.
    tam = 22 if sum(v >= 10 for v in marcas) >= 2 else 28
    fuente = f"\\fontsize{{{tam}}}{{{tam}}}\\selectfont\\bfseries"
    medio = min(0.62, (paso - 0.2) / 2)    # medio hueco
    piezas = [f"\\draw[-{{Stealth[length=3mm]}}, line width=1.4pt] (-0.5,0) -- ({largo + 0.8:.2f},0);"]
    for i, v in enumerate(marcas):
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


def comprobar_paso(dia, semana, paso, que):
    if semana < PASOS_DESDE[paso]:
        raise ErrorDeContenido(
            f"día {dia}: '{que}' de {paso} en {paso} no llega hasta la semana "
            f"{PASOS_DESDE[paso]} (ver PASOS_DESDE)"
        )


def comprobar_objeto(dia, objeto):
    if objeto not in OBJETOS:
        raise ErrorDeContenido(
            f"día {dia}: no hay dibujo para «{objeto}» (ver OBJETOS y "
            "diagrams/objetos.tex)"
        )


# Las cuentas de la primavera, con sus signos: cada día, el resultado es
# el número del día. En primavera, hasta 10 (MAX_CUENTA).
MAX_CUENTA = {3: 10, 4: 20}
SIGNOS = {"+": "+", "-": "−"}      # el menos de verdad (U+2212), el de Andika


def render_cuenta(d, tipo, num, semana, a, n, L):
    """(tex, clave) de "Suma", "Resta", "Parte", "Diez", "Problema" y
    "Bloques"."""
    maximo = MAX_CUENTA.get(trimestre_de(semana), 10)

    def hasta(total, que):
        if total > maximo:
            raise ErrorDeContenido(f"día {num}: '{tipo}' llega como mucho a {maximo} este trimestre ({que})")
        if total != n:
            raise ErrorDeContenido(f"día {num}: en '{tipo}', el resultado es el número del día ({n}), no {total}")

    if tipo == "suma":
        campos(num, a, ["objeto", "grupos"])
        comprobar_objeto(num, a["objeto"])
        grupos = a["grupos"]
        if len(grupos) != 2 or min(grupos) < 0 or max(grupos) < 1:
            raise ErrorDeContenido(f"día {num}: 'suma' suma dos grupos ({grupos})")
        for g in grupos:
            comprobar_numero(num, g, semana, "uno de los sumandos")
        total = sum(grupos)
        hasta(total, f"{grupos[0]} + {grupos[1]}")
        enunciado, instruccion = L.suma(a["objeto"])
        dibujo, escala = dibujo_dos_grupos(a["objeto"], *grupos, signo="+")
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaSuma", enunciado=enunciado, instruccion=instruccion,
            dibujo=tikz(dibujo, escala),
            respuesta=f"{grupos[0]} + {grupos[1]} = \\huecoRespuesta",
        ), ("suma", f"{grupos[0]} + {grupos[1]} = {total}")

    if tipo == "resta":
        campos(num, a, ["objeto", "total", "quita"])
        comprobar_objeto(num, a["objeto"])
        total, quita = a["total"], a["quita"]
        if not 1 <= quita <= total:
            raise ErrorDeContenido(f"día {num}: 'resta' quita de 1 al total ({total} − {quita})")
        for v in (total, quita):
            comprobar_numero(num, v, semana, "un número de la resta")
        if total > maximo:
            raise ErrorDeContenido(f"día {num}: 'resta' empieza como mucho en {maximo} este trimestre ({total})")
        hasta(total - quita, f"{total} − {quita}")
        enunciado, instruccion = L.resta(quita, a["objeto"])
        dibujo, ancho, alto = grupo(a["objeto"], total)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaResta", enunciado=enunciado, instruccion=instruccion,
            dibujo=tikz(dibujo, round(min(0.9, 13.0 / ancho, 7.0 / alto), 3)),
            respuesta=f"{total} {SIGNOS['-']} {quita} = \\huecoRespuesta",
        ), ("resta", f"{total} {SIGNOS['-']} {quita} = {total - quita}")

    if tipo == "parte":
        campos(num, a, ["objeto", "parte"])
        comprobar_objeto(num, a["objeto"])
        total, parte = a.get("total", n), a["parte"]
        if not 1 <= parte < total or total > maximo:
            raise ErrorDeContenido(
                f"día {num}: 'parte' parte de 2 a {maximo} cosas en dos grupos, de una o más ({total}, {parte})")
        for v in (total, parte, total - parte):
            comprobar_numero(num, v, semana, "un número de 'parte'")
        if total != n:
            raise ErrorDeContenido(f"día {num}: en 'parte', lo que se parte es el número del día ({n})")
        enunciado, instruccion, respuesta, clave = L.parte(total, parte, a["objeto"])
        dibujo, escala = dibujo_partido(a["objeto"], total, parte)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaParte", enunciado=enunciado, instruccion=instruccion,
            dibujo=tikz(dibujo, escala), respuesta=respuesta,
        ), ("parte", clave)

    if tipo == "diez":
        campos(num, a, ["puntos"])
        puntos = a["puntos"]
        if not 1 <= puntos <= 9:
            raise ErrorDeContenido(f"día {num}: en 'diez', el marco tiene de 1 a 9 puntos ({puntos})")
        if 10 - puntos != n:
            raise ErrorDeContenido(f"día {num}: en 'diez', lo que falta es el número del día ({n}), no {10 - puntos}")
        enunciado, instruccion = L.diez()
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaDiez", enunciado=enunciado, instruccion=instruccion,
            dibujo=dibujo_diez(puntos),
            respuesta=f"{puntos} + \\huecoRespuesta\\ = 10",
        ), ("diez", f"{puntos} + {10 - puntos} = 10")

    if tipo == "problema":
        campos(num, a, ["texto", "operacion"])
        x, signo, y = a["operacion"]
        if signo not in SIGNOS:
            raise ErrorDeContenido(f"día {num}: en 'problema', la cuenta es una suma o una resta ({signo!r})")
        resultado = x + y if signo == "+" else x - y
        if resultado < 0:
            raise ErrorDeContenido(f"día {num}: en 'problema', la resta no baja del 0 ({x} − {y})")
        for v in (x, y, resultado):
            comprobar_numero(num, v, semana, "un número del problema")
        hasta(resultado, f"{x} {SIGNOS[signo]} {y}")
        for v in (x, y):
            if not L.en_texto(a["texto"], v):
                raise ErrorDeContenido(f"día {num}: el problema tiene que decir el {v}: «{a['texto']}»")
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaProblema",
            enunciado=escapar(a["texto"]),
            instruccion=L.problema(),
            dibujo=r"\tikz\draw[dashed, line width=0.8pt, rounded corners=4mm, colorGris] (0,0) rectangle (13,5.5);",
            respuesta=f"\\huecoRespuesta\\ {SIGNOS[signo]} \\huecoRespuesta\\ = \\huecoRespuesta",
        ), ("problema", f"{x} {SIGNOS[signo]} {y} = {resultado}")

    # "bloques": decenas y unidades.
    numero = a.get("numero", n)
    comprobar_numero(num, numero, semana, "el número de los bloques")
    if not 11 <= numero <= 100 or numero != n:
        raise ErrorDeContenido(
            f"día {num}: 'bloques' es un número de 11 en adelante, el del día ({n}), no {numero}")
    enunciado, instruccion, respuesta, clave = L.bloques(numero)
    return PLANTILLA_CON_RESPUESTA.substitute(
        caja="cajaBloques", enunciado=enunciado, instruccion=instruccion,
        dibujo=dibujo_bloques(numero, 0.55), respuesta=respuesta,
    ), ("bloques", clave)


# Las actividades del verano: la tabla del 100, el dinero, la hora y medir.
VALORES_DINERO = (1, 2, 5, 10, 20)      # euros: monedas de 1 y 2, billetes de 5, 10 y 20
MAX_DINERO = 20
MEDIA_DESDE = 49                        # "y media", desde la semana 49
MAX_MIDE = 14                           # los cubitos de la regla


def dibujo_tabla(desde, faltan):
    """Media tabla del 100: cinco filas de diez, desde `desde` (1, 11,
    21...), con las casillas de `faltan` vacías. En cm."""
    celda = 1.4
    piezas = []
    for i in range(50):
        v = desde + i
        x, y = (i % 10) * celda, -(i // 10) * celda
        piezas.append(f"\\draw[line width=0.9pt] ({x:.2f},{y:.2f}) rectangle ++({celda},{celda});")
        if v not in faltan:
            piezas.append(f"\\node[font=\\fontsize{{17}}{{17}}\\selectfont\\bfseries] at "
                          f"({x + celda / 2:.2f},{y + celda / 2:.2f}) {{{v}}};")
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_dinero(valores):
    """Los billetes, primero, y después las monedas, en fila (en dos si no
    caben). En cm."""
    piezas, x, y = [], 0.0, 0.0
    orden = sorted(valores, reverse=True)
    anchos = [3.6 if v >= 5 else 2.2 for v in orden]
    filas, fila, ancho_fila = [], [], 0.0
    for v, w in zip(orden, anchos):
        if fila and ancho_fila + w > 14.5:
            filas.append(fila); fila, ancho_fila = [], 0.0
        fila.append((v, w)); ancho_fila += w
    filas.append(fila)
    for f, fila in enumerate(filas):
        total = sum(w for _, w in fila)
        x = -total / 2
        for v, w in fila:
            macro = f"\\billete{{{v}}}" if v >= 5 else f"\\monedaEuro{{{v}}}"
            piezas.append(f"\\begin{{scope}}[shift={{({x + w / 2:.2f},{-f * 2.3:.2f})}}]{macro}\\end{{scope}}")
            x += w
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def dibujo_mide(largos):
    """"Mide": un lápiz por cada largo, encima de su regla de cubitos. En cm."""
    piezas = []
    for i, largo in enumerate(largos):
        y = -i * 3.4
        piezas.append(f"\\begin{{scope}}[shift={{(0,{y:.2f})}}]\\reglaCubitos{{{MAX_MIDE}}}\\end{{scope}}")
        piezas.append(f"\\begin{{scope}}[shift={{(0,{y + 1.65:.2f})}}, yscale=1.4]\\lapizLargo{{{largo}}}\\end{{scope}}")
    return "\\begin{tikzpicture}\n" + "\n".join(piezas) + "\n\\end{tikzpicture}"


def render_verano(d, tipo, num, semana, a, n, L):
    """(tex, clave) de "La tabla del 100", "El dinero", "La hora" y "Mide"."""
    if tipo == "tabla":
        campos(num, a, ["desde", "faltan"])
        desde, faltan = a["desde"], a["faltan"]
        if desde % 10 != 1 or not 1 <= desde <= 51:
            raise ErrorDeContenido(f"día {num}: 'tabla' empieza en 1, 11, 21, 31, 41 o 51 ({desde})")
        numeros = list(range(desde, desde + 50))
        for v in numeros:
            comprobar_numero(num, v, semana, "un número de la tabla")
        if not 3 <= len(faltan) <= 8 or len(set(faltan)) != len(faltan) or any(f not in numeros for f in faltan):
            raise ErrorDeContenido(f"día {num}: en 'tabla' faltan de 3 a 8 números de la tabla ({faltan})")
        if n not in numeros:
            raise ErrorDeContenido(f"día {num}: la tabla tiene que tener el número del día ({n})")
        faltan = sorted(faltan)
        enunciado, instruccion, clave = L.tabla(faltan)
        return PLANTILLA_CAJA.substitute(
            caja="cajaTabla", enunciado=enunciado, instruccion=instruccion,
            dibujo=dibujo_tabla(desde, faltan),
        ), ("tabla", clave)

    if tipo == "dinero":
        campos(num, a, ["dinero"])
        valores = a["dinero"]
        if not 2 <= len(valores) <= 8 or any(v not in VALORES_DINERO for v in valores):
            raise ErrorDeContenido(
                f"día {num}: 'dinero' lleva de 2 a 8 monedas (1 y 2 €) y billetes (5, 10 y 20 €) ({valores})")
        total = sum(valores)
        comprobar_numero(num, total, semana, "el dinero que hay")
        if total > MAX_DINERO or total != n:
            raise ErrorDeContenido(
                f"día {num}: en 'dinero', lo que hay es el número del día ({n}), y como mucho {MAX_DINERO} € ({total})")
        enunciado, instruccion, respuesta, clave = L.dinero(total)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaDinero", enunciado=enunciado, instruccion=instruccion,
            dibujo=dibujo_dinero(valores), respuesta=respuesta,
        ), ("dinero", clave)

    if tipo == "hora":
        campos(num, a, ["hora"])
        hora, minutos = a["hora"], a.get("minutos", 0)
        if not 1 <= hora <= 12 or minutos not in (0, 30):
            raise ErrorDeContenido(f"día {num}: 'hora' es una hora del 1 al 12, en punto o y media ({hora}:{minutos})")
        if minutos == 30 and semana < MEDIA_DESDE:
            raise ErrorDeContenido(f"día {num}: 'y media' no llega hasta la semana {MEDIA_DESDE} (ver MEDIA_DESDE)")
        if hora != n:
            raise ErrorDeContenido(f"día {num}: en 'hora', la hora es el número del día ({n}), no {hora}")
        enunciado, instruccion, respuesta, clave = L.hora(hora, minutos)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaHora", enunciado=enunciado, instruccion=instruccion,
            dibujo=f"\\relojGrande{{{hora}}}{{{minutos}}}", respuesta=respuesta,
        ), ("hora", clave)

    # "mide": uno o dos lápices, sobre su regla de cubitos.
    campos(num, a, ["largos"])
    largos = a["largos"]
    if not 1 <= len(largos) <= 2 or len(set(largos)) != len(largos) or any(not 2 <= x <= MAX_MIDE for x in largos):
        raise ErrorDeContenido(f"día {num}: 'mide' lleva uno o dos lápices distintos, de 2 a {MAX_MIDE} cubitos ({largos})")
    for x in largos:
        comprobar_numero(num, x, semana, "lo que mide un lápiz")
    if n not in largos:
        raise ErrorDeContenido(f"día {num}: en 'mide', un lápiz mide el número del día ({n})")
    enunciado, instruccion, respuesta, clave = L.mide(largos)
    return PLANTILLA_CON_RESPUESTA.substitute(
        caja="cajaMide", enunciado=enunciado, instruccion=instruccion,
        dibujo=dibujo_mide(largos), respuesta=respuesta,
    ), ("mide", clave)


def render_actividad(d, L):
    """(tex, clave): la caja de la actividad del día, y su entrada de la
    clave de respuestas (None si no tiene nada que comprobar). L es la
    lengua del cuaderno (tools/idiomas.py)."""
    num, semana, a = d["dia"], d["semana"], d["actividad"]
    tipo = a.get("tipo")
    n = d["numero"]
    if tipo in DESDE_SEMANA and semana < DESDE_SEMANA[tipo]:
        raise ErrorDeContenido(
            f"día {num}: '{tipo}' no llega hasta la semana {DESDE_SEMANA[tipo]} (ver DESDE_SEMANA)"
        )
    for otra in LENGUAS:
        if tipo in otra.solo_aqui and otra is not L:
            raise ErrorDeContenido(f"día {num}: '{tipo}' solo lo tiene el cuaderno en «{otra.codigo}»")

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
        enunciado, resto = L.colorea(cuantas, a["objeto"])
        return PLANTILLA_COLOREA.substitute(
            enunciado=enunciado,
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
        enunciado, instruccion, clave = L.rodea(cuantas, a["objeto"], grupos.index(cuantas) + 1)
        return PLANTILLA_RODEA.substitute(
            enunciado=enunciado,
            instruccion=instruccion,
            escala=escala,
            grupos=dibujo,
        ), ("rodea", clave)

    if tipo == "cuenta":
        campos(num, a, ["objeto", "opciones"])
        comprobar_objeto(num, a["objeto"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "lo que se cuenta")
        opciones = a["opciones"]
        # De 2 en 2 (las ruedas de las bicis) o de 5 en 5 (los dedos de las
        # manos): se cuentan las ruedas o los dedos, no las bicis o las manos.
        de = a.get("de", 1)
        if de != 1:
            if CONTAR_DE.get(a["objeto"]) != de:
                raise ErrorDeContenido(
                    f"día {num}: 'cuenta' de {de} en {de}: " + "; ".join(
                        f"de {p} en {p}, {ESPANOL.contar_de[o][0]} de {ESPANOL.cosa(o, 2)}"
                        for o, p in CONTAR_DE.items())
                )
            comprobar_paso(num, semana, de, "cuenta")
        respuesta = cuantas * de
        for o in opciones:
            comprobar_numero(num, o, semana, "una de las opciones")
        if respuesta not in opciones or len(set(opciones)) != len(opciones) or not 2 <= len(opciones) <= 4:
            raise ErrorDeContenido(
                f"día {num}: 'cuenta' lleva de 2 a 4 opciones distintas, y una es "
                f"{respuesta} ({opciones})"
            )
        if cuantas > MAX_GRUPO:
            raise ErrorDeContenido(f"día {num}: 'cuenta' dibuja como mucho {MAX_GRUPO} cosas")
        enunciado, instruccion = L.cuenta(a["objeto"], de)
        # La bandeja (el marco del grupo) se dibuja siempre: el día del 0,
        # es lo único que hay.
        dibujo, ancho, alto = grupo(a["objeto"], cuantas)
        return PLANTILLA_CUENTA.substitute(
            enunciado=enunciado,
            instruccion=instruccion,
            escala=round(min(1.0, 13.0 / ancho, 8.0 / alto), 3),
            grupo=dibujo,
            opciones=r"\hspace{14mm}".join(str(o) for o in opciones),
        ), ("cuenta", str(respuesta))

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
        enunciado, clave = L.busca(buscar, veces)
        return PLANTILLA_BUSCA.substitute(
            enunciado=enunciado,
            columnas=columnas, filas=filas,
        ), ("busca", clave)

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
        enunciado, instruccion, clave = L.une(grupos)
        return PLANTILLA_UNE.substitute(
            enunciado=enunciado,
            instruccion=instruccion,
            dibujo=dibujo_une(a["objeto"], grupos, orden),
        ), ("une", clave)

    if tipo == "nombres":
        # "Number names": los números del -teen y los de la decena que
        # suena casi igual (13 y 30), y el nombre de cada uno, para unir.
        campos(num, a, ["numeros"])
        numeros = a["numeros"]
        if not 4 <= len(numeros) <= 6 or len(set(numeros)) != len(numeros):
            raise ErrorDeContenido(f"día {num}: 'nombres' lleva de 4 a 6 números, distintos ({numeros})")
        for x in numeros:
            comprobar_numero(num, x, semana, "uno de los números")
        if n not in numeros:
            raise ErrorDeContenido(f"día {num}: en 'nombres', uno de los números es el del día ({n})")
        rng, orden = random.Random(num), list(numeros)
        while any(o == x for o, x in zip(orden, numeros)):
            rng.shuffle(orden)
        enunciado, instruccion, clave = L.nombres_numeros(numeros)
        return PLANTILLA_CAJA.substitute(
            caja="cajaNombres", enunciado=enunciado, instruccion=instruccion,
            dibujo=dibujo_nombres(numeros, orden, L),
        ), ("nombres", clave)

    if tipo == "serie":
        campos(num, a, ["serie"])
        serie = a["serie"]
        huecos = [i for i, v in enumerate(serie) if v is None]
        dados = [(i, v) for i, v in enumerate(serie) if v is not None]
        if not 4 <= len(serie) <= 7 or not 1 <= len(huecos) <= 2 or len(dados) < 2:
            raise ErrorDeContenido(
                f"día {num}: 'serie' lleva de 4 a 7 números, y faltan 1 o 2 ({serie})"
            )
        # De uno en uno (o de 2 en 2, de 5 en 5, de 10 en 10: PASOS_DESDE),
        # hacia arriba o hacia atrás: lo dicen los que se ven.
        (i0, v0), (i1, v1) = dados[0], dados[1]
        paso = (v1 - v0) / (i1 - i0)
        completa = [v0 + paso * (i - i0) for i in range(len(serie))]
        if abs(paso) not in PASOS_DESDE or any(serie[i] != completa[i] for i, _ in dados):
            raise ErrorDeContenido(
                f"día {num}: 'serie' va de uno en uno (o de 2 en 2, de 5 en 5, de 10 en 10), "
                f"hacia arriba o hacia atrás ({serie})"
            )
        comprobar_paso(num, semana, int(abs(paso)), "serie")
        completa = [int(v) for v in completa]
        for v in completa:
            if v < 0:
                raise ErrorDeContenido(f"día {num}: 'serie' no baja del 0 ({serie})")
            comprobar_numero(num, v, semana, "un número de la serie")
        if n not in completa:
            raise ErrorDeContenido(f"día {num}: la serie tiene que pasar por el número del día ({n})")
        faltan = [completa[i] for i in huecos]
        enunciado, instruccion, clave = L.serie(int(paso), faltan)
        return PLANTILLA_SERIE.substitute(
            enunciado=enunciado,
            instruccion=instruccion,
            tren=dibujo_serie(serie),
        ), ("completa", clave)

    if tipo in ("decena", "junta"):
        campos(num, a, ["objeto"] + (["grupos"] if tipo == "junta" else []))
        comprobar_objeto(num, a["objeto"])
        if tipo == "decena":
            # Diez y algo más: la bandeja llena y la otra.
            total = a.get("total", n)
            comprobar_numero(num, total, semana, "lo que se cuenta")
            if not 11 <= total <= 20:
                raise ErrorDeContenido(f"día {num}: 'decena' es diez y algo más, del 11 al 20 ({total})")
            grupos = [10, total - 10]
            enunciado, instruccion = L.decena(a["objeto"])
        else:
            grupos = a["grupos"]
            if len(grupos) != 2 or min(grupos) < 1:
                raise ErrorDeContenido(f"día {num}: 'junta' junta dos grupos, de una cosa o más ({grupos})")
            for g in grupos:
                comprobar_numero(num, g, semana, "uno de los grupos")
            total = sum(grupos)
            if total > MAX_JUNTA:
                raise ErrorDeContenido(f"día {num}: 'junta' suma como mucho {MAX_JUNTA} ({grupos})")
            enunciado, instruccion = L.junta(a["objeto"])
        if total != n:
            raise ErrorDeContenido(f"día {num}: en '{tipo}', el total es el número del día ({n}), no {total}")
        dibujo, escala = dibujo_dos_grupos(a["objeto"], *grupos, signo=L.signo_junta)
        return PLANTILLA_CON_RESPUESTA.substitute(
            caja="cajaDecena" if tipo == "decena" else "cajaJunta",
            enunciado=enunciado, instruccion=instruccion,
            dibujo=tikz(dibujo, escala),
            respuesta=L.son(grupos[0], grupos[1], "\\huecoRespuesta"),
        ), (tipo, L.son(grupos[0], grupos[1], total))

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
            enunciado, instruccion, clave = L.compara_numeros(que, numeros, elegido)
            return PLANTILLA_CAJA.substitute(
                caja="cajaCompara",
                enunciado=enunciado,
                instruccion=instruccion,
                dibujo=dibujo_numeros(numeros),
            ), ("compara", clave)
        campos(num, a, ["objeto", "grupos"])
        comprobar_objeto(num, a["objeto"])
        grupos = a["grupos"]
        for x in grupos:
            comprobar_numero(num, x, semana, "uno de los grupos")
        if n not in grupos:
            raise ErrorDeContenido(f"día {num}: en 'compara', uno de los grupos es el número del día ({n})")
        if min(grupos) < 1 or max(grupos) > MAX_GRUPO:
            raise ErrorDeContenido(f"día {num}: un grupo de 'compara' va de 1 a {MAX_GRUPO} cosas ({grupos})")
        if que == "igual":
            if len(grupos) != 3 or len(set(grupos)) != 2:
                raise ErrorDeContenido(f"día {num}: 'compara' con 'igual' lleva tres grupos, y dos iguales ({grupos})")
        elif not 2 <= len(grupos) <= 3 or len(set(grupos)) != len(grupos):
            raise ErrorDeContenido(f"día {num}: 'compara' lleva 2 o 3 grupos, distintos ({grupos})")
        enunciado, instruccion, clave = L.compara_grupos(que, a["objeto"], grupos)
        dibujo, escala = disponer(
            [grupo(a["objeto"], x, paso=2.2) for x in grupos],
            ancho_cm=15.0, alto_cm=10.0, hueco=1.6, maxima=0.7,
        )
        return PLANTILLA_CAJA.substitute(
            caja="cajaCompara", enunciado=enunciado,
            instruccion=instruccion,
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
        enunciado, instruccion, clave = L.vecinos(numeros)
        return PLANTILLA_CAJA.substitute(
            caja="cajaVecinos",
            enunciado=enunciado,
            instruccion=instruccion,
            dibujo=dibujo_vecinos(numeros, L),
        ), ("vecinos", clave)

    if tipo == "recta":
        campos(num, a, ["desde", "hasta", "faltan"])
        desde, hasta, faltan = a["desde"], a["hasta"], a["faltan"]
        paso = a.get("paso", 1)
        if paso not in PASOS_DESDE or (hasta - desde) % paso:
            raise ErrorDeContenido(
                f"día {num}: 'recta' va de 1 en 1, de 2 en 2, de 5 en 5 o de 10 en 10, "
                f"y de {desde} se llega a {hasta} ({paso})"
            )
        comprobar_paso(num, semana, paso, "recta")
        marcas = list(range(desde, hasta + 1, paso))
        if not 5 <= len(marcas) <= 11:
            raise ErrorDeContenido(f"día {num}: 'recta' lleva de 5 a 11 números ({desde}-{hasta})")
        if (not 1 <= len(faltan) <= 3 or len(set(faltan)) != len(faltan)
                or any(f not in marcas[1:] for f in faltan)):
            raise ErrorDeContenido(
                f"día {num}: en 'recta' faltan de 1 a 3 números de la recta, y el primero se ve ({faltan})"
            )
        for v in marcas:
            comprobar_numero(num, v, semana, "un número de la recta")
        if n not in marcas:
            raise ErrorDeContenido(f"día {num}: la recta tiene que pasar por el número del día ({n})")
        faltan = sorted(faltan)
        enunciado, instruccion, clave = L.recta(paso, faltan)
        return PLANTILLA_CAJA.substitute(
            caja="cajaRecta",
            enunciado=enunciado,
            instruccion=instruccion,
            dibujo=dibujo_recta(marcas, faltan),
        ), ("recta", clave)

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
        enunciado, instruccion, clave = L.ordena(orden, ordenados)
        return PLANTILLA_CAJA.substitute(
            caja="cajaOrdena",
            enunciado=enunciado,
            instruccion=instruccion,
            dibujo=dibujo_ordena(numeros),
        ), ("ordena", clave)

    if tipo in ("suma", "resta", "parte", "diez", "problema", "bloques"):
        return render_cuenta(d, tipo, num, semana, a, n, L)

    if tipo in ("tabla", "dinero", "hora", "mide"):
        return render_verano(d, tipo, num, semana, a, n, L)

    if tipo == "dibuja":
        campos(num, a, ["prompt"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "lo que se dibuja")
        if cuantas < 1:
            raise ErrorDeContenido(f"día {num}: 'dibuja' dibuja al menos una cosa")
        if not L.dice_cuantas(a["prompt"], cuantas):
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


# Lo que se escribe a mano en cada actividad, además de lo que compone
# este script: lo que cada traducción trae en su lengua ("First Numbers"
# en content/english/q*.json, "Poznaję liczby" en content/polish/q*.json).
TEXTOS_ACTIVIDAD = {"dibuja": ("prompt",), "repasa": ("checklist", "prompt"), "problema": ("texto",)}


def cargar_traduccion(dias_es, cuaderno):
    """Los días de una traducción ("First Numbers", "Poznaję liczby"): los
    de "Aprendo los números", uno a uno, con el tema de su semana en su
    lengua (tools/idiomas.py) y su frase y los textos de su actividad de
    content/<lengua>/q*.json. Un día puede cambiar de actividad, pero solo
    por una de las que no tiene el cuaderno en español (en inglés,
    "Number names": Ingles.solo_aqui): todo lo demás es lo mismo, página
    a página."""
    L, carpeta = cuaderno.lengua, cuaderno.carpeta.relative_to(ROOT)
    textos = {}
    for ruta in sorted(cuaderno.carpeta.glob("q*.json")):
        for t in json.loads(ruta.read_text(encoding="utf-8"))["dias"]:
            if t.get("dia") in textos:
                raise ErrorDeContenido(f"el día {t.get('dia')} está dos veces en {carpeta}/")
            textos[t.get("dia")] = t
    total = cuaderno.escritos or TOTAL_DIAS
    if total > len(dias_es):
        raise ErrorDeContenido("no puede tener días que no tenga todavía «Aprendo los números»")
    if sorted(textos) != list(range(1, total + 1)):
        raise ErrorDeContenido(
            f"tienen que estar los días del 1 al {total} en {carpeta}/, sin huecos ni repetidos"
            + (f" (en obras: {cuaderno.constante})" if cuaderno.escritos else ""))
    dias = []
    for d in dias_es[:total]:
        num, t = d["dia"], textos[d["dia"]]
        sobran = set(t) - {"dia", "frase", "actividad", "prompt", "checklist", "texto"}
        if sobran:
            raise ErrorDeContenido(f"día {num}: no se usa {', '.join(sorted(sobran))}")
        if "frase" not in t:
            raise ErrorDeContenido(f"día {num}: falta 'frase'")
        a = dict(d["actividad"])
        if "actividad" in t:
            if t["actividad"].get("tipo") not in L.solo_aqui:
                raise ErrorDeContenido(
                    f"día {num}: la actividad es la de «Aprendo los números»"
                    + (f", o una de {sorted(L.solo_aqui)}, que no tiene" if L.solo_aqui else "")
                    + f" ({t['actividad'].get('tipo')!r})")
            a = dict(t["actividad"])
        necesita = TEXTOS_ACTIVIDAD.get(a["tipo"], ())
        for c in ("prompt", "checklist", "texto"):
            if (c in necesita) != (c in t):
                raise ErrorDeContenido(
                    f"día {num}: '{a['tipo']}' " + ("necesita" if c in necesita else "no lleva") + f" '{c}'")
            if c in necesita:
                a[c] = t[c]
        if "checklist" in necesita and len(t["checklist"]) != len(d["actividad"]["checklist"]):
            raise ErrorDeContenido(
                f"día {num}: 'repasa' marca las mismas {len(d['actividad']['checklist'])} cosas "
                "que en «Aprendo los números»")
        dias.append(dict(d, tema=L.temas[d["semana"] - 1], frase=t["frase"], actividad=a))
    return dias


def validar_dias(dias, L=ESPANOL, escritos=DIAS_ESCRITOS):
    total = escritos or TOTAL_DIAS
    numeros = [d["dia"] for d in dias]
    if numeros != list(range(1, total + 1)):
        raise ErrorDeContenido(
            f"tienen que estar los días del 1 al {total}, sin huecos ni repetidos"
            + (" (en obras: DIAS_ESCRITOS)" if escritos else "")
        )
    for d in dias:
        num = d["dia"]
        semana = (num - 1) // DIAS_POR_SEMANA + 1
        if d.get("semana") != semana:
            raise ErrorDeContenido(f"día {num}: es de la semana {semana}, no {d.get('semana')}")
        if d.get("tema") != L.temas[semana - 1]:
            raise ErrorDeContenido(
                f"día {num}: el tema de la semana {semana} es «{L.temas[semana - 1]}», "
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
        if not L.dice(d["frase"], n):
            raise ErrorDeContenido(
                f"día {num}: la frase tiene que decir el número del día "
                f"({' / '.join(sorted(L.formas(n)))}): «{d['frase']}»"
            )
        # En una semana con números nuevos, el día que llega uno se traza
        # (el lunes, el primero; el miércoles, el segundo), y el número del
        # día es el último que ha llegado -- el viernes, cualquiera de los
        # de la semana. El viernes, además, se repasa.
        nuevos = ESCALERA.get(semana, [])
        dia_semana = (num - 1) % DIAS_POR_SEMANA
        tipo = d["actividad"].get("tipo")
        if nuevos and len(nuevos) > len(LLEGADA):
            # Una decena entera: llega el lunes, que se traza uno de sus
            # números, y toda la semana el número del día es uno de ellos.
            if n not in nuevos:
                raise ErrorDeContenido(
                    f"día {num}: el número del día, en la semana {semana}, es uno de "
                    f"{nuevos[0]}-{nuevos[-1]}, no el {n}"
                )
            if dia_semana == 0 and tipo != "traza":
                raise ErrorDeContenido(f"día {num}: el lunes que llegan {nuevos[0]}-{nuevos[-1]}, se traza uno")
        elif nuevos:
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
    "% GENERADO por tools/gen_numeros.py a partir de {fuentes}.\n"
    "% NO EDITAR A MANO -- los cambios se perderán en la siguiente\n"
    "% ejecución de `make generate`. Edita {fuentes} en su lugar.\n\n"
)


def generar(dias, cuaderno, fuentes):
    L = cuaderno.lengua
    piezas = [CABECERA.format(nombre=cuaderno.salida_dias.relative_to(ROOT), fuentes=fuentes)]
    claves = [CABECERA.format(nombre=cuaderno.salida_clave.relative_to(ROOT), fuentes=fuentes)]
    for d in dias:
        num, semana = d["dia"], d["semana"]
        trimestre = trimestre_de(semana)
        n = d["numero"]
        actividad, clave = render_actividad(d, L)
        # Las cosas del número de hoy, tantas como el número -- el 0 es el
        # recipiente vacío --, en el sitio que deja el número (el 10 ocupa
        # más que una cifra: ver \numeroDeHoy).
        ancho = 7.2 if n < 10 else 6.4
        escala = escala_para(max(n, 1), ancho, 2.4, 0.85)
        if n > 10:
            # Del 11 al 20, no más altas que los dos marcos de diez.
            filas = -(-n // 5)
            escala = min(escala, round(4.4 / ((filas - 1 + SEPARACION_DECENA) * 2.4 + 2), 3))
        # Del 21 en adelante, ya no se dibujan las cosas, sino sus decenas y
        # sus unidades: una barra por cada diez.
        cosas = (dibujo_bloques(n, 0.3) if n > 20
                 else fila(d["objeto"], max(n, 1), escala=escala, paso=2.4))
        piezas.append(PLANTILLA_DIA.substitute(
            dia=num, semana=semana, trimestre=trimestre,
            tema=escapar(d["tema"]),
            numero=n, nombre=L.nombres[n],
            cosas=cosas,
            frase=escapar(d["frase"]),
            actividad=actividad,
        ))
        if clave:
            etiqueta, texto = clave
            claves.append(f"\\claveEntrada{{{num}}}{{\\lbl{etiqueta.capitalize()}}}{{{escapar(texto)}}}\n")
        if num == ULTIMO_DIA_TRIMESTRE.get(trimestre) and trimestre in L.nombre_medalla:
            piezas.append(L.plantilla_medalla.substitute(dia=num, estacion=L.nombre_medalla[trimestre]))
    return "\n".join(piezas), "".join(claves)


def comprobar_totaldias(cuaderno):
    """lang/es.tex, lang/en.tex y lang/pl.tex prometen los mismos 260
    días que este script."""
    m = re.search(r"\\newcommand\{\\totaldias\}\{(\d+)\}", cuaderno.lang.read_text(encoding="utf-8"))
    if not m or int(m.group(1)) != TOTAL_DIAS:
        raise ErrorDeContenido(f"\\totaldias en {cuaderno.lang.relative_to(ROOT)} tiene que ser {TOTAL_DIAS}")


def main():
    check_only = "--check" in sys.argv
    salidas, resumen = [], []
    for cuaderno in (APRENDO,) + TRADUCCIONES:
        escritos = cuaderno.escritos
        try:
            comprobar_totaldias(cuaderno)
            if cuaderno is APRENDO:
                dias = dias_es = cargar_dias()
                fuentes = "content/q*.json"
            else:
                dias = cargar_traduccion(dias_es, cuaderno)
                fuentes = f"content/q*.json y {cuaderno.carpeta.relative_to(ROOT)}/q*.json"
            validar_dias(dias, cuaderno.lengua, escritos)
            tex, clave = generar(dias, cuaderno, fuentes)
        except ErrorDeContenido as exc:
            print(f"ERROR ({cuaderno.nombre}): {exc}", file=sys.stderr)
            return 1
        salidas += [(cuaderno.salida_dias, tex), (cuaderno.salida_clave, clave)]
        obras = f", en obras: {len(dias)} de {TOTAL_DIAS} días escritos" if escritos else ""
        resumen.append(f"{cuaderno.nombre} ({len(dias)} días{obras})")

    if check_only:
        for ruta, contenido in salidas:
            actual = ruta.read_text(encoding="utf-8") if ruta.exists() else None
            if actual != contenido:
                print(
                    f"DESACTUALIZADO: {ruta.relative_to(ROOT)} no coincide con su JSON "
                    "-- ejecuta `make generate`.",
                    file=sys.stderr,
                )
                return 1
        print(f"OK: {' y '.join(resumen)} validados, y lo generado, al día.")
        return 0

    for ruta, contenido in salidas:
        ruta.write_text(contenido, encoding="utf-8")
    print(f"Escritos: {' y '.join(resumen)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
