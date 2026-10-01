"""Local UI translations. Diagnostic event IDs and game item names stay stable."""
import re
import tkinter as tk
from preferences import DEFAULT_HOTKEYS

# Source | English | Español. Templates are matched as whole messages.
_ROWS=r'''LEITURA DA ÁGUA|WATER SCAN|LECTURA DEL AGUA
Reconhecimento|Recognition|Reconocimiento
Aguardando a barra|Waiting for the bar|Esperando la barra
Azul · região   Verde · alvo\nRosa · marcador|Blue · area   Green · target\nPink · marker|Azul · área   Verde · objetivo\nRosa · marcador
Qualidade: aguardando leituras|Quality: waiting for readings|Calidad: esperando lecturas
Perfil: aguardando o jogo|Profile: waiting for the game|Perfil: esperando el juego
Resolução Roblox: aguardando|Roblox resolution: waiting|Resolución de Roblox: esperando
Resolução Roblox: {width} × {height}|Roblox resolution: {width} × {height}|Resolución de Roblox: {width} × {height}
Perfil: {mode} · escala {dpi}%|Profile: {mode} · scale {dpi}%|Perfil: {mode} · escala {dpi}%
Janela|Window|Ventana
Sem bordas / tela cheia|Borderless / fullscreen|Sin bordes / pantalla completa
REGISTROS DA SESSÃO|SESSION RECORDS|REGISTROS DE LA SESIÓN
Salvar recortes|Save snapshots|Guardar capturas
Até 20 recortes, salvos localmente.|Up to 20 snapshots, stored locally.|Hasta 20 capturas, guardadas localmente.
Abrir registros|Open records|Abrir registros
Abrir logs de texto|Open text logs|Abrir registros de texto
Log de texto ativo|Text logging enabled|Registro de texto activo
Falha ao gravar log|Unable to write log|Error al guardar el registro
SUA PESCARIA|YOUR FISHING SESSION|TU SESIÓN DE PESCA
Preparação|Preparation|Preparación
F8  ·  Marcar a água       F6  ·  Selecionar a barra|F8  ·  Mark water       F6  ·  Select bar|F8  ·  Marcar agua       F6  ·  Seleccionar barra
Automático: conferir barra em cada pesca|Automatic: check the bar on every catch|Automático: comprobar la barra en cada pesca
Barra: seleção manual salva|Bar: manual selection saved|Barra: selección manual guardada
Calibrar automaticamente a cada pesca|Calibrate automatically on every catch|Calibrar automáticamente en cada pesca
Selecionar barra com o mouse|Select bar with the mouse|Seleccionar barra con el ratón
Inventário da sessão|Session inventory|Inventario de la sesión
Itens obtidos · {n}|Items obtained · {n}|Objetos obtenidos · {n}
F4  iniciar / pausar     ·     F10  parar|F4  start / pause     ·     F10  stop|F4  iniciar / pausar     ·     F10  detener
Configurar|Settings|Configurar
Parar|Stop|Detener
Iniciar|Start|Iniciar
Pausar|Pause|Pausar
Cancelar|Cancel|Cancelar
Parado.|Stopped.|Detenido.
Pausado.|Paused.|Pausado.
Itens obtidos nesta sessão|Items obtained this session|Objetos obtenidos en esta sesión
Itens obtidos|Items obtained|Objetos obtenidos
Exportar CSV|Export CSV|Exportar CSV
Limpar lista / nova sessão|Clear list / new session|Vaciar lista / nueva sesión
Resumo|Summary|Resumen
Histórico|History|Historial
Item|Item|Objeto
Quantidade|Quantity|Cantidad
Horário|Time|Hora
Ícone|Icon|Icono
Nome não identificado|Unidentified name|Nombre no identificado
Nova sessão. Use F4 para iniciar.|New session. Use F4 to start.|Nueva sesión. Usa F4 para iniciar.
{n} ciclos   ·   {count} coletas confirmadas|{n} cycles   ·   {count} confirmed collections|{n} ciclos   ·   {count} recogidas confirmadas
{n} ciclos · {count} coletas confirmadas|{n} cycles · {count} confirmed collections|{n} ciclos · {count} recogidas confirmadas
Desde {time} · {n} itens · {count} ciclos registrados|Since {time} · {n} items · {count} recorded cycles|Desde {time} · {n} objetos · {count} ciclos registrados
Desde {time} · {n} itens · {count} ciclos registrados · {unknown} nome(s) não identificado(s)|Since {time} · {n} items · {count} recorded cycles · {unknown} unidentified name(s)|Desde {time} · {n} objetos · {count} ciclos registrados · {unknown} nombre(s) sin identificar
Não foi possível salvar o histórico em disco; exporte o CSV.|Unable to save history to disk; export the CSV.|No se pudo guardar el historial; exporta el CSV.
Leitura dos nomes indisponível; as coletas continuam registradas.|Name reading unavailable; collections are still recorded.|Lectura de nombres no disponible; las recogidas siguen registrándose.
Exportar itens|Export items|Exportar objetos
Erro ao exportar|Export error|Error al exportar
Ponto na água salvo · F8 para alterar|Water point saved · F8 to change|Punto de agua guardado · F8 para cambiar
Aponte para a água e pressione F8|Point at the water and press F8|Apunta al agua y pulsa F8
Marque a água com F8 para começar.|Mark the water with F8 to begin.|Marca el agua con F8 para comenzar.
Ajuste as opções e volte ao jogo para iniciar.|Adjust the settings, then return to the game to start.|Ajusta las opciones y vuelve al juego para iniciar.
Configurar pesca|Fishing settings|Configuración de pesca
Ajustes|Settings|Ajustes
Pesca|Fishing|Pesca
Idioma e atalhos|Language and shortcuts|Idioma y atajos
Idioma|Language|Idioma
Atalhos|Shortcuts|Atajos
Iniciar / pausar|Start / pause|Iniciar / pausar
Marcar água|Mark water|Marcar agua
Calibrar / selecionar barra|Calibrate / select bar|Calibrar / seleccionar barra
Calibrar (atalho alternativo)|Calibrate (alternate shortcut)|Calibrar (atajo alternativo)
Restaurar padrões|Restore defaults|Restaurar valores predeterminados
Escolha teclas diferentes. T permanece reservado à coleta.|Choose different keys. T remains reserved for collection.|Elige teclas diferentes. T queda reservado para recoger.
Atalhos inválidos|Invalid shortcuts|Atajos no válidos
Escolha uma tecla diferente para cada ação.|Choose a different key for each action.|Elige una tecla diferente para cada acción.
Duração do clique (s)|Click duration (s)|Duración del clic (s)
Segurar T (s)|Hold T (s)|Mantener T (s)
Esperar a pesca antes de repetir (s)|Wait before retrying a cast (s)|Espera antes de repetir el lanzamiento (s)
Esperar item depois da pesca (s)|Wait for item after fishing (s)|Espera del objeto tras pescar (s)
Só observar (não envia comandos)|Observe only (no input sent)|Solo observar (sin enviar comandos)
Modo de observação alterado.|Observation mode changed.|Modo de observación cambiado.
Calibrar a barra|Calibrate the bar|Calibrar la barra
Automático: a barra é conferida em cada pesca.\nManual: F6 congela a imagem; arraste e salve.\nF8 salva o ponto de lançamento na água.|Automatic: checks the bar on every catch.\nManual: F6 freezes the image; drag and save.\nF8 saves the casting point in the water.|Automático: comprueba la barra en cada pesca.\nManual: F6 congela la imagen; arrastra y guarda.\nF8 guarda el punto de lanzamiento en el agua.
3 lançamentos por rodada; recuperação automática. Até 5 coletas.\nT é segurado mesmo se o painel desaparecer.|3 casts per round; automatic recovery. Up to 5 collection attempts.\nT is held even if the prompt disappears.|3 lanzamientos por ronda; recuperación automática. Hasta 5 intentos de recogida.\nT se mantiene aunque desaparezca el aviso.
Prévia aparece no modo de observação|Preview appears in observation mode|Vista previa en modo de observación
Salvar e fechar|Save and close|Guardar y cerrar
Valor inválido|Invalid value|Valor no válido
Confira os tempos informados.|Check the time values.|Revisa los tiempos indicados.
Ajustes salvos. Use F4 dentro do jogo.|Settings saved. Use F4 in the game.|Ajustes guardados. Usa F4 dentro del juego.
Ajustes aplicados; não foi possível salvar nesta pasta.|Settings applied; unable to save in this folder.|Ajustes aplicados; no se pudo guardar en esta carpeta.
Perfil automático: aguardando a barra|Automatic profile: waiting for the bar|Perfil automático: esperando la barra
Perfil manual: região salva|Manual profile: saved region|Perfil manual: región guardada
Perfil: {size}|Profile: {size}|Perfil: {size}
Janela · {scale}%|Windowed · {scale}%|Ventana · {scale}%
Sem bordas / tela cheia · {scale}%|Borderless / full screen · {scale}%|Sin bordes / pantalla completa · {scale}%
Volte ao Roblox. Início em 3 segundos…|Return to Roblox. Starting in 3 seconds…|Vuelve a Roblox. Inicio en 3 segundos…
Volte ao Roblox e pressione F4.|Return to Roblox and press F4.|Vuelve a Roblox y pulsa F4.
Marque um ponto na água com F8.|Mark a water point with F8.|Marca un punto en el agua con F8.
Conferindo a tela…|Checking the screen…|Comprobando la pantalla…
Parado com F10.|Stopped with F10.|Detenido con F10.
Pausado com F4.|Paused with F4.|Pausado con F4.
Configurando…|Configuring…|Configurando…
Água marcada. Pressione F4 para iniciar.|Water marked. Press F4 to start.|Agua marcada. Pulsa F4 para iniciar.
Automático: aguardando a barra|Automatic: waiting for the bar|Automático: esperando la barra
Manual: região atual fixa|Manual: current region fixed|Manual: región actual fija
Volte ao Roblox com o minigame visível. Captura em 3 segundos…|Return to Roblox with the minigame visible. Capturing in 3 seconds…|Vuelve a Roblox con el minijuego visible. Captura en 3 segundos…
Abra o minigame no Roblox e pressione F6.|Open the minigame in Roblox and press F6.|Abre el minijuego en Roblox y pulsa F6.
Selecionando a barra. O macro está pausado.|Selecting the bar. The macro is paused.|Seleccionando la barra. El macro está pausado.
Barra manual salva · automático pode ser reativado|Manual bar saved · automatic mode can be re-enabled|Barra manual guardada · puedes reactivar el modo automático
Seleção salva. Volte ao Roblox e pressione F4.|Selection saved. Return to Roblox and press F4.|Selección guardada. Vuelve a Roblox y pulsa F4.
Barra automática confirmada · aprendendo nesta pesca|Automatic bar confirmed · learning from this catch|Barra automática confirmada · aprendiendo de esta pesca
Pausado: o Roblox perdeu o foco. Volte ao jogo e use F4.|Paused: Roblox lost focus. Return to the game and use F4.|Pausado: Roblox perdió el foco. Vuelve al juego y usa F4.
Janela alterada. Use F4 para retomar.|Window changed. Use F4 to resume.|Ventana cambiada. Usa F4 para continuar.
Leitura perdida: recalibrando durante a pesca…|Tracking lost: recalibrating during fishing…|Lectura perdida: recalibrando durante la pesca…
Dentro da faixa: {value}|Inside target: {value}|Dentro del objetivo: {value}
Leituras válidas: {value}%|Valid readings: {value}%|Lecturas válidas: {value}%
Tempo medido: {value}s|Measured time: {value}s|Tiempo medido: {value}s
Procurando na região atual…|Searching the current region…|Buscando en la región actual…
Procurando ao redor da barra…|Searching around the bar…|Buscando alrededor de la barra…
Procurando na tela do jogo…|Searching the game screen…|Buscando en la pantalla del juego…
Observando: pesca ativa|Observing: fishing active|Observando: pesca activa
Observando: item para coletar|Observing: item to collect|Observando: objeto para recoger
Observando: sem pesca ou item reconhecido|Observing: no fishing or item recognized|Observando: sin pesca ni objeto reconocido
Perfil atualizado · {n} pescas com leituras confiáveis|Profile updated · {n} catches with reliable readings|Perfil actualizado · {n} pescas con lecturas fiables
Falha interna ({error}). Tente retomar com F4.|Internal error ({error}). Try resuming with F4.|Error interno ({error}). Intenta continuar con F4.
Falha ao liberar comando. Feche o macro.|Unable to release input. Close the macro.|No se pudo soltar el comando. Cierra el macro.
Fechando|Closing|Cerrando
PESCA|FISHING|PESCA
Concentre-se no ritmo da água.|Focus on the rhythm of the water.|Concéntrate en el ritmo del agua.
Arraste ao redor da barra inteira, do topo até a base.|Drag around the entire bar, from top to bottom.|Arrastra alrededor de toda la barra, de arriba abajo.
Salvar seleção (Enter)|Save selection (Enter)|Guardar selección (Enter)
Cancelar (Esc)|Cancel (Esc)|Cancelar (Esc)
Confira o retângulo. Salvar fixa esta região no modo manual.|Check the rectangle. Saving fixes this region in manual mode.|Revisa el rectángulo. Guardar fija esta región en modo manual.
Seleção inválida. Arraste ao redor da barra vertical inteira.|Invalid selection. Drag around the entire vertical bar.|Selección no válida. Arrastra alrededor de toda la barra vertical.
Lançando a vara · tentativa {n}/{max}|Casting · attempt {n}/{max}|Lanzando la caña · intento {n}/{max}
Pesca confirmada. Acompanhando a barra.|Fishing confirmed. Tracking the bar.|Pesca confirmada. Siguiendo la barra.
Lançamento não confirmado|Cast not confirmed|Lanzamiento no confirmado
Marcador não reencontrado por 120 segundos|Marker not found for 120 seconds|Marcador no encontrado durante 120 segundos
Aguardando a recuperação das leituras da tela|Waiting for screen readings to recover|Esperando la recuperación de las lecturas de pantalla
Conferindo o estado da pesca|Checking fishing status|Comprobando el estado de la pesca
{reason}. Conferindo a tela; nova tentativa em {delay}s.|{reason}. Checking the screen; retrying in {delay}s.|{reason}. Comprobando la pantalla; nuevo intento en {delay}s.
Tentativa de coleta {n}/{max}|Collection attempt {n}/{max}|Intento de recogida {n}/{max}
Coletando com T · tentativa {n}/{max}|Collecting with T · attempt {n}/{max}|Recogiendo con T · intento {n}/{max}
Coleta confirmada|Collection confirmed|Recogida confirmada
Coleta não confirmada|Collection not confirmed|Recogida no confirmada
Sem recompensa detectada|No reward detected|No se detectó recompensa
{reason}. Próxima pesca…|{reason}. Next cast…|{reason}. Siguiente pesca…
Recuperação: aguardando uma leitura recente da tela.|Recovery: waiting for a recent screen reading.|Recuperación: esperando una lectura reciente de pantalla.
Aguardando confirmação da pesca…|Waiting for fishing confirmation…|Esperando confirmación de pesca…
Verificando se há item para coletar…|Checking for an item to collect…|Comprobando si hay un objeto para recoger…
Reencontrando a barra…|Finding the bar again…|Buscando la barra de nuevo…
Aguardando leitura da barra…|Waiting for a bar reading…|Esperando una lectura de la barra…
Aguardando confirmação da recompensa…|Waiting for reward confirmation…|Esperando confirmación de la recompensa…
Item desapareceu após T; recompensa não confirmada|Item disappeared after T; reward not confirmed|El objeto desapareció tras T; recompensa no confirmada
Nenhum item identificado em duas tentativas|No item identified in two attempts|Ningún objeto identificado en dos intentos
Conferindo novas capturas antes de decidir se repete a coleta…|Checking new frames before retrying collection…|Comprobando nuevas capturas antes de repetir la recogida…
Conferindo recompensa e presença do item após T…|Checking the reward and item after T…|Comprobando la recompensa y el objeto tras T…
Nome reconhecido|Name recognized|Nombre reconocido
Sim|Yes|Sí
Não|No|No'''

CATALOG={}
for row in _ROWS.splitlines():
    source,en,es=(value.replace('\\n','\n') for value in row.split('|'))
    CATALOG[source]={'en':en,'es':es}
PATTERNS=[]
for source,translations in sorted(CATALOG.items(),key=lambda pair:len(pair[0]),reverse=True):
    if '{' not in source:continue
    pattern='';last=0
    for match in re.finditer(r'\{(\w+)\}',source):
        pattern+=re.escape(source[last:match.start()])+f'(?P<{match[1]}>.+?)';last=match.end()
    PATTERNS.append((re.compile(pattern+re.escape(source[last:]),re.DOTALL),translations))

class Translator:
    def __init__(self,config):self.config=config

    def _translate(self,text):
        language=self.config.get('language','pt')
        if language=='pt':return text
        if text in CATALOG:return CATALOG[text].get(language,text)
        if '\n' in text:return '\n'.join(self._translate(line) for line in text.split('\n'))
        for pattern,translations in PATTERNS:
            match=pattern.fullmatch(text)
            if match:return translations.get(language,text).format(**{key:self._translate(value) for key,value in match.groupdict().items()})
        return text

    def __call__(self,text):
        text=self._translate(str(text))
        bindings=self.config.get('hotkeys',DEFAULT_HOTKEYS)
        replacements={default:bindings.get(action,default) for action,default in DEFAULT_HOTKEYS.items()}
        return re.sub(r'\bF(?:1[0-2]|[1-9])\b',lambda m:replacements.get(m[0],m[0]),text)

class LocalizedVar(tk.StringVar):
    def __init__(self,translator,master=None,value=''):
        self.translator=translator;self.raw=value
        super().__init__(master,value=translator(value))
    def set(self,value):
        self.raw=value;super().set(self.translator(value))
