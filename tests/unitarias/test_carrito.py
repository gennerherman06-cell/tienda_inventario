"""Pruebas unitarias del Carrito (sin cerrar la venta)."""
import pytest

from tienda.carrito import Carrito
from tienda.excepciones import DatoInvalido, ProductoNoEncontrado, StockInsuficiente

pytestmark = pytest.mark.unitaria


@pytest.mark.caja_negra
def test_subtotal_con_varios_productos(carrito):
    carrito.agregar("ARZ01", 2)    # 50.000
    carrito.agregar("CAF01", 1)    # 18.000
    assert carrito.subtotal() == 68_000


@pytest.mark.caja_negra
def test_tipo_de_cliente_invalido(inventario):
    with pytest.raises(DatoInvalido):
        Carrito(inventario, tipo_cliente="vip")


@pytest.mark.caja_negra
@pytest.mark.parametrize("cantidad", [0, -2, 1.5, True])
def test_agregar_con_cantidad_invalida(carrito, cantidad):
    with pytest.raises(DatoInvalido):
        carrito.agregar("ARZ01", cantidad)


@pytest.mark.caja_negra
def test_agregar_producto_que_no_existe(carrito):
    with pytest.raises(ProductoNoEncontrado):
        carrito.agregar("ZZZ99", 1)


@pytest.mark.valor_limite
def test_agregar_exactamente_el_stock_disponible(carrito):
    carrito.agregar("CAF01", 2)            # hay 2
    assert carrito.cantidad_de("CAF01") == 2


@pytest.mark.valor_limite
def test_agregar_una_unidad_mas_que_el_stock(carrito):
    with pytest.raises(StockInsuficiente):
        carrito.agregar("CAF01", 3)


@pytest.mark.estado
def test_estado_del_carrito_al_agregar_y_quitar(carrito):
    assert carrito.esta_vacio
    carrito.agregar("ARZ01", 1)
    carrito.agregar("ARZ01", 2)            # se acumula sobre el mismo ítem
    assert carrito.items == {"ARZ01": 3}
    carrito.quitar("arz01")
    assert carrito.esta_vacio
    carrito.quitar("NOEXISTE")             # quitar algo que no está no falla
    assert carrito.items == {}


@pytest.mark.estado
def test_no_permite_acumular_mas_unidades_que_el_stock(carrito):
    carrito.agregar("ACE01", 3)            # hay 5
    with pytest.raises(StockInsuficiente):
        carrito.agregar("ACE01", 3)        # 3 + 3 = 6 > 5
    assert carrito.cantidad_de("ACE01") == 3


@pytest.mark.caja_negra
def test_factura_del_carrito_aplica_descuento_de_cliente_frecuente(carrito_frecuente):
    carrito_frecuente.agregar("ARZ01", 2)  # 50.000 -> solo 5 % por ser frecuente
    factura = carrito_frecuente.factura()
    assert factura["descuento"] == 2_500
    assert factura["total"] == 56_525      # (50.000 - 2.500) * 1,19
