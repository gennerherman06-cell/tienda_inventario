# language: es
Característica: HU-01 Ver el total de la compra antes de pagar
  Como cliente
  quiero ver el total de mi compra con descuentos e IVA
  para saber cuánto voy a pagar antes de confirmar

  Antecedentes:
    Dado que la tienda tiene estos productos:
      | codigo | nombre                | precio  | stock | stock_minimo |
      | LEC01  | Leche 1 L             | 4500    | 24    | 6            |
      | PAN01  | Pan tajado            | 7800    | 8     | 3            |
      | ARZ01  | Arroz 5 kg            | 25000   | 10    | 3            |
      | TV001  | Televisor 50 pulgadas | 1800000 | 1     | 0            |

  Esquema del escenario: La factura aplica descuento e IVA según el cliente y el monto
    Dado un cliente <tipo>
    Cuando agrega al carrito "<productos>"
    Y consulta la factura
    Entonces la factura muestra subtotal <subtotal>, descuento <descuento>, IVA <iva> y total <total>

    Ejemplos: compras pequeñas
      | tipo      | productos        | subtotal | descuento | iva   | total |
      | regular   | 2 LEC01, 1 PAN01 | 16800    | 0         | 3192  | 19992 |
      | frecuente | 2 LEC01, 1 PAN01 | 16800    | 840       | 3032  | 18992 |

    Ejemplos: alrededor del umbral de 200000
      | tipo      | productos        | subtotal | descuento | iva    | total  |
      | regular   | 7 ARZ01, 2 PAN01 | 190600   | 0         | 36214  | 226814 |
      | regular   | 8 ARZ01          | 200000   | 20000     | 34200  | 214200 |

    Ejemplos: tope del 15 %
      | tipo      | productos | subtotal | descuento | iva    | total   |
      | frecuente | 1 TV001   | 1800000  | 270000    | 290700 | 1820700 |
