"""Pruebas de aceptación del usuario (UAT) automatizadas.
Cada prueba corresponde a un criterio de aceptación de una historia de usuario,
escrito con la estructura Dado / Cuando / Entonces.
"""
from unittest.mock import Mock

import pytest

from tienda.carrito import Carrito
from tienda.excepciones import PagoRechazado, StockInsuficiente
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto

pytestmark = pytest.mark.aceptacion


@pytest.fixture
def tienda():
    inv = Inventario()
    inv.agregar_producto(Producto("LEC01", "Leche 1 L", 4_500, stock=24, stock_minimo=6))
    inv.agregar_producto(Producto("PAN01", "Pan tajado", 7_800, stock=8, stock_minimo=3))
    inv.agregar_producto(Producto("TV001", "Televisor 50 pulgadas", 1_800_000, stock=1))
    return inv


@pytest.fixture
def pasarela():
    p = Mock(spec=PasarelaPago)
    p.cobrar.return_value = "AUT-000777"
    return p
# HU-01: Como cliente quiero ver el total de mi compra con descuentos e IVA
#        para saber cuánto voy a pagar antes de confirmar.


def test_hu01_cliente_regular_ve_su_total_sin_descuento(tienda):
    # Dado un cliente regular con 2 litros de leche y 1 pan en el carrito
    carrito = Carrito(tienda)
    carrito.agregar("LEC01", 2)
    carrito.agregar("PAN01", 1)
    # Cuando consulta la factura
    factura = carrito.factura()
    # Entonces ve subtotal 16.800, sin descuento, IVA 3.192 y total 19.992
    assert factura == {
        "subtotal": 16_800, "descuento": 0, "base_gravable": 16_800,
        "iva": 3_192, "total": 19_992,
    }


def test_hu01_cliente_frecuente_con_compra_grande_recibe_el_maximo_descuento(tienda):
    # Dado un cliente frecuente que compra el televisor de $1.800.000
    carrito = Carrito(tienda, tipo_cliente="frecuente")
    carrito.agregar("TV001", 1)
    # Cuando consulta la factura
    factura = carrito.factura()
    # Entonces recibe el 15 % de descuento (tope) y paga 1.820.700
    assert factura["descuento"] == 270_000
    assert factura["total"] == 1_820_700
# HU-02: Como cliente quiero pagar mi carrito para llevarme los productos.


def test_hu02_pago_aprobado_entrega_comprobante(tienda, pasarela):
    # Dado un cliente con productos en el carrito
    carrito = Carrito(tienda)
    carrito.agregar("PAN01", 2)
    # Cuando paga y la pasarela aprueba
    comprobante = carrito.confirmar_compra(pasarela)
    # Entonces recibe referencia y autorización, y su carrito queda vacío
    assert comprobante["referencia"].startswith("VENTA-")
    assert comprobante["autorizacion"] == "AUT-000777"
    assert carrito.esta_vacio


def test_hu02_pago_rechazado_conserva_carrito_y_mercancia(tienda):
    # Dado un cliente con el último televisor en el carrito
    carrito = Carrito(tienda)
    carrito.agregar("TV001", 1)
    pasarela = Mock(spec=PasarelaPago)
    pasarela.cobrar.side_effect = PagoRechazado("Tarjeta rechazada")
    # Cuando intenta pagar y el banco rechaza
    with pytest.raises(PagoRechazado):
        carrito.confirmar_compra(pasarela)
    # Entonces el televisor sigue disponible y puede intentar con otro medio de pago
    assert tienda.stock_de("TV001") == 1
    assert carrito.cantidad_de("TV001") == 1
# HU-03: Como cliente no quiero que me vendan productos que no hay.


def test_hu03_no_se_vende_mas_de_lo_que_hay(tienda):
    # Dado que solo quedan 8 panes
    carrito = Carrito(tienda)
    carrito.agregar("PAN01", 5)
    # Cuando el cliente intenta agregar 4 más
    # Entonces el sistema le avisa que no hay suficientes
    with pytest.raises(StockInsuficiente):
        carrito.agregar("PAN01", 4)
# HU-04: Como administrador quiero saber qué productos debo pedir al proveedor.


def test_hu04_administrador_ve_alerta_de_reposicion_despues_de_vender(tienda, pasarela):
    # Dado que el pan tiene stock 8 y mínimo 3
    assert "PAN01" not in {p.codigo for p in tienda.productos_por_reponer()}
    # Cuando se venden 5 panes
    carrito = Carrito(tienda)
    carrito.agregar("PAN01", 5)
    carrito.confirmar_compra(pasarela)
    # Entonces el pan aparece en la lista de productos por reponer
    assert "PAN01" in {p.codigo for p in tienda.productos_por_reponer()}
