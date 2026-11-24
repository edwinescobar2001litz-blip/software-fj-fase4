"""MODO INTERACTIVO del sistema Software FJ – Fase 4.

Permite registrar clientes, servicios y reservas en vivo desde la consola.
Toda operación se controla con excepciones y se registra en logs/sistema.log.
Comparte la clase SistemaGestion con la simulación de main.py.
"""

from logger import configurar_consola, registrar_evento, registrar_excepcion

configurar_consola()

from excepciones import (
    DatosInvalidosError,
    OperacionNoPermitidaError,
    SoftwareFJError,
)
from gestion import SistemaGestion
from validadores import validar_entero

# Lista encapsulada dentro del gestor: no se usa base de datos.
sistema = SistemaGestion()


def pedir_entero(mensaje):
    """Lee la entrada, la convierte a entero y aplica el validador común."""
    valor = input(mensaje).strip()
    try:
        numero = int(valor)  # '15' llega como texto desde la consola.
    except ValueError as error:
        raise DatosInvalidosError(
            f"Se esperaba un número entero, se recibió '{valor}'"
        ) from error
    return validar_entero(numero, "El valor numérico")


def siguiente_id_reserva():
    """Genera el siguiente código libre de reserva sin repetir los existentes."""
    usados = {reserva.codigo for reserva in sistema.reservas}
    numero = 1
    while f"RES-{numero:03d}" in usados:
        numero += 1
    return f"RES-{numero:03d}"


def registrar_cliente():
    """Opción 1: crea un cliente con validaciones robustas."""
    cliente = sistema.registrar_cliente(
        input("  ID del cliente: ").strip(),
        input("  Nombre: ").strip(),
        input("  Correo: ").strip(),
        input("  Teléfono: ").strip(),
    )
    return f"Cliente registrado: {cliente.descripcion()}"


def crear_servicio():
    """Opción 2: crea un servicio especializado (polimorfismo)."""
    print("    1. Reserva de sala   2. Alquiler de equipo   3. Asesoría")
    tipo = input("  Tipo de servicio: ").strip()
    codigo = input("  ID del servicio: ").strip()

    tipos = {"1": "sala", "2": "equipo", "3": "asesoria"}
    if tipo not in tipos:
        raise OperacionNoPermitidaError(f"Tipo de servicio inválido: '{tipo}'")

    if tipo == "1":
        datos = {"capacidad": pedir_entero("  Capacidad: ")}
    elif tipo == "2":
        datos = {"tipo_equipo": input("  Tipo de equipo: ").strip()}
    else:
        datos = {"area": input("  Área de asesoría: ").strip()}

    servicio = sistema.crear_servicio(tipos[tipo], codigo, **datos)
    return f"Servicio creado: {servicio.describir()}"


def crear_reserva():
    """Opción 3: integra cliente + servicio + duración."""
    reserva = sistema.crear_reserva(
        siguiente_id_reserva(),
        input("  ID del cliente: ").strip(),
        input("  ID del servicio: ").strip(),
        pedir_entero("  Duración en horas: "),
    )
    return f"Reserva creada: {reserva}"


def cambiar_estado(accion):
    """Opciones 4/5/6: confirma, cancela o procesa una reserva."""
    codigo = input("  ID de la reserva: ").strip()
    getattr(sistema, f"{accion}_reserva")(codigo)
    reserva = sistema.buscar_reserva(codigo)
    return f"Reserva {codigo} -> {accion.upper()} | Estado: {reserva.estado}"


def listar_todo():
    """Opción 7: muestra el estado actual de las listas internas."""
    contenido = sistema.listar()
    print(f"\n  Clientes ({len(contenido['clientes'])}):")
    for cliente in contenido["clientes"]:
        print(f"    - {cliente}")
    print(f"  Servicios ({len(contenido['servicios'])}):")
    for servicio in contenido["servicios"]:
        print(f"    - {servicio}")
    print(f"  Reservas ({len(contenido['reservas'])}):")
    for reserva in contenido["reservas"]:
        print(f"    - {reserva}")
    return "Listado mostrado"


def menu():
    """Bucle principal: nunca se detiene ante errores."""
    registrar_evento("===== INICIO DE MODO INTERACTIVO =====")
    print("\n=== SISTEMA INTEGRAL SOFTWARE FJ (modo interactivo) ===")

    while True:  # Bucle infinito controlado: solo se rompe con la opción 0.
        print("\n  1. Registrar cliente      2. Crear servicio")
        print("  3. Crear reserva          4. Confirmar reserva")
        print("  5. Cancelar reserva       6. Procesar reserva")
        print("  7. Listar todo            0. Salir")

        opcion = input("\n  Opción: ").strip()
        try:
            if opcion == "1":
                resultado = registrar_cliente()
            elif opcion == "2":
                resultado = crear_servicio()
            elif opcion == "3":
                resultado = crear_reserva()
            elif opcion == "4":
                resultado = cambiar_estado("confirmar")
            elif opcion == "5":
                resultado = cambiar_estado("cancelar")
            elif opcion == "6":
                resultado = cambiar_estado("procesar")
            elif opcion == "7":
                resultado = listar_todo()
            elif opcion == "0":
                print("  Saliendo del sistema...")
                break
            else:
                raise OperacionNoPermitidaError(
                    f"Opción '{opcion}' no válida. Intente de nuevo."
                )
        except SoftwareFJError as error:
            print(f"  Error controlado: {type(error).__name__}: {error}")
            registrar_excepcion(f"Menú op {opcion}", error)
        except Exception as error:
            print(f"  Error inesperado: {type(error).__name__}: {error}")
            registrar_excepcion(f"Menú op {opcion} INESPERADO", error)
        else:
            print(f"  {resultado}")
            registrar_evento(f"Menú op {opcion} exitosa: {resultado}")
        finally:
            # Este bloque se ejecuta siempre; aquí solo marcamos el fin del ciclo.
            pass

    registrar_evento("===== FIN DE MODO INTERACTIVO =====")


if __name__ == "__main__":
    menu()
