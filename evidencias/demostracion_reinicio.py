"""Reproduce D-12 sobre la versión 3: la numeración vuelve a 1 al reiniciar.

Uso (desde la carpeta tienda_inventario, con el código de la versión 3):
    python evidencias/demostracion_reinicio.py
"""
import importlib
from unittest.mock import Mock

import tienda.carrito as tc
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto


def venta():
    inv = Inventario()
    inv.agregar_producto(Producto("PAN01", "Pan tajado", 7800, 8, 3))
    c = tc.Carrito(inv)
    c.agregar("PAN01", 1)
    p = Mock(spec=PasarelaPago)
    p.cobrar.return_value = "AUT-000777"
    return c.confirmar_compra(p)["referencia"]


print("Día de trabajo:     ", venta(), venta())
importlib.reload(tc)   # se cierra y se vuelve a abrir el programa
print("Después de reiniciar:", venta())
