"""Laboratorio 3: pruebas escritas a partir de los mutantes que sobrevivieron.

La primera corrida de mutmut sobre la versión 4 dejó vivos 65 de 277 mutantes,
aunque la cobertura de líneas y ramas era del 100 %. Cada grupo de pruebas de
este archivo responde a un tipo de mutante sobreviviente.
"""

import re
from unittest.mock import Mock

import pytest

from tienda import descuentos
from tienda.carrito import Carrito
from tienda.consecutivo import ContadorVentas
from tienda.excepciones import DatoInvalido, ErrorPasarela, StockInsuficiente
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto

pytestmark = pytest.mark.mutacion


@pytest.fixture
def tienda():
    inv = Inventario()
    inv.agregar_producto(Producto("PAN01", "Pan tajado", 7_800, stock=8, stock_minimo=3))
    inv.agregar_producto(Producto("ACE01", "Aceite 3 L", 40_000, stock=5, stock_minimo=2))
    return inv


def _pasarela(**kwargs):
    pasarela = Mock(spec=PasarelaPago)
    for clave, valor in kwargs.items():
        setattr(pasarela.cobrar, clave, valor)
    return pasarela


# ---------- 1. Mensajes que lee el usuario (40 mutantes) ----------
# Con D-07 el Laboratorio 2 dejó claro que un mensaje equivocado también es un
# defecto. Estas pruebas revisan el texto exacto del mensaje.

@pytest.mark.parametrize("codigo, nombre, mensaje", [
    ("", "Pan", "El código del producto es obligatorio"),
    ("P1", "", "El nombre del producto es obligatorio"),
    ("P1", "   ", "El nombre del producto es obligatorio"),
])
def test_mensajes_al_registrar_un_producto(codigo, nombre, mensaje):
    with pytest.raises(DatoInvalido, match=f"^{mensaje}$"):
        Producto(codigo, nombre, 1_000, stock=1, stock_minimo=0)


def test_mensajes_de_los_calculos_de_dinero():
    with pytest.raises(DatoInvalido, match="^El subtotal debe ser un entero no negativo$"):
        descuentos.porcentaje_descuento(-1)
    with pytest.raises(DatoInvalido, match="^Tipo de cliente desconocido: vip$"):
        descuentos.porcentaje_descuento(1_000, "vip")
    with pytest.raises(DatoInvalido, match="^La base del IVA debe ser un entero no negativo$"):
        descuentos.calcular_iva(-1)


def test_mensajes_del_carrito(tienda):
    with pytest.raises(DatoInvalido, match="^Tipo de cliente desconocido: vip$"):
        Carrito(tienda, "vip")
    carrito = Carrito(tienda)
    with pytest.raises(DatoInvalido, match="^La cantidad debe ser un entero mayor que cero$"):
        carrito.agregar("PAN01", 0)


def test_mensajes_del_inventario(tienda):
    with pytest.raises(DatoInvalido, match="^La cantidad debe ser un entero mayor que cero$"):
        tienda.registrar_entrada("PAN01", 0)
    with pytest.raises(StockInsuficiente, match="^Stock insuficiente de ACE01: hay 5, se piden 6$"):
        tienda.registrar_salida("ACE01", 6)


def test_mensaje_cuando_el_stock_cambia_antes_de_pagar(tienda):
    carrito = Carrito(tienda)
    carrito.agregar("ACE01", 5)
    tienda.registrar_salida("ACE01", 1)          # otro cliente se llevó un aceite
    with pytest.raises(StockInsuficiente, match="^El stock de ACE01 cambió; revise su carrito$"):
        carrito.confirmar_compra(_pasarela(return_value="AUT-1"))


def test_mensajes_de_la_pasarela(tienda):
    carrito = Carrito(tienda)
    carrito.agregar("PAN01", 1)
    with pytest.raises(ErrorPasarela) as falla:
        carrito.confirmar_compra(_pasarela(side_effect=TimeoutError("sin respuesta")))
    assert re.fullmatch(r"No se pudo confirmar el pago de VENTA-\d{5} \(TimeoutError\)\. "
                        r"Verifique con el banco si se hizo el cobro antes de reintentar\.", str(falla.value))
    with pytest.raises(ErrorPasarela) as sin_codigo:
        carrito.confirmar_compra(_pasarela(return_value=None))
    assert re.fullmatch(r"La pasarela no devolvió código de autorización para VENTA-\d{5}\. "
                        r"Verifique con el banco si se hizo el cobro antes de reintentar\.",
                        str(sin_codigo.value))


def test_mensaje_de_la_pasarela_real():
    with pytest.raises(NotImplementedError,
                       match="^Conexión con el proveedor de pagos no disponible en este entorno$"):
        PasarelaPago().cobrar(10_000, "VENTA-PRUEBA")


# ---------- 2. Valores por defecto (7 mutantes) ----------

def test_el_cliente_por_defecto_es_regular():
    assert descuentos.porcentaje_descuento(250_000) == descuentos.porcentaje_descuento(250_000, "regular")
    assert descuentos.valor_descuento(250_000) == 25_000
    assert descuentos.total_a_pagar(16_800)["total"] == 19_992


def test_agregar_sin_cantidad_agrega_una_unidad(tienda):
    carrito = Carrito(tienda)
    carrito.agregar("PAN01")
    assert carrito.cantidad_de("PAN01") == 1


# ---------- 3. Huecos de comportamiento (9 mutantes) ----------

def test_rn06_el_redondeo_sube_con_medio_peso():
    # 150 x 19 % = 28,5. Con redondeo comercial (RN-06) es 29; con el redondeo
    # bancario que usa Decimal por defecto sería 28. La prueba del Laboratorio 1
    # usaba 50 x 19 % = 9,5, que da 10 con los dos métodos y no los distingue.
    assert descuentos.calcular_iva(150) == 29


def test_cantidad_de_un_producto_que_no_esta_en_el_carrito_es_cero(tienda):
    assert Carrito(tienda).cantidad_de("ACE01") == 0


def test_el_comprobante_trae_el_precio_unitario(tienda):
    carrito = Carrito(tienda)
    carrito.agregar("PAN01", 2)
    comprobante = carrito.confirmar_compra(_pasarela(return_value="AUT-1"))
    assert comprobante["productos"][0]["precio_unitario"] == 7_800


def test_contador_sin_archivo_funciona_en_memoria(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    contador = ContadorVentas()
    assert contador.siguiente() == "VENTA-00001"
    contador.confirmar()
    assert contador.siguiente() == "VENTA-00002"
    assert list(tmp_path.iterdir()) == []          # no escribió ningún archivo
