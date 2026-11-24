# Software FJ – Fase 4: Manejo de Excepciones

Sistema integral de gestión de clientes, servicios y reservas orientado a objetos.
Sin base de datos: usa listas internas encapsuladas y un archivo rotativo de logs
(`logs/sistema.log`).

## Integrantes del grupo

| # | Nombre | Rol | Commit principal |
|---|--------|-----|------------------|
| 1 | (completar) | Excepciones personalizadas y validadores | `feat: custom exceptions and validators` |
| 2 | (completar) | Logger y registro de trazas | `feat: logging system` |
| 3 | (completar) | Entidad abstracta y Cliente | `feat: entity and client` |
| 4 | (completar) | Servicios y sobrecarga | `feat: polymorphic services` |
| 5 | (completar) | Reservas, gestión, simulación e informe | `feat: reserves and simulation` |

## Ejecución

Requiere Python 3.8 o superior (solo biblioteca estándar).

```bash
py -3 excepciones.py     # 1. Jerarquía de excepciones
py -3 validadores.py     # 2. Validadores centralizados
py -3 logger.py          # 3. Configuración del log
py -3 entidades.py       # 4. Cliente y clase abstracta Entidad
py -3 servicios.py       # 5. Servicios polimórficos y sobrecargados
py -3 gestion.py         # 6. Listas internas y reglas de negocio
py -3 reservas.py        # 7. Máquina de estados de reserva
py -3 pruebas.py         # 8. 27 pruebas automatizadas
py -3 main.py            # 9. Simulación de 24 operaciones
py -3 menu.py            # 10. Modo interactivo
```

También puede ejecutarse `py -3 -m unittest -v pruebas` para el detalle de las pruebas.

## Estructura

| Archivo | Responsabilidad |
|---------|-----------------|
| `excepciones.py` | Jerarquía de excepciones propias (`SoftwareFJError` y derivadas) |
| `validadores.py` | Validación de texto, números, enteros, porcentajes y booleanos con encadenamiento |
| `logger.py` | Log rotativo UTF-8, rutas absolutas y `registrar_excepcion()` con traza |
| `entidades.py` | Clase abstracta `Entidad` y clase `Cliente` encapsulada |
| `servicios.py` | Clase abstracta `Servicio` y tres servicios especializados |
| `gestion.py` | `SistemaGestion`: listas privadas, altas, búsquedas y cambios de estado |
| `reservas.py` | Clase `Reserva`, enum `EstadoReserva` y transiciones controladas |
| `pruebas.py` | Pruebas `unittest` de los casos válidos y de los 8 fallos corregidos |
| `main.py` | Simulación secuencial de 21 operaciones |
| `menu.py` | Interfaz interactiva de consola |
| `informe.md` / `informe.pdf` | Documento de entrega de la Fase 4 |

## Características POO aplicadas

- **Abstracción**: `Entidad` y `Servicio` son clases abstractas (`ABC`).
- **Herencia**: `Cliente`, `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`.
- **Polimorfismo**: `calcular_costo()`, `describir()`, `descripcion()` y
  `validar_parametros()` (cada servicio añade su propia regla: aforo, cantidad
  de equipos o nivel de asesoría).
- **Encapsulamiento**: atributos privados + `@property` + listas detrás de `SistemaGestion`.
- **Sobrecarga**: `@singledispatchmethod` en `costo_final()` con `impuesto`,
  `descuento` y variantes para `int`, `float` y tipo genérico.
- **Excepciones**: personalizadas + `try/except`, `try/except/else`,
  `try/except/finally` y `raise ... from error`.

## Correcciones de la verificación secuencial

Al ejecutar cada módulo por separado y probar datos adversos se detectaron y
corrigieron ocho fallos:

1. Correo numérico → `TypeError` en la expresión regular.
2. Capacidad textual → `TypeError` al comparar con cero.
3. Tarifa textual → `TypeError` al comparar con cero.
4. Horas textuales → `TypeError` al calcular el costo.
5. `impuesto` con horas `float` → `TypeError` por sobrecarga incompleta.
6. `descuento` con horas `int` → `TypeError` por sobrecarga incompleta.
7. Cliente inválido en una reserva → `AttributeError`.
8. Duración textual en una reserva → `TypeError`.

Ahora todos esos casos producen `TipoDatoInvalidoError` (con `TypeError` como
causa encadenada) u otras excepciones propias del sistema, quedan registrados en
el log y la aplicación continúa ejecutándose.

## Evidencia

- `logs/sistema.log`: eventos, errores controlados, errores imprevistos y trazas.
- `pruebas.py`: 27 pruebas automatizadas, todas en estado **OK**.
- `main.py`: 24 operaciones (8 exitosas, 15 errores controlados, 1 imprevisto).
