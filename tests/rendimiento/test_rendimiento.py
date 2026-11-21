"""Laboratorio 3: pruebas de rendimiento y de carga.

Los presupuestos de tiempo son para una caja de tienda de barrio: el cajero no
debe notar demora al consultar la factura o al cobrar. Un tiempo de respuesta
por debajo de 100 ms se percibe como inmediato (Nielsen, 1993); los presupuestos
de estas pruebas son mucho más estrictos porque miden solo la lógica, sin la
pantalla ni la red.
"""

import time
from unittest.mock import Mock

import pytest

from tienda.carrito import Carrito
from tienda.consecutivo import ContadorVentas
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago
from tienda.producto import Producto

pytestmark = pytest.mark.rendimiento

MILISEGUNDO = 0.001


def _tienda(productos=50, stock=10_000):
    inv = Inventario()
    for i in range(productos):
        precio = 1_000 + i * 50
        inv.agregar_producto(Producto(f"P{i:03d}", f"Producto {i}", precio, stock=stock, stock_minimo=5))
    return inv


def _pasarela():
    pasarela = Mock(spec=PasarelaPago)
    pasarela.cobrar.return_value = "AUT-000777"
    return pasarela


def test_factura_de_un_carrito_con_50_productos(benchmark):
    inv = _tienda()
    carrito = Carrito(inv, "frecuente")
    for i in range(50):
        carrito.agregar(f"P{i:03d}", 2)
    factura = benchmark(carrito.factura)
    assert factura["subtotal"] == sum((1_000 + i * 50) * 2 for i in range(50))
    assert benchmark.stats.stats.mean < 1 * MILISEGUNDO


def test_cobro_de_una_venta_de_10_productos(benchmark):
    inv = _tienda()
    pasarela = _pasarela()

    def preparar():
        carrito = Carrito(inv)
        for i in range(10):
            carrito.agregar(f"P{i:03d}", 1)
        return (carrito,), {}

    def cobrar(carrito):
        return carrito.confirmar_compra(pasarela)

    benchmark.pedantic(cobrar, setup=preparar, rounds=200)
    assert benchmark.stats.stats.mean < 2 * MILISEGUNDO


@pytest.mark.parametrize("con_archivo", [False, True], ids=["en_memoria", "en_archivo"])
def test_costo_de_guardar_la_numeracion(benchmark, tmp_path, con_archivo):
    contador = ContadorVentas(tmp_path / "consecutivo.json" if con_archivo else None)
    benchmark(contador.confirmar)
    assert benchmark.stats.stats.mean < 5 * MILISEGUNDO


def test_carga_10000_ventas_seguidas_sin_perder_unidades_ni_numeros():
    inv = _tienda(productos=1, stock=10_000)
    pasarela = _pasarela()
    referencias = []
    inicio = time.perf_counter()
    for _ in range(10_000):
        carrito = Carrito(inv)
        carrito.agregar("P000", 1)
        referencias.append(carrito.confirmar_compra(pasarela)["referencia"])
    duracion = time.perf_counter() - inicio

    numeros = [int(r.split("-")[1]) for r in referencias]
    assert inv.stock_de("P000") == 0                              # no se perdió ni se duplicó ninguna unidad
    assert numeros == list(range(numeros[0], numeros[0] + 10_000))  # numeración sin huecos ni repetidos
    assert pasarela.cobrar.call_count == 10_000
    assert duracion < 5, f"10.000 ventas tardaron {duracion:.2f} s"
