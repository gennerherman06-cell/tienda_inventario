# language: es
Característica: HU-02 Pagar el carrito
  Como cliente
  quiero pagar mi carrito
  para llevarme los productos con un comprobante de la compra

  Antecedentes:
    Dado que la tienda tiene estos productos:
      | codigo | nombre                | precio  | stock | stock_minimo |
      | LEC01  | Leche 1 L             | 4500    | 24    | 6            |
      | PAN01  | Pan tajado            | 7800    | 8     | 3            |
      | TV001  | Televisor 50 pulgadas | 1800000 | 1     | 0            |
    Y un cliente regular

  Escenario: Pago aprobado entrega comprobante y descuenta el inventario
    Dado que el cliente tiene en el carrito "2 PAN01"
    Cuando paga y el banco aprueba el pago
    Entonces recibe un comprobante con número de venta y código de autorización
    Y el carrito queda vacío
    Y el stock de "PAN01" queda en 6

  Escenario: Pago rechazado conserva el carrito y la mercancía, y se puede reintentar
    Dado que el cliente tiene en el carrito "1 TV001"
    Cuando paga y el banco rechaza el pago
    Entonces el carrito conserva "1 TV001"
    Y el stock de "TV001" queda en 1
    Cuando paga y el banco aprueba el pago
    Entonces el stock de "TV001" queda en 0

  Escenario: No se puede pagar un carrito vacío
    Cuando intenta pagar sin productos en el carrito
    Entonces el sistema rechaza con el mensaje "No hay productos en el carrito"
    Y no se le cobra nada al cliente

  Escenario: El comprobante muestra qué se compró
    Dado que el cliente tiene en el carrito "2 LEC01, 1 PAN01"
    Cuando paga y el banco aprueba el pago
    Entonces el comprobante lista estos productos:
      | codigo | nombre     | cantidad | valor |
      | LEC01  | Leche 1 L  | 2        | 9000  |
      | PAN01  | Pan tajado | 1        | 7800  |

  Escenario: Un pago rechazado no deja huecos en la numeración de ventas
    Dado que un cliente compró "1 PAN01" con pago aprobado
    Y que otro cliente intentó pagar "1 LEC01" y el banco rechazó el pago
    Cuando un tercer cliente compra "2 LEC01" con pago aprobado
    Entonces las dos ventas aprobadas tienen números consecutivos
