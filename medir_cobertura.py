"""Mide la cobertura de líneas del paquete `tienda` usando solo la biblioteca estándar.
Uso:  python medir_cobertura.py
(Si en el equipo está instalado pytest-cov, el equivalente es:
 pytest --cov=tienda --cov-branch --cov-report=term-missing --cov-report=html)
"""
import sys
import trace
from pathlib import Path
import pytest
RAIZ = Path(__file__).parent
PAQUETE = RAIZ / "tienda"


def main() -> int:
    tracer = trace.Trace(count=1, trace=0, ignoredirs=[sys.prefix, sys.exec_prefix])
    resultado = {}
    tracer.runfunc(
        lambda: resultado.setdefault(
            "codigo", pytest.main(["-q", "-p", "no:cacheprovider", "--junitxml=evidencias/v2_junit.xml"])
        )
    )
    conteos = tracer.results().counts
    filas, total_ej, total_cub = [], 0, 0
    for archivo in sorted(PAQUETE.glob("*.py")):
        ejecutables = {ln for ln in trace._find_executable_linenos(str(archivo)) if isinstance(ln, int) and ln > 0}
        cubiertas = {ln for (f, ln), n in conteos.items() if Path(f).resolve() == archivo.resolve() and n > 0}
        faltantes = sorted(ejecutables - cubiertas)
        ej, cub = len(ejecutables), len(ejecutables & cubiertas)
        total_ej += ej
        total_cub += cub
        pct = 100.0 if ej == 0 else cub * 100 / ej
        filas.append((f"tienda/{archivo.name}", ej, ej - cub, pct, faltantes))
    print("\nCOBERTURA DE LÍNEAS DEL PAQUETE tienda")
    print(f"{'Módulo':<26}{'Líneas':>8}{'Sin cubrir':>12}{'Cobertura':>11}   Líneas sin cubrir")
    print("-" * 80)
    for nombre, ej, falt, pct, faltantes in filas:
        print(f"{nombre:<26}{ej:>8}{falt:>12}{pct:>10.1f}%   {', '.join(map(str, faltantes)) or '-'}")
    print("-" * 80)
    pct_total = total_cub * 100 / total_ej
    print(f"{'TOTAL':<26}{total_ej:>8}{total_ej - total_cub:>12}{pct_total:>10.1f}%")
    return resultado["codigo"]


if __name__ == "__main__":
    sys.exit(main())
