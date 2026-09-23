#!/usr/bin/env python3
"""Lee un .log de pdflatex correctamente -- nunca `grep '^!'`.

Con `-file-line-error`, una línea de error EMPIEZA por una ruta
(`./main.tex:42: Undefined control sequence.`), no por `!` -- así que un
`grep '^!'` no la ve. Y con `-interaction=nonstopmode`, `pdflatex` escribe
igualmente un PDF encima del error, así que el código de salida y el
propio PDF dicen los dos que todo ha ido bien. Este script es el único
sitio que debe leerse para saber si un build es de verdad limpio.

Falla (exit 1) si encuentra:
  - un error real de LaTeX (línea `ruta:número: mensaje`, o "Fatal error
    occurred, no output PDF file produced");
  - una caja `Overfull \\hbox` o `Overfull \\vbox` -- en este cuaderno,
    donde cada día tiene que caber en una sola página con un diseño
    fijo, una caja desbordada es un defecto visual real, no ruido;
  - un carácter que la letra del cuaderno no tiene ("Missing character:
    There is no ★ in font ...") -- LuaLaTeX lo deja en blanco y sigue,
    sin error: un símbolo o un emoji copiado en un texto desaparece de la
    página en silencio.

Solo informa (no falla) de las cajas `Underfull`, que casi siempre son
inofensivas.

Uso:
    python3 tools/checklog.py main.log [otro.log ...]
"""

import re
import sys
from pathlib import Path

PATRON_ERROR_RUTA = re.compile(r"^[^\s:][^:\n]*:\d+:\s")
PATRON_OVERFULL = re.compile(r"^Overfull \\[hv]box")
PATRON_UNDERFULL = re.compile(r"^Underfull \\[hv]box")
PATRON_SIN_GLIFO = re.compile(r"^Missing character: There is no ")


def revisar(ruta):
    """Devuelve (errores, overfull, underfull), cada uno una lista de líneas."""
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    lineas = texto.splitlines()

    errores = []
    overfull = []
    underfull = []

    if "Fatal error occurred, no output PDF file produced" in texto:
        errores.append("Fatal error occurred, no output PDF file produced")

    for linea in lineas:
        if PATRON_ERROR_RUTA.match(linea) or PATRON_SIN_GLIFO.match(linea):
            errores.append(linea)
        elif PATRON_OVERFULL.match(linea):
            overfull.append(linea)
        elif PATRON_UNDERFULL.match(linea):
            underfull.append(linea)

    return errores, overfull, underfull


def main():
    rutas = [Path(a) for a in sys.argv[1:]]
    if not rutas:
        print("Uso: python3 tools/checklog.py main.log [otro.log ...]", file=sys.stderr)
        return 2

    fallo = False
    for ruta in rutas:
        if not ruta.exists():
            print(f"ERROR: no existe {ruta}", file=sys.stderr)
            fallo = True
            continue

        errores, overfull, underfull = revisar(ruta)

        if errores:
            fallo = True
            print(f"ERRORES en {ruta}:", file=sys.stderr)
            for linea in errores:
                print(f"  {linea}", file=sys.stderr)

        if overfull:
            fallo = True
            print(f"OVERFULL en {ruta}:", file=sys.stderr)
            for linea in overfull:
                print(f"  {linea}", file=sys.stderr)

        if underfull:
            print(f"(underfull, no bloqueante, en {ruta}: {len(underfull)})")

        if not errores and not overfull:
            print(f"OK: {ruta} sin errores ni cajas overfull.")

    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main())
