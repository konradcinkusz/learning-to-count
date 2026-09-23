#!/usr/bin/env python3
"""Comprueba el invariante "1 día = 1 página" leyendo el .aux compilado.

Cada \\begin{diapagina}{N}{...}{...} escribe \\label{dia:N} como lo
primero que hace. LaTeX anota en el .aux, para cada \\label, la página en
la que cayó -- \\newlabel{dia:N}{{<ref>}{<pagina>}...}. Si un día ocupa
más de una página (el texto o la actividad no cupieron), el salto entre
la página del día N y la del día N+1 será mayor que 1, y este script lo
señala con el número de día exacto -- no hace falta compilar cada día
por separado ni mirar el PDF a ojo.

El último día no tiene un día N+1 con el que compararse: se compara con
la página donde empieza la clave de respuestas, que la marca con
\\etiquetaPagina{clave} (preamble.tex). Un documento sin esa etiqueta
(una prueba de un solo trimestre, por ejemplo) se comprueba sin ella.

Uso:
    python3 tools/check_pages.py [main.aux]
"""

import re
import sys
from pathlib import Path

PATRON_LABEL = re.compile(r"\\newlabel\{dia:(\d+)\}\{\{[^{}]*\}\{(\d+)\}")
# \etiquetaPagina{clave} (preamble.tex), al empezar la clave de
# respuestas: la página que viene justo después del último día.
PATRON_CLAVE = re.compile(r"\\newlabel\{clave\}\{\{[^{}]*\}\{(\d+)\}")

# Fin de trimestre (T1-T3): tools/gen_days.py inserta una página de
# medalla, sin \label propio, justo después del último día del
# trimestre (ver PLANTILLA_MEDALLA) -- el salto hasta el primer día del
# trimestre siguiente es de 2 páginas a propósito, no un desbordamiento.
SALTOS_ESPERADOS = {65: 2, 130: 2, 195: 2}

# Antes del día 1 van la portada, "Cómo usar este cuaderno" y el mapa del
# curso, una página cada uno: si "Cómo usar" (que crece con cada
# actividad nueva) se desborda, el día 1 ya no cae en la página 4.
PAGINA_DIA_1 = 4


def leer_paginas(ruta_aux):
    texto = ruta_aux.read_text(encoding="utf-8", errors="replace")
    paginas = {}
    for m in PATRON_LABEL.finditer(texto):
        dia, pagina = int(m.group(1)), int(m.group(2))
        paginas[dia] = pagina
    return paginas


def leer_pagina_clave(ruta_aux):
    """La página donde empieza la clave de respuestas, o None si el .aux
    no la tiene (un documento de prueba sin clave, por ejemplo)."""
    texto = ruta_aux.read_text(encoding="utf-8", errors="replace")
    m = PATRON_CLAVE.search(texto)
    return int(m.group(1)) if m else None


def main():
    posicionales = [a for a in sys.argv[1:] if not a.startswith("--")]
    ruta_aux = Path(posicionales[0] if posicionales else "main.aux")
    if not ruta_aux.exists():
        print(
            f"ERROR: no existe {ruta_aux} -- compila primero con "
            "`make build` (o `latexmk -pdf main.tex`).",
            file=sys.stderr,
        )
        return 1

    paginas = leer_paginas(ruta_aux)
    if not paginas:
        print(
            f"ERROR: {ruta_aux} no contiene ninguna etiqueta dia:N -- "
            "¿se generó content/generated-days.tex antes de compilar?",
            file=sys.stderr,
        )
        return 1

    dias_ordenados = sorted(paginas)
    problemas = []

    esperado = dias_ordenados[0]
    for dia in dias_ordenados:
        if dia != esperado:
            problemas.append(f"falta el día {esperado} (o los días no son consecutivos)")
            esperado = dia
        esperado += 1

    if dias_ordenados[0] == 1 and paginas[1] != PAGINA_DIA_1:
        problemas.append(
            f"el día 1 está en la página {paginas[1]}, no en la {PAGINA_DIA_1} -- "
            "la portada, \"Cómo usar\" o el mapa del curso se han desbordado"
        )

    for a, b in zip(dias_ordenados, dias_ordenados[1:]):
        salto = paginas[b] - paginas[a]
        esperado_salto = SALTOS_ESPERADOS.get(a, 1)
        if salto != esperado_salto:
            problemas.append(
                f"día {a} (página {paginas[a]}) -> día {b} (página {paginas[b]}): "
                f"salto de {salto} página(s), debería ser exactamente "
                f"{esperado_salto} -- el día {a} probablemente se ha "
                "desbordado a una segunda página"
            )

    # El último día no tiene otro día detrás con el que comparar: lo que
    # viene después es la clave de respuestas (o, si el último día cierra
    # un trimestre, su medalla y luego la clave).
    pagina_clave = leer_pagina_clave(ruta_aux)
    if pagina_clave is not None:
        ultimo = dias_ordenados[-1]
        salto = pagina_clave - paginas[ultimo]
        esperado_salto = SALTOS_ESPERADOS.get(ultimo, 1)
        if salto != esperado_salto:
            problemas.append(
                f"día {ultimo} (página {paginas[ultimo]}) -> clave de respuestas "
                f"(página {pagina_clave}): salto de {salto} página(s), debería "
                f"ser exactamente {esperado_salto} -- el último día probablemente "
                "se ha desbordado a una segunda página"
            )

    print(
        f"Días {dias_ordenados[0]}-{dias_ordenados[-1]}: "
        f"páginas {paginas[dias_ordenados[0]]}-{paginas[dias_ordenados[-1]]}."
    )
    if problemas:
        print("PROBLEMAS ENCONTRADOS:", file=sys.stderr)
        for p in problemas:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"OK: los {len(dias_ordenados)} días ocupan exactamente una página cada uno.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
