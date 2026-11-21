"""Control de inventario: altas, entradas, salidas y alertas de reposición."""
from tienda.excepciones import (
    DatoInvalido,
    ProductoDuplicado,
    ProductoNoEncontrado,
    StockInsuficiente,
)
from tienda.producto import Producto


class Inventario:
    def __init__(self):
        self._productos: dict[str, Producto] = {}

    def agregar_producto(self, producto: Producto) -> None:
        if producto.codigo in self._productos:
            raise ProductoDuplicado(f"Ya existe un producto con código {producto.codigo}")
        self._productos[producto.codigo] = producto

    def obtener(self, codigo: str) -> Producto:
        clave = (codigo or "").strip().upper()
        if clave not in self._productos:
            raise ProductoNoEncontrado(f"No existe el producto {codigo}")
        return self._productos[clave]

    def stock_de(self, codigo: str) -> int:
        return self.obtener(codigo).stock

    def registrar_entrada(self, codigo: str, cantidad: int) -> int:
        """Suma unidades al stock (compra a proveedor). Devuelve el stock nuevo."""
        self._validar_cantidad(cantidad)
        producto = self.obtener(codigo)
        producto.stock += cantidad
        return producto.stock

    def registrar_salida(self, codigo: str, cantidad: int) -> int:
        """Resta unidades del stock (venta). Devuelve el stock nuevo."""
        self._validar_cantidad(cantidad)
        producto = self.obtener(codigo)
        if cantidad > producto.stock:   # corrección D-01: antes era ">="
            raise StockInsuficiente(
                f"Stock insuficiente de {producto.codigo}: hay {producto.stock}, se piden {cantidad}"
            )
        producto.stock -= cantidad
        return producto.stock

    def productos_por_reponer(self) -> list[Producto]:
        return [p for p in self._productos.values() if p.requiere_reposicion]

    def valor_total(self) -> int:
        """Valor del inventario a precio de venta sin IVA."""
        return sum(p.precio * p.stock for p in self._productos.values())

    def __len__(self) -> int:
        return len(self._productos)

    @staticmethod
    def _validar_cantidad(cantidad: int) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise DatoInvalido("La cantidad debe ser un entero mayor que cero")
