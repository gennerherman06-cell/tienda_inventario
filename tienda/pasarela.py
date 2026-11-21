"""Pasarela de pago externa.
En producción esta clase se conectaría con un proveedor de pagos por internet.
En las pruebas se reemplaza por un doble de prueba (mock) para no depender de la red
ni hacer cobros reales.
"""
from tienda.excepciones import PagoRechazado


class PasarelaPago:
    def cobrar(self, valor: int, referencia: str) -> str:
        """Cobra el valor y devuelve el código de autorización.
        Lanza PagoRechazado si el proveedor no aprueba la transacción.
        """
        raise NotImplementedError("Conexión con el proveedor de pagos no disponible en este entorno")


__all__ = ["PasarelaPago", "PagoRechazado"]
