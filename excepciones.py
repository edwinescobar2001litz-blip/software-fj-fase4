"""Excepciones personalizadas del sistema Software FJ.

Todas las excepciones propias descienden de :class:`SoftwareFJError`, de modo
que la capa de presentación puede distinguir los fallos previstos de los
errores imprevistos de Python y mantener la aplicación en funcionamiento.
"""


class SoftwareFJError(Exception):
    """Clase base de la jerarquía de excepciones del sistema."""


class DatosInvalidosError(SoftwareFJError):
    """Se lanza cuando un dato existe pero no cumple las validaciones."""


class TipoDatoInvalidoError(DatosInvalidosError):
    """Se lanza cuando el tipo de un dato no es el esperado.

    Normalmente se encadena con un ``TypeError`` original mediante
    ``raise ... from error`` para conservar la causa raíz.
    """


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio o está vacío."""


class EntidadNoEncontradaError(ParametroFaltanteError):
    """Se lanza cuando no existe una entidad con el identificador indicado."""


class IdentificadorDuplicadoError(SoftwareFJError):
    """Se lanza al intentar registrar dos entidades con el mismo ID."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una acción en un estado inválido."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio marcado como inactivo se quiere utilizar."""


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo produce un importe ilógico (<= 0)."""


class ReservaIncorrectaError(SoftwareFJError):
    """Se lanza cuando una reserva es incorrecta o no se pudo confirmar."""
