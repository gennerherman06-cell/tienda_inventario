"""Ciclo 3 de pruebas (Actividad 4): robustez, tipos de dato y fallas de la pasarela.

Estas pruebas se escribieron después de una sesión de pruebas exploratorias sobre
la versión 3. Cada una describe el comportamiento correcto; las que fallan sobre
la versión 3 son la evidencia de los defectos D-08 a D-12.
"""

from unittest.mock import Mock

import pytest

from tienda import descuentos
from tienda.carrito import Carrito
from tienda.excepciones import DatoInvalido, ErrorTienda
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto

pytestmark = pytest.mark.robustez


@pytest.fixture
def tienda():
    inv = Inventario()
    inv.agregar_producto(Producto("LEC01", "Leche 1 L", 4_500, stock=24, stock_minimo=6))
    return inv


def _pasarela(**kwargs):
    pasarela = Mock(spec=PasarelaPago)
    for clave, valor in kwargs.items():
        setattr(pasarela.cobrar, clave, valor)
    return pasarela


# ---------- D-08: booleanos aceptados como números ----------

@pytest.mark.parametrize("campo", ["precio", "stock", "stock_minimo"])
def test_d08_producto_rechaza_booleanos_en_campos_numericos(campo):
    datos = {"precio": 1_000, "stock": 5, "stock_minimo": 1}
    datos[campo] = True
    with pytest.raises(DatoInvalido):
        Producto("BOO01", "Producto de prueba", **datos)


@pytest.mark.parametrize("funcion", [descuentos.porcentaje_descuento, descuentos.calcular_iva])
def test_d08_calculos_de_dinero_rechazan_booleanos(funcion):
    with pytest.raises(DatoInvalido):
        funcion(True)


# ---------- D-09: el producto acepta datos inválidos después de creado ----------

@pytest.mark.parametrize("campo, valor", [("stock", -5), ("precio", -1), ("precio", 0), ("stock_minimo", -2)])
def test_d09_producto_no_acepta_datos_invalidos_despues_de_creado(tienda, campo, valor):
    producto = tienda.obtener("LEC01")
    with pytest.raises(DatoInvalido):
        setattr(producto, campo, valor)


# ---------- D-10: respuesta de la pasarela sin autorización ----------

@pytest.mark.parametrize("respuesta", [None, ""])
def test_d10_venta_sin_codigo_de_autorizacion_no_se_confirma(tienda, respuesta):
    carrito = Carrito(tienda)
    carrito.agregar("LEC01", 2)
    with pytest.raises(ErrorTienda):
        carrito.confirmar_compra(_pasarela(return_value=respuesta))
    assert tienda.stock_de("LEC01") == 24
    assert carrito.items == {"LEC01": 2}


# ---------- D-11: falla técnica de la pasarela ----------

@pytest.mark.parametrize("falla", [TimeoutError("sin respuesta"), ConnectionError("red caída")])
def test_d11_falla_tecnica_de_la_pasarela_se_informa_como_error_de_la_tienda(tienda, falla):
    carrito = Carrito(tienda)
    carrito.agregar("LEC01", 1)
    with pytest.raises(ErrorTienda) as error:
        carrito.confirmar_compra(_pasarela(side_effect=falla))
    assert "verifique" in str(error.value).lower()
    assert tienda.stock_de("LEC01") == 24
    assert carrito.items == {"LEC01": 1}


# ---------- D-12: la numeración de ventas se reinicia ----------

def test_d12_la_numeracion_continua_despues_de_reiniciar(tmp_path):
    from tienda.consecutivo import ContadorVentas  # no existe en la versión 3

    archivo = tmp_path / "consecutivo.json"
    hoy = ContadorVentas(archivo)
    hoy.confirmar()
    hoy.confirmar()                                   # VENTA-00001 y VENTA-00002
    despues_de_reiniciar = ContadorVentas(archivo)    # el programa se vuelve a abrir
    assert despues_de_reiniciar.siguiente() == "VENTA-00003"


def test_d12_la_caja_guarda_la_numeracion_en_el_archivo_configurado(tienda, tmp_path, monkeypatch):
    import json

    import tienda.carrito as modulo_carrito

    archivo = tmp_path / "consecutivo.json"
    monkeypatch.setattr(modulo_carrito, "_contador", modulo_carrito._contador)  # se restaura al final
    modulo_carrito.configurar_numeracion(archivo)
    carrito = Carrito(tienda)
    carrito.agregar("LEC01", 1)
    comprobante = carrito.confirmar_compra(_pasarela(return_value="AUT-000777"))
    assert comprobante["referencia"] == "VENTA-00001"
    assert json.loads(archivo.read_text(encoding="utf-8")) == {"ultima_venta": 1}
