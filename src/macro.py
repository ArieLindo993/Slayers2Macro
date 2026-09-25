"""Macro visual local para Slayers 2 / Windows."""
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import numpy as np
import mss
from PIL import Image, ImageTk, ImageDraw
from detector import detect
from engine import Engine
from signals import Signals
from item_history import ItemHistory, RewardReader
from calibration import AutoCalibration,locate_bar,search_bar
from selection import BarSelection
from product import APP_NAME,VERSION,GAME_PROFILE
from local_data import data_directory,migrate_legacy,ProfileStore
from diagnostics import Diagnostics,TrackingMetrics,annotated_preview

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
          'wait_seconds':20.,'result_wait':12.,'recast_seconds':1.5,
          'cast_hold':.25,'t_hold':1.5,'max_cast':3,'max_collect':5,'collect_timeout':35.,'auto_calibrate':True}

class App:
    def __init__(self):
        self.root=tk.Tk();self.root.title(APP_NAME+' · '+VERSION)
        self.root.geometry('820x610');self.root.resizable(False,False)
        self.base=Path(sys.executable if getattr(sys,'frozen',False) else __file__).parent
        self.data=data_directory();migrate_legacy(self.base,self.data)
        self.config_path=self.data/'config.json'
        self.profiles=ProfileStore(self.data/'profiles.json');self.profile_key=None
        self.metrics=TrackingMetrics();self.round_metrics=TrackingMetrics();self.last_metrics=0
        self.diagnostics=Diagnostics(self.data/'diagnostics');self.last_diagnostic=-float('inf')
        self.diagnostic_worker=ThreadPoolExecutor(max_workers=1,thread_name_prefix='diagnostico-local')
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
            for key,lo,hi in [('cast_hold',.08,1),('t_hold',.2,5),('wait_seconds',10,60),('result_wait',5,20)]:
                value=saved.get(key)
                if isinstance(value,(int,float)) and lo<=value<=hi:self.config[key]=value
            point=saved.get('cast')
            if isinstance(point,list) and len(point)==2 and all(isinstance(v,(int,float)) and 0<v<1 for v in point):self.config['cast']=point
            roi=saved.get('roi')
            if isinstance(roi,list) and len(roi)==4 and all(isinstance(v,(int,float)) for v in roi):
                x,y,w,h=roi
                if 0<=x<1 and 0<=y<1 and .005<w<.3 and .05<h<.9 and x+w<=1 and y+h<=1:self.config['roi']=roi
        except (ValueError,TypeError,OSError):pass
        self.calibration=AutoCalibration(self.config.get('calibration_profile'))
        if self.config['auto_calibrate'] and self.calibration.profile.get('roi'):
            self.config['roi']=list(self.calibration.profile['roi'])
        self.calibration_worker=ThreadPoolExecutor(max_workers=1,thread_name_prefix='calibracao')
        self.calibration_job=None;self.calibration_epoch=0;self.last_calibration=0
        self.selection=None;self.pending_selection=None
        assets=Path(getattr(sys,'_MEIPASS',self.base))/'assets'
        self.signals=Signals(assets)
        self.vision_worker=ThreadPoolExecutor(max_workers=1,thread_name_prefix='sinais-visuais')
        self.scene_job=None;self.scene_epoch=0;self.scene_time=0.;self.paused_state=None
        self.engine=Engine(self.config)
        self.history=ItemHistory(self.data/'historico')
        self.history_window=None;self.history_tables=None
        self.reader=RewardReader();self.worker=ThreadPoolExecutor(max_workers=1,thread_name_prefix='leitura-itens')
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
        bg='#f7f8fa';ink='#20282e';muted='#69757d'
        self.root.configure(bg=bg)
        style=ttk.Style(self.root);style.theme_use('clam')
        style.configure('.',font=('Segoe UI',10),background=bg,foreground=ink)
        style.configure('TFrame',background=bg)
        style.configure('TLabel',background=bg,foreground=ink)
        style.configure('Muted.TLabel',foreground=muted)
        style.configure('TButton',padding=(13,9),borderwidth=0,background='#e9edf0')
        style.map('TButton',background=[('active','#dfe5e9')])
        style.configure('Go.TButton',background='#167c66',foreground='white',font=('Segoe UI',11,'bold'))
        style.map('Go.TButton',background=[('active','#126451')])
        style.configure('TCheckbutton',background=bg)
        style.map('TCheckbutton',background=[('active',bg)])
        style.configure('TSpinbox',fieldbackground='white',foreground=ink)
        main=ttk.Frame(self.root,padding=20);main.pack(side='left',fill='both',expand=True)
        vision=ttk.Frame(self.root,padding=16,width=230);vision.pack(side='right',fill='y');vision.pack_propagate(False)
        ttk.Label(vision,text='Reconhecimento',font=('Segoe UI',14,'bold')).pack(anchor='w')
        self.live_preview=ttk.Label(vision,text='Aguardando a barra',anchor='center')
        self.live_preview.pack(fill='x',pady=12)
        ttk.Label(vision,text='Azul: região lida\nVerde: faixa alvo\nRosa: marcador',style='Muted.TLabel').pack(anchor='w')
        self.metrics_text=tk.StringVar(value='Qualidade: aguardando leituras')
        ttk.Label(vision,textvariable=self.metrics_text,wraplength=195).pack(anchor='w',pady=14)
        self.profile_text=tk.StringVar(value='Perfil: aguardando o jogo')
        ttk.Label(vision,textvariable=self.profile_text,wraplength=195,style='Muted.TLabel').pack(anchor='w')
        self.diagnostic_var=tk.BooleanVar(value=self.config.get('diagnostics_enabled',True))
        ttk.Checkbutton(vision,text='Diagnóstico local',variable=self.diagnostic_var,command=self.toggle_diagnostics).pack(anchor='w',pady=(16,0))
        ttk.Label(vision,text='Só o recorte da barra.\nAté 20 registros. Sem envio.',style='Muted.TLabel').pack(anchor='w',pady=6)
        ttk.Button(vision,text='Abrir diagnósticos',command=self.open_diagnostics).pack(anchor='w')
        head=ttk.Frame(main);head.pack(fill='x')
        ttk.Label(head,text=APP_NAME,font=('Segoe UI',23,'bold')).pack(side='left')
        ttk.Label(head,text=VERSION,style='Muted.TLabel',font=('Segoe UI',9)).pack(side='right')
        ttk.Label(main,text='Perfil de jogo: '+GAME_PROFILE,style='Muted.TLabel').pack(anchor='w')
        ttk.Label(main,textvariable=self.status,font=('Segoe UI',12),wraplength=415).pack(anchor='w',fill='x',pady=(24,12))
        ttk.Label(main,textvariable=self.counter,style='Muted.TLabel').pack(anchor='w')
        ttk.Label(main,textvariable=self.point_status,style='Muted.TLabel').pack(anchor='w',pady=(12,16))
        self.history_button=ttk.Button(main,text='Itens obtidos · 0',command=self.open_history)
        self.history_button.pack(anchor='w')
        ttk.Label(main,text='F8 marca a água · F6 seleciona a barra com o mouse',style='Muted.TLabel').pack(anchor='w',pady=(12,0))
        self.bar_status=tk.StringVar(value='Automático: conferir barra em cada pesca' if self.config['auto_calibrate'] else 'Barra: seleção manual salva')
        ttk.Label(main,textvariable=self.bar_status,style='Muted.TLabel',wraplength=480).pack(anchor='w',pady=4)
        self.auto_var=tk.BooleanVar(value=self.config['auto_calibrate'])
        ttk.Checkbutton(main,text='Calibrar automaticamente a cada pesca',variable=self.auto_var,command=self.toggle_auto).pack(anchor='w')
        ttk.Button(main,text='Selecionar barra com o mouse',command=self.schedule_selection).pack(anchor='w',pady=6)
        row=ttk.Frame(main);row.pack(fill='x',side='bottom')
        ttk.Label(row,text='F4 inicia / pausa   ·   F10 para',style='Muted.TLabel',font=('Segoe UI',9)).pack(side='bottom',pady=(14,0))
        ttk.Button(row,text='Configurar',command=self.open_settings).pack(side='right')
        ttk.Button(row,text='Parar',command=lambda:self.stop('Parado.')).pack(side='right',padx=5)
        self.start_button=ttk.Button(row,text='Iniciar',style='Go.TButton',command=self.button_start)
        self.start_button.pack(side='left',fill='x',expand=True,padx=(0,10))

    def open_history(self):
        # Abrir a janela pausa normalmente por perda de foco; o histórico é preservado.
        if self.history_window and self.history_window.winfo_exists():self.history_window.lift();return
        win=self.history_window=tk.Toplevel(self.root);win.title('Itens obtidos nesta sessão')
        win.geometry('660x460');win.minsize(540,360);win.configure(bg='#f7f8fa')
        frame=ttk.Frame(win,padding=20);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='Itens obtidos',font=('Segoe UI',18,'bold')).pack(anchor='w')
        self.history_info=tk.StringVar()
        ttk.Label(frame,textvariable=self.history_info,style='Muted.TLabel',wraplength=610).pack(anchor='w',pady=(5,12))
        tabs=ttk.Notebook(frame);tabs.pack(fill='both',expand=True)
        self.history_tables=[]
        for title,columns in [('Resumo',('Item','Quantidade')),('Histórico',('Horário','Item','Quantidade'))]:
            page=ttk.Frame(tabs);tabs.add(page,text=title)
            table=ttk.Treeview(page,columns=columns,show='headings',selectmode='browse')
            for column in columns:
                table.heading(column,text=column);table.column(column,width=340 if column=='Item' else 100,anchor='w' if column=='Item' else 'center')
            scroll=ttk.Scrollbar(page,orient='vertical',command=table.yview)
            table.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');table.pack(fill='both',expand=True)
            self.history_tables.append(table)
        ttk.Button(frame,text='Exportar CSV',command=self.export_history).pack(anchor='e',pady=(12,0))
        ttk.Button(frame,text='Limpar lista / nova sessão',command=self.clear_history).pack(anchor='w')
        self.refresh_history()

    def clear_history(self):
        self.stop('Nova sessão. Use F4 para iniciar.')
        self.history.save()
        self.history=ItemHistory(self.data/'historico');self.metrics.reset();self.round_metrics.reset()
        self.ocr_results={};self.confirmation_jobs=[];self.ocr_job=None;self.last_reward_crop=None
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
            self.history_tables[0].insert('','end',values=(name,qty))
        for entry in reversed(self.history.entries):
            self.history_tables[1].insert('','end',values=(datetime.fromisoformat(entry['time']).strftime('%H:%M:%S'),entry['name'],entry['quantity'] if entry['quantity'] is not None else '?'))

    def export_history(self):
        path=filedialog.asksaveasfilename(parent=self.history_window,title='Exportar itens',defaultextension='.csv',
               initialfile='itens-'+self.history.started.strftime('%Y%m%d-%H%M%S')+'.csv',filetypes=[('CSV','*.csv')])
        if path:
            try:self.history.export(path)
            except OSError as exc:messagebox.showerror('Erro ao exportar',str(exc),parent=self.history_window)

    def poll_ocr(self):
        remaining=[]
        for future,cycle in self.confirmation_jobs:
            if not future.done():remaining.append((future,cycle));continue
            try:
                if self.history.identify(cycle,future.result()):self.refresh_history()
            except Exception as exc:self.ocr_error=str(exc);self.refresh_history()
        self.confirmation_jobs=remaining
        if self.ocr_job is None or not self.ocr_job[0].done():return
        future,cycle,captured=self.ocr_job;self.ocr_job=None
        try:
            result=future.result();self.ocr_error=None
        except Exception as exc:
            self.ocr_error=str(exc);self.refresh_history();return
        if result:
            self.ocr_results[cycle]=(result,captured)
            if self.history.identify(cycle,result):self.refresh_history()

    def submit_ocr(self,crop,now):
        if self.ocr_job is not None:return
        self.last_ocr=now
        self.ocr_job=(self.worker.submit(self.reader.read,crop.copy()),self.cycle_id,now)

    def refresh_point(self):
        self.point_status.set('Ponto na água salvo · F8 para alterar' if self.config['cast'] else 'Aponte para a água e pressione F8')

    def open_settings(self):
        self.stop('Ajuste as opções e volte ao jogo para iniciar.')
        if self.settings and self.settings.winfo_exists():self.settings.lift();return
        self.settings=tk.Toplevel(self.root);self.settings.title('Configurar pesca')
        self.settings.geometry('540x570');self.settings.resizable(False,False);self.settings.configure(bg='#f7f8fa')
        frame=ttk.Frame(self.settings,padding=22);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='Ajustes',font=('Segoe UI',18,'bold')).pack(anchor='w',pady=(0,14))
        self.fields={}
        for key,label,lo,hi in [('cast_hold','Duração do clique (s)',.08,1),('t_hold','Segurar T (s)',.2,5),
                               ('wait_seconds','Esperar a pesca antes de repetir (s)',10,60),
                               ('result_wait','Esperar item depois da pesca (s)',5,20)]:
            row=ttk.Frame(frame);row.pack(fill='x',pady=5)
            ttk.Label(row,text=label).pack(side='left')
            var=tk.StringVar(value=str(self.config[key]));self.fields[key]=(var,lo,hi)
            ttk.Spinbox(row,textvariable=var,from_=lo,to=hi,increment=.1,width=7).pack(side='right')
        ttk.Checkbutton(frame,text='Só observar (não envia comandos)',variable=self.dry,
                        command=lambda:self.stop('Modo de observação alterado.')).pack(anchor='w',pady=12)
        ttk.Label(frame,text='Calibrar a barra',font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(4,6))
        ttk.Label(frame,text='Automático: a barra é conferida em cada pesca.\nManual: F6 congela a imagem; arraste e salve.\nF8 salva o ponto de lançamento na água.',style='Muted.TLabel').pack(anchor='w')
        ttk.Label(frame,text='Até 3 lançamentos e 5 tentativas de coleta.\nT é segurado mesmo se o painel desaparecer.',style='Muted.TLabel').pack(anchor='w',pady=12)
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
        self.status.set('Ajustes salvos. Use F4 dentro do jogo.')

    def save(self):
        try:
            self.config_path.write_text(json.dumps(self.config,indent=2),encoding='utf-8')
            self.profiles.save(self.profile_key,self.config['roi'],self.calibration.profile)
        except OSError:self.status.set('Ajustes aplicados; não foi possível salvar nesta pasta.')

    def toggle_diagnostics(self):
        self.config['diagnostics_enabled']=self.diagnostic_var.get();self.save()

    def open_diagnostics(self):
        folder=self.data/'diagnostics';folder.mkdir(parents=True,exist_ok=True)
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
            fallback=self.config['roi'] if not self.profiles.profiles else DEFAULTS['roi']
            roi,learned=self.profiles.load(key,fallback)
            self.profile_key=key;self.config['roi']=roi
            self.config['calibration_profile']=learned;self.calibration=AutoCalibration(learned)
            self.calibration_epoch+=1;self.save()
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
        if down!=self.t_down:send_t(down);self.t_down=down

    def stop(self,reason):
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
        if self.paused_state in ('RESULTADO','MIRANDO_ITEM','TECLA_T','VERIFICANDO_COLETA'):
            self.engine.state='RESULTADO';self.engine.deadline=time.monotonic()+1
        self.paused_state=None;self.scene_epoch+=1;self.scene_time=0
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

    def toggle_auto(self):
        self.config['auto_calibrate']=self.auto_var.get()
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
        candidate=future.result()
        if not self.config['auto_calibrate'] or epoch!=self.calibration_epoch or now-captured>1:return
        if self.engine.state not in ('INICIO','ESPERANDO','PESCANDO','RESULTADO'):return
        roi=self.calibration.observe(candidate)
        if roi:
            self.config['roi']=roi;self.engine.control.reset()
            self.bar_status.set('Barra automática confirmada · aprendendo nesta pesca')

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
            elif kind=='stop':self.stop(value)
            elif kind=='aim':
                if not self.active or game_window()!=self.window:self.stop('Janela alterada. Use F4 para retomar.');break
                _,x,y,w,h=self.window
                if not value or not all(0<v<1 for v in value):raise RuntimeError('Ponto de ação inválido.')
                if not U.SetCursorPos(int(x+value[0]*w),int(y+value[1]*h)):raise RuntimeError('Não foi possível posicionar o mouse.')

    def update(self,now):
        if game_window()!=self.window:self.stop('Pausado: volte ao Roblox e use F4.');return
        self.poll_calibration(now)
        rgb=self.sample();reading=detect(rgb)
        if self.engine.state=='PESCANDO':
            self.metrics.observe(reading,now)
            self.round_metrics.observe(reading,now)
            self.calibration.sample(reading)
            if reading is None and now-self.engine.last_marker>=.5 and self.diagnostic_var.get() and now-self.last_diagnostic>=10 and (self.diagnostic_job is None or self.diagnostic_job.done()):
                self.last_diagnostic=now
                self.diagnostic_job=self.diagnostic_worker.submit(self.diagnostics.save,rgb.copy(),'PESCANDO',self.calibration.search_stage,self.metrics.summary())
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
            except OSError:self.status.set('Não foi possível salvar o diagnóstico local.')
            self.diagnostic_job=None
        if self.scene_job is not None and self.scene_job[0].done():
            future,epoch,captured=self.scene_job;self.scene_job=None
            scene=future.result()
            if epoch==self.scene_epoch and now-captured<1:
                self.scene=scene;self.scene_time=captured
        if now-self.scene_time>1:
            self.scene={'fishing':False,'loot':None,'reward':False}
        if now-self.last_scene>=.25 and self.scene_job is None:
            full=self.sample(full=True)
            if self.config['auto_calibrate'] and not self.calibration.locked and self.calibration_job is None and self.engine.state in ('INICIO','ESPERANDO','PESCANDO','RESULTADO'):
                stage=self.calibration.search_stage
                self.bar_status.set({'current':'Procurando na região atual…','nearby':'Procurando ao redor da barra…','screen':'Procurando na tela do jogo…'}[stage])
                self.calibration_job=(self.calibration_worker.submit(search_bar,full,self.config['roi'][:],stage),self.calibration_epoch,now)
            # A busca de painel jamais bloqueia o controle de 20 ms da barra.
            self.scene_job=(self.vision_worker.submit(self.signals.scan,full),self.scene_epoch,now)
            previous=self.cycle_id-1
            entry=self.history.by_cycle.get(previous)
            if (not self.dry.get() and self.scene.get('reward') and entry and not entry['identified']
                and now-self.last_ocr>=.75 and self.history_retries.get(previous,0)<3
                and not any(cycle==previous for _,cycle in self.confirmation_jobs)):
                crop=RewardReader.crop(full,self.scene.get('reward_point'))
                self.confirmation_jobs.append((self.worker.submit(self.reader.read,crop),previous))
                self.history_retries[previous]=self.history_retries.get(previous,0)+1;self.last_ocr=now
            if not self.dry.get() and self.engine.state in ('RESULTADO','MIRANDO_ITEM','TECLA_T','VERIFICANDO_COLETA'):
                crop=RewardReader.crop(full,self.scene.get('reward_point'))
                if self.scene.get('reward'):self.last_reward_crop=crop
                if now-self.last_ocr>=.75:self.submit_ocr(crop,now)
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
        text_reward=parsed is not None and now-captured<4
        previous_state=self.engine.state
        actions=self.engine.step(now,reading,self.scene['fishing'],self.scene['loot'],self.scene.get('reward',False) or text_reward)
        if previous_state=='PESCANDO' and self.engine.state!='PESCANDO' and self.config['auto_calibrate']:
            profile=self.calibration.finish()
            if profile:
                self.config['calibration_profile']=profile
                self.config['roi']=list(profile['roi']);self.save()
                self.bar_status.set(f'Perfil atualizado · {profile["rounds"]} pescas com leituras confiáveis')
        self.execute(actions)
        if self.engine.collected>previous_collected:
            self.history.record(self.cycle_id,parsed if text_reward else None,1 if self.scene.get('reward') else None)
            if not text_reward and self.last_reward_crop is not None:
                self.confirmation_jobs.append((self.worker.submit(self.reader.read,self.last_reward_crop.copy()),self.cycle_id))
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
            self.round_metrics.reset()
            self.cycle_id+=1;self.last_reward_crop=None
            self.calibration.begin();self.calibration_epoch+=1
            # Resultados antigos só interessam enquanto resolvem uma linha pendente.
            self.ocr_results={k:v for k,v in self.ocr_results.items() if k>=self.cycle_id-1}
        if self.active:self.status.set(self.engine.message)
        self.counter.set(f'{self.engine.cycles} ciclos   ·   {self.engine.collected} coletas confirmadas')

    def tick(self):
        try:
            self.poll_ocr()
            self.keys()
            if self.pending_selection is not None and time.monotonic()>=self.pending_selection:self.open_selection(game_window())
            if self.pending_start is not None and time.monotonic()>=self.pending_start:self.start(game_window())
            if self.active:self.update(time.monotonic())
        except Exception as exc:
            try:self.stop('Falha interna ('+type(exc).__name__+'). Tente retomar com F4.')
            except Exception:self.active=False;self.status.set('Falha ao liberar comando. Feche o macro.');self.root.destroy();return
        self.root.after(20,self.tick)

    def close(self):
        try:self.stop('Fechando')
        finally:
            if self.selection:self.selection.cancel()
            self.diagnostic_worker.shutdown(wait=True,cancel_futures=False)
            self.calibration_worker.shutdown(wait=True,cancel_futures=True)
            self.vision_worker.shutdown(wait=True,cancel_futures=True)
            self.worker.shutdown(wait=True,cancel_futures=False);self.poll_ocr();self.history.save()
            self.capture.close();self.root.destroy()

    def run(self):
        try:self.root.mainloop()
        finally:
            try:self.mouse(False)
            finally:self.key_t(False)


if __name__=='__main__':
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
        app.history.path=None;app.close();Path(sys.argv[2]).write_text(json.dumps(result),encoding='utf-8')
        test_data.cleanup()
    else:App().run()
