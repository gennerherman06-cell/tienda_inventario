# language: es
Característica: HU-03 No vender lo que no hay
  Como cliente
  no quiero que me vendan productos que no hay
  para no enterarme en la caja de que mi pedido no se puede despachar

  Antecedentes:
    Dado que la tienda tiene estos productos:
      | codigo | nombre     | precio | stock | stock_minimo |
      | PAN01  | Pan tajado | 7800   | 8     | 3            |
    Y un cliente regular
    Y que el cliente tiene en el carrito "5 PAN01"

  Escenario: Se pueden agregar las unidades que quedan hasta la última
    Cuando agrega al carrito "3 PAN01"
    Entonces el carrito conserva "8 PAN01"

  Escenario: No se puede pasar del stock sumando lo que ya está en el carrito
    Cuando intenta agregar al carrito "4 PAN01"
    Entonces el sistema rechaza la operación
    Y el carrito conserva "5 PAN01"

  Escenario: El aviso le dice al cliente cuántas unidades puede agregar todavía
    Cuando intenta agregar al carrito "4 PAN01"
    Entonces el sistema rechaza con el mensaje "Solo puede agregar 3 unidades más de PAN01"

  Escenario: Un código que no existe se rechaza sin tocar el carrito
    Cuando intenta agregar al carrito "1 XYZ01"
    Entonces el sistema rechaza con el mensaje "No existe el producto XYZ01"
    Y el carrito conserva "5 PAN01"

  Escenario: Si ya tiene todo el stock en el carrito, el aviso se lo dice
    Dado que el cliente tiene en el carrito "3 PAN01"
    Cuando intenta agregar al carrito "1 PAN01"
    Entonces el sistema rechaza con el mensaje "Ya tiene en el carrito todas las unidades de PAN01"
    Y el carrito conserva "8 PAN01"
