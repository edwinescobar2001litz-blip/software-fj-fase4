# SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS — SOFTWARE FJ

**Componente práctico – Fase 4: Manejo de excepciones en aplicaciones orientadas a objetos**

---

## Portada

**Universidad Nacional Abierta y a Distancia – UNAD**  
Escuela de Ciencias Básicas, Tecnología e Ingeniería  
Programa: Ingeniería de Sistemas / [completar programa]  
Curso: Programación Orientada a Objetos [completar nombre exacto del curso]  
Unidad 4 – Actividad 4: Implementación del manejo de excepciones  

**Sistema Integral de Gestión de Clientes, Servicios y Reservas — Software FJ**

Grupo: [completar número]  

| # | Integrante | Rol asignado | Commit principal |
|---|------------|--------------|------------------|
| 1 | [completar] | Excepciones personalizadas | `feat: custom exceptions` |
| 2 | [completar] | Registro de logs | `feat: logging system` |
| 3 | [completar] | Entidad abstracta y Cliente | `feat: entity and client` |
| 4 | [completar] | Servicios y sobrecarga de métodos | `feat: polymorphic services` |
| 5 | [completar] | Reservas, simulación e informe | `feat: reserves and simulation` |

Fecha de entrega: 22 de noviembre de 2026

---

## 1. Introducción

El presente trabajo corresponde a la Fase 4 del proyecto asignado en el Anexo 3, consistente en el desarrollo de un **Sistema Integral de Gestión de Clientes, Servicios y Reservas** para la empresa Software FJ, que ofrece reservas de salas, alquiler de equipos y asesorías especializadas. La actividad se desarrolló de forma colaborativa por un equipo de cinco estudiantes, empleando Python como lenguaje de implementación y GitHub como entorno de control de versiones y trabajo conjunto.

El resultado de aprendizaje abordado fue *implementar el manejo de excepciones en el desarrollo de aplicaciones orientadas a objetos buscando estabilidad y robustez, permitiendo una gestión adecuada de errores en el funcionamiento de las soluciones*. En coherencia con lo anterior, se construyó una aplicación modular sin motor de base de datos, en la que toda la información se gestiona mediante objetos y listas internas, y en la que los eventos y errores se registran exclusivamente en un archivo de texto (`logs/sistema.log`).

La solución aplica de manera rigurosa los principios de abstracción, herencia, polimorfismo y encapsulamiento, e incorpora excepciones personalizadas, bloques `try/except`, `try/except/else`, `try/except/finally`, encadenamiento de excepciones mediante `raise ... from` y sobrecarga de métodos mediante `@singledispatchmethod`. Adicionalmente, se implementó un modo interactivo, una simulación de veinticuatro operaciones que combinan casos válidos e inválidos y veintisiete pruebas automatizadas, con el fin de evidenciar que la aplicación continúa operando incluso cuando se presentan fallos graves o datos incorrectos.

---

## 2. Enlace del repositorio en GitHub

**Repositorio del proyecto:** `[PEGAR AQUÍ EL ENLACE DEL REPOSITORIO GITHUB]`

Estructura del repositorio:

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Simulación de 24 operaciones y función genérica `ejecutar_operacion()` |
| `menu.py` | Modo interactivo para registrar y gestionar entidades en vivo |
| `excepciones.py` | Jerarquía de excepciones personalizadas |
| `validadores.py` | Validación centralizada de tipos, rangos y porcentajes |
| `logger.py` | Log rotativo UTF-8 con trazas completas de error |
| `entidades.py` | Clase abstracta `Entidad` y clase `Cliente` |
| `servicios.py` | Clase abstracta `Servicio` y tres servicios especializados |
| `gestion.py` | Clase `SistemaGestion`: listas internas, altas, búsquedas y estados |
| `reservas.py` | Clase `Reserva` y enum `EstadoReserva` |
| `pruebas.py` | 27 pruebas automatizadas con `unittest` |
| `.vscode/` | Configuración para ejecutar y depurar en Visual Studio Code |
| `logs/sistema.log` | Registro de eventos y errores generado en la ejecución |
| `ejecutar.bat` / `ejecutar_menu.bat` | Lanzadores para Windows |
| `README.md` | Documentación general, orden de ejecución y tabla de integrantes |

La participación de los cinco integrantes se evidencia en el historial de commits del repositorio, donde cada miembro aportó un módulo diferente, integrados posteriormente en un único proyecto funcional.

---

## 3. Desarrollo de la solución

### 3.1 Diseño orientado a objetos

- **Abstracción:** las clases `Entidad` y `Servicio` son abstractas y definen la interfaz común (`descripcion()`, `calcular_costo()`, `describir()`).
- **Herencia:** `Cliente`, `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` derivan de las clases abstractas correspondientes.
- **Polimorfismo:** cada servicio sobrescribe `calcular_costo()`, `describir()` y `validar_parametros()`; la reserva invoca `costo_final()` sin conocer la clase concreta del servicio. Así, la sala valida el aforo, el alquiler la cantidad de equipos y la asesoría el nivel solicitado.
- **Encapsulamiento:** los atributos se declaran con guion bajo (`_nombre`, `_correo`, `_telefono`, `_estado`, `_clientes`, `_servicios`, `_reservas`) y se accede a ellos mediante propiedades (`@property`) con validación centralizada en `validadores.py`.
- **Gestión de colecciones:** la clase `SistemaGestion` concentra las listas internas, el control de identificadores duplicados, las búsquedas y las transiciones de estado, de modo que `main.py` y `menu.py` compartan una sola implementación.
- **Sobrecarga:** `costo_final()` usa `@singledispatchmethod` para ofrecer tres variantes según el tipo de `horas`. Las tres aceptan `impuesto` y `descuento` opcionales, validados en el rango `[0, 1]`.

### 3.2 Estrategia de manejo de excepciones

| Excepción | Situación que controla |
|-----------|------------------------|
| `SoftwareFJError` | Clase base de la jerarquía del sistema |
| `DatosInvalidosError` | Correo, nombre, tarifa, capacidad, duración, impuestos o descuentos inválidos |
| `TipoDatoInvalidoError` | Tipo de dato incorrecto; conserva el `TypeError` original como causa |
| `ParametroFaltanteError` | Identificador, área o equipo omitido |
| `EntidadNoEncontradaError` | Búsqueda de un cliente, servicio o reserva inexistente |
| `IdentificadorDuplicadoError` | Registro de dos entidades del mismo tipo con igual ID |
| `OperacionNoPermitidaError` | Confirmar una reserva cancelada o procesar una pendiente |
| `ServicioNoDisponibleError` | Intento de usar un servicio marcado como no disponible |
| `CalculoInconsistenteError` | Costos calculados iguales o menores a cero |
| `ReservaIncorrectaError` | Duración negativa o fallo al confirmar la reserva |

Todas las operaciones se envuelven en la función `ejecutar_operacion()`, que emplea `try/except/else/finally`: captura primero las excepciones propias del sistema, después cualquier error imprevisto, ejecuta el bloque `else` únicamente cuando no hay fallos y garantiza el registro en el bloque `finally`. En `Reserva.confirmar()` y en los validadores se usa `raise ... from error` para conservar la causa original. La función `registrar_excepcion()` del logger añade la traza completa mediante `exc_info=True`, lo que facilita la depuración sin detener la ejecución.

### 3.3 Registro de eventos

El módulo `logger.py` configura un logger con codificación UTF-8, nivel `INFO`, formato de fecha, nivel, módulo y mensaje, y rotación automática del archivo a partir de 1 MB. Las rutas se calculan desde `__file__`, de modo que el registro funciona aunque el programa se lance desde otra carpeta. Cada alta de cliente, servicio o reserva, cada cambio de estado y cada error detectado —incluida su traza— queda registrado en `logs/sistema.log`, cumpliendo el requisito de no utilizar bases de datos.

---

## 4. Resultados de la ejecución

La simulación ejecutó **24 operaciones**: 8 exitosas, 15 errores controlados y 1 error inesperado (`ZeroDivisionError`), todos ellos registrados y sin interrumpir el programa. La batería `pruebas.py` ejecutó **27 pruebas automatizadas**, todas en estado **OK**. El modo interactivo fue probado con datos válidos e inválidos, confirmándose que tras cada error el menú vuelve a mostrarse normalmente.

| Operación | Resultado |
|-----------|-----------|
| 1 y 4 | Clientes válidos registrados (Ana Pérez, María López) |
| 2 y 3 | Correo inválido y nombre demasiado corto → `DatosInvalidosError` |
| 5 | Identificador de cliente duplicado → `IdentificadorDuplicadoError` |
| 6 | Correo numérico → `TipoDatoInvalidoError` con causa `TypeError` |
| 7 y 11 | Servicios de sala, equipo y asesoría creados correctamente |
| 8 y 9 | Tarifa negativa y capacidad textual → errores propios del sistema |
| 10 | Servicio no disponible → `ServicioNoDisponibleError` |
| 12 | Reserva RES-001 confirmada y procesada por `$170.0` |
| 13 y 14 | Duración negativa y cliente inexistente → errores controlados |
| 15 | Confirmar reserva cancelada → `OperacionNoPermitidaError` |
| 16 | Servicio caído → `ReservaIncorrectaError` con causa raíz registrada |
| 17 | Reserva RES-006 por `$648.0` (descuento por 6 horas) |
| 18 y 19 | Sobrecarga: `$202.3` con IVA y `$130.5` con descuento |
| 20 | Descuento del 150 % → `DatosInvalidosError` |
| 21 | División por cero → error imprevisto controlado |
| 22 | Parámetros faltantes al crear servicio → `ParametroFaltanteError` con causa `TypeError` |
| 23 | Asistentes superiores al aforo → `DatosInvalidosError` (validación polimórfica) |
| 24 | Descuento del 100 % → `CalculoInconsistenteError` |

Durante la verificación secuencial se detectaron y corrigieron ocho fallos adicionales: correo numérico, capacidad textual, tarifa textual, horas textuales y duración textual provocaban `TypeError`; `impuesto` con horas decimales y `descuento` con horas enteras provocaban `TypeError` por sobrecargas incompletas; y un cliente inválido en una reserva provocaba `AttributeError`. Todos ellos pasaron a convertirse en `TipoDatoInvalidoError` con su causa encadenada. También se corrigió el `UnicodeEncodeError` de la consola `cp1252` de Windows mediante la reconfiguración UTF-8 centralizada en `logger.py`. Estas correcciones refuerzan la evidencia de robustez del sistema.

---

## 5. Conclusiones

A partir del desarrollo de la Fase 4 se concluye que el manejo estructurado de excepciones es fundamental para garantizar la continuidad operativa de una aplicación orientada a objetos. El uso de excepciones personalizadas permitió clasificar claramente los errores —datos inválidos, parámetros faltantes, operaciones no permitidas, servicios no disponibles y cálculos inconsistentes—, mientras que el encadenamiento con `raise ... from` conservó la causa original para facilitar el diagnóstico.

La combinación de bloques `try/except/else/finally` aseguró que cada operación registrara su resultado sin interrumpir el flujo general: incluso el error inesperado de división por cero fue capturado y documentado, y el sistema continuó hasta la operación final. El archivo de logs se convirtió así en la evidencia central de estabilidad, al registrar tanto eventos normales como errores controlados, sin depender de una base de datos.

La abstracción y el polimorfismo facilitaron la extensibilidad del diseño: incorporar un nuevo servicio solo requiere heredar de `Servicio` e implementar `calcular_costo()` y `describir()`, sin modificar la lógica de `Reserva`. La sobrecarga de `costo_final()` permitió además atender escenarios de impuestos y descuentos con una interfaz uniforme. La centralización de reglas en `validadores.py` y en `SistemaGestion` evitó duplicar comprobaciones y permitió que la simulación y el modo interactivo compartieran exactamente el mismo comportamiento ante errores.

Finalmente, el trabajo colaborativo se materializó en módulos independientes integrados en un único proyecto, con responsabilidades claramente distribuidas entre los cinco integrantes y reflejadas en el historial de commits. Las correcciones derivadas de la ejecución secuencial de cada segmento y de las 27 pruebas automatizadas demuestran que la robustez no solo se declara en el código, sino que se valida ejecutando el sistema ante situaciones adversas.

---

## 6. Referencias bibliográficas

Cuevas Álvarez, A. (2016). *Python 3: curso práctico*. RAMA Editorial. https://elibronet.bibliotecavirtual.unad.edu.co/es/ereader/unad/106404?page=373

Romano, F., Baka, B., & Phillips, D. (2019). *Getting started with Python: Understand key data structures and use Python in object-oriented programming*. Packt Publishing.

Silva, F. D. (2025). *Basics of using GitHub* [Objeto virtual de información]. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75882

Van Rossum, G., & Drake Jr, F. L. (2024). *El tutorial de Python*. Python Software Foundation. https://docs.python.org/es/3.12/tutorial/errors.html

Zambrano, J. P. (2025). *Introducción al uso de GitHub* [Objeto virtual de información]. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75876
