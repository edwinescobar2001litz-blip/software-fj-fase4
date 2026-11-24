"""Servicios especializados de Software FJ con polimorfismo y sobrecarga."""

from abc import ABC, abstractmethod
from functools import singledispatchmethod

from entidades import Entidad
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
)
from logger import registrar_error, registrar_evento, registrar_excepcion
from validadores import (
    validar_booleano,
    validar_entero,
    validar_numero,
    validar_porcentaje,
    validar_texto,
)


# ---------------------------------------------------------------------------
# Clase abstracta Servicio
# ---------------------------------------------------------------------------
class Servicio(Entidad, ABC):
    """Clase abstracta base para todos los servicios de la empresa."""

    def __init__(self, codigo, nombre, tarifa_base, disponible=True):
        super().__init__(codigo)  # Valida el identificador en Entidad.

        # Atributos encapsulados y validados antes de registrarse.
        self._nombre = validar_texto(nombre, "El nombre del servicio", minimo=3)
        self._tarifa_base = validar_numero(tarifa_base, "La tarifa base", minimo=0)
        self._disponible = validar_booleano(disponible, "La disponibilidad")

        registrar_evento(f"Servicio creado: {self._nombre} ({self.identificador})")

    # ---------- Propiedades de solo lectura ----------
    @property
    def nombre(self):
        """Nombre comercial del servicio."""
        return self._nombre

    @property
    def tarifa_base(self):
        """Tarifa por hora (siempre positiva)."""
        return self._tarifa_base

    @property
    def disponible(self):
        """Indica si el servicio puede reservarse."""
        return self._disponible

    def verificar_disponibilidad(self):
        """Lanza una excepción propia si el servicio está fuera de servicio."""
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio {self._nombre} no está disponible"
            )
        return True

    # ----- Métodos abstractos (polimorfismo) -----
    @abstractmethod
    def calcular_costo(self, horas, **kwargs):
        """Calcula el costo base. Cada servicio lo implementa a su manera."""
        raise NotImplementedError("Cada servicio debe implementar su costo")

    @abstractmethod
    def describir(self):
        """Descripción especializada del servicio."""
        raise NotImplementedError("Cada servicio debe describirse")

    def descripcion(self):
        """Implementación del método abstracto heredado de Entidad."""
        return self.describir()

    # ----- Utilidades de validación comunes -----
    def _validar_horas(self, horas):
        """Valida la duración y evita errores de tipo antes de multiplicar."""
        return validar_numero(horas, "Las horas", minimo=0)

    def validar_parametros(self, horas, **kwargs):
        """Valida los parámetros comunes; cada servicio sobrescribe este método.

        Returns:
            Diccionario con ``horas`` validada y el resto de parámetros
            comprobados, listo para reutilizarse en el cálculo del costo.
        """
        return {"horas": self._validar_horas(horas), **kwargs}

    def _validar_total(self, total):
        """Evita cálculos inconsistentes o valores no numéricos."""
        # Primero comprobamos el tipo; el rango se valida aquí para poder
        # lanzar CalculoInconsistenteError en lugar de DatosInvalidosError.
        numero = validar_numero(total, "El total calculado")
        if numero <= 0:
            raise CalculoInconsistenteError(
                f"Cálculo inconsistente en {self._nombre}: {numero}"
            )
        return numero

    def _calcular_costo_final(self, horas, impuesto, descuento, **kwargs):
        """Núcleo común de las tres variantes sobrecargadas de ``costo_final``."""
        # La validación es polimórfica: cada servicio comprueba sus propios
        # parámetros (asistentes, cantidad, nivel, ...) antes de cotizar.
        parametros = self.validar_parametros(horas, **kwargs)
        horas_validas = parametros["horas"]
        impuesto_validado = validar_porcentaje(impuesto, "El impuesto")
        descuento_validado = validar_porcentaje(descuento, "El descuento")

        try:
            self.verificar_disponibilidad()
            base = self.calcular_costo(horas_validas, **kwargs)
            total = base * (1 + impuesto_validado) * (1 - descuento_validado)
            self._validar_total(total)
        except (ServicioNoDisponibleError, DatosInvalidosError,
                CalculoInconsistenteError) as error:
            # Se registra la causa y se relanza: las variantes sobrecargadas
            # reciben exactamente la misma excepción, sin importar el tipo de horas.
            registrar_excepcion(f"Fallo al cotizar {self.identificador}", error)
            raise
        else:
            registrar_evento(
                f"Cotización {self.identificador}: {horas_validas}h -> ${round(total, 2)}"
            )
            return round(total, 2)

    # ----- Método sobrecargado -----
    @singledispatchmethod
    def costo_final(self, horas, *, impuesto=0.0, descuento=0.0, **kwargs):
        """Variante genérica: cualquier tipo de horas, con impuesto y descuento.

        Las implementaciones registradas más abajo muestran la sobrecarga real
        según el tipo de ``horas``. Las tres comparten el mismo núcleo de cálculo
        y ahora aceptan **ambos** parámetros opcionales, defecto corregido.
        """
        return self._calcular_costo_final(horas, impuesto, descuento, **kwargs)

    @costo_final.register
    def _(self, horas: int, *, impuesto=0.0, descuento=0.0, **kwargs):
        """Sobrecarga para duraciones enteras (por ejemplo, 3 horas)."""
        return self._calcular_costo_final(horas, impuesto, descuento, **kwargs)

    @costo_final.register
    def _(self, horas: float, *, impuesto=0.0, descuento=0.0, **kwargs):
        """Sobrecarga para duraciones decimales (por ejemplo, 2.5 horas)."""
        return self._calcular_costo_final(horas, impuesto, descuento, **kwargs)


# ---------------------------------------------------------------------------
# Servicios especializados
# ---------------------------------------------------------------------------
class ReservaSala(Servicio):
    """Reserva de salas: tarifa por hora más cargo fijo de limpieza."""

    CARGO_LIMPIEZA = 20.0

    def __init__(self, codigo, capacidad, tarifa_base=50.0, disponible=True):
        super().__init__(codigo, "Reserva de Sala", tarifa_base, disponible)
        self._capacidad = validar_entero(capacidad, "La capacidad", minimo=0)

    @property
    def capacidad(self):
        """Cantidad máxima de personas de la sala."""
        return self._capacidad

    def calcular_costo(self, horas, **kwargs):
        horas = self._validar_horas(horas)
        return (self._tarifa_base * horas) + self.CARGO_LIMPIEZA

    def validar_parametros(self, horas, **kwargs):
        """Añade la regla propia de la sala: no superar su capacidad."""
        datos = super().validar_parametros(horas, **kwargs)
        if "asistentes" in kwargs:
            asistentes = validar_entero(
                kwargs["asistentes"], "Los asistentes", minimo=0
            )
            if asistentes > self._capacidad:
                raise DatosInvalidosError(
                    f"La sala admite {self._capacidad} asistentes, "
                    f"se solicitaron {asistentes}"
                )
            datos["asistentes"] = asistentes
        return datos

    def describir(self):
        return f"Sala para {self._capacidad} personas – ${self._tarifa_base}/h"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos: tarifa por hora más seguro obligatorio."""

    SEGURO = 35.0

    def __init__(self, codigo, tipo_equipo, tarifa_base=80.0, disponible=True):
        super().__init__(codigo, "Alquiler de Equipo", tarifa_base, disponible)
        self._tipo_equipo = validar_texto(tipo_equipo, "El tipo de equipo", minimo=3)

    @property
    def tipo_equipo(self):
        """Tipo de equipo alquilado."""
        return self._tipo_equipo

    def calcular_costo(self, horas, **kwargs):
        horas = self._validar_horas(horas)
        return (self._tarifa_base * horas) + self.SEGURO

    def validar_parametros(self, horas, **kwargs):
        """Añade la regla propia del alquiler: cantidad de equipos positiva."""
        datos = super().validar_parametros(horas, **kwargs)
        if "cantidad" in kwargs:
            cantidad = validar_entero(kwargs["cantidad"], "La cantidad", minimo=0)
            datos["cantidad"] = cantidad
        return datos

    def describir(self):
        return f"Equipo {self._tipo_equipo} – ${self._tarifa_base}/h + seguro"


class AsesoriaEspecializada(Servicio):
    """Asesoría: tarifa por hora con 10 % de descuento desde 5 horas."""

    UMBRAL_DESCUENTO = 5
    DESCUENTO = 0.10
    NIVELES = ("básico", "intermedio", "avanzado")

    def __init__(self, codigo, area, tarifa_base=120.0, disponible=True):
        super().__init__(codigo, "Asesoría Especializada", tarifa_base, disponible)
        self._area = validar_texto(area, "El área de asesoría", minimo=3)

    @property
    def area(self):
        """Área de especialización de la asesoría."""
        return self._area

    def calcular_costo(self, horas, **kwargs):
        horas = self._validar_horas(horas)
        subtotal = self._tarifa_base * horas
        if horas >= self.UMBRAL_DESCUENTO:
            subtotal *= (1 - self.DESCUENTO)
        return subtotal

    def validar_parametros(self, horas, **kwargs):
        """Añade la regla propia de la asesoría: nivel reconocido."""
        datos = super().validar_parametros(horas, **kwargs)
        if "nivel" in kwargs:
            nivel = validar_texto(kwargs["nivel"], "El nivel", minimo=3).lower()
            if nivel not in self.NIVELES:
                raise DatosInvalidosError(
                    f"Nivel '{nivel}' no válido. Use: {', '.join(self.NIVELES)}"
                )
            datos["nivel"] = nivel
        return datos

    def describir(self):
        return f"Asesoría en {self._area} – ${self._tarifa_base}/h"


if __name__ == "__main__":
    # Prueba secuencial del segmento de servicios.
    try:
        sala = ReservaSala("SAL-01", 20)
        print(sala.describir())
        print("Costo 3h:", sala.costo_final(3))
        print("Costo 3h + IVA:", sala.costo_final(3, impuesto=0.19))
        print("Costo 2.5h con dto:", sala.costo_final(2.5, descuento=0.10))
        print("Costo 3h con IVA y dto:", sala.costo_final(
            3, impuesto=0.19, descuento=0.10))
    except (DatosInvalidosError, ParametroFaltanteError,
            ServicioNoDisponibleError) as error:
        registrar_error(f"Error controlado en prueba de servicios: {error}")
    except Exception as error:
        registrar_excepcion("Error inesperado en prueba de servicios", error)
    finally:
        print("Fin de la prueba de servicios")

    # La validación de parámetros también es polimórfica: la sala rechaza
    # más asistentes de los que caben, antes de calcular cualquier costo.
    try:
        sala.costo_final(2, asistentes=25)
    except DatosInvalidosError as error:
        print("Validación de sala rechazada:", error)
