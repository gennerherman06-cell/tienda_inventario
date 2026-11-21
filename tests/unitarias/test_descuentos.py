"""Pruebas unitarias de las reglas de descuento e IVA."""
from decimal import Decimal

import pytest

from tienda import descuentos
from tienda.excepciones import DatoInvalido

pytestmark = pytest.mark.unitaria
# ---------- caja blanca: una prueba por cada camino de porcentaje_descuento ----------


@pytest.mark.caja_blanca
@pytest.mark.parametrize(
    "subtotal, cliente, esperado, camino",
    [
        (100_000, "regular",   Decimal("0.00"), "ningún if se cumple"),
        (300_000, "regular",   Decimal("0.10"), "solo se cumple el if del monto"),
        (100_000, "frecuente", Decimal("0.05"), "solo se cumple el if de cliente frecuente"),
        (300_000, "frecuente", Decimal("0.15"), "se cumplen ambos y se aplica el tope"),
    ],
)
def test_caminos_de_porcentaje_descuento(subtotal, cliente, esperado, camino):
    assert descuentos.porcentaje_descuento(subtotal, cliente) == esperado, camino


@pytest.mark.caja_blanca
@pytest.mark.parametrize("subtotal", [-1, 1.5, "1000"])
def test_rama_de_validacion_de_subtotal(subtotal):
    with pytest.raises(DatoInvalido):
        descuentos.porcentaje_descuento(subtotal)


@pytest.mark.caja_blanca
def test_rama_de_validacion_de_tipo_de_cliente():
    with pytest.raises(DatoInvalido):
        descuentos.porcentaje_descuento(100_000, "vip")


@pytest.mark.caja_blanca
def test_el_tope_nunca_se_supera_aunque_cambien_las_reglas(monkeypatch):
    # Se fuerza la suma a 20 % para comprobar que la rama min(..., TOPE) funciona.
    monkeypatch.setattr(descuentos, "PORCENTAJE_FRECUENTE", Decimal("0.10"))
    assert descuentos.porcentaje_descuento(300_000, "frecuente") == Decimal("0.15")
# ---------- valor límite del umbral de $200.000 ----------


@pytest.mark.valor_limite
@pytest.mark.parametrize(
    "subtotal, esperado",
    [
        (199_999, Decimal("0.00")),   # un peso por debajo
        (200_000, Decimal("0.10")),   # exactamente en el umbral: "desde $200.000"
        (200_001, Decimal("0.10")),   # un peso por encima
        (0, Decimal("0.00")),         # menor valor posible
    ],
)
def test_umbral_de_descuento_por_monto(subtotal, esperado):
    assert descuentos.porcentaje_descuento(subtotal, "regular") == esperado
# ---------- caja negra: IVA, redondeo y factura ----------


@pytest.mark.caja_negra
@pytest.mark.parametrize(
    "base, iva",
    [
        (100_000, 19_000),
        (0, 0),
        (50, 10),      # 9,5 se redondea hacia arriba
        (49, 9),       # 9,31 se redondea hacia abajo
    ],
)
def test_calculo_de_iva_con_redondeo_comercial(base, iva):
    assert descuentos.calcular_iva(base) == iva


@pytest.mark.caja_negra
def test_iva_rechaza_base_negativa():
    with pytest.raises(DatoInvalido):
        descuentos.calcular_iva(-100)


@pytest.mark.caja_negra
def test_factura_completa_de_cliente_frecuente_con_compra_grande():
    factura = descuentos.total_a_pagar(250_000, "frecuente")
    assert factura == {
        "subtotal": 250_000,
        "descuento": 37_500,       # 15 %
        "base_gravable": 212_500,
        "iva": 40_375,             # 19 % de la base
        "total": 252_875,
    }
