# language: es
Característica: HU-05 Registrar productos nuevos
  Como administrador
  quiero registrar los productos que empiezo a vender
  para poder venderlos y controlar su stock desde el primer día

  Antecedentes:
    Dado que la tienda tiene estos productos:
      | codigo | nombre     | precio | stock | stock_minimo |
      | PAN01  | Pan tajado | 7800   | 8     | 3            |

  Escenario: Registro de un producto con el código escrito en minúsculas y con espacios
    Cuando el administrador registra el producto " hue01 " "Huevos AA x30" con precio 18000, stock 12 y mínimo 4
    Entonces el stock de "HUE01" queda en 12

  Esquema del escenario: Datos que el sistema no debe aceptar
    Cuando el administrador intenta registrar el producto "<codigo>" "<nombre>" con precio <precio>, stock <stock> y mínimo 2
    Entonces el sistema rechaza con el mensaje "<mensaje>"

    Ejemplos:
      | codigo | nombre        | precio | stock | mensaje                                    |
      | PAN01  | Pan integral  | 8500   | 5     | Ya existe un producto con código PAN01     |
      | CAF01  | Café 500 g    | 0      | 5     | El precio debe ser un entero mayor que cero |
      | CAF01  | Café 500 g    | 18000  | -1    | El stock no puede ser negativo             |
