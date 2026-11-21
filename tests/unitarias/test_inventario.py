"""Pruebas unitarias de Inventario."""
import pytest

from tienda.excepciones import (
    DatoInvalido,
    ProductoDuplicado,
    ProductoNoEncontrado,
    StockInsuficiente,
)
from tienda.inventario import Inventario
from tienda.producto import Producto

pytestmark = pytest.mark.unitaria
# ---------- caja negra ----------


@pytest.mark.caja_negra
def test_agregar_y_obtener_producto(inventario):
    assert len(inventario) == 3
    assert inventario.obtener("arz01").nombre == "Arroz 5 kg"   # no distingue mayúsculas


@pytest.mark.caja_negra
def test_no_permite_codigos_duplicados(inventario):
    with pytest.raises(ProductoDuplicado):
        inventario.agregar_producto(Producto("ARZ01", "Otro arroz", 20_000))


@pytest.mark.caja_negra
@pytest.mark.parametrize("codigo", ["NOEXISTE", "", None])
def test_obtener_codigo_inexistente(inventario, codigo):
    with pytest.raises(ProductoNoEncontrado):
        inventario.obtener(codigo)


@pytest.mark.caja_negra
def test_valor_total_del_inventario(inventario):
    # 25.000*10 + 40.000*5 + 18.000*2
    assert inventario.valor_total() == 486_000


@pytest.mark.caja_negra
@pytest.mark.parametrize("cantidad", [0, -1, 2.5, "3", True])
def test_cantidades_invalidas_en_entrada_y_salida(inventario, cantidad):
    with pytest.raises(DatoInvalido):
        inventario.registrar_entrada("ARZ01", cantidad)
    with pytest.raises(DatoInvalido):
        inventario.registrar_salida("ARZ01", cantidad)
# ---------- valor límite ----------


@pytest.mark.valor_limite
@pytest.mark.parametrize(
    "cantidad, stock_esperado",
    [
        (1, 4),   # mínimo válido
        (4, 1),   # justo por debajo del stock
        (5, 0),   # exactamente el stock disponible: debe permitirse
    ],
)
def test_salida_en_los_limites_validos(inventario, cantidad, stock_esperado):
    assert inventario.registrar_salida("ACE01", cantidad) == stock_esperado


@pytest.mark.valor_limite
def test_salida_una_unidad_por_encima_del_stock(inventario):
    with pytest.raises(StockInsuficiente):
        inventario.registrar_salida("ACE01", 6)
    assert inventario.stock_de("ACE01") == 5   # no se tocó el stock
# ---------- estado ----------


@pytest.mark.estado
def test_estado_del_stock_tras_entradas_y_salidas(inventario):
    assert inventario.stock_de("ARZ01") == 10            # estado inicial
    inventario.registrar_entrada("ARZ01", 5)
    assert inventario.stock_de("ARZ01") == 15
    inventario.registrar_salida("ARZ01", 12)
    assert inventario.stock_de("ARZ01") == 3             # estado final coherente


@pytest.mark.estado
def test_lista_de_reposicion_cambia_con_las_ventas(inventario):
    def codigos():
        return {p.codigo for p in inventario.productos_por_reponer()}
    assert codigos() == {"CAF01"}                        # el café ya está en el mínimo
    inventario.registrar_salida("ACE01", 3)              # el aceite queda en 2 (su mínimo)
    assert codigos() == {"CAF01", "ACE01"}
    inventario.registrar_entrada("CAF01", 10)            # se repone el café
    assert codigos() == {"ACE01"}


@pytest.mark.estado
def test_inventario_nuevo_esta_vacio():
    inv = Inventario()
    assert len(inv) == 0
    assert inv.valor_total() == 0
    assert inv.productos_por_reponer() == []
