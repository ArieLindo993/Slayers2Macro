"""Macro visual local para Slayers 2 / Windows."""
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import sys
import time
import traceback
import multiprocessing
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from background import BackgroundWorker
from datetime import datetime
import numpy as np
import mss
from PIL import Image, ImageTk, ImageDraw
from detector import detect
from engine import Engine
from signals import Signals
from item_history import ItemHistory, RewardReader
from item_icons import decode_icon
from calibration import AutoCalibration,locate_bar,search_bar
from selection import BarSelection
from product import APP_NAME,VERSION,GAME_PROFILE,DETECTOR_REVISION
from local_data import data_directory,migrate_legacy,ProfileStore
from diagnostics import Diagnostics,TrackingMetrics,annotated_preview,RuntimeJournal
from session_log import SessionLog
from theme import configure_theme,masthead,section,BG

U = C.WinDLL('user32', use_last_error=True)
K = C.WinDLL('kernel32', use_last_error=True)
try:
    U.SetProcessDpiAwarenessContext(C.c_void_p(-4))
except Exception:
    U.SetProcessDPIAware()
U.GetForegroundWindow.restype = W.HWND
U.GetClientRect.argtypes = [W.HWND, C.POINTER(W.RECT)]
U.ClientToScreen.argtypes = [W.HWND, C.POINTER(W.POINT)]
U.GetWindowThreadProcessId.argtypes = [W.HWND, C.POINTER(W.DWORD)]
K.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
K.OpenProcess.restype = W.HANDLE
K.QueryFullProcessImageNameW.argtypes = [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)]
K.CloseHandle.argtypes = [W.HANDLE]
U.GetAsyncKeyState.argtypes = [C.c_int]
U.GetAsyncKeyState.restype = C.c_short

# INPUT precisa incluir a união completa para ter o tamanho correto no Windows x64.
class MouseInput(C.Structure):
    _fields_=[('dx',W.LONG),('dy',W.LONG),('mouseData',W.DWORD),('dwFlags',W.DWORD),('time',W.DWORD),('dwExtraInfo',C.c_size_t)]
class KeyInput(C.Structure):
    _fields_=[('wVk',W.WORD),('wScan',W.WORD),('dwFlags',W.DWORD),('time',W.DWORD),('dwExtraInfo',C.c_size_t)]
class InputUnion(C.Union):
    _fields_=[('mi',MouseInput),('ki',KeyInput)]
class Input(C.Structure):
    _anonymous_=('data',)
    _fields_=[('type',W.DWORD),('data',InputUnion)]
U.SendInput.argtypes=[W.UINT,C.POINTER(Input),C.c_int]
U.SendInput.restype=W.UINT

def send_mouse(down):
    event=Input(type=0,mi=MouseInput(0,0,0,0x0002 if down else 0x0004,0,0))
    if U.SendInput(1,C.byref(event),C.sizeof(Input))!=1:
        raise RuntimeError('Windows não aceitou o comando de mouse.')

def send_t(down):
    # Scan code físico da tecla T, com key-down e key-up separados.
    event=Input(type=1,ki=KeyInput(0,0x14,0x0008 | (0 if down else 0x0002),0,0))
    if U.SendInput(1,C.byref(event),C.sizeof(Input))!=1:
        raise RuntimeError('Windows não aceitou o comando da tecla T.')


def game_window():
    hwnd = U.GetForegroundWindow()
    pid = W.DWORD()
    U.GetWindowThreadProcessId(hwnd, C.byref(pid))
    handle = K.OpenProcess(0x1000, False, pid.value)
    if not handle:
        return None
    try:
        name = C.create_unicode_buffer(32768)
        size = W.DWORD(len(name))
        if not K.QueryFullProcessImageNameW(handle, 0, name, C.byref(size)):
            return None
        if os.path.basename(name.value).lower() not in ('robloxplayerbeta.exe', 'windows10universal.exe'):
            return None
    finally:
        K.CloseHandle(handle)
    rect, origin = W.RECT(), W.POINT(0, 0)
    if not U.GetClientRect(hwnd, C.byref(rect)) or not U.ClientToScreen(hwnd, C.byref(origin)):
        return None
    if rect.right < 640 or rect.bottom < 360:
        return None
    return (int(hwnd), origin.x, origin.y, rect.right, rect.bottom)


def cursor_relative(window):
    p = W.POINT()
    U.GetCursorPos(C.byref(p))
    return ((p.x-window[1])/window[3], (p.y-window[2])/window[4])



DEFAULTS={'roi':[.733,.289,.034,.369],'cast':None,'anticipation':.10,
          'wait_seconds':20.,'result_wait':2.,'recast_seconds':1.5,
          'cast_hold':.25,'t_hold':3.0,'max_cast':3,'max_collect':5,'collect_timeout':35.,'auto_calibrate':True,'fast_collection_defaults':True}

# Observações lentas continuam úteis por um intervalo limitado. A barra usa
# capturas próprias em cada tick; nunca usa imagens atrasadas para mover o mouse.
SCENE_MAX_AGE=2.5

class App:
    def __init__(self):
        self.root=tk.Tk();self.root.title(APP_NAME+' · '+VERSION)
        self.root.geometry('900x720');self.root.resizable(False,False)
        self.base=Path(sys.executable if getattr(sys,'frozen',False) else __file__).parent
        self.data=data_directory();migrate_legacy(self.base,self.data)
        self.config_path=self.data/'config.json'
        self.session_log=SessionLog(self.data/'logs')
        self.session_log.event('APLICATIVO_ABERTO',versao=VERSION)
        self.last_log_snapshot=0;self.tracking_lost=False;self.previous_scene_item=False
        self.journal=RuntimeJournal(self.data/'runtime.json');self.journal.record('startup','INICIO')
        self.last_runtime=0
        self.profiles=ProfileStore(self.data/'profiles.json');self.profile_key=None
        self.metrics=TrackingMetrics();self.round_metrics=TrackingMetrics();self.last_metrics=0
        self.diagnostics=Diagnostics(self.data/'diagnostics');self.last_diagnostic=-float('inf')
        self.diagnostic_worker=BackgroundWorker('diagnostico-local',timeout=10,max_pending=1)
        self.diagnostic_job=None;self.last_live_preview=0
        self.config=dict(DEFAULTS)
        try:
            saved=json.loads(self.config_path.read_text('utf-8'))
            if not isinstance(saved,dict):raise ValueError()
            self.config['auto_calibrate']=saved.get('auto_calibrate',True) is not False
            self.config['diagnostics_enabled']=saved.get('diagnostics_enabled',True) is not False
            profile=saved.get('calibration_profile')
            if isinstance(profile,dict):
                roi=profile.get('roi',[])
                if len(roi)==4 and all(isinstance(v,(int,float)) and 0<v<1 for v in roi) and roi[0]+roi[2]<=1 and roi[1]+roi[3]<=1:
                    self.config['calibration_profile']=profile
            for key,lo,hi in [('cast_hold',.08,1),('t_hold',.2,5),('wait_seconds',10,60),('result_wait',.5,20)]:
                value=saved.get(key)
                if isinstance(value,(int,float)) and lo<=value<=hi:self.config[key]=value
            point=saved.get('cast')
            if isinstance(point,list) and len(point)==2 and all(isinstance(v,(int,float)) and 0<v<1 for v in point):self.config['cast']=point
            roi=saved.get('roi')
            if isinstance(roi,list) and len(roi)==4 and all(isinstance(v,(int,float)) for v in roi):
                x,y,w,h=roi
                if 0<=x<1 and 0<=y<1 and .005<w<.3 and .05<h<.9 and x+w<=1 and y+h<=1:self.config['roi']=roi
            # Migra o antigo padrão de 12 s uma única vez; mantém outros ajustes.
            if not saved.get('fast_collection_defaults') and self.config['result_wait']==12:
                self.config['result_wait']=2.
            self.config['fast_collection_defaults']=True
        except (ValueError,TypeError,OSError):pass
        if self.config['auto_calibrate'] and self.config.get('calibration_profile',{}).get('detector_revision')!=DETECTOR_REVISION:
            self.config['roi']=list(DEFAULTS['roi']);self.config['calibration_profile']={}
        self.calibration=AutoCalibration(self.config.get('calibration_profile'))
        if self.config['auto_calibrate'] and self.calibration.profile.get('roi'):
            self.config['roi']=list(self.calibration.profile['roi'])
        self.calibration_worker=BackgroundWorker('calibracao',timeout=10,max_pending=1)
        self.calibration_job=None;self.calibration_epoch=0;self.last_calibration=0
        self.selection=None;self.pending_selection=None
        assets=Path(getattr(sys,'_MEIPASS',self.base))/'assets'
        self.signals=Signals(assets)
        self.vision_worker=BackgroundWorker('sinais-visuais',timeout=10,max_pending=1)
        self.scene_job=None;self.scene_epoch=0;self.scene_time=0.;self.paused_state=None
        self.scene_latency=None;self.scene_dropped=0;self.last_vision_warning=-float('inf')
        self.capture_retry_at=0.;self.capture_failures=0;self.started_at=0.;self.last_tick=None
        self.tick_max_ms=0.;self.tick_stage='inicio';self.full_scene_at=0.
        self.engine=Engine(self.config)
        self.history=ItemHistory(self.data/'historico',log=self.session_log)
        self.history_window=None;self.history_tables=None
        self.history_photos={};self.pending_icons={}
        self.reader=RewardReader();self.worker=BackgroundWorker('leitura-itens',timeout=30,max_pending=3)
        self.ocr_job=None;self.confirmation_jobs=[];self.history_retries={};self.last_ocr=0.;self.ocr_results={};self.ocr_error=None
        self.cycle_id=0;self.last_reward_crop=None
        self.capture=mss.MSS();self.active=False;self.held=False;self.t_down=False
        self.window=None;self.pending_start=None;self.corner=None;self.previous_keys={}
        self.last_scene=0.;self.last_preview=0.;self.scene={'fishing':False,'loot':None,'reward':False}
        self.settings=None;self.preview=None
        self.dry=tk.BooleanVar(value=False)
        self.status=tk.StringVar(value='Marque a água com F8 para começar.')
        self.counter=tk.StringVar(value='0 ciclos   ·   0 coletas confirmadas')
        self.point_status=tk.StringVar()
        self.build_ui();self.refresh_point()
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.after(20,self.tick)

    def build_ui(self):
        configure_theme(self.root)
        main=ttk.Frame(self.root,padding=(26,20));main.pack(side='left',fill='both',expand=True)
        ttk.Separator(self.root,orient='vertical').pack(side='left',fill='y',pady=22)
        vision=ttk.Frame(self.root,padding=(20,24),width=262);vision.pack(side='right',fill='y');vision.pack_propagate(False)
        ttk.Label(vision,text='LEITURA DA ÁGUA',style='Accent.TLabel').pack(anchor='w')
        ttk.Label(vision,text='Reconhecimento',font=('Segoe UI',16,'bold')).pack(anchor='w',pady=(4,6))
        preview_card=ttk.Frame(vision,style='Panel.TFrame',padding=12);preview_card.pack(fill='x')
        self.live_preview=ttk.Label(preview_card,text='Aguardando a barra',anchor='center',style='PanelMuted.TLabel')
        self.live_preview.pack(fill='x',pady=4)
        ttk.Label(vision,text='Azul · região   Verde · alvo\nRosa · marcador',style='Muted.TLabel',font=('Segoe UI',9)).pack(anchor='w',pady=(10,0))
        self.metrics_text=tk.StringVar(value='Qualidade: aguardando leituras')
        ttk.Label(vision,textvariable=self.metrics_text,wraplength=218).pack(anchor='w',pady=10)
        self.profile_text=tk.StringVar(value='Perfil: aguardando o jogo')
        ttk.Label(vision,textvariable=self.profile_text,wraplength=218,style='Muted.TLabel').pack(anchor='w')
        ttk.Separator(vision).pack(fill='x',pady=10)
        ttk.Label(vision,text='REGISTROS DA SESSÃO',style='Accent.TLabel').pack(anchor='w',pady=(0,8))
        self.diagnostic_var=tk.BooleanVar(value=self.config.get('diagnostics_enabled',True))
        ttk.Checkbutton(vision,text='Salvar recortes',variable=self.diagnostic_var,command=self.toggle_diagnostics).pack(anchor='w')
        ttk.Label(vision,text='Até 20 recortes, salvos localmente.',style='Muted.TLabel',font=('Segoe UI',9)).pack(anchor='w',pady=(3,6))
        ttk.Button(vision,text='Abrir registros',style='Compact.TButton',command=self.open_diagnostics).pack(fill='x')
        ttk.Button(vision,text='Abrir logs de texto',style='Compact.TButton',command=self.open_logs).pack(fill='x',pady=6)
        self.log_status=tk.StringVar(value='Log de texto ativo')
        ttk.Label(vision,textvariable=self.log_status,style='Muted.TLabel',font=('Segoe UI',9)).pack(anchor='w')
        masthead(main,APP_NAME,VERSION,GAME_PROFILE)
        status_card=ttk.Frame(main,style='Panel.TFrame',padding=18);status_card.pack(fill='x')
        ttk.Label(status_card,text='SUA PESCARIA',style='PanelMuted.TLabel',font=('Segoe UI',9,'bold')).pack(anchor='w')
        ttk.Label(status_card,textvariable=self.status,font=('Segoe UI',12),style='Panel.TLabel',wraplength=510).pack(anchor='w',fill='x',pady=(9,10))
        ttk.Label(status_card,textvariable=self.counter,style='PanelMuted.TLabel').pack(anchor='w')
        section(main,'Preparação')
        ttk.Label(main,textvariable=self.point_status,style='Muted.TLabel',wraplength=530).pack(anchor='w',pady=(0,9))
        ttk.Label(main,text='F8  ·  Marcar a água       F6  ·  Selecionar a barra',style='Muted.TLabel',font=('Segoe UI',9)).pack(anchor='w')
        self.bar_status=tk.StringVar(value='Automático: conferir barra em cada pesca' if self.config['auto_calibrate'] else 'Barra: seleção manual salva')
        ttk.Label(main,textvariable=self.bar_status,style='Muted.TLabel',wraplength=530).pack(anchor='w',pady=(12,6))
        self.auto_var=tk.BooleanVar(value=self.config['auto_calibrate'])
        ttk.Checkbutton(main,text='Calibrar automaticamente a cada pesca',variable=self.auto_var,command=self.toggle_auto).pack(anchor='w')
        ttk.Button(main,text='Selecionar barra com o mouse',command=self.schedule_selection).pack(anchor='w',pady=(10,0))
        section(main,'Inventário da sessão')
        self.history_button=ttk.Button(main,text='Itens obtidos · 0',command=self.open_history)
        self.history_button.pack(fill='x')
        row=ttk.Frame(main);row.pack(fill='x',side='bottom',pady=(18,0))
        ttk.Label(row,text='F4  iniciar / pausar     ·     F10  parar',style='Muted.TLabel',font=('Segoe UI',9)).pack(side='bottom',pady=(12,0))
        ttk.Button(row,text='Configurar',command=self.open_settings).pack(side='right')
        ttk.Button(row,text='Parar',style='Stop.TButton',command=lambda:self.stop('Parado.')).pack(side='right',padx=7)
        self.start_button=ttk.Button(row,text='Iniciar',style='Go.TButton',command=self.button_start)
        self.start_button.pack(side='left',fill='x',expand=True,padx=(0,7))

    def open_history(self):
        # Abrir a janela pausa normalmente por perda de foco; o histórico é preservado.
        if self.history_window and self.history_window.winfo_exists():self.history_window.lift();return
        win=self.history_window=tk.Toplevel(self.root);win.title('Itens obtidos nesta sessão')
        win.geometry('660x460');win.minsize(540,360);win.configure(bg=BG)
        frame=ttk.Frame(win,padding=20);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='Itens obtidos',font=('Segoe UI',18,'bold')).pack(anchor='w')
        self.history_info=tk.StringVar()
        ttk.Label(frame,textvariable=self.history_info,style='Muted.TLabel',wraplength=610).pack(anchor='w',pady=(5,12))
        footer=ttk.Frame(frame);footer.pack(side='bottom',fill='x',pady=(12,0))
        ttk.Button(footer,text='Exportar CSV',command=self.export_history).pack(side='right')
        ttk.Button(footer,text='Limpar lista / nova sessão',command=self.clear_history).pack(side='left')
        tabs=ttk.Notebook(frame);tabs.pack(fill='both',expand=True)
        self.history_tables=[]
        ttk.Style(self.root).configure('History.Treeview',rowheight=42)
        for title,columns in [('Resumo',('Item','Quantidade')),('Histórico',('Horário','Item','Quantidade'))]:
            page=ttk.Frame(tabs);tabs.add(page,text=title)
            table=ttk.Treeview(page,columns=columns,show='tree headings',selectmode='browse',style='History.Treeview')
            table.heading('#0',text='Ícone');table.column('#0',width=58,minwidth=58,stretch=False,anchor='center')
            for column in columns:
                table.heading(column,text=column);table.column(column,width=340 if column=='Item' else 100,anchor='w' if column=='Item' else 'center')
            scroll=ttk.Scrollbar(page,orient='vertical',command=table.yview)
            table.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');table.pack(fill='both',expand=True)
            self.history_tables.append(table)
        self.refresh_history()

    def clear_history(self):
        self.stop('Nova sessão. Use F4 para iniciar.')
        self.history.save()
        self.session_log.event('NOVA_SESSAO_DE_ITENS')
        self.history=ItemHistory(self.data/'historico',log=self.session_log);self.metrics.reset();self.round_metrics.reset()
        self.ocr_results={};self.confirmation_jobs=[];self.ocr_job=None;self.last_reward_crop=None
        self.history_retries={}
        self.pending_icons={};self.history_photos={}
        self.engine.reset(time.monotonic());self.engine.state='PARADO';self.paused_state=None
        self.refresh_history();self.counter.set('0 ciclos · 0 coletas confirmadas')

    def refresh_history(self):
        self.history_button.configure(text=f'Itens obtidos · {self.history.total}')
        if not self.history_window or not self.history_window.winfo_exists():return
        unknown=sum(not e['identified'] for e in self.history.entries)
        text=f'Desde {self.history.started:%H:%M:%S} · {self.history.total} itens · {len(self.history.entries)} ciclos registrados'
        if unknown:text+=f' · {unknown} nome(s) não identificado(s)'
        if self.history.error:text+='\nNão foi possível salvar o histórico em disco; exporte o CSV.'
        if self.ocr_error:text+='\nLeitura dos nomes indisponível; as coletas continuam registradas.'
        self.history_info.set(text)
        for table in self.history_tables:
            children=table.get_children()
            if children:table.delete(*children)
        for name,qty in sorted(self.history.totals().items(),key=lambda item:item[0].casefold()):
            key=self.history.icons_by_name.get(name.casefold().strip())
            self.history_tables[0].insert('','end',values=(name,qty),**self.history_icon(key))
        for entry in reversed(self.history.entries):
            self.history_tables[1].insert('','end',values=(datetime.fromisoformat(entry['time']).strftime('%H:%M:%S'),entry['name'],entry['quantity'] if entry['quantity'] is not None else '?'),**self.history_icon(entry.get('icon')))
        self.history_photos={k:v for k,v in self.history_photos.items() if k in self.history.icons}

    def history_icon(self,key):
        if not key:return {'text':'—'}
        if key not in self.history_photos:
            image=decode_icon(self.history.icons.get(key))
            if image is None:return {'text':'—'}
            image.thumbnail((32,35),Image.Resampling.LANCZOS)
            self.history_photos[key]=ImageTk.PhotoImage(image,master=self.root)
        return {'image':self.history_photos[key]}

    def export_history(self):
        path=filedialog.asksaveasfilename(parent=self.history_window,title='Exportar itens',defaultextension='.csv',
               initialfile='itens-'+self.history.started.strftime('%Y%m%d-%H%M%S')+'.csv',filetypes=[('CSV','*.csv')])
        if path:
            try:self.history.export(path)
            except OSError as exc:messagebox.showerror('Erro ao exportar',str(exc),parent=self.history_window)

    def apply_reward_reading(self,cycle,result):
        entry=self.history.by_cycle.get(cycle)
        was_unconfirmed=bool(entry and entry.get('status')=='unconfirmed')
        if not self.history.identify(cycle,result,confirm=True):return
        if was_unconfirmed:
            self.engine.collected+=1
            self.engine.unconfirmed=max(0,self.engine.unconfirmed-1)
            self.counter.set(f'{self.engine.cycles} ciclos   ·   {self.engine.collected} coletas confirmadas')
        self.history.set_icon(cycle,self.pending_icons.pop(cycle,None))
        self.refresh_history()

    def poll_ocr(self):
        remaining=[]
        for future,cycle in self.confirmation_jobs:
            if not future.done():remaining.append((future,cycle));continue
            try:
                self.apply_reward_reading(cycle,future.result())
            except Exception as exc:
                self.session_log.event('ERRO_RECONHECIMENTO_ITEM',tipo=type(exc).__name__,ciclo=cycle)
                self.ocr_error=str(exc);self.refresh_history()
        self.confirmation_jobs=remaining
        if self.ocr_job is None or not self.ocr_job[0].done():return
        future,cycle,captured=self.ocr_job;self.ocr_job=None
        try:
            result=future.result();self.ocr_error=None
        except Exception as exc:
            self.session_log.event('ERRO_RECONHECIMENTO_ITEM',tipo=type(exc).__name__,ciclo=cycle)
            self.ocr_error=str(exc);self.refresh_history();return
        if result:
            self.ocr_results[cycle]=(result,captured)
            self.apply_reward_reading(cycle,result)

    def submit_ocr(self,crop,now):
        if self.ocr_job is not None:return
        self.last_ocr=now
        future=self.submit_background(self.worker,self.reader.read,crop.copy())
        if future is not None:self.ocr_job=(future,self.cycle_id,now)

    def refresh_point(self):
        self.point_status.set('Ponto na água salvo · F8 para alterar' if self.config['cast'] else 'Aponte para a água e pressione F8')

    def open_settings(self):
        self.stop('Ajuste as opções e volte ao jogo para iniciar.')
        if self.settings and self.settings.winfo_exists():self.settings.lift();return
        self.settings=tk.Toplevel(self.root);self.settings.title('Configurar pesca')
        self.settings.geometry('540x570');self.settings.resizable(False,False);self.settings.configure(bg=BG)
        frame=ttk.Frame(self.settings,padding=22);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='Ajustes',font=('Segoe UI',18,'bold')).pack(anchor='w',pady=(0,14))
        self.fields={}
        for key,label,lo,hi in [('cast_hold','Duração do clique (s)',.08,1),('t_hold','Segurar T (s)',.2,5),
                               ('wait_seconds','Esperar a pesca antes de repetir (s)',10,60),
                               ('result_wait','Esperar item depois da pesca (s)',.5,20)]:
            row=ttk.Frame(frame);row.pack(fill='x',pady=5)
            ttk.Label(row,text=label).pack(side='left')
            var=tk.StringVar(value=str(self.config[key]));self.fields[key]=(var,lo,hi)
            ttk.Spinbox(row,textvariable=var,from_=lo,to=hi,increment=.1,width=7).pack(side='right')
        ttk.Checkbutton(frame,text='Só observar (não envia comandos)',variable=self.dry,
                        command=lambda:self.stop('Modo de observação alterado.')).pack(anchor='w',pady=12)
        ttk.Label(frame,text='Calibrar a barra',font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(4,6))
        ttk.Label(frame,text='Automático: a barra é conferida em cada pesca.\nManual: F6 congela a imagem; arraste e salve.\nF8 salva o ponto de lançamento na água.',style='Muted.TLabel').pack(anchor='w')
        ttk.Label(frame,text='3 lançamentos por rodada; recuperação automática. Até 5 coletas.\nT é segurado mesmo se o painel desaparecer.',style='Muted.TLabel').pack(anchor='w',pady=12)
        self.preview=ttk.Label(frame,text='Prévia aparece no modo de observação',anchor='center')
        self.preview.pack(fill='x',expand=True)
        ttk.Button(frame,text='Salvar e fechar',style='Go.TButton',command=self.apply_settings).pack(fill='x',side='bottom')

    def apply_settings(self):
        values={}
        try:
            for key,(var,lo,hi) in self.fields.items():
                value=float(var.get().replace(',','.'))
                if not lo<=value<=hi:raise ValueError()
                values[key]=value
        except ValueError:
            messagebox.showerror('Valor inválido','Confira os tempos informados.',parent=self.settings);return
        self.config.update(values);self.save();self.settings.destroy();self.settings=None;self.preview=None
        self.session_log.event('AJUSTES_SALVOS',**values)
        self.status.set('Ajustes salvos. Use F4 dentro do jogo.')

    def save(self):
        try:
            self.config_path.write_text(json.dumps(self.config,indent=2),encoding='utf-8')
            self.profiles.save(self.profile_key,self.config['roi'],self.calibration.profile,self.config['auto_calibrate'])
        except OSError:self.status.set('Ajustes aplicados; não foi possível salvar nesta pasta.')

    def toggle_diagnostics(self):
        self.config['diagnostics_enabled']=self.diagnostic_var.get();self.save()

    def open_diagnostics(self):
        folder=self.data;folder.mkdir(parents=True,exist_ok=True)
        os.startfile(folder)

    def open_logs(self):
        folder=self.data/'logs';folder.mkdir(parents=True,exist_ok=True)
        os.startfile(folder)

    def choose_profile(self,window):
        try:
            U.GetDpiForWindow.argtypes=[W.HWND];U.GetDpiForWindow.restype=W.UINT
            dpi=U.GetDpiForWindow(window[0]) or 96
            U.GetWindowLongW.argtypes=[W.HWND,C.c_int];U.GetWindowLongW.restype=W.LONG
            mode='window' if U.GetWindowLongW(window[0],-16)&0x00C00000 else 'borderless'
        except (AttributeError,OSError):dpi=96;mode='window'
        key=self.profiles.key(window[3],window[4],mode,dpi)
        if key!=self.profile_key:
            if self.profile_key:self.save()
            # A configuração antiga só serve para migrar o primeiro perfil.
            fallback=DEFAULTS['roi'] if self.config['auto_calibrate'] or self.profiles.profiles else self.config['roi']
            roi,learned=self.profiles.load(key,fallback)
            automatic=self.profiles.profiles.get(key,{}).get('automatic',True if self.profiles.profiles else self.config['auto_calibrate']) is not False
            self.config['auto_calibrate']=automatic;self.auto_var.set(automatic)
            self.profile_key=key;self.config['roi']=roi
            self.config['calibration_profile']=learned;self.calibration=AutoCalibration(learned)
            self.calibration_epoch+=1;self.save()
            self.bar_status.set('Perfil automático: aguardando a barra' if automatic else 'Perfil manual: região salva')
        self.profile_text.set(f'Perfil: {window[3]} × {window[4]}\n'+('Janela' if mode=='window' else 'Sem bordas / tela cheia')+f' · {round(dpi/96*100)}%')

    def button_start(self):
        self.pending_selection=None
        if self.active or self.pending_start is not None:self.stop('Pausado.');return
        self.pending_start=time.monotonic()+3
        self.status.set('Volte ao Roblox. Início em 3 segundos…');self.start_button.configure(text='Cancelar')

    def mouse(self,down):
        if down and (not self.active or self.dry.get() or game_window()!=self.window):return
        if down!=self.held:send_mouse(down);self.held=down

    def key_t(self,down):
        if down and (not self.active or self.dry.get() or game_window()!=self.window):return
        if down!=self.t_down:
            send_t(down);self.t_down=down
            self.session_log.event('COMANDO_T_PRESSIONADO' if down else 'COMANDO_T_LIBERADO',ciclo=self.cycle_id)

    def stop(self,reason):
        self.session_log.event('APLICATIVO_FECHADO' if reason=='Fechando' else 'MACRO_PAUSADO',motivo=reason,estado=self.engine.state,ciclo=self.cycle_id)
        code=('closed' if reason=='Fechando' else 'internal_error' if reason.startswith('Falha interna') else
              'focus_lost' if 'Roblox' in reason or 'Janela alterada' in reason else
              'fishing_timeout' if '120 segundos' in reason else 'cast_unconfirmed' if '3 lançamentos' in reason else 'user_pause')
        self.journal.record(code,self.engine.state,active=False,cycles=self.engine.cycles)
        self.metrics.pause();self.round_metrics.pause()
        self.pending_selection=None
        if self.active:
            self.paused_state=self.engine.state
        self.active=False;self.pending_start=None
        # T e mouse são liberados separadamente mesmo se um comando falhar.
        try:self.mouse(False)
        finally:self.key_t(False)
        self.engine.state='PARADO';self.status.set(reason);self.start_button.configure(text='Iniciar')

    def start(self,window):
        self.pending_selection=None
        self.pending_start=None
        if not window:self.stop('Volte ao Roblox e pressione F4.');return
        self.choose_profile(window)
        if not self.config['cast'] and not self.dry.get():self.stop('Marque um ponto na água com F8.');return
        self.window=window;self.engine.reset(time.monotonic(),preserve_counts=True);self.active=True
        self.started_at=time.monotonic();self.capture_retry_at=0.;self.capture_failures=0
        self.session_log.event('MACRO_INICIADO',ciclo=self.cycle_id,modo='observação' if self.dry.get() else 'pesca',calibracao='automática' if self.config['auto_calibrate'] else 'manual',segurar_T=self.config['t_hold'],perfil=self.profile_key)
        self.journal.record('started',self.engine.state,active=True,cycles=self.engine.cycles)
        if self.paused_state in ('RESULTADO','MIRANDO_ITEM','TECLA_T','VERIFICANDO_COLETA'):
            self.engine.state='RESULTADO';self.engine.deadline=time.monotonic()+1
        self.paused_state=None;self.scene_epoch+=1;self.scene_time=0
        self.pending_icons={}
        self.calibration.begin();self.calibration_epoch+=1
        self.last_scene=0.;self.scene={'fishing':False,'loot':None,'reward':False}
        self.start_button.configure(text='Pausar');self.status.set('Conferindo a tela…')

    def keys(self):
        if self.selection is not None:return
        keys={k:bool(U.GetAsyncKeyState(k)&0x8000) for k in (0x73,0x75,0x76,0x77,0x79)}
        rising={k for k,v in keys.items() if v and not self.previous_keys.get(k)};self.previous_keys=keys
        if 0x79 in rising:self.pending_selection=None;self.stop('Parado com F10.');return
        window=game_window()
        if 0x73 in rising:
            if self.active or self.pending_start is not None:self.stop('Pausado com F4.')
            else:self.start(window)
        if not window:return
        if rising.intersection({0x75,0x76}):self.open_selection(window);return
        if 0x77 in rising:self.stop('Configurando…')
        if 0x77 in rising:
            point=cursor_relative(window)
            if all(0<v<1 for v in point):
                self.config['cast']=list(point);self.save();self.refresh_point();self.status.set('Água marcada. Pressione F4 para iniciar.')
                self.session_log.event('AGUA_MARCADA',ponto=point)

    def toggle_auto(self):
        self.config['auto_calibrate']=self.auto_var.get()
        self.session_log.event('MODO_CALIBRACAO_ALTERADO',automatico=self.config['auto_calibrate'])
        self.calibration.begin();self.calibration_epoch+=1;self.save()
        self.bar_status.set('Automático: aguardando a barra' if self.auto_var.get() else 'Manual: região atual fixa')

    def schedule_selection(self):
        self.stop('Volte ao Roblox com o minigame visível. Captura em 3 segundos…')
        self.pending_selection=time.monotonic()+3

    def open_selection(self,window):
        self.pending_selection=None
        if not window:self.status.set('Abra o minigame no Roblox e pressione F6.');return
        self.stop('Selecionando a barra. O macro está pausado.')
        self.window=window
        self.choose_profile(window)
        rgb=self.sample(full=True)
        self.calibration_epoch+=1
        self.selection=BarSelection(self.root,rgb,window,self.save_selection,self.selection_closed)

    def save_selection(self,roi):
        self.session_log.event('CALIBRACAO_MANUAL_SALVA',regiao=roi)
        self.config['roi']=roi;self.config['auto_calibrate']=False;self.auto_var.set(False)
        self.calibration.profile={};self.config['calibration_profile']={}
        self.calibration.begin();self.calibration_epoch+=1;self.save()
        self.bar_status.set('Barra manual salva · automático pode ser reativado')
        self.status.set('Seleção salva. Volte ao Roblox e pressione F4.')

    def selection_closed(self):
        self.selection=None

    def poll_calibration(self,now):
        if self.calibration_job is None or not self.calibration_job[0].done():return
        future,epoch,captured=self.calibration_job;self.calibration_job=None
        try:result=future.result()
        except Exception as exc:
            self.background_error('calibracao',exc);return
        if not self.config['auto_calibrate'] or epoch!=self.calibration_epoch or not 0<=now-captured<SCENE_MAX_AGE:return
        if self.engine.state not in ('INICIO','ESPERANDO','PESCANDO','RESULTADO','RECUPERANDO'):return
        # Uma lista, painel ou inventário não pode ensinar um novo perfil.
        # A confirmação do minigame vem de um sinal independente da barra.
        if not result['fishing']:
            self.calibration.pending=[]
            return
        roi=self.calibration.observe(result['candidate'])
        if roi:
            self.session_log.event('BARRA_LOCALIZADA',ciclo=self.cycle_id,regiao=roi)
            self.config['roi']=roi;self.engine.control.reset()
            self.bar_status.set('Barra automática confirmada · aprendendo nesta pesca')

    def background_error(self,component,exc):
        self.session_log.event('FALHA_TAREFA_VISUAL',componente=component,tipo=type(exc).__name__,
                               estado=self.engine.state,ciclo=self.cycle_id,acao='tentar nova captura')

    def submit_background(self,worker,function,*args):
        if not worker.can_submit:return None
        try:return worker.submit(function,*args)
        except Exception as exc:
            self.background_error(worker.name,exc)
            return None

    def poll_scene(self,now):
        if self.scene_job is not None and self.scene_job[0].done():
            job=self.scene_job;future,epoch,captured=job[:3];self.scene_job=None
            icon_cycle=job[3] if len(job)>3 else None
            try:scene=future.result()
            except Exception as exc:self.background_error('sinais',exc)
            else:
                self.scene_latency=max(0,now-captured)
                if epoch==self.scene_epoch and captured>self.scene_time and 0<=now-captured<SCENE_MAX_AGE:
                    self.scene=scene;self.scene_time=captured
                    if (not self.dry.get() and scene.get('reward') and scene.get('reward_icon')
                        and icon_cycle is not None and icon_cycle in (self.cycle_id-1,self.cycle_id)):
                        if icon_cycle in self.history.by_cycle:
                            if self.history.set_icon(icon_cycle,scene['reward_icon']):self.refresh_history()
                        else:self.pending_icons[icon_cycle]=scene['reward_icon']
                    visible=bool(scene.get('loot'))
                    if visible!=self.previous_scene_item:
                        self.session_log.event('ITEM_NA_VARA_DETECTADO' if visible else 'ITEM_NA_VARA_NAO_VISIVEL',ciclo=self.cycle_id)
                        self.previous_scene_item=visible
                else:
                    self.scene_dropped+=1
                    if now-self.last_vision_warning>=10:
                        self.last_vision_warning=now
                        self.session_log.event('CAPTURA_DESCARTADA',idade=round(now-captured,3),
                            mesma_etapa=epoch==self.scene_epoch,ciclo=self.cycle_id)
        if not 0<=now-self.scene_time<SCENE_MAX_AGE:
            self.scene={'fishing':False,'loot':None,'reward':False}

    def sync_window(self):
        current=game_window()
        if not current or not self.window or current[0]!=self.window[0]:
            self.stop('Pausado: o Roblox perdeu o foco. Volte ao jogo e use F4.');return False
        if current!=self.window:
            # A mesma janela continua em primeiro plano: ajuste as coordenadas,
            # invalide capturas antigas e solte comandos antes de observar de novo.
            self.mouse(False);self.key_t(False)
            self.window=current;self.choose_profile(current)
            self.scene_epoch+=1;self.scene_time=0.;self.scene={'fishing':False,'loot':None,'reward':False}
            self.calibration.begin();self.calibration_epoch+=1
            self.session_log.event('JANELA_REDIMENSIONADA',largura=current[3],altura=current[4],ciclo=self.cycle_id)
            self.execute(self.engine.recover(time.monotonic(),reason='vision_unavailable'))
        return True

    def sample(self,full=False):
        _,x,y,w,h=self.window
        if full:box={'left':x,'top':y,'width':w,'height':h}
        else:
            rx,ry,rw,rh=self.config['roi']
            box={'left':x+int(rx*w),'top':y+int(ry*h),'width':max(12,int(rw*w)),'height':max(60,int(rh*h))}
        return np.asarray(self.capture.grab(box))[:,:,:3][:,:,::-1].copy()

    def execute(self,actions):
        for kind,value in actions:
            if kind=='mouse':self.mouse(value)
            elif kind=='t':self.key_t(value)
            elif kind=='recover':
                self.session_log.event('RECUPERACAO_DE_LANCAMENTO',ciclo=self.cycle_id,rodada=value,
                    regiao=self.config['roi'],pesca_visivel=self.scene.get('fishing'),
                    item_visivel=bool(self.scene.get('loot')),pontuacao_pesca=self.scene.get('exit_score'),
                    idade_captura=round(time.monotonic()-self.scene_time,2) if self.scene_time else None,
                    motivo=self.engine.recovery_reason)
                self.calibration.begin();self.calibration.search_stage='screen';self.calibration_epoch+=1
            elif kind=='stop':self.stop(value)
            elif kind=='aim':
                if not self.active or game_window()!=self.window:self.stop('Janela alterada. Use F4 para retomar.');break
                _,x,y,w,h=self.window
                if not value or not all(0<v<1 for v in value):raise RuntimeError('Ponto de ação inválido.')
                if not U.SetCursorPos(int(x+value[0]*w),int(y+value[1]*h)):raise RuntimeError('Não foi possível posicionar o mouse.')

    def update(self,now):
        if not self.sync_window():return
        if now<self.capture_retry_at:return
        self.tick_stage='sinais';self.poll_scene(now)
        self.tick_stage='calibracao'
        self.poll_calibration(now)
        self.tick_stage='captura'
        rgb=self.sample();reading=detect(rgb,require_marker_shape=self.config['auto_calibrate'] and not self.calibration.locked)
        self.capture_failures=0
        lost=self.engine.state=='PESCANDO' and reading is None and now-self.engine.last_marker>=.2
        if lost!=self.tracking_lost:
            if lost or reading is not None:self.session_log.event('LEITURA_PERDIDA' if lost else 'LEITURA_RECUPERADA',ciclo=self.cycle_id)
            self.tracking_lost=lost
        if self.engine.state=='PESCANDO':
            self.metrics.observe(reading,now)
            self.round_metrics.observe(reading,now)
            self.calibration.sample(reading)
            if reading is None and now-self.engine.last_marker>=.5 and self.diagnostic_var.get() and now-self.last_diagnostic>=10 and (self.diagnostic_job is None or self.diagnostic_job.done()):
                self.last_diagnostic=now
                self.diagnostic_job=self.submit_background(self.diagnostic_worker,self.diagnostics.save,rgb.copy(),'PESCANDO',self.calibration.search_stage,self.metrics.summary())
            if self.config['auto_calibrate'] and self.calibration.check_tracking(reading,now):
                self.calibration_epoch+=1
                self.bar_status.set('Leitura perdida: recalibrando durante a pesca…')
        else:self.metrics.pause();self.round_metrics.pause()
        if now-self.last_live_preview>=.15:
            self.live_photo=ImageTk.PhotoImage(annotated_preview(rgb,reading))
            self.live_preview.configure(image=self.live_photo,text='');self.last_live_preview=now
            quality=self.metrics.summary();inside=quality['inside_percent']
            self.metrics_text.set(('Dentro da faixa: —' if inside is None else f'Dentro da faixa: {inside:.1f}%')+f'\nLeituras válidas: {quality["valid_percent"]:.1f}%\nTempo medido: {quality["observed_seconds"]:.1f}s')
        if self.diagnostic_job is not None and self.diagnostic_job.done():
            try:self.diagnostic_job.result()
            except Exception as exc:self.background_error('diagnostico',exc)
            self.diagnostic_job=None
        if now-self.last_scene>=.25 and self.scene_job is None and self.vision_worker.can_submit:
            self.tick_stage='captura'
            full=self.sample(full=True)
            captured=time.monotonic()
            self.tick_stage='agendamento_visual'
            if self.config['auto_calibrate'] and self.calibration_job is None and (not self.calibration.locked or now-getattr(self,'last_calibration_search',0)>=1) and self.engine.state in ('INICIO','ESPERANDO','PESCANDO','RESULTADO','RECUPERANDO'):
                stage=self.calibration.search_stage
                self.bar_status.set({'current':'Procurando na região atual…','nearby':'Procurando ao redor da barra…','screen':'Procurando na tela do jogo…'}[stage])
                future=self.submit_background(self.calibration_worker,self.signals.find_bar,full,self.config['roi'][:],stage)
                if future is not None:self.calibration_job=(future,self.calibration_epoch,captured)
                self.last_calibration_search=now
            # A busca de painel jamais bloqueia o controle de 20 ms da barra.
            quick=self.engine.state=='PESCANDO' and reading is not None and now-self.full_scene_at<1
            if not quick:self.full_scene_at=now
            future=self.submit_background(self.vision_worker,self.signals.scan,full,quick)
            icon_cycle=(self.cycle_id-1 if self.engine.state=='REINICIANDO' else self.cycle_id
                if self.engine.state in ('RESULTADO','MIRANDO_ITEM','TECLA_T','VERIFICANDO_COLETA') else None)
            if future is not None:self.scene_job=(future,self.scene_epoch,captured,icon_cycle)
            previous=self.cycle_id-1
            entry=self.history.by_cycle.get(previous)
            if (not self.dry.get() and self.engine.state=='REINICIANDO' and self.worker.can_submit and entry
                and (not entry['identified'] or entry.get('status')=='unconfirmed')
                and now-self.last_ocr>=.75 and self.history_retries.get(previous,0)<3
                and not any(cycle==previous for _,cycle in self.confirmation_jobs)):
                crop=RewardReader.crop(full,self.scene.get('reward_point'))
                future=self.submit_background(self.worker,self.reader.read,crop)
                if future is not None:self.confirmation_jobs.append((future,previous))
                self.history_retries[previous]=self.history_retries.get(previous,0)+1;self.last_ocr=now
            if not self.dry.get() and self.engine.state in ('RESULTADO','MIRANDO_ITEM','TECLA_T','VERIFICANDO_COLETA'):
                crop=RewardReader.crop(full,self.scene.get('reward_point'))
                if self.scene.get('reward'):self.last_reward_crop=crop
                if now-self.last_ocr>=.75 and self.worker.can_submit:self.submit_ocr(crop,now)
            self.last_scene=time.monotonic()
        now=time.monotonic()
        if self.preview is not None and self.preview.winfo_exists() and now-self.last_preview>.25:
            im=Image.fromarray(rgb);im.thumbnail((70,90));self.photo=ImageTk.PhotoImage(im)
            self.preview.configure(image=self.photo,text='');self.last_preview=now
        if self.dry.get():
            self.status.set('Observando: '+('pesca ativa' if reading or self.scene['fishing'] else 'item para coletar' if self.scene['loot'] else 'sem pesca ou item reconhecido'))
            return
        previous_cycles=self.engine.cycles;previous_collected=self.engine.collected
        parsed,captured=self.ocr_results.get(self.cycle_id,(None,0))
        # A leitura pertence ao ciclo capturado. Inicialização do OCR pode demorar
        # mais que quatro segundos na primeira coleta, sem invalidar a evidência.
        text_reward=parsed is not None
        previous_state=self.engine.state
        self.tick_stage='controle'
        if (reading is None and now-max(self.scene_time,self.started_at)>5
            and self.engine.state!='RECUPERANDO'):
            actions=self.engine.recover(now,reason='vision_unavailable')
        else:
            scene_valid=0<=now-self.scene_time<SCENE_MAX_AGE
            actions=self.engine.step(now,reading,self.scene['fishing'],self.scene['loot'],
                (self.scene.get('reward',False) and scene_valid) or text_reward,
                scene_stamp=self.scene_time,scene_valid=scene_valid)
        if previous_state in ('TECLA_T','VERIFICANDO_COLETA') and self.scene_time!=getattr(self,'last_collect_log_stamp',None):
            self.last_collect_log_stamp=self.scene_time
            self.session_log.event('VERIFICACAO_ITEM_APOS_T',ciclo=self.cycle_id,
                indicador_visivel=bool(self.scene.get('loot')),recompensa_visivel=bool(self.scene.get('reward')),
                pesca_visivel=bool(self.scene.get('fishing')),leitura_barra=reading is not None,
                idade_captura=round(now-self.scene_time,3),captura_valida=0<=now-self.scene_time<SCENE_MAX_AGE,
                capturas_sem_item=self.engine.absent_frames,item_visto_na_coleta=self.engine.loot_seen,
                tentativa=self.engine.collect_attempts,decisao=self.engine.state)
        if self.engine.state!=previous_state:
            events={'POSICIONANDO':'LANCAMENTO_PREPARADO','CLIQUE':'VARA_LANCADA','ESPERANDO':'AGUARDANDO_PESCA','PESCANDO':'MINIGAME_INICIADO','RESULTADO':'MINIGAME_ENCERRADO','MIRANDO_ITEM':'TENTATIVA_DE_COLETA','TECLA_T':'T_PRESSIONADO','VERIFICANDO_COLETA':'T_LIBERADO_VERIFICANDO_COLETA','REINICIANDO':'PREPARANDO_PROXIMA_PESCA','PARADO':'PARADA_AUTOMATICA','RECUPERANDO':'RECUPERACAO_AUTOMATICA'}
            self.session_log.event(events.get(self.engine.state,'MUDANCA_DE_ESTADO'),ciclo=self.cycle_id,anterior=previous_state,estado=self.engine.state,lancamento=self.engine.attempts,tentativa_coleta=self.engine.collect_attempts,descricao=self.engine.message)
        if previous_state=='PESCANDO' and self.engine.state!='PESCANDO':
            self.session_log.event('MINIGAME_FINALIZADO',ciclo=self.cycle_id,proxima_etapa=self.engine.state)
        if previous_state=='PESCANDO' and self.engine.state!='PESCANDO' and self.config['auto_calibrate']:
            profile=self.calibration.finish()
            if profile:
                self.config['calibration_profile']=profile
                self.config['roi']=list(profile['roi']);self.save()
                self.bar_status.set(f'Perfil atualizado · {profile["rounds"]} pescas com leituras confiáveis')
        self.tick_stage='comandos';self.execute(actions)
        self.tick_stage='historico'
        if self.engine.collected>previous_collected:
            self.history.record(self.cycle_id,parsed if text_reward else None,1 if self.scene.get('reward') else None)
            self.history.set_icon(self.cycle_id,self.pending_icons.pop(self.cycle_id,None))
            if not text_reward and self.last_reward_crop is not None and self.worker.can_submit:
                future=self.submit_background(self.worker,self.reader.read,self.last_reward_crop.copy())
                if future is not None:self.confirmation_jobs.append((future,self.cycle_id))
            self.refresh_history()
        if self.engine.cycles>previous_cycles:
            if self.engine.collected==previous_collected:
                self.history.record_outcome(self.cycle_id,self.engine.outcome)
                self.refresh_history()
            entry=self.history.by_cycle.get(self.cycle_id)
            if entry:
                entry['tracking_quality']=self.round_metrics.summary()
                entry['display_profile']=self.profile_key
                entry['anticipation']=self.config['anticipation']
                self.history.save()
            self.session_log.event('CICLO_CONCLUIDO',ciclo=self.cycle_id,resultado=self.engine.outcome,leituras_validas=self.round_metrics.summary()['valid_percent'],tempo_na_faixa=self.round_metrics.summary()['inside_percent'])
            self.round_metrics.reset()
            self.cycle_id+=1;self.last_reward_crop=None
            self.calibration.begin();self.calibration_epoch+=1
            # Resultados antigos só interessam enquanto resolvem uma linha pendente.
            self.ocr_results={k:v for k,v in self.ocr_results.items() if k>=self.cycle_id-1}
            self.history_retries={k:v for k,v in self.history_retries.items() if k>=self.cycle_id-1}
            self.pending_icons={k:v for k,v in self.pending_icons.items() if k>=self.cycle_id-1}
        if self.active:self.status.set(self.engine.message)
        self.counter.set(f'{self.engine.cycles} ciclos   ·   {self.engine.collected} coletas confirmadas')

    def tick(self):
        began=time.monotonic()
        try:
            self.tick_stage='tarefas'
            for worker in (self.worker,self.vision_worker,self.calibration_worker,self.diagnostic_worker):worker.poll()
            self.tick_stage='ocr'
            self.poll_ocr()
            self.tick_stage='atalhos'
            self.keys()
            if self.pending_selection is not None and time.monotonic()>=self.pending_selection:self.open_selection(game_window())
            if self.pending_start is not None and time.monotonic()>=self.pending_start:self.start(game_window())
            if self.active:self.update(time.monotonic())
            now=time.monotonic()
            self.tick_max_ms=max(self.tick_max_ms,(now-began)*1000)
            self.tick_stage='registros'
            if now-self.last_runtime>=5:
                self.last_runtime=now
                self.journal.checkpoint(self.engine.state,self.active,self.engine.cycles,now-self.scene_time)
            if now-self.last_log_snapshot>=30:
                self.last_log_snapshot=now
                self.session_log.event('ESTADO_PERIODICO',ativo=self.active,estado=self.engine.state,ciclo=self.cycle_id,
                    idade_leitura=round(now-self.scene_time,2) if self.scene_time else None,
                    atraso_analise=round(self.scene_latency,3) if self.scene_latency is not None else None,
                    capturas_descartadas=self.scene_dropped,maior_tick_ms=round(self.tick_max_ms,1),
                    capturas_recuperacao=self.engine.recovery_frames,
                    prazo_recuperacao=round(max(0,self.engine.deadline-now),1) if self.engine.state=='RECUPERANDO' else None,
                    tarefas_visao=self.vision_worker.pending_count,tarefas_ocr=self.worker.pending_count,
                    reinicios_visao=self.vision_worker.restarts,reinicios_calibracao=self.calibration_worker.restarts,
                    reinicios_ocr=self.worker.restarts)
                self.tick_max_ms=0.
            self.log_status.set('Falha ao gravar log' if self.session_log.error else 'Log de texto ativo')
        except mss.exception.ScreenShotError as exc:
            # Uma captura temporariamente indisponível não cancela a sessão.
            self.capture_failures+=1;now=time.monotonic()
            self.capture_retry_at=now+min(10,self.capture_failures)
            self.session_log.event('FALHA_CAPTURA',tipo=type(exc).__name__,etapa=self.tick_stage,
                                   tentativa=self.capture_failures,ciclo=self.cycle_id)
            try:
                self.execute(self.engine.recover(now,reason='vision_unavailable'))
                self.scene_epoch+=1;self.scene_time=0.;self.calibration_epoch+=1
                try:self.capture.close()
                except Exception:pass
                self.capture=mss.MSS()
            except Exception as failure:
                if not self.fail(failure):return
        except Exception as exc:
            if not self.fail(exc):return
        self.root.after(20,self.tick)

    def fail(self,exc):
        frames=traceback.extract_tb(exc.__traceback__)[-5:]
        trace=' > '.join(f'{Path(f.filename).name}:{f.lineno}:{f.name}' for f in frames)
        self.session_log.event('ERRO_INTERNO',tipo=type(exc).__name__,estado=self.engine.state,ciclo=self.cycle_id,
                               etapa=self.tick_stage,origem=trace)
        try:self.stop('Falha interna ('+type(exc).__name__+'). Tente retomar com F4.')
        except Exception:
            self.active=False;self.status.set('Falha ao liberar comando. Feche o macro.');self.root.destroy();return False
        return True

    def close(self):
        try:self.stop('Fechando')
        finally:
            if self.selection:self.selection.cancel()
            # shutdown has a bounded wait (at most one second per worker).
            self.diagnostic_worker.shutdown(cancel_futures=True)
            self.calibration_worker.shutdown(cancel_futures=True)
            self.vision_worker.shutdown(cancel_futures=True)
            self.worker.shutdown(cancel_futures=True);self.poll_ocr();self.history.save()
            self.session_log.event('ENCERRAMENTO_CONCLUIDO')
            self.capture.close();self.root.destroy()

    def run(self):
        try:self.root.mainloop()
        finally:
            try:self.mouse(False)
            finally:self.key_t(False)


if __name__=='__main__':
    multiprocessing.freeze_support()
    if len(sys.argv)==4 and sys.argv[1]=='--calibration-test':
        rgb=np.array(Image.open(sys.argv[2]).convert('RGB'))
        result=locate_bar(rgb)
        Path(sys.argv[3]).write_text(json.dumps(result),encoding='utf-8')
    elif len(sys.argv)==4 and sys.argv[1]=='--ocr-test':
        rgb=np.array(Image.open(sys.argv[2]).convert('RGB'))
        result=RewardReader().read(RewardReader.crop(rgb))
        Path(sys.argv[3]).write_text(json.dumps(result),encoding='utf-8')
    elif len(sys.argv)==3 and sys.argv[1]=='--self-test':
        import tempfile
        test_data=tempfile.TemporaryDirectory(prefix='fishing-selftest-')
        os.environ['FISHING_MACRO_DATA_DIR']=test_data.name
        app=App();app.root.withdraw();app.root.update_idletasks()
        result={'startup':True,'active':app.active,'screen_capture':False,'version':VERSION}
        test=app.capture.grab({'left':0,'top':0,'width':20,'height':20})
        result['screen_capture']=np.asarray(test).shape==(20,20,4)
        engine=Engine(dict(DEFAULTS,cast=[.5,.5]))
        engine.track(0);engine.step(1,None,False,(.5,.3))
        result['collect_without_prompt']=('t',True) in engine.step(1.3,None,False,None)
        result['vision_background']=hasattr(app,'vision_worker')
        result['auto_calibration']=app.config['auto_calibrate']
        result['manual_selection']=callable(app.open_selection)
        # Exercise spawn in the frozen executable, including the OCR model.
        # All frames are synthetic and no game input is sent.
        blank=np.zeros((1080,1920,3),np.uint8)
        jobs=[(app.vision_worker,app.vision_worker.submit(app.signals.scan,blank)),
              (app.calibration_worker,app.calibration_worker.submit(app.signals.find_bar,blank,DEFAULTS['roi'],'screen')),
              (app.worker,app.worker.submit(app.reader.read,np.zeros((48,352,3),np.uint8)))]
        deadline=time.monotonic()+30
        while not all(future.done() for _,future in jobs) and time.monotonic()<deadline:
            for worker,_ in jobs:worker.poll()
            time.sleep(.02)
        result['isolated_workers']=all(f.done() and f.exception() is None for _,f in jobs)
        result['blank_scene_safe']=result['isolated_workers'] and not jobs[0][1].result()['fishing'] and not jobs[1][1].result()['fishing'] and jobs[2][1].result() is None
        app.history.path=None;app.close();Path(sys.argv[2]).write_text(json.dumps(result),encoding='utf-8')
        test_data.cleanup()
    else:App().run()
