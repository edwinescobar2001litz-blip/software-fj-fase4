"""Validadores reutilizables del sistema Software FJ.

Este módulo centraliza las comprobaciones de tipos y rangos para que las
clases ``Cliente``, ``Servicio``, ``Reserva`` y ``SistemaGestion`` apliquen
siempre las mismas reglas. Cuando el error es de tipo se encadena la
excepción original con ``raise ... from`` para conservar la causa raíz.
"""

from numbers import Integral, Real

from excepciones import (
    DatosInvalidosError,
    ParametroFaltanteError,
    TipoDatoInvalidoError,
)


def validar_texto(valor, nombre, minimo=1):
    """Valida que ``valor`` sea texto no vacío y devuelve una copia sin espacios.

    Args:
        valor: dato recibido desde el exterior (puede ser de cualquier tipo).
        nombre: etiqueta del campo para mensajes claros de error.
        minimo: cantidad mínima de caracteres exigida.

    Raises:
        ParametroFaltanteError: si el valor es ``None`` o está vacío.
        TipoDatoInvalidoError: si el valor no es una cadena de texto.
        DatosInvalidosError: si la cadena es más corta que ``minimo``.
    """
    # Un valor ausente nunca puede continuar: es un parámetro obligatorio.
    if valor is None:
        raise ParametroFaltanteError(f"{nombre} es obligatorio")

    # Si no es texto, se informa del tipo real recibido y se encadena TypeError.
    if not isinstance(valor, str):
        raise TipoDatoInvalidoError(
            f"{nombre} debe ser texto, se recibió {type(valor).__name__}"
        ) from TypeError(f"Tipo recibido: {type(valor).__name__}")

    texto = valor.strip()  # Normalizamos espacios antes de cualquier otra regla.

    if not texto:
        raise ParametroFaltanteError(f"{nombre} es obligatorio")

    if len(texto) < minimo:
        raise DatosInvalidosError(
            f"{nombre} debe tener al menos {minimo} caracteres"
        )

    return texto


def validar_numero(valor, nombre, minimo=None, exclusivo=True):
    """Valida un número real (entero o decimal), excluyendo booleanos.

    Args:
        valor: dato a validar.
        nombre: etiqueta del campo para los mensajes.
        minimo: cota inferior opcional.
        exclusivo: si es ``True`` exige ``valor > minimo``; si no, ``valor >= minimo``.

    Returns:
        El valor original, conservando su tipo (``int`` o ``float``).
    """
    if valor is None:
        raise ParametroFaltanteError(f"{nombre} es obligatorio")

    # bool es subclase de int, por lo que se descarta explícitamente.
    if isinstance(valor, bool) or not isinstance(valor, Real):
        raise TipoDatoInvalidoError(
            f"{nombre} debe ser numérico, se recibió {type(valor).__name__}"
        ) from TypeError(f"Tipo recibido: {type(valor).__name__}")

    # Comparamos ya con un tipo numérico seguro, sin riesgo de TypeError.
    if minimo is not None:
        incumple = valor <= minimo if exclusivo else valor < minimo
        if incumple:
            operador = "mayor que" if exclusivo else "mayor o igual que"
            raise DatosInvalidosError(
                f"{nombre} debe ser {operador} {minimo}, se recibió {valor}"
            )

    return valor


def validar_entero(valor, nombre, minimo=None, exclusivo=True):
    """Valida un número entero positivo (o con la cota indicada)."""
    numero = validar_numero(valor, nombre, minimo=minimo, exclusivo=exclusivo)

    if not isinstance(numero, Integral):
        raise TipoDatoInvalidoError(
            f"{nombre} debe ser un número entero, se recibió {numero}"
        ) from TypeError(f"Se recibió el decimal {numero}")

    return int(numero)


def validar_porcentaje(valor, nombre):
    """Valida impuestos y descuentos en el rango cerrado ``[0, 1]``."""
    numero = validar_numero(valor, nombre, minimo=0, exclusivo=False)

    if numero > 1:
        raise DatosInvalidosError(
            f"{nombre} debe estar entre 0 y 1 (0 % - 100 %), se recibió {numero}"
        )

    return numero


def validar_booleano(valor, nombre):
    """Exige un booleano real en lugar de aceptar textos como 'False'."""
    if not isinstance(valor, bool):
        raise TipoDatoInvalidoError(
            f"{nombre} debe ser verdadero o falso, se recibió {type(valor).__name__}"
        ) from TypeError(f"Tipo recibido: {type(valor).__name__}")

    return valor
