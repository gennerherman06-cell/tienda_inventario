"""Pruebas unitarias de Producto."""
import pytest

from tienda.excepciones import DatoInvalido
from tienda.producto import Producto

pytestmark = pytest.mark.unitaria


@pytest.mark.caja_negra
def test_crea_producto_valido_y_normaliza_codigo():
    # Arrange / Act
    p = Producto("  arz01 ", " Arroz 5 kg ", 25_000, stock=10, stock_minimo=3)
    # Assert
    assert p.codigo == "ARZ01"
    assert p.nombre == "Arroz 5 kg"
    assert p.precio == 25_000


@pytest.mark.caja_negra
@pytest.mark.parametrize(
    "codigo, nombre, precio, stock, minimo",
    [
        ("", "Arroz", 1000, 1, 0),        # código vacío
        ("   ", "Arroz", 1000, 1, 0),     # código solo espacios
        ("A1", "", 1000, 1, 0),           # nombre vacío
        ("A1", "Arroz", 0, 1, 0),         # precio cero
        ("A1", "Arroz", -5, 1, 0),        # precio negativo
        ("A1", "Arroz", 10.5, 1, 0),      # precio no entero
        ("A1", "Arroz", 1000, -1, 0),     # stock negativo
        ("A1", "Arroz", 1000, 1, -1),     # stock mínimo negativo
    ],
)
def test_rechaza_datos_invalidos(codigo, nombre, precio, stock, minimo):
    with pytest.raises(DatoInvalido):
        Producto(codigo, nombre, precio, stock=stock, stock_minimo=minimo)


@pytest.mark.valor_limite
@pytest.mark.parametrize(
    "stock, minimo, esperado",
    [
        (4, 3, False),   # justo por encima del mínimo
        (3, 3, True),    # exactamente en el mínimo
        (2, 3, True),    # por debajo del mínimo
        (0, 0, True),    # agotado y sin mínimo
    ],
)
def test_requiere_reposicion_en_los_limites(stock, minimo, esperado):
    p = Producto("X1", "Prueba", 1000, stock=stock, stock_minimo=minimo)
    assert p.requiere_reposicion is esperado


@pytest.mark.valor_limite
def test_precio_minimo_aceptado_es_un_peso():
    assert Producto("X1", "Prueba", 1).precio == 1
