"""Prueba unitaria de la pasarela real.
Confirma que la clase real no hace cobros desde el entorno de pruebas; por eso
en las pruebas de integración y aceptación se usa un mock en su lugar.
"""
import pytest

from tienda.pasarela import PasarelaPago

pytestmark = pytest.mark.unitaria


@pytest.mark.caja_negra
def test_pasarela_real_no_disponible_en_entorno_de_pruebas():
    with pytest.raises(NotImplementedError):
        PasarelaPago().cobrar(10_000, "VENTA-PRUEBA")
