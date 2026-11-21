"""Errores propios del dominio de la tienda."""


class ErrorTienda(Exception):
    """Clase base para los errores de la tienda."""


class DatoInvalido(ErrorTienda):
    """Se lanza cuando un dato de entrada no cumple las reglas del negocio."""


class ProductoNoEncontrado(ErrorTienda):
    """Se lanza cuando se busca un código que no existe en el inventario."""


class ProductoDuplicado(ErrorTienda):
    """Se lanza al intentar registrar dos veces el mismo código."""


class StockInsuficiente(ErrorTienda):
    """Se lanza cuando se pide más cantidad de la que hay disponible."""


class CarritoVacio(ErrorTienda):
    """Se lanza al intentar pagar un carrito sin productos."""


class PagoRechazado(ErrorTienda):
    """Lo lanza la pasarela de pago cuando el cobro no se aprueba."""


class ErrorPasarela(ErrorTienda):
    """corrección D-10 y D-11: la pasarela respondió algo inválido o falló por razones técnicas.

    No se sabe con certeza si el banco cobró, así que la venta no se confirma y
    el mensaje le pide al cajero verificar con el banco antes de reintentar.
    """
