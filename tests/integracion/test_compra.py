"""Pruebas de integración: Carrito + Inventario + Descuentos + Pasarela de pago.
La pasarela es un servicio externo, por eso se reemplaza por un mock. Así se puede
simular un pago aprobado o rechazado sin depender de la red.
"""
from unittest.mock import Mock

import pytest

from tienda.excepciones import CarritoVacio, PagoRechazado
from tienda.pasarela import PasarelaPago

pytestmark = pytest.mark.integracion


def test_compra_exitosa_descuenta_inventario_y_cobra_el_total(carrito, inventario, pasarela_ok):
    carrito.agregar("ARZ01", 4)            # 100.000
    carrito.agregar("ACE01", 3)            # 120.000 -> subtotal 220.000 (aplica 10 %)
    resultado = carrito.confirmar_compra(pasarela_ok)
    # el inventario quedó actualizado
    assert inventario.stock_de("ARZ01") == 6
    assert inventario.stock_de("ACE01") == 2
    # la pasarela recibió exactamente el total calculado por el módulo de descuentos
    assert resultado["total"] == 235_620   # (220.000 - 22.000) * 1,19
    pasarela_ok.cobrar.assert_called_once_with(235_620, resultado["referencia"])
    assert resultado["autorizacion"] == "AUT-123456"
    # el carrito queda listo para otra compra
    assert carrito.esta_vacio


def test_pago_rechazado_no_modifica_el_inventario(carrito, inventario):
    pasarela = Mock(spec=PasarelaPago)
    pasarela.cobrar.side_effect = PagoRechazado("Fondos insuficientes")
    carrito.agregar("ARZ01", 2)
    carrito.agregar("CAF01", 1)
    with pytest.raises(PagoRechazado):
        carrito.confirmar_compra(pasarela)
    # si no se cobró, la mercancía sigue disponible
    assert inventario.stock_de("ARZ01") == 10
    assert inventario.stock_de("CAF01") == 2
    # y el cliente no pierde su carrito
    assert carrito.items == {"ARZ01": 2, "CAF01": 1}


def test_no_se_puede_pagar_un_carrito_vacio(carrito, pasarela_ok):
    with pytest.raises(CarritoVacio):
        carrito.confirmar_compra(pasarela_ok)
    pasarela_ok.cobrar.assert_not_called()


def test_dos_compras_seguidas_tienen_referencias_distintas(carrito, pasarela_ok):
    carrito.agregar("ARZ01", 1)
    primera = carrito.confirmar_compra(pasarela_ok)
    carrito.agregar("ARZ01", 1)
    segunda = carrito.confirmar_compra(pasarela_ok)
    assert primera["referencia"] != segunda["referencia"]
    assert pasarela_ok.cobrar.call_count == 2


def test_venta_agota_producto_y_lo_marca_para_reposicion(carrito, inventario, pasarela_ok):
    carrito.agregar("ACE01", 5)            # se lleva todo el aceite
    carrito.confirmar_compra(pasarela_ok)
    assert inventario.stock_de("ACE01") == 0
    assert "ACE01" in {p.codigo for p in inventario.productos_por_reponer()}


def test_si_otro_cliente_compra_antes_no_se_cobra(inventario, pasarela_ok):
    """Prueba de regresión de D-03: el stock se revisa otra vez antes de cobrar."""
    from tienda.carrito import Carrito
    from tienda.excepciones import StockInsuficiente
    cliente_a = Carrito(inventario)
    cliente_b = Carrito(inventario)
    cliente_a.agregar("CAF01", 2)
    cliente_b.agregar("CAF01", 2)          # los dos ven 2 cafés disponibles
    cliente_b.confirmar_compra(pasarela_ok)  # B paga primero y se lleva todo
    with pytest.raises(StockInsuficiente):
        cliente_a.confirmar_compra(pasarela_ok)
    assert pasarela_ok.cobrar.call_count == 1   # a A nunca se le cobró
    assert inventario.stock_de("CAF01") == 0
