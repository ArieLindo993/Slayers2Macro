# Historial de versiones

[Português](../CHANGELOG.md) · [English](CHANGELOG.en.md) · **Español** · [Guía de uso](README.es.md)

Las entradas anteriores se resumen a continuación. El [historial en portugués](../CHANGELOG.md) incluye investigaciones y validaciones detalladas. Las pruebas automáticas y con capturas no garantizan sesiones ininterrumpidas en el juego.

## [7.4.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.4.0)

- Interfaz en portugués (predeterminado), inglés y español, seleccionable en **Configurar → Idioma y atajos**. Se aplica al guardar sin perder historial ni contadores.
- Traducción de ventana principal, estados de pesca, ajustes, historial, selección manual y CSV exportado mediante el botón. Los nombres del juego y los formatos de registros técnicos permanecen estables.
- Atajos configurables para iniciar/pausar, marcar agua, calibración principal/alternativa y detener. Se mantienen F4, F8, F6, F7 y F10 como valores predeterminados.
- F1–F12, letras y números; T reservada para recoger. Validación de duplicados, botón para restaurar valores e instrucciones que muestran las teclas elegidas.
- La configuración pausa la pesca y bloquea los atajos mientras se edita. La tecla de detener cancela la selección manual; Enter y Esc siguen disponibles.
- Preferencias locales independientes de los perfiles de pantalla. Valores antiguos o no válidos usan los predeterminados. Sin cambios en el controlador, tiempos o comando T del juego.
- Guías e historiales en tres idiomas, enlazados en GitHub e incluidos en las descargas. Los scripts del actualizador siguen en portugués.
- 88 pruebas automáticas, incluyendo parámetros de traducción, atajos, conflictos, persistencia, CSV y conservación de datos, junto con los tests anteriores e inspección visual.

## [7.3.1](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.1)

- El reconocimiento tardío corrige una sola vez la entrada original y el contador, incluida la demora del primer uso del lector. Se permiten lecturas adicionales antes del siguiente lanzamiento.
- Recorte ampliado y unión de palabras de la misma línea. Fragmentos conocidos de Clown Fish y diferencias de mayúsculas comparten totales e iconos, sin unir especies por semejanza. Se conservan las sesiones anteriores.
- 81 pruebas automáticas y comprobaciones con OuwFish y Metal Scraps reales. El aviso específico del primer descubrimiento aún requiere validación en el juego; no se inventan recompensas sin pruebas.

## [7.3.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.0)

- Miniaturas reales en Resumen e Historial, vinculadas a la captura y al ciclo original, incluso con resultados tardíos. Se reutilizan por nombre y se guardan en JSON local; CSV solo textual.
- Hasta 256 miniaturas por sesión; su ausencia no impide pescar. 77 pruebas e inspección con capturas reales.

## [7.2.2](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.2.2)

- Corrección de la recuperación bloqueada por el reinicio repetido de las pruebas entre capturas. Se controlan observaciones independientes, orden y latencia.
- Recuperación tras 120 segundos sin marcador, procesos aislados con colas limitadas, reinicio de tareas bloqueadas y gestión de errores transitorios o cambios de tamaño. Las pausas manuales siguen siendo manuales.
- Más diagnósticos y pruebas prolongadas simuladas; correcciones de integridad, preparación y retorno del actualizador. La simulación no garantiza estabilidad durante toda una noche.

## [7.1.1](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.1)

- Icono de anzuelo sustituido por el de la página de Slayers 2; eliminados los cuadrados verdes. Imagen incluida sin descarga adicional; cambio solo visual.

## [7.1.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.0)

- Tema azul oscuro y jade inspirado en pesca y anime, ventana de 900 × 720 reorganizada, estilos coherentes y controles de inicio/parada destacados. Mecánicas y ajustes conservados.

## [7.0.9](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.9)

- Espera tras el minijuego reducida de 12 a 2 segundos, con migración única del antiguo valor predeterminado. Ausencia validada con dos capturas distintas durante al menos 0,6 segundos; intervalo de reintento de 0,6 segundos. T permanece en 3 segundos.

## [7.0.8](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.8)

- Las pequeñas demoras de procesamiento ya no borran pruebas de ausencia. Solo cuentan capturas válidas y ordenadas; reaparición, pesca activa o pausas superiores a tres segundos reinician la comprobación. Registro detallado tras T. Desaparecer no confirma una recompensa por sí solo.

## [7.0.7](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.7)

- Tres lanzamientos sin confirmar activan recuperación, con esperas de 15–60 segundos, en vez de pausa definitiva. Lecturas recientes antes de relanzar y prioridad para pesca u objetos visibles. Historial y contadores conservados; sin reconexión a Roblox.

## [7.0.6](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.6)

- Archivos de texto por apertura, con fecha, milisegundos y zona horaria; eventos de pesca, recogida, lectura, calibración, pausas, recuperación y errores; estado cada 30 segundos. Registros previos conservados localmente, separados del resumen limitado de ejecución.

## [7.0.5](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.5)

- Geometría más estricta y señal independiente reciente del minijuego para evitar confundir texto con la barra. Reinicio de perfiles automáticos antiguos; selección manual y preferencias conservadas.
- `runtime.json` limitado, estado periódico, detección de interrupciones previas, acceso a registros y auditoría que excluye datos de ejecución de las publicaciones.

## [7.0.4](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.4)

- Mejor detección de objetivos translúcidos/amarillos y marcadores oscuros fuera del objetivo. Pruebas sintéticas y con vídeo real; la tasa de lectura no equivale a victorias de pesca.

## [7.0.3](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.3)

- Relocalización periódica de la barra, tratamiento de superposición blanca y búsqueda durante la pesca activa. Recompensas confirmadas terminan la recogida; ausencia persistente o dos intentos sin objeto pueden finalizar tras observaciones independientes. Resultados sin confirmar separados.

## [7.0.2](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.2)

- T predeterminada de 1,5 a 3 segundos, conservando valores guardados. Progreso visible en el actualizador y límite de 30 segundos para consultar versiones.

## [7.0.1](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.1)

- Vista previa más pequeña y conservación del modo automático/manual por perfil de pantalla, actualizando también la opción visible.

## [7.0.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.0)

- Marca genérica Fishing Macro, vista previa anotada, métricas, búsqueda gradual, perfiles de pantalla, diagnósticos locales limitados y scripts de inicio/retorno.
- Datos separados del ejecutable, migración aditiva, auditoría de privacidad y avisos de bibliotecas de terceros.

## [6.1.0](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v6.1.0)

- Primera versión registrada: F8 para agua, F4 para iniciar/pausar, F10 para detener, F6 para selección manual, calibración automática, control del minijuego, recogida manteniendo T, reintentos limitados, pausa al perder foco, historial por lectura de texto y ejecutable/actualizador con SHA-256.
- El ZIP separado del actualizador se añadió después de esta etiqueta y antes de la 7.0.0. No hay etiquetas anteriores que permitan reconstruir con precisión los cambios de cada prototipo.
