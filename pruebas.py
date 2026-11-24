"""Pruebas automatizadas de la Fase 4 (biblioteca estándar ``unittest``).

Cada prueba cubre uno de los fallos detectados durante la verificación
secuencial y comprueba que ahora se produce una excepción del sistema con su
causa raíz encadenada, en lugar de un TypeError/AttributeError imprevisto.

Ejecución:
    py -3 pruebas.py
    py -3 -m unittest -v pruebas
"""

import os
import unittest

from entidades import Cliente
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    EntidadNoEncontradaError,
    IdentificadorDuplicadoError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaIncorrectaError,
    ServicioNoDisponibleError,
    SoftwareFJError,
    TipoDatoInvalidoError,
)
from gestion import SistemaGestion
from logger import ARCHIVO_LOG, registrar_evento
from reservas import EstadoReserva, Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala
from validadores import validar_entero, validar_porcentaje, validar_texto


class PruebaExcepciones(unittest.TestCase):
    """Verifica la jerarquía de excepciones personalizadas."""

    def test_jerarquia(self):
        self.assertTrue(issubclass(TipoDatoInvalidoError, DatosInvalidosError))
        self.assertTrue(issubclass(DatosInvalidosError, SoftwareFJError))
        self.assertTrue(issubclass(EntidadNoEncontradaError, ParametroFaltanteError))


class PruebaValidadores(unittest.TestCase):
    """Verifica tipos, rangos y encadenamiento de errores de tipo."""

    def test_texto_no_cadena_encadena_typeerror(self):
        with self.assertRaises(TipoDatoInvalidoError) as contexto:
            validar_texto(123, "El nombre")
        self.assertIsInstance(contexto.exception.__cause__, TypeError)

    def test_numero_texto_encadena_typeerror(self):
        with self.assertRaises(TipoDatoInvalidoError) as contexto:
            validar_entero("20", "La capacidad")
        self.assertIsInstance(contexto.exception.__cause__, TypeError)

    def test_porcentaje_fuera_de_rango(self):
        with self.assertRaises(DatosInvalidosError):
            validar_porcentaje(1.5, "El descuento")


class PruebaCliente(unittest.TestCase):
    """Verifica las validaciones encapsuladas de Cliente."""

    def test_cliente_valido(self):
        cliente = Cliente("CLI-001", "Ana Pérez", "ana@mail.com", "3001234567")
        self.assertTrue(cliente.validar())
        self.assertIn("Ana Pérez", cliente.descripcion())

    def test_correo_numerico_ya_no_es_typeerror(self):
        with self.assertRaises(TipoDatoInvalidoError) as contexto:
            Cliente("CLI-002", "Luis Gómez", 12345, "3009876543")
        self.assertIsInstance(contexto.exception.__cause__, TypeError)

    def test_nombre_corto_y_correo_invalido(self):
        with self.assertRaises(DatosInvalidosError):
            Cliente("CLI-003", "Jo", "jo@mail.com", "3011111111")
        with self.assertRaises(DatosInvalidosError):
            Cliente("CLI-004", "María López", "correo-mal", "3105554433")


class PruebaServicios(unittest.TestCase):
    """Verifica polimorfismo y las tres variantes sobrecargadas."""

    def setUp(self):
        self.sala = ReservaSala("SAL-01", 20)
        self.equipo = AlquilerEquipo("EQU-01", "Proyector", 80.0)
        self.asesoria = AsesoriaEspecializada("ASE-01", "Datos", 120.0)

    def test_polimorfismo_en_descripcion_y_costo(self):
        servicios = [self.sala, self.equipo, self.asesoria]
        descripciones = [servicio.describir() for servicio in servicios]
        self.assertTrue(any("Sala" in texto for texto in descripciones))
        self.assertTrue(any("Proyector" in texto for texto in descripciones))
        self.assertTrue(any("Datos" in texto for texto in descripciones))
        self.assertNotEqual(
            self.sala.calcular_costo(3), self.asesoria.calcular_costo(3)
        )

    def test_sobrecarga_impuesto_con_horas_enteras(self):
        self.assertEqual(self.sala.costo_final(3, impuesto=0.19), 202.3)

    def test_sobrecarga_descuento_con_horas_decimales(self):
        self.assertEqual(self.sala.costo_final(2.5, descuento=0.10), 130.5)

    def test_impuesto_y_descuento_juntos(self):
        esperado = round(170.0 * 1.19 * 0.90, 2)
        self.assertEqual(self.sala.costo_final(3, impuesto=0.19, descuento=0.10),
                         esperado)

    def test_horas_texto_encadena_typeerror(self):
        with self.assertRaises(TipoDatoInvalidoError) as contexto:
            self.sala.costo_final("3")
        self.assertIsInstance(contexto.exception.__cause__, TypeError)

    def test_capacidad_texto_y_tarifa_texto(self):
        with self.assertRaises(TipoDatoInvalidoError):
            ReservaSala("SAL-02", "20")
        with self.assertRaises(TipoDatoInvalidoError):
            ReservaSala("SAL-03", 20, "50")

    def test_servicio_no_disponible(self):
        caido = AsesoriaEspecializada("ASE-02", "Sistemas", disponible=False)
        with self.assertRaises(ServicioNoDisponibleError):
            caido.verificar_disponibilidad()
        with self.assertRaises(ServicioNoDisponibleError):
            caido.costo_final(2)

    def test_validacion_polimorfica_de_parametros(self):
        # Cada servicio añade su propia regla antes de calcular el costo.
        with self.assertRaises(DatosInvalidosError):
            self.sala.costo_final(2, asistentes=25)      # capacidad 20
        with self.assertRaises(DatosInvalidosError):
            self.equipo.costo_final(2, cantidad=0)
        with self.assertRaises(DatosInvalidosError):
            self.asesoria.costo_final(2, nivel="experto")

    def test_calculo_inconsistente_desde_la_api_publica(self):
        # 6 h de asesoría = 648; con 100 % de descuento el total sería 0.
        with self.assertRaises(CalculoInconsistenteError):
            self.asesoria.costo_final(6, descuento=1.0)


class PruebaReserva(unittest.TestCase):
    """Verifica la máquina de estados y el encadenamiento de excepciones."""

    def setUp(self):
        self.cliente = Cliente("CLI-001", "Ana Pérez", "ana@mail.com", "3001234567")
        self.sala = ReservaSala("SAL-01", 20)

    def test_ciclo_completo(self):
        reserva = Reserva("RES-001", self.cliente, self.sala, 3)
        self.assertEqual(reserva.estado, "PENDIENTE")
        self.assertEqual(reserva.confirmar(), 170.0)
        self.assertEqual(reserva.estado, "CONFIRMADA")
        reserva.procesar()
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA.value)

    def test_duracion_texto_y_negativa(self):
        with self.assertRaises(TipoDatoInvalidoError):
            Reserva("RES-002", self.cliente, self.sala, "2")
        with self.assertRaises(DatosInvalidosError):
            Reserva("RES-003", self.cliente, self.sala, -2)

    def test_colaboradores_invalidos(self):
        with self.assertRaises(TipoDatoInvalidoError) as contexto:
            Reserva("RES-004", "anonimo", self.sala, 2)
        self.assertIsInstance(contexto.exception.__cause__, TypeError)

    def test_operaciones_no_permitidas(self):
        reserva = Reserva("RES-005", self.cliente, self.sala, 2)
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.procesar()
        reserva.cancelar()
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.confirmar()

    def test_encadenamiento_servicio_caido(self):
        caido = AsesoriaEspecializada("ASE-01", "Sistemas", disponible=False)
        reserva = Reserva("RES-006", self.cliente, caido, 2)
        with self.assertRaises(ReservaIncorrectaError) as contexto:
            reserva.confirmar()
        self.assertIsInstance(contexto.exception.__cause__, ServicioNoDisponibleError)


class PruebaSistemaGestion(unittest.TestCase):
    """Verifica listas internas, duplicados, búsquedas y fábrica de servicios."""

    def setUp(self):
        self.sistema = SistemaGestion()
        self.sistema.registrar_cliente("CLI-001", "Ana Pérez", "ana@mail.com",
                                       "3001234567")

    def test_duplicados(self):
        with self.assertRaises(IdentificadorDuplicadoError):
            self.sistema.registrar_cliente("CLI-001", "Otra Ana", "otra@mail.com",
                                           "3001112222")

    def test_busqueda_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.sistema.buscar_cliente("CLI-999")

    def test_fabrica_y_parametros_faltantes(self):
        servicio = self.sistema.crear_servicio("sala", "SAL-01", capacidad=20)
        self.assertIsInstance(servicio, ReservaSala)
        with self.assertRaises(ParametroFaltanteError) as contexto:
            self.sistema.crear_servicio("sala", "SAL-02")
        self.assertIsInstance(contexto.exception.__cause__, TypeError)

    def test_reserva_integrada(self):
        self.sistema.crear_servicio("sala", "SAL-01", capacidad=20)
        reserva = self.sistema.crear_reserva("RES-001", "CLI-001", "SAL-01", 3)
        self.sistema.confirmar_reserva("RES-001")
        self.sistema.procesar_reserva("RES-001")
        self.assertEqual(reserva.estado, "PROCESADA")
        self.assertEqual(self.sistema.resumen()["reservas"], 1)


class PruebaLogger(unittest.TestCase):
    """Verifica que el archivo de log existe y sigue disponible."""

    def test_archivo_de_log(self):
        registrar_evento("Prueba automatizada del archivo de log")
        self.assertTrue(os.path.isfile(ARCHIVO_LOG))
        self.assertGreater(os.path.getsize(ARCHIVO_LOG), 0)


class PruebaCalculo(unittest.TestCase):
    """Verifica que los cálculos inconsistentes se detecten."""

    def test_total_inconsistente(self):
        servicio = ReservaSala("SAL-01", 20)
        with self.assertRaises(CalculoInconsistenteError):
            servicio._validar_total(0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
