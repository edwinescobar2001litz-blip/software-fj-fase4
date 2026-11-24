"""Punto de entrada del sistema Software FJ – Fase 4.

Ejecuta 21 operaciones secuenciales (válidas e inválidas) para demostrar que
la aplicación sigue funcionando aunque se presenten errores controlados o
imprevistos. Toda la información permanece en objetos y listas en memoria;
solo los eventos y errores se escriben en ``logs/sistema.log``.
"""

from logger import configurar_consola, registrar_evento, registrar_excepcion

configurar_consola()  # UTF-8 en consola antes de imprimir cualquier mensaje.

from excepciones import SoftwareFJError
from gestion import SistemaGestion


def ejecutar_operacion(numero, descripcion, funcion):
    """Ejecuta una operación controlando CUALQUIER error y registrándolo."""
    print(f"\n--- Operación {numero}: {descripcion} ---")
    try:
        resultado = funcion()
    except SoftwareFJError as error:
        # Error previsto por el sistema: se documenta y el flujo continúa.
        print(f"  Error controlado: {type(error).__name__}: {error}")
        registrar_excepcion(f"Op {numero} [{descripcion}]", error)
    except Exception as error:
        # Error imprevisto: también se controla para garantizar estabilidad.
        print(f"  Error inesperado: {type(error).__name__}: {error}")
        registrar_excepcion(f"Op {numero} [{descripcion}] INESPERADO", error)
    else:
        # Solo se ejecuta si no hubo ninguna excepción.
        print(f"  Éxito: {resultado}")
        registrar_evento(f"Op {numero} exitosa: {resultado}")
    finally:
        # Siempre se ejecuta, haya o no error.
        print("  Operación finalizada (registro en log)")


def reserva_completa(sistema, codigo, cliente, servicio, horas):
    """Crea, confirma y procesa una reserva; devuelve su representación."""
    reserva = sistema.crear_reserva(codigo, cliente, servicio, horas)
    sistema.confirmar_reserva(reserva.codigo)
    sistema.procesar_reserva(reserva.codigo)
    return str(reserva)


def main():
    """Punto de entrada de la simulación de 21 operaciones."""
    registrar_evento("===== INICIO DE SIMULACIÓN SOFTWARE FJ =====")
    sistema = SistemaGestion()

    # Servicio dado de baja: se crea correctamente pero falla al intentar usarlo.
    servicio_caido = sistema.crear_servicio(
        "asesoria", "ASE-01", area="Sistemas", disponible=False
    )

    # --- Clientes: válidos, inválidos, duplicados y de tipo incorrecto ---
    ejecutar_operacion(1, "Cliente válido", lambda: sistema.registrar_cliente(
        "CLI-001", "Ana Pérez", "ana@softfj.com", "3001234567"
    ).descripcion())
    ejecutar_operacion(2, "Cliente con correo inválido", lambda: sistema.registrar_cliente(
        "CLI-002", "Luis Gómez", "correo-mal", "3009876543"
    ))
    ejecutar_operacion(3, "Cliente con nombre corto", lambda: sistema.registrar_cliente(
        "CLI-004", "Jo", "jo@softfj.com", "3011111111"
    ))
    ejecutar_operacion(4, "Cliente válido 2", lambda: sistema.registrar_cliente(
        "CLI-003", "María López", "maria@softfj.com", "3105554433"
    ).descripcion())
    ejecutar_operacion(5, "Cliente con ID duplicado", lambda: sistema.registrar_cliente(
        "CLI-001", "Otra Ana", "otra@softfj.com", "3001112222"
    ))
    ejecutar_operacion(6, "Cliente con correo numérico (error de tipo encadenado)",
                       lambda: sistema.registrar_cliente(
                           "CLI-005", "Carlos Ruiz", 12345, "3005556666"
                       ))

    # --- Servicios: creación correcta, tarifa inválida, tipo inválido y baja ---
    ejecutar_operacion(7, "Servicio sala válido", lambda: sistema.crear_servicio(
        "sala", "SAL-01", capacidad=20
    ).describir())
    ejecutar_operacion(8, "Servicio con tarifa inválida", lambda: sistema.crear_servicio(
        "equipo", "EQU-01", tipo_equipo="Laptop", tarifa_base=-10
    ))
    ejecutar_operacion(9, "Servicio con capacidad de tipo texto",
                       lambda: sistema.crear_servicio(
                           "sala", "SAL-02", capacidad="20"
                       ))
    ejecutar_operacion(10, "Servicio no disponible",
                       servicio_caido.verificar_disponibilidad)
    ejecutar_operacion(11, "Servicios adicionales para las reservas", lambda:
                       " | ".join(servicio.describir() for servicio in (
                           sistema.crear_servicio(
                               "equipo", "EQU-02", tipo_equipo="Proyector",
                               tarifa_base=80.0
                           ),
                           sistema.crear_servicio(
                               "asesoria", "ASE-02", area="Datos",
                               tarifa_base=120.0
                           ),
                       )))

    sala = sistema.buscar_servicio("SAL-01")

    # --- Reservas: exitosas y fallidas por distintas causas ---
    ejecutar_operacion(12, "Reserva exitosa (sala)", lambda: reserva_completa(
        sistema, "RES-001", "CLI-001", "SAL-01", 3
    ))
    ejecutar_operacion(13, "Reserva con duración inválida", lambda:
                       sistema.crear_reserva("RES-002", "CLI-001", "SAL-01", -2))
    ejecutar_operacion(14, "Reserva con cliente inexistente", lambda:
                       sistema.crear_reserva("RES-003", "CLI-999", "SAL-01", 2))
    ejecutar_operacion(15, "Confirmar reserva cancelada (operación no permitida)",
                       lambda: confirmar_reserva_cancelada(
                           sistema, "RES-004", "CLI-003", "EQU-02"
                       ))
    ejecutar_operacion(16, "Reserva con servicio no disponible", lambda:
                       sistema.confirmar_reserva(
                           sistema.crear_reserva(
                               "RES-005", "CLI-001", "ASE-01", 2
                           ).codigo
                       ))
    ejecutar_operacion(17, "Reserva exitosa con asesoría (6 horas)",
                       lambda: reserva_completa(
                           sistema, "RES-006", "CLI-003", "ASE-02", 6
                       ))

    # --- Métodos sobrecargados y errores de cálculo ---
    ejecutar_operacion(18, "Sobrecarga: impuesto con horas enteras", lambda:
                       f"Sala 3h + IVA 19 %: ${sala.costo_final(3, impuesto=0.19)}")
    ejecutar_operacion(19, "Sobrecarga: descuento con horas decimales", lambda:
                       f"Sala 2.5h con 10 % dto: "
                       f"${sala.costo_final(2.5, descuento=0.10)}")
    ejecutar_operacion(20, "Descuento fuera de rango", lambda:
                       sala.costo_final(3, descuento=1.5))
    ejecutar_operacion(21, "Error imprevisto (división por cero simulada)",
                       lambda: 10 / 0)

    # --- Casos adicionales exigidos por el enunciado ---
    asesoria = sistema.buscar_servicio("ASE-02")
    ejecutar_operacion(22, "Parámetros faltantes al crear servicio", lambda:
                       sistema.crear_servicio("equipo", "EQU-03"))
    ejecutar_operacion(23, "Validación polimórfica: asistentes > capacidad", lambda:
                       sala.costo_final(2, asistentes=25))
    ejecutar_operacion(24, "Cálculo inconsistente (descuento del 100 %)", lambda:
                       asesoria.costo_final(6, descuento=1.0))

    registrar_evento("===== FIN DE SIMULACIÓN SOFTWARE FJ =====")

    conteo = sistema.resumen()
    print("\nResumen:")
    print(f"  Clientes en memoria: {conteo['clientes']}")
    print(f"  Servicios en memoria: {conteo['servicios']}")
    print(f"  Reservas en memoria: {conteo['reservas']}")
    print("  Revisa logs/sistema.log para ver todos los eventos y errores.")


def confirmar_reserva_cancelada(sistema, codigo, cliente, servicio):
    """Cancela una reserva y después intenta confirmarla (debe fallar)."""
    reserva = sistema.crear_reserva(codigo, cliente, servicio, 2)
    sistema.cancelar_reserva(reserva.codigo)
    return sistema.confirmar_reserva(reserva.codigo)


if __name__ == "__main__":
    main()
