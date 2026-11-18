"""check_pages.py: one day = one page, read from a synthetic .aux."""

import subprocess
import sys

import check_pages
from conftest import ROOT


def aux(tmp_path, paginas, clave=None):
    lineas = [f"\\newlabel{{dia:{d}}}{{{{1}}{{{p}}}{{x}}{{y}}{{z}}}}" for d, p in paginas.items()]
    if clave is not None:
        lineas.append(f"\\newlabel{{clave}}{{{{1}}{{{clave}}}{{x}}{{y}}{{z}}}}")
    ruta = tmp_path / "x.aux"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return ruta


def ejecutar(ruta):
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_pages.py"), str(ruta)],
        capture_output=True, text=True,
    )


def test_labels_are_parsed(tmp_path):
    assert check_pages.leer_paginas(aux(tmp_path, {1: 5, 2: 6})) == {1: 5, 2: 6}


def test_one_page_per_day_passes(tmp_path):
    ruta = aux(tmp_path, {1: 5, 2: 6, 3: 7}, clave=8)
    assert ejecutar(ruta).returncode == 0


def test_overflowing_day_fails_and_names_the_day(tmp_path):
    ruta = aux(tmp_path, {1: 5, 2: 6, 3: 8, 4: 9}, clave=10)
    r = ejecutar(ruta)
    assert r.returncode == 1
    assert "día 2" in r.stderr


def test_day_one_not_on_page_five_fails(tmp_path):
    r = ejecutar(aux(tmp_path, {1: 6, 2: 7}))
    assert r.returncode == 1
    assert "página 6" in r.stderr


def test_missing_day_fails(tmp_path):
    r = ejecutar(aux(tmp_path, {1: 5, 3: 7}))
    assert r.returncode == 1
    assert "falta el día 2" in r.stderr


def test_last_day_overflowing_into_answer_key_fails(tmp_path):
    r = ejecutar(aux(tmp_path, {1: 5, 2: 6}, clave=9))
    assert r.returncode == 1
    assert "clave de respuestas" in r.stderr


def test_aux_without_day_labels_fails(tmp_path):
    ruta = tmp_path / "x.aux"
    ruta.write_text("\\relax\n", encoding="utf-8")
    assert ejecutar(ruta).returncode == 1


def test_missing_aux_fails(tmp_path):
    assert ejecutar(tmp_path / "no.aux").returncode == 1
