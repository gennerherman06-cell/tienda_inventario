"""Reporte de aceptación para el dueño de la tienda.

Lee el JSON que genera pytest-bdd con --cucumberjson y arma una página HTML
con cada historia de usuario y sus escenarios en verde (cumple) o rojo (no cumple).

Uso:
    pytest --cucumberjson=evidencias/cucumber.json
    python reporte_aceptacion.py evidencias/cucumber.json evidencias/reporte.html
"""

import html
import json
import sys


def estado_escenario(escenario):
    estados = [paso["result"]["status"] for paso in escenario["steps"]]
    return "cumple" if all(e == "passed" for e in estados) else "no cumple"


def resumen(ruta_json):
    historias = []
    for feature in json.load(open(ruta_json, encoding="utf-8")):
        escenarios = [(e["name"], estado_escenario(e)) for e in feature["elements"]]
        historias.append((feature["name"], escenarios))
    return historias


def a_html(historias):
    filas = []
    for historia, escenarios in historias:
        ok = sum(1 for _, est in escenarios if est == "cumple")
        filas.append(f"<h2>{html.escape(historia)} ({ok} de {len(escenarios)})</h2><ul>")
        for nombre, est in escenarios:
            color = "#1a7f37" if est == "cumple" else "#cf222e"
            filas.append(f'<li><b style="color:{color}">{est}</b> {html.escape(nombre)}</li>')
        filas.append("</ul>")
    return ("<!DOCTYPE html><meta charset='utf-8'><title>Reporte de aceptación</title>"
            "<body style='font-family:sans-serif;max-width:800px;margin:auto'>"
            "<h1>Reporte de aceptación: tienda e inventario</h1>" + "".join(filas))


def main(ruta_json, ruta_html):
    historias = resumen(ruta_json)
    for historia, escenarios in historias:
        ok = sum(1 for _, est in escenarios if est == "cumple")
        print(f"{historia}: {ok} de {len(escenarios)} escenarios cumplen")
    with open(ruta_html, "w", encoding="utf-8") as salida:
        salida.write(a_html(historias))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
