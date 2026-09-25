"""Seleção manual sobre uma captura congelada, sem cliques no jogo."""
import tkinter as tk
from PIL import Image,ImageTk
from calibration import selection_roi


class BarSelection:
    def __init__(self,parent,rgb,window,on_save,on_close):
        self.on_save=on_save;self.on_close=on_close
        self.size=(rgb.shape[1],rgb.shape[0]);self.roi=None;self.start=None;self.rect=None
        self.win=tk.Toplevel(parent);self.win.overrideredirect(True)
        _,x,y,w,h=window
        self.win.geometry(f'{w}x{h}{x:+d}{y:+d}');self.win.attributes('-topmost',True)
        self.canvas=tk.Canvas(self.win,highlightthickness=0,cursor='crosshair')
        self.canvas.pack(fill='both',expand=True)
        self.photo=ImageTk.PhotoImage(Image.fromarray(rgb),master=self.win)
        self.canvas.create_image(0,0,image=self.photo,anchor='nw')
        self.canvas.bind('<ButtonPress-1>',self.press)
        self.canvas.bind('<B1-Motion>',self.drag)
        self.canvas.bind('<ButtonRelease-1>',self.release)
        panel=tk.Frame(self.win,bg='#17252e',padx=18,pady=10)
        panel.place(relx=.5,y=14,anchor='n')
        self.message=tk.StringVar(value='Arraste ao redor da barra inteira, do topo até a base.')
        tk.Label(panel,textvariable=self.message,bg='#17252e',fg='white',font=('Segoe UI',12)).pack()
        row=tk.Frame(panel,bg='#17252e');row.pack(pady=(8,0))
        self.button=tk.Button(row,text='Salvar seleção (Enter)',command=self.accept,state='disabled')
        self.button.pack(side='left',padx=8)
        tk.Button(row,text='Cancelar (Esc)',command=self.cancel).pack(side='left',padx=8)
        self.win.bind('<Return>',lambda e:self.accept())
        self.win.bind('<Escape>',lambda e:self.cancel())
        self.win.bind('<F10>',lambda e:self.cancel())
        self.win.focus_force();self.win.grab_set()

    def press(self,event):
        self.start=(event.x,event.y);self.roi=None;self.button.configure(state='disabled')
        if self.rect:self.canvas.delete(self.rect)
        self.rect=self.canvas.create_rectangle(event.x,event.y,event.x,event.y,outline='#36f6ae',width=3)

    def drag(self,event):
        if self.start:self.canvas.coords(self.rect,*self.start,event.x,event.y)

    def release(self,event):
        if self.start is None:return
        self.drag(event)
        self.roi=selection_roi(self.start,(event.x,event.y),self.size)
        self.button.configure(state='normal' if self.roi else 'disabled')
        self.message.set('Confira o retângulo. Salvar fixa esta região no modo manual.' if self.roi else 'Seleção inválida. Arraste ao redor da barra vertical inteira.')

    def accept(self):
        if self.roi is None:return
        self.on_save(self.roi);self.close()

    def cancel(self):self.close()

    def close(self):
        self.win.grab_release();self.win.destroy();self.on_close()
