"""Reglas de descuento e IVA.
Reglas del negocio:
- Compras con subtotal desde $200.000 tienen 10 % de descuento.
- El cliente frecuente recibe 5 % adicional.
- El descuento total nunca supera el 15 %.
- El IVA (19 %) se calcula sobre el valor ya descontado.
- Los valores se redondean al peso, con redondeo comercial (0,5 sube).
"""
from decimal import ROUND_HALF_UP, Decimal

from tienda.excepciones import DatoInvalido
from tienda.producto import es_entero

UMBRAL_DESCUENTO = 200_000
PORCENTAJE_POR_MONTO = Decimal("0.10")
PORCENTAJE_FRECUENTE = Decimal("0.05")
TOPE_DESCUENTO = Decimal("0.15")
TASA_IVA = Decimal("0.19")
TIPOS_CLIENTE = ("regular", "frecuente")


def _redondear(valor: Decimal) -> int:
    return int(valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def porcentaje_descuento(subtotal: int, tipo_cliente: str = "regular") -> Decimal:
    if not es_entero(subtotal) or subtotal < 0:   # corrección D-08
        raise DatoInvalido("El subtotal debe ser un entero no negativo")
    if tipo_cliente not in TIPOS_CLIENTE:
        raise DatoInvalido(f"Tipo de cliente desconocido: {tipo_cliente}")
    porcentaje = Decimal("0")
    if subtotal >= UMBRAL_DESCUENTO:   # corrección D-02: antes era ">"
        porcentaje += PORCENTAJE_POR_MONTO
    if tipo_cliente == "frecuente":
        porcentaje += PORCENTAJE_FRECUENTE
    return min(porcentaje, TOPE_DESCUENTO)


def valor_descuento(subtotal: int, tipo_cliente: str = "regular") -> int:
    return _redondear(Decimal(subtotal) * porcentaje_descuento(subtotal, tipo_cliente))


def calcular_iva(base: int) -> int:
    if not es_entero(base) or base < 0:   # corrección D-08
        raise DatoInvalido("La base del IVA debe ser un entero no negativo")
    return _redondear(Decimal(base) * TASA_IVA)


def total_a_pagar(subtotal: int, tipo_cliente: str = "regular") -> dict:
    """Devuelve el desglose completo de la factura."""
    descuento = valor_descuento(subtotal, tipo_cliente)
    base = subtotal - descuento
    iva = calcular_iva(base)
    return {
        "subtotal": subtotal,
        "descuento": descuento,
        "base_gravable": base,
        "iva": iva,
        "total": base + iva,
    }
