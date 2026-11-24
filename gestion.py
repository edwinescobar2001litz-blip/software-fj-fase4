"""Gestión en memoria de clientes, servicios y reservas (sin base de datos).

La clase :class:`SistemaGestion` encapsula las tres listas internas y expone
una API única. Así `main.py` y `menu.py` comparten las mismas reglas de
duplicados, búsquedas y cambios de estado.
"""

from entidades import Cliente
from excepciones import (
    EntidadNoEncontradaError,
    IdentificadorDuplicadoError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    SoftwareFJError,
)
from logger import registrar_excepcion
from reservas import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala
from validadores import validar_texto

# Fábricas disponibles para crear servicios desde un tipo legible.
FABRICAS_SERVICIO = {
    "sala": ReservaSala,
    "equipo": AlquilerEquipo,
    "asesoria": AsesoriaEspecializada,
}


class SistemaGestion:
    """Administra clientes, servicios y reservas mediante listas privadas."""

    def __init__(self):
        self._clientes = []
        self._servicios = []
        self._reservas = []

    # ---------- Acceso de solo lectura a las listas ----------
    @property
    def clientes(self):
        """Copia de solo lectura de la lista de clientes."""
        return tuple(self._clientes)

    @property
    def servicios(self):
        """Copia de solo lectura de la lista de servicios."""
        return tuple(self._servicios)

    @property
    def reservas(self):
        """Copia de solo lectura de la lista de reservas."""
        return tuple(self._reservas)

    # ---------- Utilidades internas ----------
    def _verificar_duplicado(self, lista, identificador, tipo):
        """Impide registrar dos entidades del mismo tipo con igual ID."""
        if any(entidad.identificador == identificador for entidad in lista):
            raise IdentificadorDuplicadoError(
                f"Ya existe un {tipo} con identificador '{identificador}'"
            )

    def _buscar(self, lista, identificador, tipo):
        """Busca por ID o lanza una excepción controlada y descriptiva."""
        id_buscado = validar_texto(identificador, f"El identificador de {tipo}")
        for entidad in lista:
            if entidad.identificador == id_buscado:
                return entidad
        raise EntidadNoEncontradaError(
            f"No existe {tipo} con identificador '{id_buscado}'"
        )

    # ---------- Altas ----------
    def registrar_cliente(self, identificador, nombre, correo, telefono):
        """Crea y almacena un cliente después de validar los datos y el ID."""
        id_cliente = validar_texto(identificador, "El identificador")
        self._verificar_duplicado(self._clientes, id_cliente, "cliente")

        cliente = Cliente(id_cliente, nombre, correo, telefono)
        self._clientes.append(cliente)
        return cliente

    def crear_servicio(self, tipo, codigo, **datos):
        """Fábrica polimórfica: crea el servicio concreto según ``tipo``."""
        clave = validar_texto(tipo, "El tipo de servicio").lower()
        if clave not in FABRICAS_SERVICIO:
            raise OperacionNoPermitidaError(
                f"Tipo de servicio '{clave}' no soportado. "
                f"Use una de: {', '.join(FABRICAS_SERVICIO)}"
            )

        id_servicio = validar_texto(codigo, "El identificador")
        self._verificar_duplicado(self._servicios, id_servicio, "servicio")

        try:
            servicio = FABRICAS_SERVICIO[clave](id_servicio, **datos)
        except TypeError as error:
            # Un argumento omitido o con nombre incorrecto se convierte en
            # excepción del sistema, conservando el mensaje original.
            raise ParametroFaltanteError(
                f"Faltan parámetros para crear un servicio '{clave}': {error}"
            ) from error

        self._servicios.append(servicio)
        return servicio

    def crear_reserva(self, codigo, id_cliente, id_servicio, duracion):
        """Integra un cliente y un servicio existentes en una nueva reserva."""
        id_reserva = validar_texto(codigo, "El código de reserva")
        self._verificar_duplicado(self._reservas, id_reserva, "reserva")

        cliente = self.buscar_cliente(id_cliente)
        servicio = self.buscar_servicio(id_servicio)
        reserva = Reserva(id_reserva, cliente, servicio, duracion)
        self._reservas.append(reserva)
        return reserva

    # ---------- Búsquedas ----------
    def buscar_cliente(self, identificador):
        """Devuelve el cliente con el ID indicado."""
        return self._buscar(self._clientes, identificador, "el cliente")

    def buscar_servicio(self, identificador):
        """Devuelve el servicio con el ID indicado."""
        return self._buscar(self._servicios, identificador, "el servicio")

    def buscar_reserva(self, identificador):
        """Devuelve la reserva con el ID indicado."""
        return self._buscar(self._reservas, identificador, "la reserva")

    # ---------- Cambios de estado ----------
    def _operar_reserva(self, accion, identificador):
        """Ejecuta confirmar/cancelar/procesar con registro centralizado."""
        reserva = self.buscar_reserva(identificador)
        try:
            return getattr(reserva, accion)()
        except SoftwareFJError as error:
            registrar_excepcion(
                f"Operación '{accion}' rechazada para {reserva.codigo}", error
            )
            raise
        except Exception as error:
            registrar_excepcion(
                f"Error inesperado en '{accion}' para {reserva.codigo}", error
            )
            raise

    def confirmar_reserva(self, identificador):
        """Confirma una reserva pendiente y calcula su costo."""
        return self._operar_reserva("confirmar", identificador)

    def cancelar_reserva(self, identificador):
        """Cancela una reserva activa."""
        return self._operar_reserva("cancelar", identificador)

    def procesar_reserva(self, identificador):
        """Procesa una reserva confirmada."""
        return self._operar_reserva("procesar", identificador)

    # ---------- Información ----------
    def resumen(self):
        """Devuelve un diccionario con los conteos actuales."""
        return {
            "clientes": len(self._clientes),
            "servicios": len(self._servicios),
            "reservas": len(self._reservas),
        }

    def listar(self):
        """Devuelve representaciones en texto de las tres colecciones."""
        return {
            "clientes": [str(cliente) for cliente in self._clientes],
            "servicios": [
                f"{servicio.identificador} | {servicio.describir()}"
                for servicio in self._servicios
            ],
            "reservas": [str(reserva) for reserva in self._reservas],
        }
