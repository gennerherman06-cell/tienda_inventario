# Tienda e inventario: pruebas (Laboratorios 1, 2 y 3, Actividad 4)

    pip install -r requirements.txt
    pytest                                     # las 134 pruebas
    pytest -m aceptacion                       # solo aceptación (6 del Lab 1 + 23 en Gherkin)
    pytest tests/aceptacion_bdd                # solo los escenarios Gherkin del Lab 2
    pytest --cov=tienda --cov-branch --cov-report=term-missing
    pytest --cucumberjson=evidencias/cucumber.json
    python reporte_aceptacion.py evidencias/cucumber.json evidencias/reporte.html

Las historias de usuario en Gherkin están en tests/aceptacion_bdd/features/.
El flujo de integración continua está en .github/workflows/pruebas.yml.

Actividad 4: pruebas de robustez en tests/robustez (pytest -m robustez).
Plantilla de reporte de defectos en .github/ISSUE_TEMPLATE/defecto.md.

Laboratorio 3: automatización con nox y un gancho de git.

    nox                 estilo, pruebas completas con reportes y rendimiento
    nox -s rapidas      lo que corre el gancho antes de cada commit
    nox -s mutacion     pruebas de mutación con mutmut
    git config core.hooksPath .githooks    activar el gancho después de clonar
