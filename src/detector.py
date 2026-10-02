"""Detecção visual e controle, sem acesso ao jogo ou à memória dele."""
from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class Reading:
    target: float
    marker: float
    band: float


def longest_run(mask, minimum, maximum=None):
    indices = np.flatnonzero(mask)
    if not len(indices):
        return None
    groups = np.split(indices, np.flatnonzero(np.diff(indices) > 1) + 1)
    groups = [run for run in groups if len(run)>=minimum and (maximum is None or len(run)<=maximum)]
    if not groups:return None
    run = max(groups, key=len)
    if len(run) < minimum:
        return None
    return float((run[0] + run[-1]) / 2), len(run)


def outlined_target(rgb, margin, minimum, maximum):
    """Find paired yellow or neon-green target edges independently of the fill."""
    a=rgb.astype(np.int16)
    r,g,b=a[...,0],a[...,1],a[...,2]
    # The red/green balance distinguishes the yellow edge from a green map
    # even after a one-pixel outline is blended into nearby scenery.
    yellow=(r>100)&(g>110)&(b<165)&(r>g*.55)&(r>b*1.7)&(g>b*1.3)
    # Slayers 2 renders the same outline as lime green on some frames. When
    # the target crosses a green island its translucent fill merges with the
    # scenery, but the saturated, bright frame remains visible. Pairing its
    # two short horizontal edges avoids treating the island itself as a band.
    lime=(g>170)&((g-r)>50)&((g-b)>50)
    edge=yellow|lime
    central=edge[:,margin:rgb.shape[1]-margin]
    if central.shape[1]<1:return None
    # Scale the coverage threshold for narrow ROIs: four continuous pixels are
    # enough to keep the same visual test at compact Roblox resolutions.
    coverage=central.mean(axis=1)
    rows=coverage>=max(.30,min(.55,4/central.shape[1]))
    indices=np.flatnonzero(rows)
    if not len(indices):return None
    groups=np.split(indices,np.flatnonzero(np.diff(indices)>1)+1)
    lines=[group for group in groups if len(group)<=max(3,int(rgb.shape[0]*.025))]
    pairs=[]
    for i,top in enumerate(lines):
        for bottom in lines[i+1:]:
            size=int(bottom[-1]-top[0]+1)
            if not minimum<=size<=maximum:continue
            strength=min(float(coverage[top].mean()),float(coverage[bottom].mean()))
            center=(float(top[0])+float(bottom[-1]))/2
            pairs.append((strength,center,size))
    if not pairs:return None
    _,center,size=max(pairs,key=lambda item:(item[0],-item[2]))
    return center,size


def detect(rgb,require_marker_shape=False):
    h, w = rgb.shape[:2]
    if h < 60 or w < 12:
        return None
    a = rgb.astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # A faixa tem preenchimento translúcido verde/amarelo; o marcador
    # permanece claro mesmo quando os dois se sobrepõem.
    green = (g > 65) & (g > b * 1.02) & (r > 25) & (r < g * 1.4) & ((g > r * 1.12) | (r > b * 1.2))
    white = (r > 150) & (g > 160) & (b > 125) & ((np.maximum(r, g) - b) < 100) & (abs(r-g) < 85)
    # O mesmo marcador fica azul-acinzentado em quadros de baixo brilho.
    # Exija componente vermelha suficiente para excluir a água azul ao fundo.
    white |= (r>105)&(g>125)&(b>140)&(b>=g)&((b-r)<105)&(abs(r-g)<60)
    margin = max(2, int(w * .28))
    central = white[:, margin:w-margin]
    white_rows = central.mean(axis=1) > .35
    marker = longest_run(white_rows, max(3, int(h*.018)), h*.13)
    color_coverage = green.mean(axis=1)
    green_rows = color_coverage > .18
    # Fora do alvo o preenchimento amarelo/translúcido pode assumir a cor
    # do cenário. As bordas superior/inferior e laterais continuam coloridas.
    # Reconstrua só lacunas delimitadas, com suporte lateral em quase todas
    # as linhas; não una manchas separadas por fundo sem contorno.
    gaps=np.flatnonzero(~green_rows)
    if len(gaps):
        for gap in np.split(gaps,np.flatnonzero(np.diff(gaps)>1)+1):
            start,end=int(gap[0]),int(gap[-1])+1
            if start==0 or end==h or len(gap)>h*.15:continue
            if np.mean((color_coverage[start:end]>=.035)|white_rows[start:end])>=.8:
                green_rows[start:end]=True
    # O marcador pode ocultar o meio do alvo. Una apenas um intervalo
    # branco delimitado por verde dos dois lados, nunca o fundo escuro.
    if marker is not None:
        start=int(round(marker[0]-(marker[1]-1)/2));end=start+marker[1]
        if start>0 and end<h and green_rows[start-1] and green_rows[end]:
            green_rows[start:end]=True
    minimum=max(5,int(h*.035));maximum=h*.25
    # The translucent fill can inherit a green map texture and become
    # indistinguishable from the scenery. The target's thin yellow frame stays
    # visible in that case, so prefer its paired horizontal edges.
    target=outlined_target(rgb,margin,minimum,maximum)
    if target is None:
        target = longest_run(green_rows, minimum, maximum)
    if marker is None or target is None:
        return None
    if require_marker_shape:
        # A calibração não pode confundir linhas de texto com o quadrado
        # branco: exija um componente compacto e preenchido no centro.
        _,_,stats,_=cv2.connectedComponentsWithStats(white.astype(np.uint8),8)
        compact=False
        for x,y,bw,bh,area in stats[1:]:
            if (w*.2<=bw<=w*.7 and .55<=bw/max(1,bh)<=1.8
                and max(3,h*.018)<=bh<=h*.13 and area/(bw*bh)>=.72
                and abs(x+bw/2-w/2)<=w*.2 and y<=marker[0]<y+bh):
                compact=True;break
        if not compact:return None
    if marker[1] > h*.13 or not h*.035 <= target[1] <= h*.25:
        return None
    return Reading(target[0]/h, marker[0]/h, target[1]/h)


class Controller:
    def __init__(self):
        self.reset()

    def reset(self):
        self.last = None
        self.velocity = 0.
        self.held = False

    def step(self, reading, now, anticipation=.10):
        if self.last:
            old_y, old_time = self.last
            dt = now - old_time
            if .005 < dt < .25:
                v = np.clip((reading.marker-old_y)/dt, -3., 3.)
                self.velocity = .6*self.velocity + .4*float(v)
            else:
                self.velocity = 0.
        self.last = (reading.marker, now)
        predicted = reading.marker + self.velocity*anticipation
        error = predicted-reading.target
        deadzone = max(.008, reading.band*.12)
        if error > deadzone:
            self.held = True
        elif error < -deadzone:
            self.held = False
        return self.held
