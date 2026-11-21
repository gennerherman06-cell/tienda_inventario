# language: es
Característica: HU-04 Saber qué pedir al proveedor
  Como administrador
  quiero saber qué productos debo pedir al proveedor
  para no quedarme sin mercancía

  Antecedentes:
    Dado que la tienda tiene estos productos:
      | codigo | nombre     | precio | stock | stock_minimo |
      | LEC01  | Leche 1 L  | 4500   | 24    | 6            |
      | PAN01  | Pan tajado | 7800   | 8     | 3            |

  Escenario: Un producto entra en la lista de reposición después de vender
    Cuando se venden "5 PAN01" con pago aprobado
    Entonces "PAN01" aparece en la lista de reposición
    Y "LEC01" no aparece en la lista de reposición

  Escenario: Un producto que llega justo a su mínimo ya se debe pedir
    Cuando se venden "18 LEC01" con pago aprobado
    Entonces "LEC01" aparece en la lista de reposición

  Escenario: Al llegar mercancía el producto sale de la lista
    Dado que se vendieron "5 PAN01" con pago aprobado
    Cuando el administrador registra la llegada de 10 unidades de "PAN01"
    Entonces el stock de "PAN01" queda en 13
    Y "PAN01" no aparece en la lista de reposición

  Escenario: Una venta con pago rechazado no dispara la alerta
    Cuando un cliente intenta comprar "5 PAN01" y el banco rechaza el pago
    Entonces "PAN01" no aparece en la lista de reposición
