"""Pruebas de aceptación del usuario escritas en Gherkin (Laboratorio 2).

Las historias están en la carpeta features/ en español. Este archivo conecta
cada frase con el código de la tienda. Los pasos solo usan la interfaz pública
(Inventario, Carrito y la pasarela), igual que lo haría la caja de la tienda.
"""

from unittest.mock import Mock

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tienda.carrito import Carrito
from tienda.excepciones import ErrorTienda, PagoRechazado
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto

pytestmark = pytest.mark.aceptacion

scenarios("features")


# ---------- utilidades ----------

def _lista(texto):
    """Convierte "2 LEC01, 1 PAN01" en [("LEC01", 2), ("PAN01", 1)]."""
    items = []
    for parte in texto.split(","):
        cantidad, codigo = parte.strip().split()
        items.append((codigo, int(cantidad)))
    return items


def _pasarela(aprueba, autorizacion="AUT-000777"):
    pasarela = Mock(spec=PasarelaPago)
    if aprueba:
        pasarela.cobrar.return_value = autorizacion
    else:
        pasarela.cobrar.side_effect = PagoRechazado("Transacción rechazada por el banco")
    return pasarela


def _comprar(ctx, texto, aprueba):
    """Un cliente nuevo arma su carrito y paga. Devuelve el comprobante o None."""
    carrito = Carrito(ctx["inv"])
    for codigo, cantidad in _lista(texto):
        carrito.agregar(codigo, cantidad)
    try:
        comprobante = carrito.confirmar_compra(_pasarela(aprueba))
    except PagoRechazado:
        return None
    ctx["aprobadas"].append(comprobante["referencia"])
    return comprobante


def _intentar(ctx, funcion, *args):
    try:
        return funcion(*args)
    except ErrorTienda as error:
        ctx["error"] = error


@pytest.fixture
def ctx():
    return {"inv": Inventario(), "carrito": None, "factura": None,
            "comprobante": None, "pasarela": None, "error": None, "aprobadas": []}


# ---------- Dado ----------

@given("que la tienda tiene estos productos:")
def tienda_con_productos(ctx, datatable):
    encabezado, *filas = datatable
    for fila in filas:
        d = dict(zip(encabezado, fila, strict=True))
        ctx["inv"].agregar_producto(Producto(
            d["codigo"], d["nombre"], int(d["precio"]),
            stock=int(d["stock"]), stock_minimo=int(d["stock_minimo"])))


@given(parsers.parse("un cliente {tipo}"))
def un_cliente(ctx, tipo):
    ctx["carrito"] = Carrito(ctx["inv"], tipo_cliente=tipo)


@given(parsers.parse('que el cliente tiene en el carrito "{productos}"'))
@when(parsers.parse('agrega al carrito "{productos}"'))
def agregar(ctx, productos):
    for codigo, cantidad in _lista(productos):
        ctx["carrito"].agregar(codigo, cantidad)


@given(parsers.parse('que un cliente compró "{productos}" con pago aprobado'))
@given(parsers.parse('que se vendieron "{productos}" con pago aprobado'))
@when(parsers.parse('se venden "{productos}" con pago aprobado'))
@when(parsers.parse('un tercer cliente compra "{productos}" con pago aprobado'))
def venta_aprobada(ctx, productos):
    assert _comprar(ctx, productos, aprueba=True) is not None


@given(parsers.parse('que otro cliente intentó pagar "{productos}" y el banco rechazó el pago'))
@when(parsers.parse('un cliente intenta comprar "{productos}" y el banco rechaza el pago'))
def venta_rechazada(ctx, productos):
    assert _comprar(ctx, productos, aprueba=False) is None


# ---------- Cuando ----------

@when("consulta la factura")
def consultar_factura(ctx):
    ctx["factura"] = ctx["carrito"].factura()


@when("paga y el banco aprueba el pago")
def pagar_aprobado(ctx):
    ctx["pasarela"] = _pasarela(aprueba=True)
    ctx["comprobante"] = ctx["carrito"].confirmar_compra(ctx["pasarela"])


@when("paga y el banco rechaza el pago")
def pagar_rechazado(ctx):
    ctx["pasarela"] = _pasarela(aprueba=False)
    with pytest.raises(PagoRechazado):
        ctx["carrito"].confirmar_compra(ctx["pasarela"])


@when("intenta pagar sin productos en el carrito")
def pagar_vacio(ctx):
    ctx["pasarela"] = _pasarela(aprueba=True)
    _intentar(ctx, ctx["carrito"].confirmar_compra, ctx["pasarela"])


@when(parsers.parse('intenta agregar al carrito "{productos}"'))
def intentar_agregar(ctx, productos):
    for codigo, cantidad in _lista(productos):
        _intentar(ctx, ctx["carrito"].agregar, codigo, cantidad)


@when(parsers.parse('el administrador registra la llegada de {cantidad:d} unidades de "{codigo}"'))
def registrar_llegada(ctx, cantidad, codigo):
    ctx["inv"].registrar_entrada(codigo, cantidad)


@when(parsers.parse('el administrador registra el producto "{codigo}" "{nombre}" con precio '
                    '{precio:d}, stock {stock:d} y mínimo {minimo:d}'))
def registrar_producto(ctx, codigo, nombre, precio, stock, minimo):
    ctx["inv"].agregar_producto(Producto(codigo, nombre, precio, stock=stock, stock_minimo=minimo))


@when(parsers.parse('el administrador intenta registrar el producto "{codigo}" "{nombre}" con '
                    'precio {precio:d}, stock {stock:d} y mínimo {minimo:d}'))
def intentar_registrar_producto(ctx, codigo, nombre, precio, stock, minimo):
    _intentar(ctx, lambda: ctx["inv"].agregar_producto(
        Producto(codigo, nombre, precio, stock=stock, stock_minimo=minimo)))


# ---------- Entonces ----------

@then(parsers.parse("la factura muestra subtotal {subtotal:d}, descuento {descuento:d}, "
                    "IVA {iva:d} y total {total:d}"))
def verificar_factura(ctx, subtotal, descuento, iva, total):
    f = ctx["factura"]
    assert (f["subtotal"], f["descuento"], f["iva"], f["total"]) == (subtotal, descuento, iva, total)


@then("recibe un comprobante con número de venta y código de autorización")
def verificar_comprobante(ctx):
    assert ctx["comprobante"]["referencia"].startswith("VENTA-")
    assert ctx["comprobante"]["autorizacion"] == "AUT-000777"


@then("el carrito queda vacío")
def carrito_vacio(ctx):
    assert ctx["carrito"].esta_vacio


@then(parsers.parse('el stock de "{codigo}" queda en {stock:d}'))
def verificar_stock(ctx, codigo, stock):
    assert ctx["inv"].stock_de(codigo) == stock


@then(parsers.parse('el carrito conserva "{productos}"'))
def verificar_carrito(ctx, productos):
    assert ctx["carrito"].items == dict(_lista(productos))


@then(parsers.parse('el sistema rechaza con el mensaje "{mensaje}"'))
def verificar_mensaje(ctx, mensaje):
    assert ctx["error"] is not None, "Se esperaba un rechazo y la operación se aceptó"
    assert str(ctx["error"]) == mensaje


@then("el sistema rechaza la operación")
def verificar_rechazo(ctx):
    assert ctx["error"] is not None, "Se esperaba un rechazo y la operación se aceptó"


@then("no se le cobra nada al cliente")
def sin_cobro(ctx):
    ctx["pasarela"].cobrar.assert_not_called()


@then("el comprobante lista estos productos:")
def verificar_detalle(ctx, datatable):
    encabezado, *filas = datatable
    esperado = [{"codigo": f[0], "nombre": f[1], "cantidad": int(f[2]), "valor": int(f[3])}
                for f in filas]
    detalle = ctx["comprobante"].get("productos")
    assert detalle is not None, "El comprobante no trae el detalle de productos"
    obtenido = [{k: p[k] for k in ("codigo", "nombre", "cantidad", "valor")} for p in detalle]
    assert obtenido == esperado


@then("las dos ventas aprobadas tienen números consecutivos")
def verificar_consecutivos(ctx):
    primera, segunda = (int(r.split("-")[1]) for r in ctx["aprobadas"])
    assert segunda == primera + 1, f"Hay un hueco: {ctx['aprobadas'][0]} y {ctx['aprobadas'][1]}"


@then(parsers.parse('"{codigo}" aparece en la lista de reposición'))
def en_reposicion(ctx, codigo):
    assert codigo in {p.codigo for p in ctx["inv"].productos_por_reponer()}


@then(parsers.parse('"{codigo}" no aparece en la lista de reposición'))
def fuera_de_reposicion(ctx, codigo):
    assert codigo not in {p.codigo for p in ctx["inv"].productos_por_reponer()}
