"""Modelo de producto."""
from dataclasses import dataclass

from tienda.excepciones import DatoInvalido


def es_entero(valor) -> bool:
    """corrección D-08: bool es subclase de int en Python, así que se excluye aparte."""
    return isinstance(valor, int) and not isinstance(valor, bool)


@dataclass
class Producto:
    codigo: str
    nombre: str
    precio: int          # precio unitario en pesos colombianos, sin IVA
    stock: int = 0
    stock_minimo: int = 0

    # corrección D-09: los campos numéricos se validan al crear el producto
    # y cada vez que cambian.
    _REGLAS = {
        "precio": (lambda v: es_entero(v) and v > 0, "El precio debe ser un entero mayor que cero"),
        "stock": (lambda v: es_entero(v) and v >= 0, "El stock no puede ser negativo"),
        "stock_minimo": (lambda v: es_entero(v) and v >= 0, "El stock mínimo no puede ser negativo"),
    }

    def __setattr__(self, campo, valor):
        regla = Producto._REGLAS.get(campo)
        if regla and not regla[0](valor):
            raise DatoInvalido(regla[1])
        super().__setattr__(campo, valor)

    def __post_init__(self):
        if not self.codigo or not self.codigo.strip():
            raise DatoInvalido("El código del producto es obligatorio")
        if not self.nombre or not self.nombre.strip():
            raise DatoInvalido("El nombre del producto es obligatorio")
        self.codigo = self.codigo.strip().upper()
        self.nombre = self.nombre.strip()

    @property
    def requiere_reposicion(self) -> bool:
        """Indica si el producto llegó o bajó de su stock mínimo."""
        return self.stock <= self.stock_minimo
