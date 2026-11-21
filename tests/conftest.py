"""Fixtures compartidas por todas las pruebas."""
from unittest.mock import Mock

import pytest

from tienda.carrito import Carrito
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto


@pytest.fixture
def inventario():
    """Inventario nuevo en cada prueba, con tres productos de ejemplo."""
    inv = Inventario()
    inv.agregar_producto(Producto("ARZ01", "Arroz 5 kg", 25_000, stock=10, stock_minimo=3))
    inv.agregar_producto(Producto("ACE01", "Aceite 3 L", 40_000, stock=5, stock_minimo=2))
    inv.agregar_producto(Producto("CAF01", "Café 500 g", 18_000, stock=2, stock_minimo=2))
    return inv


@pytest.fixture
def carrito(inventario):
    return Carrito(inventario)


@pytest.fixture
def carrito_frecuente(inventario):
    return Carrito(inventario, tipo_cliente="frecuente")


@pytest.fixture
def pasarela_ok():
    """Doble de prueba de la pasarela que siempre aprueba el cobro."""
    pasarela = Mock(spec=PasarelaPago)
    pasarela.cobrar.return_value = "AUT-123456"
    return pasarela
