"""Negative and positive tests for the content validators in
tools/gen_numeros.py. Every day below is synthetic and built in memory."""

import pytest

import gen_numeros as g
from idiomas import ESPANOL


def dia(**cambios):
    """A valid day 1 (week 1: only the number 1 has arrived)."""
    base = {
        "dia": 1,
        "semana": 1,
        "tema": ESPANOL.temas[0],
        "numero": 1,
        "objeto": "toby",
        "frase": "Lucía tiene un perro.",
        "actividad": {"tipo": "traza"},
    }
    base.update(cambios)
    return base


def validar(*dias):
    g.validar_dias(list(dias), ESPANOL, len(dias))


def test_valid_day_passes():
    validar(dia())


def test_number_not_yet_introduced_fails():
    with pytest.raises(g.ErrorDeContenido, match="todavía no ha llegado"):
        validar(dia(numero=7, frase="Hay siete perros."))


def test_traced_number_not_yet_introduced_fails():
    d = dia(actividad={"tipo": "traza", "numero": 5})
    with pytest.raises(g.ErrorDeContenido, match="todavía no ha llegado"):
        g.render_actividad(d, ESPANOL)


def test_coloured_number_not_yet_introduced_fails():
    d = dia(actividad={"tipo": "colorea", "objeto": "toby", "total": 12, "cuantas": 9})
    with pytest.raises(g.ErrorDeContenido, match="todavía no ha llegado"):
        g.render_actividad(d, ESPANOL)


def test_activity_before_its_week_fails():
    d = dia(actividad={"tipo": "suma"})
    with pytest.raises(g.ErrorDeContenido, match="no llega hasta la semana"):
        g.render_actividad(d, ESPANOL)


@pytest.mark.parametrize(
    "cambio, mensaje",
    [
        ({"semana": 2}, "es de la semana 1"),
        ({"tema": "otro tema"}, "el tema de la semana 1"),
        ({"objeto": "inexistente"}, "no hay dibujo"),
        ({"frase": "Hola."}, "la frase tiene que decir el número"),
        ({"actividad": {"tipo": "dibuja"}}, "se traza"),
    ],
)
def test_structural_errors_fail(cambio, mensaje):
    with pytest.raises(g.ErrorDeContenido, match=mensaje):
        validar(dia(**cambio))


def test_missing_and_repeated_days_fail():
    with pytest.raises(g.ErrorDeContenido, match="sin huecos ni repetidos"):
        g.validar_dias([dia(), dia()], ESPANOL, 2)
