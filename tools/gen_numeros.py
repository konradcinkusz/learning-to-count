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
DIAS_ESCRITOS = 10

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
}

# Un grupo de cosas que hay que distinguir de un vistazo (los grupos de
# "rodea") no pasa de 6: más que eso ya no se ve, se cuenta.
MAX_GRUPO = 6


def conocidos(semana):
    """Los números que ya han llegado al terminar esa semana."""
    return {n for s in range(1, semana + 1) for n in ESCALERA.get(s, [])}


def trimestre_de(semana):
    return (semana - 1) // SEMANAS_POR_TRIMESTRE + 1


# Cómo se llama cada número, y cómo puede aparecer en la frase del día
# (la frase de un día con el 1 dice "un perro" o "una manzana").
NOMBRES = {
    0: "cero", 1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco",
    6: "seis", 7: "siete", 8: "ocho", 9: "nueve", 10: "diez",
}
FORMAS_EN_FRASE = {
    0: {"cero", "ningún", "ninguna", "ninguno", "nada"},
    1: {"uno", "un", "una"},
}


def formas(n):
    return FORMAS_EN_FRASE.get(n, {NOMBRES[n]})


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
}


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
    está llena, también centrada."""
    macro = OBJETOS[objeto][0]
    piezas = []
    filas = [min(por_fila, n - i) for i in range(0, n, por_fila)]
    for f, cuantas in enumerate(filas):
        for i in range(cuantas):
            x = (i - (cuantas - 1) / 2) * paso
            y = -f * paso
            piezas.append(_cosa(macro, x, y))
    return (
        f"\\begin{{tikzpicture}}[objeto, scale={escala}, baseline=(current bounding box.center)]"
        + "".join(piezas) + "\\end{tikzpicture}"
    )


def grupo(objeto, n, paso=2.3):
    """Las piezas de un grupo de n cosas (n <= MAX_GRUPO), como los puntos
    de un dado: de un vistazo se ve cuántas son."""
    macro = OBJETOS[objeto][0]
    return "".join(_cosa(macro, x * paso, y * paso) for x, y in POSICIONES_DADO[n])


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
\renglonTraza{$numero}
\renglonTraza{$numero}
\renglonTraza{$numero}
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
\begin{tikzpicture}[objeto, scale=1]
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
# primera vista, así que lo que hay que mirar son los números.
FORMAS_BUSCA = [
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt] (0,0) circle (3.8mm);",
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt, line join=round] (-4mm,-3.4mm) -- (4mm,-3.4mm) -- (0,3.8mm) -- cycle;",
    r"\tikz[baseline=-4.2mm]\draw[line width=1.8pt] (-3.4mm,-3.4mm) rectangle (3.4mm,3.4mm);",
]

ORDINALES = {1: "el primero", 2: "el segundo", 3: "el tercero", 4: "el cuarto"}


# --------------------------------------------------------------------
# Actividades
# --------------------------------------------------------------------
def comprobar_numero(dia, n, semana, que):
    if n not in conocidos(semana):
        raise ErrorDeContenido(
            f"día {dia}: {que} es {n}, que todavía no ha llegado en la semana "
            f"{semana} (ver ESCALERA: hasta ahora, {sorted(conocidos(semana))})"
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

    if tipo == "traza":
        cifra = a.get("numero", n)
        comprobar_numero(num, cifra, semana, "el número que se traza")
        return PLANTILLA_TRAZA.substitute(trazo=trazo(cifra), numero=cifra), None

    if tipo == "colorea":
        campos(num, a, ["objeto", "total"])
        comprobar_objeto(num, a["objeto"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "lo que se colorea")
        total = a["total"]
        if not cuantas < total <= 10:
            raise ErrorDeContenido(
                f"día {num}: 'colorea' tiene que tener más cosas que las que se "
                f"colorean, y como mucho 10 (colorea {cuantas} de {total})"
            )
        resto = ("Las demás, déjalas en blanco." if genero(a["objeto"]) == "f"
                 else "Los demás, déjalos en blanco.")
        return PLANTILLA_COLOREA.substitute(
            enunciado=f"Colorea {cuantas} {nombre_objeto(a['objeto'], cuantas)}.",
            resto=resto,
            cosas=fila(a["objeto"], total, escala=escala_para(total, 15.0, 2.5, 1.3)),
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
        if max(grupos) > MAX_GRUPO or min(grupos) < 1:
            raise ErrorDeContenido(
                f"día {num}: un grupo de 'rodea' va de 1 a {MAX_GRUPO} cosas ({grupos})"
            )
        piezas = []
        ancho, hueco = 6.8, 1.6
        escala = round(min(0.7, 15.0 / (len(grupos) * ancho + (len(grupos) - 1) * hueco)), 3)
        for i, g in enumerate(grupos):
            x = (i - (len(grupos) - 1) / 2) * (ancho + hueco)
            piezas.append(
                f"\\draw[dashed, line width=0.8pt, rounded corners=4mm, colorGris] "
                f"({x - ancho / 2:.2f},{-ancho / 2:.2f}) rectangle ({x + ancho / 2:.2f},{ancho / 2:.2f});"
                f"\\begin{{scope}}[shift={{({x:.2f},0)}}]{grupo(a['objeto'], g, paso=2.2)}\\end{{scope}}"
            )
        cosa = nombre_objeto(a["objeto"], cuantas)
        solo = "sola" if genero(a["objeto"]) == "f" else "solo"
        enunciado = (f"Rodea donde hay {cuantas} {cosa}." if cuantas != 1
                     else f"Rodea donde hay {cuantas} {cosa} {solo}.")
        posicion = grupos.index(cuantas) + 1
        clave = f"{ORDINALES[posicion]} ({cuantas} {cosa})"
        return PLANTILLA_RODEA.substitute(
            enunciado=enunciado,
            instruccion="Un adulto lee la pregunta. Rodea con el lápiz todo el grupo.",
            escala=escala,
            grupos="\n".join(piezas),
        ), ("rodea", clave)

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
        return PLANTILLA_CUENTA.substitute(
            enunciado=f"¿{cuantos} {plural} hay?",
            instruccion=("Un adulto lee la pregunta. Cuenta señalando cada una con "
                         "el dedo, y rodea el número." if genero(a["objeto"]) == "f" else
                         "Un adulto lee la pregunta. Cuenta señalando cada uno con "
                         "el dedo, y rodea el número."),
            grupo=grupo(a["objeto"], cuantas),
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
        relleno = [str(o) for o in a["otros"]] + FORMAS_BUSCA
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

    if tipo == "dibuja":
        campos(num, a, ["prompt"])
        cuantas = a.get("cuantas", n)
        comprobar_numero(num, cuantas, semana, "lo que se dibuja")
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
        if n > 10:
            raise ErrorDeContenido(f"día {num}: el número del día va del 0 al 10 en otoño")
        if not any(re.search(rf"\b{re.escape(f)}\b", d["frase"].lower()) for f in formas(n)):
            raise ErrorDeContenido(
                f"día {num}: la frase tiene que decir el número del día "
                f"({' / '.join(sorted(formas(n)))}): «{d['frase']}»"
            )
        # El lunes de una semana con número nuevo se traza el número
        # nuevo, y ese es el número de toda la semana; el viernes, repaso.
        nuevos = ESCALERA.get(semana, [])
        if nuevos and n != nuevos[0]:
            raise ErrorDeContenido(
                f"día {num}: el número de la semana {semana} es el {nuevos[0]}, no el {n}"
            )
        dia_semana = (num - 1) % DIAS_POR_SEMANA
        tipo = d["actividad"].get("tipo")
        if dia_semana == 0 and nuevos and tipo != "traza":
            raise ErrorDeContenido(
                f"día {num}: el lunes de una semana con número nuevo se traza ese número"
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
        piezas.append(PLANTILLA_DIA.substitute(
            dia=num, semana=semana, trimestre=trimestre,
            tema=escapar(d["tema"]),
            numero=n, nombre=NOMBRES[n],
            cosas=fila(d["objeto"], n, escala=escala_para(n, 7.2, 2.4, 0.85), paso=2.4),
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
