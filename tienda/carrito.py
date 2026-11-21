"""Carrito de compras y cierre de la venta."""

from tienda import descuentos
from tienda.consecutivo import ContadorVentas
from tienda.excepciones import (
    CarritoVacio,
    DatoInvalido,
    ErrorPasarela,
    PagoRechazado,
    StockInsuficiente,
)
from tienda.inventario import Inventario
from tienda.pasarela import PasarelaPago

# corrección D-05: el número de venta solo avanza cuando el pago se aprueba.
# corrección D-12: el contador vive en ContadorVentas, que puede guardarse en un
# archivo para que la numeración siga después de reiniciar el programa.
_contador = ContadorVentas()


def configurar_numeracion(ruta) -> None:
    """Hace que la numeración de ventas se guarde en un archivo (uso en producción)."""
    global _contador
    _contador = ContadorVentas(ruta)


class Carrito:
    def __init__(self, inventario: Inventario, tipo_cliente: str = "regular"):
        if tipo_cliente not in descuentos.TIPOS_CLIENTE:
            raise DatoInvalido(f"Tipo de cliente desconocido: {tipo_cliente}")
        self._inventario = inventario
        self.tipo_cliente = tipo_cliente
        self._items: dict[str, int] = {}

    # ----- manejo de ítems -----
    def agregar(self, codigo: str, cantidad: int = 1) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise DatoInvalido("La cantidad debe ser un entero mayor que cero")
        producto = self._inventario.obtener(codigo)
        # corrección D-04: se valida lo que ya está en el carrito más lo nuevo
        en_carrito = self._items.get(producto.codigo, 0)
        if en_carrito + cantidad > producto.stock:
            # corrección D-07: el aviso dice cuántas unidades se pueden agregar todavía
            disponibles = producto.stock - en_carrito
            if disponibles == 0:
                mensaje = f"Ya tiene en el carrito todas las unidades de {producto.codigo}"
            else:
                mensaje = f"Solo puede agregar {disponibles} unidades más de {producto.codigo}"
            raise StockInsuficiente(mensaje)
        self._items[producto.codigo] = en_carrito + cantidad

    def quitar(self, codigo: str) -> None:
        clave = (codigo or "").strip().upper()
        self._items.pop(clave, None)

    def cantidad_de(self, codigo: str) -> int:
        return self._items.get((codigo or "").strip().upper(), 0)

    @property
    def items(self) -> dict[str, int]:
        return dict(self._items)

    @property
    def esta_vacio(self) -> bool:
        return not self._items

    # ----- valores -----
    def subtotal(self) -> int:
        return sum(
            self._inventario.obtener(codigo).precio * cantidad
            for codigo, cantidad in self._items.items()
        )

    def factura(self) -> dict:
        return descuentos.total_a_pagar(self.subtotal(), self.tipo_cliente)

    def detalle(self) -> list[dict]:
        """corrección D-06: líneas de la compra para el comprobante."""
        lineas = []
        for codigo, cantidad in self._items.items():
            producto = self._inventario.obtener(codigo)
            lineas.append({
                "codigo": codigo,
                "nombre": producto.nombre,
                "cantidad": cantidad,
                "precio_unitario": producto.precio,
                "valor": producto.precio * cantidad,
            })
        return lineas

    # ----- cierre de la venta -----
    def confirmar_compra(self, pasarela: PasarelaPago) -> dict:
        """Cobra el total, descuenta el inventario y vacía el carrito."""
        if self.esta_vacio:
            raise CarritoVacio("No hay productos en el carrito")

        factura = self.factura()
        productos = self.detalle()
        referencia = _contador.siguiente()

        # corrección D-03: primero se verifica el stock, luego se cobra y solo
        # con el pago aprobado se descuenta el inventario.
        for codigo, cantidad in self._items.items():
            if cantidad > self._inventario.stock_de(codigo):
                raise StockInsuficiente(f"El stock de {codigo} cambió; revise su carrito")

        try:
            autorizacion = pasarela.cobrar(factura["total"], referencia)
        except PagoRechazado:
            raise
        except Exception as falla:
            # corrección D-11: una falla técnica no se muestra como un error de Python
            raise ErrorPasarela(
                f"No se pudo confirmar el pago de {referencia} ({type(falla).__name__}). "
                "Verifique con el banco si se hizo el cobro antes de reintentar."
            ) from falla
        if not isinstance(autorizacion, str) or not autorizacion.strip():
            # corrección D-10: sin código de autorización no hay venta
            raise ErrorPasarela(
                f"La pasarela no devolvió código de autorización para {referencia}. "
                "Verifique con el banco si se hizo el cobro antes de reintentar."
            )
        _contador.confirmar()   # corrección D-05: solo aquí se gasta el número

        for codigo, cantidad in self._items.items():
            self._inventario.registrar_salida(codigo, cantidad)

        self._items.clear()
        return {**factura, "productos": productos,
                "referencia": referencia, "autorizacion": autorizacion}
