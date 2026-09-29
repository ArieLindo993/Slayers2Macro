"""Apresentação visual: não altera captura, atalhos ou controle da pesca."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys
from PIL import Image,ImageTk

BG='#0b1319'
PANEL='#111f27'
RAISED='#192d35'
INK='#e8efed'
MUTED='#9eafb3'
JADE='#62d4b2'
GOLD='#c9b27c'

def configure_theme(root):
    root.configure(bg=BG)
    style=ttk.Style(root);style.theme_use('clam')
    style.configure('.',font=('Segoe UI',10),background=BG,foreground=INK)
    style.configure('TFrame',background=BG)
    style.configure('Panel.TFrame',background=PANEL)
    style.configure('TLabel',background=BG,foreground=INK)
    style.configure('Muted.TLabel',foreground=MUTED)
    style.configure('Accent.TLabel',foreground=JADE,font=('Segoe UI',9,'bold'))
    style.configure('Panel.TLabel',background=PANEL,foreground=INK)
    style.configure('PanelMuted.TLabel',background=PANEL,foreground=MUTED)
    style.configure('TButton',padding=(14,10),borderwidth=1,background=RAISED,foreground=INK,
                    bordercolor='#2c434b',lightcolor=RAISED,darkcolor=RAISED,focuscolor=JADE)
    style.map('TButton',background=[('disabled',PANEL),('pressed','#274c50'),('active','#24424b')],
              foreground=[('disabled','#64787e')],bordercolor=[('focus',JADE)])
    style.configure('Go.TButton',background='#226853',foreground='#f1fff9',font=('Segoe UI',11,'bold'),bordercolor='#388b70')
    style.map('Go.TButton',background=[('pressed','#1c5143'),('active','#2b8066')])
    style.configure('Compact.TButton',padding=(12,7))
    style.configure('Stop.TButton',foreground='#e4b7ae')
    style.configure('TCheckbutton',background=BG,foreground=INK,indicatorbackground=RAISED,indicatorforeground=JADE)
    style.map('TCheckbutton',background=[('active',BG)],foreground=[('disabled',MUTED)],
              indicatorbackground=[('selected','#28795f'),('active','#35515a')])
    style.configure('TSpinbox',fieldbackground=PANEL,foreground=INK,arrowcolor=JADE,
                    background=RAISED,bordercolor='#35505a',insertcolor=INK,padding=6)
    style.map('TSpinbox',fieldbackground=[('readonly',PANEL)],foreground=[('disabled',MUTED)])
    style.configure('TCombobox',fieldbackground=PANEL,background=RAISED,foreground=INK,
                    arrowcolor=JADE,bordercolor='#35505a',padding=6)
    style.map('TCombobox',fieldbackground=[('readonly',PANEL)],foreground=[('readonly',INK)],
              selectbackground=[('readonly',PANEL)],selectforeground=[('readonly',INK)])
    root.option_add('*TCombobox*Listbox.background',PANEL)
    root.option_add('*TCombobox*Listbox.foreground',INK)
    root.option_add('*TCombobox*Listbox.selectBackground','#275647')
    root.option_add('*TCombobox*Listbox.selectForeground',INK)
    style.configure('Treeview',background=PANEL,fieldbackground=PANEL,foreground=INK,rowheight=30,borderwidth=0,bordercolor=PANEL,lightcolor=PANEL,darkcolor=PANEL)
    style.configure('Treeview.Heading',background=RAISED,foreground=JADE,padding=9,font=('Segoe UI',10,'bold'),bordercolor='#29404a',lightcolor=RAISED,darkcolor=RAISED)
    style.map('Treeview',background=[('selected','#275647')],foreground=[('selected','#ffffff')])
    style.map('Treeview.Heading',background=[('active','#24424b')])
    style.configure('TNotebook',background=BG,borderwidth=0)
    style.configure('TNotebook.Tab',background=PANEL,foreground=MUTED,padding=(16,9))
    style.map('TNotebook.Tab',background=[('selected',RAISED)],foreground=[('selected',JADE)])
    style.configure('Vertical.TScrollbar',background=RAISED,troughcolor=BG,arrowcolor=MUTED,borderwidth=0,bordercolor=BG,lightcolor=RAISED,darkcolor=RAISED)
    style.configure('TSeparator',background='#29404a')
    return style

def masthead(parent,title,version,profile,tr=str):
    canvas=tk.Canvas(parent,height=104,bg=BG,highlightthickness=0)
    canvas.pack(fill='x',pady=(0,18))
    assets=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'assets'
    with Image.open(assets/'game_icon.png') as source:
        canvas.game_icon=ImageTk.PhotoImage(source.convert('RGB').resize((64,64),Image.Resampling.LANCZOS),master=canvas)
    def draw(event):
        canvas.delete('all');w=event.width
        canvas.create_image(0,12,image=canvas.game_icon,anchor='nw')
        canvas.create_text(78,12,text=profile.upper()+'  /  '+tr('PESCA'),anchor='nw',fill=GOLD,font=('Segoe UI',9,'bold'))
        canvas.create_text(76,31,text=title,anchor='nw',fill=INK,font=('Segoe UI',25,'bold'))
        canvas.create_text(78,72,text=tr('Concentre-se no ritmo da água.'),anchor='nw',fill=MUTED,font=('Segoe UI',10))
        canvas.create_text(w-4,83,text=version if version.startswith('Beta ') else 'v'+version,anchor='e',fill=MUTED,font=('Segoe UI',9))
        canvas.create_line(0,102,w,102,fill='#28413e')
        canvas.create_line(0,102,64,102,fill=JADE,width=2)
    canvas.bind('<Configure>',draw)
    return canvas

def section(parent,label):
    ttk.Label(parent,text=label.upper(),style='Accent.TLabel').pack(anchor='w',pady=(18,8))
