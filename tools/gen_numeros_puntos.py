#!/usr/bin/env python3
"""Extrae el contorno real de cada número del 0 al 9, desde la propia
letra del cuaderno (fonts/andika/Andika-Bold.ttf), y lo guarda como una
nube de puntos en content/numeros-trazo.json -- los puntos que se
repasan con el dedo o con el lápiz en la actividad "Traza".

Es la herramienta de "Aprendo a leer" (tools/gen_letras_puntos.py, en
https://github.com/konradcinkusz/learning-to-read), con los números en
vez de las letras: el mismo glifo de la misma letra, así que el 4 que
se traza es exactamente el 4 que se lee en el resto del cuaderno.

Herramienta de desarrollo, NO forma parte de `make generate`: se
ejecuta a mano solo si cambia la letra o la separación de los puntos.
Su salida (content/numeros-trazo.json) SÍ se versiona en git,
precisamente para que el resto del pipeline (tools/gen_numeros.py) no
dependa de matplotlib ni de fontTools.

Requiere matplotlib y numpy (no son dependencias del proyecto --
instálalas aparte: pip install matplotlib numpy).

Uso:
    python3 tools/gen_numeros_puntos.py
"""

import json
import sys
from pathlib import Path

try:
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from matplotlib.patches import PathPatch
    import matplotlib.pyplot as plt
except ImportError:
    print(
        "ERROR: hacen falta matplotlib y numpy -- pip install matplotlib numpy",
        file=sys.stderr,
    )
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "fonts" / "andika" / "Andika-Bold.ttf"
OUTPUT_FILE = ROOT / "content" / "numeros-trazo.json"

NUMEROS = list("0123456789")

# Distancia entre puntos, en unidades de em (tamaño de letra = 1.0): la
# misma que las letras de "Aprendo a leer", que se trazan al mismo tamaño
# (ESCALA_TRAZO_CM en tools/gen_numeros.py) -- lo bastante juntos para que
# el contorno se lea como un número, lo bastante separados para que cada
# punto sea un sitio claro donde apoyar el lápiz.
ESPACIADO_PUNTOS_EM = 0.028


# Un punto del contorno solo se queda si está en el borde que se ve: en
# Andika, el 6 y el 9 son un solo contorno que se cruza consigo mismo
# (la curva de dentro se monta sobre el palo), y el tramo que queda
# DENTRO del trazo relleno no es borde de nada -- dibujado, sería una
# fila de puntos en medio del número. Se rellena el glifo como lo pinta
# cualquier programa (regla del devanado distinto de cero) y se quita
# cada punto que, a RADIO_BORDE_EM en todas direcciones, sigue dentro.
PX_POR_EM = 800
RADIO_BORDE_EM = 0.012


def relleno(tp, margen=0.05):
    """El glifo relleno, como matriz de booleanos (True = tinta), y la
    función que pasa de (x, y) en em a (fila, columna)."""
    ext = tp.get_extents()
    x0, y0 = ext.x0 - margen, ext.y0 - margen
    x1, y1 = ext.x1 + margen, ext.y1 + margen
    ancho, alto = (x1 - x0) * PX_POR_EM, (y1 - y0) * PX_POR_EM
    fig = plt.figure(figsize=(ancho / 100, alto / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.axis("off")
    ax.add_patch(PathPatch(tp, facecolor="black", edgecolor="none", antialiased=False))
    fig.canvas.draw()
    tinta = np.asarray(fig.canvas.buffer_rgba())[..., 0] < 128
    plt.close(fig)
    filas, columnas = tinta.shape

    def a_pixel(x, y):
        c = int((x - x0) / (x1 - x0) * columnas)
        f = int((y1 - y) / (y1 - y0) * filas)
        return min(max(f, 0), filas - 1), min(max(c, 0), columnas - 1)

    return tinta, a_pixel


def en_el_borde(x, y, tinta, a_pixel):
    for i in range(16):
        angulo = 2 * np.pi * i / 16
        f, c = a_pixel(x + RADIO_BORDE_EM * np.cos(angulo), y + RADIO_BORDE_EM * np.sin(angulo))
        if not tinta[f, c]:
            return True
    return False


def contornos_de_caracter(caracter, ruta_fuente, espaciado=ESPACIADO_PUNTOS_EM):
    """Una lista de contornos (uno por trazo cerrado del glifo: el 8 tiene
    tres -- el de fuera y los dos agujeros --, el 1 uno), cada uno como
    lista de (x, y) repartidos a distancia de arco aproximadamente
    constante a lo largo del contorno real, y solo los que están en el
    borde que se ve (ver en_el_borde). TextPath (FreeType, vía
    matplotlib) aplana las curvas de la fuente."""
    fp = FontProperties(fname=str(ruta_fuente))
    tp = TextPath((0, 0), caracter, size=1.0, prop=fp)
    tinta, a_pixel = relleno(tp)
    contornos = []
    for poligono in tp.to_polygons():
        poligono = np.asarray(poligono)
        if len(poligono) < 3:
            continue
        longitud_segmento = np.hypot(*np.diff(poligono, axis=0).T)
        longitud_arco = np.concatenate([[0], np.cumsum(longitud_segmento)])
        total = longitud_arco[-1]
        if total <= 0:
            continue
        n = max(int(round(total / espaciado)), 4)
        objetivos = np.linspace(0, total, n, endpoint=False)
        xs = np.interp(objetivos, longitud_arco, poligono[:, 0])
        ys = np.interp(objetivos, longitud_arco, poligono[:, 1])
        puntos = [
            (round(float(x), 4), round(float(y), 4))
            for x, y in zip(xs, ys)
            if en_el_borde(x, y, tinta, a_pixel)
        ]
        if puntos:
            contornos.append(puntos)
    return contornos


def main():
    if not FONT_PATH.exists():
        print(f"ERROR: no existe {FONT_PATH}", file=sys.stderr)
        return 1

    datos = {
        "_comentario": (
            "Puntos de contorno (glifo real de fonts/andika/Andika-Bold.ttf, "
            "vía matplotlib) para las páginas de trazo -- GENERADO por "
            "tools/gen_numeros_puntos.py, no editar a mano. Unidades: em "
            "(tamaño de letra = 1.0), origen en la línea base."
        )
    }
    for numero in NUMEROS:
        contornos = contornos_de_caracter(numero, FONT_PATH)
        xs = [x for c in contornos for x, _ in c]
        ys = [y for c in contornos for _, y in c]
        datos[numero] = {
            "contornos": contornos,
            "bbox": [min(xs), min(ys), max(xs), max(ys)] if xs else [0, 0, 0, 0],
        }
        print(f"{numero}: {len(contornos)} contornos, {len(xs)} puntos")

    OUTPUT_FILE.write_text(
        json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"Escrito {OUTPUT_FILE} con {len(NUMEROS)} números.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
