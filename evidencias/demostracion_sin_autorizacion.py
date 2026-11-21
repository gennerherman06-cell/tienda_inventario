"""Reproduce D-10 sobre la versión 3: venta confirmada sin código de autorización.

Uso (desde la carpeta tienda_inventario, con el código de la versión 3):
    python evidencias/demostracion_sin_autorizacion.py
"""
from unittest.mock import Mock

from tienda.carrito import Carrito
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto

inv = Inventario()
inv.agregar_producto(Producto("LEC01", "Leche 1 L", 4500, 24, 6))
c = Carrito(inv)
c.agregar("LEC01", 2)
p = Mock(spec=PasarelaPago)
p.cobrar.return_value = None
comp = c.confirmar_compra(p)
print("Comprobante:", comp["referencia"], "| autorización:", comp["autorizacion"], "| total:", comp["total"])
print("Stock de LEC01 después de la venta:", inv.stock_de("LEC01"))
