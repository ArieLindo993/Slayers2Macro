# Fishing Macro

[Português](../README.md) · [English](README.en.md) · **Español**

Macro visual para Windows y **Slayers 2 en Roblox**. **Beta 0.0.47** integra el minijuego circular de noviembre: lanzamiento, salpicadura, mantener/soltar el ratón, toques A/D y recogida con T.

**[Descargar actualizador](https://github.com/ArieLindo993/Slayers2Macro/releases/latest/download/Atualizador.zip)** · **[Descargas](https://github.com/ArieLindo993/Slayers2Macro/releases)** · **[Cambios](CHANGELOG.es.md)**

## Instalar

1. Descarga **Atualizador.zip**, pulsa con el botón derecho y elige **Extraer todo**. Guarda la carpeta en un lugar donde puedas escribir. Code → Download ZIP contiene los fuentes.
2. Ejecuta **Atualizar.cmd** desde la carpeta extraída. Espera la descarga, verificación y extracción. Escribe **S** cuando aparezca **Abrir agora? (S/N)**.
3. Abre **Configurar → Idioma e atalhos**, elige **Español** y pulsa **Salvar e fechar**.

Necesitas Windows y Roblox; el paquete no requiere Python, Git ni AutoHotkey. Conserva Atualizar.ps1 junto a los .cmd y la carpeta .install. Si falta el script, extrae el ZIP completo de nuevo; si desaparece tras extraerlo, revisa la cuarentena y el origen del paquete. No ejecutes accesos dentro del ZIP. Iniciar.cmd abre la instalación local; Atualizar.cmd actualiza; Voltar-versao.cmd restaura la versión anterior disponible. El actualizador mantiene los textos en portugués.

Para instalar manualmente, extrae **Slayers2Macro.zip** y abre **Slayers2Macro.exe** conservando los archivos adjuntos. .sha256 sirve para comprobar la integridad.

## Pescar

1. Equipa la caña cerca del agua y fija la cámara. Apunta donde caerá la línea y aparecerá la salpicadura; pulsa **F8**.
2. Deja la calibración automática activada y pulsa **F4** con Roblox en primer plano.
3. El macro lanza y deja asentar la línea. La protección predeterminada es de **3 segundos**, con comprobación de estabilización. Tras reconocer la salpicadura, espera **0,18 segundos (180 ms)** antes de pulsar. Ajusta **Protección tras lanzar (s)** y **Retraso del enganche (s)** según el vuelo y la respuesta del juego.
4. El objetivo es **mantener la aguja dentro del arco verde**. Según la [guía del minijuego](https://www.youtube.com/watch?v=BO6waB_XXhY&t=90s), **flecha verde hacia la derecha = mantener el botón derecho; flecha roja hacia la izquierda = mantener el botón izquierdo**. El macro suelta el botón anterior antes de cambiar. Cerca del borde verde en la dirección de la presión, alivia ambos botones y retoma dentro de un margen seguro. A/D sigue independiente. La respuesta específica a saltos todavía requiere una señal visual confirmada; el alivio de borde es un control distinto.
5. Las tarjetas activas A/D piden uno o dos toques según sus puntos, junto al control del ratón.
6. Tras el resultado, mantiene **T tres segundos** por defecto, comprueba Claim/nombre/peso y vuelve a pescar. Observa las primeras rondas en la vista previa.

Roblox debe seguir visible y enfocado. Perder foco pausa y suelta las entradas; vuelve y continúa con F4. Si mueves cámara o personaje, marca el agua de nuevo. La salpicadura se busca alrededor del punto marcado.

| Predeterminado | Acción |
| --- | --- |
| F4 | Iniciar / pausar |
| F8 | Marcar agua / región de búsqueda de salpicadura |
| F6 / F7 | Seleccionar el círculo completo en una imagen congelada; Enter guarda y Esc cancela |
| F10 | Detener / soltar entradas |

En **Configurar → Idioma y atajos** puedes cambiar idioma y teclas. A, D y T se reservan para el juego; los atajos antiguos en conflicto vuelven a los valores predeterminados. Se conserva el historial y las indicaciones muestran las teclas elegidas.

El modo automático localiza el anillo segmentado en cada ronda y vuelve a buscarlo aunque el marcador salga del arco verde. El modo manual fija la selección del círculo completo; lee las teclas a sus lados. Los perfiles circulares se separan por tamaño, bordes y DPI; no reutilizan selecciones verticales antiguas. Se muestra la resolución activa. **Solo observar** lee sin enviar entradas.

## Historial y soporte

El historial agrupa cantidades por nombre validado y muestra horario, peso leído e iconos cuando están disponibles en la notificación. Los nombres nuevos requieren dos imágenes distintas con confianza alta. Se exporta a CSV; el JSON local también guarda peso y origen de confirmación.

El nombre en Claim no confirma una adquisición. La notificación de recompensa sí; sin ella, la ausencia persistente de Claim después de mantener T permite **inferir** la recogida. El JSON distingue claim_after_hold de reward_notification. La física y cambios de interfaz pueden afectar esa inferencia.

Los registros locales guardan fecha, hora, etapas, salpicadura, entradas y resultados. **Ayuda y soporte** abre los registros o copia un resumen sin usuario, rutas personales, imágenes ni contenido del registro. No se envía nada automáticamente. Las grabaciones, ajustes, capturas e historiales personales quedan fuera del repositorio público y los paquetes. La ventana se puede redimensionar.

## Validación

Las pruebas automáticas cubren el flujo integrado, entradas simultáneas, liberación, perfiles, historial y lectura. La reproducción local incluye el aviso A de dos toques sin entradas al juego. No demuestra una victoria en directo; faltan comprobar sesiones largas y ventanas pequeñas reales con la nueva interfaz. También se prueban fotogramas redimensionados.

[Numeración beta y versiones anteriores](VERSIONING.es.md) · [Cambios](CHANGELOG.es.md)

El nombre es genérico; el perfil disponible es específico de Slayers 2. Los fuentes y descargas son públicos. No hay pagos, activación por clave, autenticación de clientes ni restricciones de copia. Desarrollo: Python 3.12, requirements.txt y build.py. Las herramientas de reproducción requieren además imageio-ffmpeg.
