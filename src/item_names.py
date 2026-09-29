"""Names observed in rewards; conservative aliases, never arbitrary fuzzy merging."""
import re

def key(name):return re.sub(r'[^a-z0-9]','',str(name).casefold())

NAMES=('Clown Fish','Golden Fish','Zebra Fish','Crustadon','Krathulon','Coral','Sea Horse',
       'OuwFish','OuwFwesh','Refinement Ore','Mythic Refinement Ore','Metal Scraps',
       'Silk Thread','Squid Beanie','Lost Cape','Lost Lantern','Lost Outfit','Lost Shotgun')
KNOWN={key(name):name for name in NAMES}
ALIASES={}
for canonical,variants in {
    'Clown Fish':('clown','clown f','clown fi','clown fis','cown fish'),
    'Golden Fish':('goden fish','goiden fish','gorden fish'),
    'Zebra Fish':('zenra fish','zeora fish'),
    'Crustadon':('custadon','cstadon','ostadon','tadon'),
    'Sea Horse':('eahorse','sehorse'),
    'Coral':('conal','mcoral'),
    'OuwFwesh':('ouufwesh',),
    'Refinement Ore':('refnement ore',),
}.items():
    for variant in variants:ALIASES[key(variant)]=canonical

def canonical_name(name):
    name=' '.join(str(name).split());normalized=key(name)
    return KNOWN.get(normalized,ALIASES.get(normalized,name))

def resembles_known(text,candidate):
    limit=2 if len(candidate)>=8 else 1
    if abs(len(text)-len(candidate))>limit:return False
    previous=list(range(len(candidate)+1))
    for i,char in enumerate(text,1):
        current=[i]
        for j,other in enumerate(candidate,1):
            current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(char!=other)))
        if min(current)>limit:return False
        previous=current
    return previous[-1]<=limit

def name_evidence(name):
    canonical=canonical_name(name);normalized=key(canonical)
    known=normalized in KNOWN
    # A shared suffix like Fish or Ore cannot establish which item was caught.
    fragment=(not known and (len(normalized)<5 or
        any(normalized in candidate or resembles_known(normalized,candidate) for candidate in KNOWN) or
        (normalized.endswith('fish') and len(normalized[:-4])<4)))
    return canonical,known,fragment
