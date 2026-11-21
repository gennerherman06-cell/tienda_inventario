# Tienda e inventario: pruebas (Laboratorios 1 y 2)

    pip install -r requirements.txt
    pytest                                     # las 114 pruebas (Lab 1, Lab 2 y Actividad 4)
    pytest -m aceptacion                       # solo aceptación (6 del Lab 1 + 23 en Gherkin)
    pytest tests/aceptacion_bdd                # solo los escenarios Gherkin del Lab 2
    pytest --cov=tienda --cov-branch --cov-report=term-missing
    pytest --cucumberjson=evidencias/cucumber.json
    python reporte_aceptacion.py evidencias/cucumber.json evidencias/reporte.html

Las historias de usuario en Gherkin están en tests/aceptacion_bdd/features/.
El flujo de integración continua está en .github/workflows/pruebas.yml.

Actividad 4: pruebas de robustez en tests/robustez (pytest -m robustez).
Plantilla de reporte de defectos en .github/ISSUE_TEMPLATE/defecto.md.
