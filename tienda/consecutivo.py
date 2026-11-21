"""Numeración de ventas (corrección D-12).

En la versión 3 el número de la última venta vivía en una variable del módulo
carrito.py, así que volvía a cero cada vez que se reiniciaba el programa y se
repetían números de venta. ContadorVentas guarda el último número en un archivo
JSON cuando se le da una ruta. Sin ruta funciona solo en memoria, que es lo que
usan las pruebas.
"""

import json
from pathlib import Path


class ContadorVentas:
    def __init__(self, ruta=None):
        self._ruta = Path(ruta) if ruta else None
        self._ultima = 0
        if self._ruta and self._ruta.exists():
            self._ultima = json.loads(self._ruta.read_text(encoding="utf-8"))["ultima_venta"]

    def siguiente(self) -> str:
        """Número que tendrá la próxima venta aprobada. No lo gasta (corrección D-05)."""
        return f"VENTA-{self._ultima + 1:05d}"

    def confirmar(self) -> None:
        """Gasta el número; se llama solo cuando el pago fue aprobado."""
        self._ultima += 1
        if self._ruta:
            self._ruta.write_text(json.dumps({"ultima_venta": self._ultima}), encoding="utf-8")
