"""Clase Reserva: integra cliente, servicio, duración y estado."""

from enum import Enum

from entidades import Cliente
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    OperacionNoPermitidaError,
    ReservaIncorrectaError,
    ServicioNoDisponibleError,
    TipoDatoInvalidoError,
)
from logger import registrar_error, registrar_evento, registrar_excepcion
from servicios import ReservaSala, Servicio
from validadores import validar_numero, validar_texto


class EstadoReserva(Enum):
    """Estados permitidos de una reserva (evita cadenas mal escritas)."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"


class Reserva:
    """Reserva con la transición PENDIENTE -> CONFIRMADA -> PROCESADA / CANCELADA."""

    # Se mantiene por compatibilidad con código que consultaba este conjunto.
    ESTADOS_VALIDOS = {estado.value for estado in EstadoReserva}

    def __init__(self, codigo, cliente, servicio, duracion_horas):
        self._codigo = validar_texto(codigo, "El código de reserva", minimo=3)

        # Comprobamos las colaboraciones antes de acceder a sus atributos:
        # así un string en lugar de Cliente no provoca un AttributeError.
        if not isinstance(cliente, Cliente):
            raise TipoDatoInvalidoError(
                f"La reserva requiere un Cliente, se recibió {type(cliente).__name__}"
            ) from TypeError(f"Tipo recibido: {type(cliente).__name__}")

        if not isinstance(servicio, Servicio):
            raise TipoDatoInvalidoError(
                f"La reserva requiere un Servicio, se recibió {type(servicio).__name__}"
            ) from TypeError(f"Tipo recibido: {type(servicio).__name__}")

        self._duracion = validar_numero(duracion_horas, "La duración", minimo=0)
        self._cliente = cliente
        self._servicio = servicio
        self._estado = EstadoReserva.PENDIENTE
        self._costo = None

        registrar_evento(
            f"Reserva creada: {self._codigo} | {cliente.nombre} | "
            f"{servicio.nombre} | {self._duracion}h"
        )

    # ---------- Propiedades ----------
    @property
    def codigo(self):
        """Código único de la reserva."""
        return self._codigo

    @property
    def identificador(self):
        """Alias que permite tratar la reserva como una entidad más."""
        return self._codigo

    @property
    def estado(self):
        """Estado actual como texto (compatible con el menú y la simulación)."""
        return self._estado.value

    @property
    def cliente(self):
        """Cliente titular de la reserva."""
        return self._cliente

    @property
    def servicio(self):
        """Servicio reservado."""
        return self._servicio

    @property
    def duracion(self):
        """Duración contratada en horas."""
        return self._duracion

    @property
    def costo(self):
        """Costo calculado al confirmar (``None`` si aún no se confirmó)."""
        return self._costo

    # ---------- Máquina de estados ----------
    def confirmar(self):
        """Confirma la reserva y calcula el costo final del servicio."""
        if self._estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self.estado}"
            )

        try:
            # costo_final ya valida disponibilidad, horas, impuestos y descuentos.
            self._costo = self._servicio.costo_final(self._duracion)
        except (ServicioNoDisponibleError, DatosInvalidosError,
                CalculoInconsistenteError) as error:
            registrar_excepcion(
                f"Causa raíz al confirmar la reserva {self._codigo}", error
            )
            # Encadenamiento: se conserva la excepción original para el log.
            raise ReservaIncorrectaError(
                f"No se pudo confirmar la reserva {self._codigo}"
            ) from error
        else:
            self._estado = EstadoReserva.CONFIRMADA
            registrar_evento(
                f"Reserva confirmada: {self._codigo} | Costo: ${self._costo}"
            )
            return self._costo
        finally:
            registrar_evento(
                f"Intento de confirmación finalizado: {self._codigo}"
            )

    def cancelar(self):
        """Cancela una reserva que todavía no esté cancelada o procesada."""
        try:
            if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
                raise OperacionNoPermitidaError(
                    f"No se puede cancelar una reserva {self.estado}"
                )
            self._estado = EstadoReserva.CANCELADA
            self._costo = None
        except OperacionNoPermitidaError as error:
            registrar_error(f"Cancelación rechazada {self._codigo}: {error}")
            raise
        else:
            registrar_evento(f"Reserva cancelada: {self._codigo}")
        finally:
            registrar_evento(f"Intento de cancelación finalizado: {self._codigo}")

    def procesar(self):
        """Procesa una reserva previamente confirmada."""
        try:
            if self._estado != EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"No se puede procesar una reserva en estado {self.estado}"
                )
            if self._costo is None:
                raise CalculoInconsistenteError(
                    f"La reserva {self._codigo} no tiene un costo calculado"
                )
            self._estado = EstadoReserva.PROCESADA
        except (OperacionNoPermitidaError, CalculoInconsistenteError) as error:
            registrar_error(f"Procesamiento rechazado {self._codigo}: {error}")
            raise
        else:
            registrar_evento(
                f"Reserva procesada: {self._codigo} | ${self._costo}"
            )
        finally:
            registrar_evento(f"Intento de procesamiento finalizado: {self._codigo}")

    def validar(self):
        """Comprueba que cliente, servicio y duración sigan siendo válidos."""
        return bool(
            self.cliente.validar()
            and self.servicio.verificar_disponibilidad()
            and validar_numero(self._duracion, "La duración", minimo=0)
        )

    def __str__(self):
        importe = f"${self._costo}" if self._costo is not None else "—"
        return (f"Reserva {self._codigo} | {self.estado} | "
                f"{self.cliente.nombre} | {self.servicio.nombre} | {importe}")


if __name__ == "__main__":
    # Prueba secuencial del segmento de reservas, incluido el encadenamiento.
    cliente = Cliente("CLI-001", "Ana Pérez", "ana@mail.com", "3001234567")
    sala = ReservaSala("SAL-01", 20)
    try:
        reserva = Reserva("RES-001", cliente, sala, 3)
        reserva.confirmar()
        reserva.procesar()
    except ReservaIncorrectaError as error:
        registrar_error(f"Error encadenado en prueba de reserva: {error}")
        print("Causa raíz:", type(error.__cause__).__name__)
    except Exception as error:
        registrar_excepcion("Error inesperado en prueba de reserva", error)
    else:
        print("Reserva OK:", reserva)
    finally:
        print("Fin de la prueba de reservas")
