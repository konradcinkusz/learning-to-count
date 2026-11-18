"""checklog.py must see file-line-error lines, overfull boxes and missing
glyphs, which a naive `grep '^!'` misses. Logs here are synthetic."""

import subprocess
import sys

import checklog
from conftest import ROOT

LIMPIO = "This is LuaTeX (synthetic)\nOutput written on main.pdf (270 pages).\n"


def escribir(tmp_path, texto):
    ruta = tmp_path / "x.log"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def test_clean_log_has_no_findings(tmp_path):
    errores, overfull, _ = checklog.revisar(escribir(tmp_path, LIMPIO))
    assert errores == [] and overfull == []


def test_file_line_error_is_detected(tmp_path):
    texto = LIMPIO + "./main.tex:42: Undefined control sequence.\n"
    errores, _, _ = checklog.revisar(escribir(tmp_path, texto))
    assert errores == ["./main.tex:42: Undefined control sequence."]


def test_overfull_box_is_detected(tmp_path):
    texto = LIMPIO + "Overfull \\hbox (3.0pt too wide) in paragraph at lines 1--2\n"
    _, overfull, _ = checklog.revisar(escribir(tmp_path, texto))
    assert len(overfull) == 1


def test_missing_glyph_is_an_error(tmp_path):
    texto = LIMPIO + "Missing character: There is no X in font Andika!\n"
    errores, _, _ = checklog.revisar(escribir(tmp_path, texto))
    assert len(errores) == 1


def test_underfull_is_not_blocking(tmp_path):
    texto = LIMPIO + "Underfull \\hbox (badness 10000) in paragraph\n"
    errores, overfull, underfull = checklog.revisar(escribir(tmp_path, texto))
    assert errores == [] and overfull == [] and len(underfull) == 1


def ejecutar(ruta):
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "checklog.py"), str(ruta)],
        capture_output=True, text=True,
    )


def test_exit_code_fails_on_error_and_passes_when_clean(tmp_path):
    assert ejecutar(escribir(tmp_path, LIMPIO)).returncode == 0
    mal = escribir(tmp_path, LIMPIO + "./main.tex:9: Missing $ inserted.\n")
    assert ejecutar(mal).returncode == 1


def test_missing_log_file_fails(tmp_path):
    assert ejecutar(tmp_path / "no-existe.log").returncode == 1
