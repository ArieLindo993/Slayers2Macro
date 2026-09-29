# Historial de versiones

[Português](../CHANGELOG.md) · [English](CHANGELOG.en.md) · **Español** · [Guía de uso](README.es.md)

Las entradas anteriores se resumen a continuación. El [historial en portugués](../CHANGELOG.md) incluye investigaciones y validaciones detalladas. Las pruebas automáticas y con capturas no garantizan sesiones ininterrumpidas en el juego.

## [Beta 0.0.35](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.35-beta)

### Corrección de capturas en ventanas pequeñas

- Amplía el recorte para incluir el aviso completo en ventanas pequeñas y cuando nombre y cantidad comparten línea.
- Las lecturas OCR que terminan antes de guardar el ciclo se conservan y se asocian a la captura correcta cuando se registra.
- Los avisos que siguen visibles mientras se espera una nueva picada ya no se asignan al ciclo nuevo.
- Diagnóstico del último registro: no se detectó ningún aviso en las 10 capturas con ventana de 800×599; en pantalla completa se detectaron 8/10. Los nombres se leyeron en los avisos detectados, pero las demás capturas quedaron sin confirmar. La corrección trata los fallos de lectura y asociación del ciclo.
- Mantiene la validación de nombres y los casos de pesca vacía.

## [Beta 0.0.34](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.34-beta)

### Recuperación de avisos y OCR

- Detecta avisos de recompensa con interfaz fija o escalada según la ventana y selecciona el recorte geométrico correcto.
- Si la lectura normal no separa texto pequeño o parcialmente desvanecido, vuelve a intentarlo con contraste local mejorado. Se mantiene la validación existente de nombres y cantidades.
- El registro muestra la geometría elegida, la similitud visual y si OCR encontró texto de recompensa.
- Evidencia local: el registro anterior anotó 9 ciclos sin indicador ni aviso de objeto; luego identificó Crustadon x1 cuando apareció un aviso. Otro aviso fue detectado, pero Roblox perdió el foco antes de terminar OCR.
- Validación: pasaron las 112 pruebas y la auditoría de empaquetado, incluidas 5 comprobaciones geométricas. Aún hace falta confirmar una sesión real continua.

## [Beta 0.0.33](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.33-beta)

### Validación más rigurosa de nombres

- Catálogo de nombres observados y correcciones explícitas para variantes de Golden Fish, Clown Fish, Crustadon, Coral, Sea Horse y otros. OuwFish/OuwFwesh y Refinement Ore/Mythic Refinement Ore siguen separados.
- Fragmentos como Fish, a Fish y Ore, palabras cortadas en el borde y posibles errores cercanos a nombres conocidos quedan como **Nombre no identificado**, conservando la cantidad.
- Los nombres nuevos requieren lecturas coincidentes y fiables en dos imágenes diferentes. Reprocesar la misma imagen no confirma un nombre nuevo; los errores parecidos a nombres conocidos no se aprenden como especies nuevas.
- Una lectura posterior contradictoria no sustituye un nombre validado. La identificación tardía no duplica recogidas; la memoria de pendientes está limitada.
- Nombres pendientes y conflictos registrados. Se conservan archivos antiguos; la validación se aplica a las nuevas entradas.
- Incluye las miniaturas mejoradas y recompensas directas de Beta 0.0.32.
- Validación: 107 pruebas, reproducción local de un historial real conservando cantidades y lectura de capturas reales de OuwFish/Metal Scraps. Sin publicar datos personales.

## [Beta 0.0.32](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.32-beta)

### Iconos más nítidos y recompensas directas al inventario

- Las notificaciones se comprueban también durante la lectura rápida del minijuego. Un aviso nuevo puede confirmar un objeto enviado al inventario sin indicador Collect ni pulsar T.
- Si el aviso coincide con el último fotograma del minijuego, se conserva hasta terminar la pesca. No se cuentan de nuevo avisos previos o persistentes de la ronda anterior.
- El lector usa el mismo fotograma y ciclo original de la detección; también empieza a leer cuando desaparece la barra.
- Miniaturas elegidas entre capturas distintas según contraste del aviso y detalle del icono. Se rechazan cuadros muy tenues y se permite mejorar la imagen sin sustituirla por otra peor al desaparecer. Se actualizan las entradas del mismo objeto en la sesión; los archivos antiguos no se reprocesan. Sin imagen adecuada, queda un guion.
- Nuevos eventos de notificación y actualización de iconos en el registro.
- Validación: 99 pruebas automáticas y una secuencia real de recompensa. La recogida directa se simuló y aún necesita validación en el juego.

## [Beta 0.0.31](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.31-beta)

### Numeración beta desde el comienzo

- Todas las versiones se clasifican como beta, desde Beta 0.0.0 hasta Beta 0.0.31, incluidos paquetes anteriores a Git, variantes intermedias y el prototipo AutoHotkey.
- La [tabla de equivalencias](VERSIONING.es.md) registra identificadores antiguos, hashes de paquetes locales y etiquetas conservadas. No se inventan versiones para intentos sin archivos.
- Título e interfaz muestran Beta 0.0.31; los registros identifican 0.0.31-beta. Se actualizan nombres y descripciones de releases anteriores; los paquetes históricos siguen siendo originales.
- El actualizador muestra el nombre público y sigue instalando por ID. Se conserva el canal de descarga sin reiniciar datos, atajos ni idioma.
- Solo cambios de nomenclatura, documentación y distribución; mecánicas de pesca conservadas.

## [Beta 0.0.30](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.4.0)

- Interfaz en portugués (predeterminado), inglés y español, seleccionable en **Configurar → Idioma y atajos**. Se aplica al guardar sin perder historial ni contadores.
- Traducción de ventana principal, estados de pesca, ajustes, historial, selección manual y CSV exportado mediante el botón. Los nombres del juego y los formatos de registros técnicos permanecen estables.
- Atajos configurables para iniciar/pausar, marcar agua, calibración principal/alternativa y detener. Se mantienen F4, F8, F6, F7 y F10 como valores predeterminados.
- F1–F12, letras y números; T reservada para recoger. Validación de duplicados, botón para restaurar valores e instrucciones que muestran las teclas elegidas.
- La configuración pausa la pesca y bloquea los atajos mientras se edita. La tecla de detener cancela la selección manual; Enter y Esc siguen disponibles.
- Preferencias locales independientes de los perfiles de pantalla. Valores antiguos o no válidos usan los predeterminados. Sin cambios en el controlador, tiempos o comando T del juego.
- Guías e historiales en tres idiomas, enlazados en GitHub e incluidos en las descargas. Los scripts del actualizador siguen en portugués.
- 88 pruebas automáticas, incluyendo parámetros de traducción, atajos, conflictos, persistencia, CSV y conservación de datos, junto con los tests anteriores e inspección visual.

## [Beta 0.0.29](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.1)

- El reconocimiento tardío corrige una sola vez la entrada original y el contador, incluida la demora del primer uso del lector. Se permiten lecturas adicionales antes del siguiente lanzamiento.
- Recorte ampliado y unión de palabras de la misma línea. Fragmentos conocidos de Clown Fish y diferencias de mayúsculas comparten totales e iconos, sin unir especies por semejanza. Se conservan las sesiones anteriores.
- 81 pruebas automáticas y comprobaciones con OuwFish y Metal Scraps reales. El aviso específico del primer descubrimiento aún requiere validación en el juego; no se inventan recompensas sin pruebas.

## [Beta 0.0.28](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.0)

- Miniaturas reales en Resumen e Historial, vinculadas a la captura y al ciclo original, incluso con resultados tardíos. Se reutilizan por nombre y se guardan en JSON local; CSV solo textual.
- Hasta 256 miniaturas por sesión; su ausencia no impide pescar. 77 pruebas e inspección con capturas reales.

## [Beta 0.0.27](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.2.2)

- Corrección de la recuperación bloqueada por el reinicio repetido de las pruebas entre capturas. Se controlan observaciones independientes, orden y latencia.
- Recuperación tras 120 segundos sin marcador, procesos aislados con colas limitadas, reinicio de tareas bloqueadas y gestión de errores transitorios o cambios de tamaño. Las pausas manuales siguen siendo manuales.
- Más diagnósticos y pruebas prolongadas simuladas; correcciones de integridad, preparación y retorno del actualizador. La simulación no garantiza estabilidad durante toda una noche.

## [Beta 0.0.24](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.1)

- Icono de anzuelo sustituido por el de la página de Slayers 2; eliminados los cuadrados verdes. Imagen incluida sin descarga adicional; cambio solo visual.

## [Beta 0.0.23](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.0)

- Tema azul oscuro y jade inspirado en pesca y anime, ventana de 900 × 720 reorganizada, estilos coherentes y controles de inicio/parada destacados. Mecánicas y ajustes conservados.

## [Beta 0.0.22](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.9)

- Espera tras el minijuego reducida de 12 a 2 segundos, con migración única del antiguo valor predeterminado. Ausencia validada con dos capturas distintas durante al menos 0,6 segundos; intervalo de reintento de 0,6 segundos. T permanece en 3 segundos.

## [Beta 0.0.21](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.8)

- Las pequeñas demoras de procesamiento ya no borran pruebas de ausencia. Solo cuentan capturas válidas y ordenadas; reaparición, pesca activa o pausas superiores a tres segundos reinician la comprobación. Registro detallado tras T. Desaparecer no confirma una recompensa por sí solo.

## [Beta 0.0.20](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.7)

- Tres lanzamientos sin confirmar activan recuperación, con esperas de 15–60 segundos, en vez de pausa definitiva. Lecturas recientes antes de relanzar y prioridad para pesca u objetos visibles. Historial y contadores conservados; sin reconexión a Roblox.

## [Beta 0.0.19](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.6)

- Archivos de texto por apertura, con fecha, milisegundos y zona horaria; eventos de pesca, recogida, lectura, calibración, pausas, recuperación y errores; estado cada 30 segundos. Registros previos conservados localmente, separados del resumen limitado de ejecución.

## [Beta 0.0.18](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.5)

- Geometría más estricta y señal independiente reciente del minijuego para evitar confundir texto con la barra. Reinicio de perfiles automáticos antiguos; selección manual y preferencias conservadas.
- `runtime.json` limitado, estado periódico, detección de interrupciones previas, acceso a registros y auditoría que excluye datos de ejecución de las publicaciones.

## [Beta 0.0.17](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.4)

- Mejor detección de objetivos translúcidos/amarillos y marcadores oscuros fuera del objetivo. Pruebas sintéticas y con vídeo real; la tasa de lectura no equivale a victorias de pesca.

## [Beta 0.0.16](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.3)

- Relocalización periódica de la barra, tratamiento de superposición blanca y búsqueda durante la pesca activa. Recompensas confirmadas terminan la recogida; ausencia persistente o dos intentos sin objeto pueden finalizar tras observaciones independientes. Resultados sin confirmar separados.

## [Beta 0.0.15](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.2)

- T predeterminada de 1,5 a 3 segundos, conservando valores guardados. Progreso visible en el actualizador y límite de 30 segundos para consultar versiones.

## [Beta 0.0.14](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.1)

- Vista previa más pequeña y conservación del modo automático/manual por perfil de pantalla, actualizando también la opción visible.

## [Beta 0.0.13](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.0)

- Marca genérica Fishing Macro, vista previa anotada, métricas, búsqueda gradual, perfiles de pantalla, diagnósticos locales limitados y scripts de inicio/retorno.
- Datos separados del ejecutable, migración aditiva, auditoría de privacidad y avisos de bibliotecas de terceros.

## [Beta 0.0.12](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v6.1.0)

- Primera versión registrada: F8 para agua, F4 para iniciar/pausar, F10 para detener, F6 para selección manual, calibración automática, control del minijuego, recogida manteniendo T, reintentos limitados, pausa al perder foco, historial por lectura de texto y ejecutable/actualizador con SHA-256.
- El ZIP separado del actualizador se añadió después de esta etiqueta y antes de la Beta 0.0.13. No hay etiquetas anteriores que permitan reconstruir con precisión los cambios de cada prototipo.
