"""Automatización de las tareas de prueba (Laboratorio 3).

Cada sesión es una tarea que se corre con un solo comando:

    nox -s estilo        revisión de estilo con ruff
    nox -s rapidas       pruebas sin las de rendimiento, para antes de cada commit
    nox -s completas     todas las pruebas funcionales con cobertura y reportes
    nox -s rendimiento   pruebas de rendimiento y carga con pytest-benchmark
    nox -s mutacion      pruebas de mutación con mutmut (la más lenta)
    nox                  estilo, completas y rendimiento, en ese orden

python=False hace que nox use el Python ya instalado, porque en la máquina de
la tienda no siempre hay internet para crear entornos nuevos.
"""

import nox

nox.options.sessions = ["estilo", "completas", "rendimiento"]
nox.options.error_on_missing_interpreters = False

REPORTES = "reportes"


@nox.session(python=False)
def estilo(session):
    session.run("ruff", "check", "tienda", "tests", "reporte_aceptacion.py", "noxfile.py")


@nox.session(python=False)
def rapidas(session):
    session.run("pytest", "-q", "-x", "-p", "no:cacheprovider", "-m", "not rendimiento")


@nox.session(python=False)
def completas(session):
    session.run(
        "pytest", "-q", "-p", "no:cacheprovider", "-m", "not rendimiento",
        "--cov=tienda", "--cov-branch", "--cov-report=term-missing",
        f"--cov-report=html:{REPORTES}/cobertura", "--cov-fail-under=100",
        f"--junitxml={REPORTES}/junit.xml",
        f"--html={REPORTES}/pruebas.html", "--self-contained-html",
        f"--cucumberjson={REPORTES}/cucumber.json",
    )
    session.run("python", "reporte_aceptacion.py", f"{REPORTES}/cucumber.json",
                f"{REPORTES}/aceptacion.html")


@nox.session(python=False)
def rendimiento(session):
    session.run(
        "pytest", "-q", "-p", "no:cacheprovider", "-m", "rendimiento",
        "--benchmark-columns=min,mean,median,max,rounds", "--benchmark-sort=mean",
        f"--benchmark-json={REPORTES}/rendimiento.json",
    )


@nox.session(python=False)
def mutacion(session):
    session.run("mutmut", "run")
    session.run("mutmut", "results")
