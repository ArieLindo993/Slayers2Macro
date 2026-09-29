# Fishing Macro

[Português](../README.md) · [English](README.en.md) · **Español**

Macro de pesca para **Slayers 2 en Roblox**, para Windows, con calibración automática, historial de la sesión y diagnósticos locales. El nombre del producto es genérico; el perfil actual es específico para Slayers 2.

**[Descargar actualizador](https://github.com/ArieLindo993/Slayers2Macro/releases/latest/download/Atualizador.zip)** · **[Versiones y descargas](https://github.com/ArieLindo993/Slayers2Macro/releases)** · **[Historial de cambios](CHANGELOG.es.md)**

**Beta 0.0.31:** toda la historia del macro usa ahora numeración beta desde cero, incluidos los prototipos anteriores a Git. Consulta la [tabla completa de equivalencias](VERSIONING.es.md). Se conservan funciones, ajustes e historial.

## Instalar e iniciar

Necesitas Windows y Roblox. No hace falta instalar Python, Git ni AutoHotkey. Necesitas internet para descargar actualizaciones y jugar.

1. Descarga **Atualizador.zip**, haz clic derecho y selecciona **Extraer todo**. Guarda la carpeta extraída en un lugar donde puedas escribir archivos. **Code → Download ZIP** de GitHub descarga el código fuente, no la aplicación lista para usar.
2. Abre la carpeta y ejecuta **Atualizar.cmd**. Mantén `Atualizar.ps1` y los demás scripts juntos. No los ejecutes dentro del ZIP.
3. Espera la descarga, la comprobación de integridad y la extracción. Cuando aparezca **Abrir agora? (S/N)**, escribe **S** para abrir el macro. Los scripts del actualizador conservan sus nombres y mensajes en portugués.
4. En el macro, abre **Configurar → Idioma e atalhos**, selecciona **Español** y pulsa **Salvar e fechar**. Después, las opciones se llamarán **Configurar → Idioma y atajos → Guardar y cerrar**.

Para instalar manualmente, descarga **Slayers2Macro.zip**, extrae todo y abre **Slayers2Macro.exe**, conservando los archivos que lo acompañan. El archivo `.sha256` sirve para verificar la descarga; no es una aplicación. El actualizador lo comprueba automáticamente.

## Primera sesión de pesca

1. Entra en Slayers 2, equipa la caña y sitúate cerca del agua.
2. Con Roblox en primer plano, apunta el ratón a un lugar válido del agua y pulsa **F8** para guardar el punto de lanzamiento.
3. Deja activada la calibración automática y pulsa **F4**.
4. El macro lanza la caña, espera el minijuego, sigue el marcador y mantiene **T** para recoger la recompensa. Observa la primera ronda mediante la vista previa y el estado.
5. Pulsa **F10** para detenerlo. Al perder el foco, el macro se pausa y suelta los comandos; vuelve a Roblox y pulsa **F4** para continuar.

Roblox debe permanecer visible y en primer plano. El macro utiliza el ratón y el teclado mientras está activo. Gestiona lanzamientos fallidos y pescas sin recompensa. Hay hasta tres lanzamientos por ronda y cinco intentos de recogida, con finalización anticipada cuando las pruebas lo permiten. Que un objeto desaparezca no basta para confirmar una recompensa. Si no identifica un objeto en los dos primeros intentos, comprueba su ausencia antes de volver a pescar.

## Idioma y atajos

Abre **Configurar → Idioma y atajos**. Elige **Português**, **English** o **Español**, configura las teclas y pulsa **Guardar y cerrar**. Los cambios se aplican sin reiniciar, conservando historial y contadores, y quedan guardados para futuras aperturas y actualizaciones.

| Predeterminado | Acción |
| --- | --- |
| F8 | Marcar agua / guardar el punto de lanzamiento |
| F4 | Iniciar o pausar |
| F6 | Calibrar manualmente / seleccionar la barra |
| F7 | Atajo alternativo de calibración manual |
| F10 | Detener y soltar los comandos |

Se admiten F1–F12, letras y números. **T queda reservada para recoger en el juego**. Cada acción necesita una tecla diferente; no se pueden guardar duplicados. **Restaurar valores predeterminados** restablece los campos de atajos; guarda para aplicarlos. Los atajos no inician la pesca mientras la configuración está abierta. En la selección manual, **Enter** guarda, **Esc** cancela y la tecla configurada para detener también cancela.

Las instrucciones de la interfaz muestran tus teclas elegidas. F4/F8/F6/F10 en esta guía se refieren a los valores de fábrica. El clic del ratón y la recogida con T conservan su funcionamiento actual.

Se traducen menús, mensajes de estado, historial, selección manual y CSV exportado mediante el botón. Los nombres de los objetos permanecen como en el juego. Los registros técnicos, JSON y CSV automáticos conservan un formato estable. El idioma del macro no cambia el idioma de Roblox.

## Calibración y seguimiento

**Automática:** comprueba la barra en cada pesca. Necesita tres observaciones consistentes para confirmar su posición. Las rondas fiables refinan el perfil de pantalla, sin garantizar mejoras en cada intento. Sigue comprobando la posición periódicamente. Si pierde la barra, amplía la búsqueda desde la región actual a sus alrededores y a la pantalla del juego. Tras 120 segundos sin encontrar el marcador, inicia la recuperación automática en vez de detenerse definitivamente.

**Manual:** muestra el minijuego y pulsa F6. En la captura congelada, arrastra alrededor de toda la barra vertical y guarda. Se activa el modo manual. Vuelve a Roblox y pulsa F4. Puedes reactivar la calibración automática en la ventana principal.

Los perfiles separan la calibración según el tamaño de ventana, los bordes y la escala de Windows. Azul indica la región analizada, verde el objetivo y rosa el marcador. El tiempo dentro del objetivo mide intervalos con lecturas válidas, no el porcentaje de pescas ganadas.

## Ajustes de pesca

Abre **Configurar → Pesca**, cambia los valores y guarda.

| Ajuste | Predeterminado | Intervalo permitido |
| --- | --- | --- |
| Duración del clic | 0,25 s | 0,08–1 s |
| Mantener T | 3 s | 0,2–5 s |
| Espera antes de repetir el lanzamiento | 20 s | 10–60 s |
| Espera del objeto tras pescar | 2 s | 0,5–20 s |

Las actualizaciones conservan los ajustes, salvo migraciones documentadas. Si tenías T en 1,5 segundos, cámbialo manualmente para usar 3 segundos. La antigua espera de objeto de 12 segundos migra una vez a 2 segundos. **Solo observar** muestra la detección sin enviar comandos al juego.

## Historial y diagnósticos

**Objetos obtenidos** abre un resumen y un historial cronológico. La lectura de texto puede fallar; “Nombre no identificado” es un marcador provisional. Una recompensa reconocida tarde puede corregir el ciclo original y el contador sin duplicarlo. Variantes conocidas como “Clown” y “Clown F” se agrupan como **Clown Fish**. No se reescriben archivos de sesiones anteriores.

Las miniaturas proceden del aviso de recompensa del juego, se reutilizan por nombre y se guardan en el JSON local. Hay un límite de 256 miniaturas distintas por sesión. Las imágenes ausentes muestran un guion; no hay catálogo en línea ni recuperación retroactiva. El CSV solo contiene texto. **Vaciar lista / nueva sesión** inicia una lista nueva y conserva los archivos anteriores en disco.

**Abrir registros** abre la carpeta local de datos. Las capturas opcionales de diagnóstico se limitan a 20 pares de imagen y registro. Desactivarlas no desactiva los registros de texto ni las miniaturas de objetos.

**Abrir registros de texto** muestra los archivos de cada sesión. Registran lanzamientos, inicios, pausas, pesca, calibración, intentos de recogida, recompensas, recuperación y errores, con fecha, hora y zona horaria local. Hay un resumen periódico cada 30 segundos. Son registros de eventos, no un vídeo de cada fotograma. Un cierre abrupto puede dejar únicamente las últimas entradas completas. `runtime.json` conserva hasta 200 eventos recientes y actualiza su estado cada cinco segundos.

Visión, calibración, lectura de nombres y diagnósticos usan procesos con colas limitadas. Las tareas bloqueadas se reinician. Tres lanzamientos sin confirmar activan la recuperación con una espera de 15–60 segundos; un minijuego u objeto reconocido tiene prioridad. Cambiar el tamaño de la misma ventana de Roblox activa un ajuste. Las pausas manuales y la pérdida de foco requieren que reanudes; la recuperación no reconecta Roblox ni cambia el punto de agua.

## Actualizar, volver de versión y resolver problemas

Cierra el macro antes de actualizar. Conserva la carpeta oculta `.install` del actualizador.

| Script | Función |
| --- | --- |
| Atualizar.cmd | Consultar GitHub, instalar la última versión y ofrecer abrirla |
| Iniciar.cmd | Abrir la versión instalada sin buscar actualizaciones |
| Voltar-versao.cmd | Cambiar a la versión anterior instalada con este actualizador |

Para actualizar el propio actualizador, extrae un nuevo **Atualizador.zip** en la misma carpeta, sustituyendo sus archivos y conservando `.install`. Volver atrás requiere una versión anterior instalada por el mismo actualizador. Después, usa **Iniciar.cmd** para evitar actualizarla otra vez de inmediato.

Si la ventana de comandos parece detenida, deja tiempo para descargar y extraer. Si faltan scripts, extrae el ZIP completo. Cierra el macro si el actualizador indica que está abierto. Reintenta tras fallos de red o integridad. Si no inicia la pesca, coloca Roblox en primer plano, equipa la caña y marca el agua. Si falla el seguimiento, revisa la vista previa y prueba la selección manual. Para informar de un problema, incluye la versión, el estado y los pasos; revisa registros e imágenes antes de compartirlos.

## Datos locales y desarrollo

Configuración, perfiles, historial y diagnósticos están en `%LOCALAPPDATA%\FishingMacro`, separados de la instalación. No hay telemetría ni envío automático de estos datos. El actualizador consulta GitHub. Vídeos personales, ajustes, historiales y registros no se incluyen en el repositorio ni en la distribución. Los diagnósticos capturan la región seleccionada; una selección incorrecta puede incluir otros elementos visibles.

El repositorio y las descargas son públicos. Actualmente no hay pagos, activación con clave, autenticación de clientes ni restricciones de copia. Los recursos visuales distribuidos son recortes de indicadores y el icono de la [página de Slayers 2 en Roblox](https://www.roblox.com/games/16205713724/Slayers-2).

Para desarrollar, usa Windows y Python 3.12 en un entorno virtual:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python audit.py
python src/macro.py
```

`python build.py` genera los paquetes y prueba el inicio del ejecutable. Una etiqueta `v*` activa la publicación para Windows. Mantén alineados etiqueta, versión de `src/product.py` e historiales de cambios. Las traducciones están en `src/i18n.py`; las validaciones, en `src/preferences.py`. Los paquetes incluyen avisos de bibliotecas en `THIRD_PARTY`. Los tests y las pruebas con capturas no sustituyen una sesión larga en el juego; cambios en su interfaz pueden requerir ajustes.
