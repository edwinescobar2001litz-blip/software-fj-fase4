"""Entidades generales y clase Cliente del sistema Software FJ."""

import re

from abc import ABC, abstractmethod

from excepciones import DatosInvalidosError
from logger import registrar_error, registrar_evento
from validadores import validar_texto

# Patrón de correo sencillo: usuario @ dominino . extensión (alfanumérica).
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$")


# ---------------------------------------------------------------------------
# Clase abstracta: Entidad
# ---------------------------------------------------------------------------
class Entidad(ABC):
    """Clase abstracta que representa una entidad general del sistema."""

    def __init__(self, identificador):
        # El validador centralizado garantiza texto no vacío y tipo correcto.
        self._identificador = validar_texto(identificador, "El identificador")

    @property
    def identificador(self):
        """Getter de solo lectura para el identificador."""
        return self._identificador

    @abstractmethod
    def descripcion(self):
        """Método abstracto: cada entidad debe describirse a sí misma."""
        raise NotImplementedError("Las clases derivadas deben implementarlo")

    def __str__(self):
        """Representación en texto de la entidad."""
        return f"{self.__class__.__name__} [{self._identificador}]"


# ---------------------------------------------------------------------------
# Clase Cliente
# ---------------------------------------------------------------------------
class Cliente(Entidad):
    """Cliente con validaciones robustas y datos personales encapsulados."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)  # Validación del ID en la clase base.

        # Inicializamos los atributos encapsulados antes de usar los setters.
        self._nombre = None
        self._correo = None
        self._telefono = None

        # Los setters contienen las validaciones, así no se duplican reglas.
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

        registrar_evento(f"Cliente creado: {self.nombre} ({self.identificador})")

    # ---------- Propiedades con validación ----------
    @property
    def nombre(self):
        """Obtiene el nombre del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        """Exige texto de al menos 3 caracteres."""
        self._nombre = validar_texto(valor, "El nombre", minimo=3)

    @property
    def correo(self):
        """Obtiene el correo del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor):
        """Valida el tipo del dato y su formato con una expresión regular."""
        correo = validar_texto(valor, "El correo")
        if not PATRON_CORREO.fullmatch(correo):
            raise DatosInvalidosError(f"Correo inválido: {correo}")
        self._correo = correo

    @property
    def telefono(self):
        """Obtiene el teléfono del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        """Acepta entre 7 y 15 dígitos, sin espacios ni signos."""
        # validar_texto lanza TipoDatoInvalidoError si llega un entero, por
        # ejemplo; con Cadena limpia comprobamos la longitud y los dígitos.
        telefono = validar_texto(valor, "El teléfono", minimo=7)
        if len(telefono) > 15 or not telefono.isdigit():
            raise DatosInvalidosError(f"Teléfono inválido: {telefono}")
        self._telefono = telefono

    def validar(self):
        """Comprueba que la instancia siga siendo coherente antes de usarla."""
        return bool(
            validar_texto(self._identificador, "El identificador")
            and validar_texto(self._nombre, "El nombre", minimo=3)
            and PATRON_CORREO.fullmatch(self._correo)
            and self._telefono.isdigit()
        )

    # ---------- Método abstracto implementado ----------
    def descripcion(self):
        """Descripción polimórfica del cliente."""
        return f"Cliente {self._nombre} – {self._correo}"


if __name__ == "__main__":
    # Prueba del segmento: muestra los bloques try/except/else/finally.
    try:
        cliente = Cliente("CLI-001", "Ana Pérez", "ana@mail.com", "3001234567")
    except (DatosInvalidosError, ValueError) as error:
        registrar_error(f"Error al crear cliente: {error}")
    else:
        print("Cliente OK:", cliente.descripcion())
        print("Validación:", cliente.validar())
    finally:
        print("Fin de la prueba de entidades y cliente")
