"""Validated user preferences, independent of fishing/display profiles."""
LANGUAGES={'pt':'Português','en':'English','es':'Español'}
DEFAULT_HOTKEYS={'toggle':'F4','water':'F8','calibrate':'F6','calibrate_alt':'F7','stop':'F10'}
KEY_CODES={f'F{i}':0x6f+i for i in range(1,13)}
KEY_CODES.update({c:ord(c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' if c!='T'})

def validate_hotkeys(value):
    if not isinstance(value,dict):raise ValueError('Invalid shortcuts')
    result={action:str(value.get(action,default)).upper() for action,default in DEFAULT_HOTKEYS.items()}
    if any(key not in KEY_CODES for key in result.values()):raise ValueError('Unsupported key')
    if len(set(result.values()))!=len(result):raise ValueError('Duplicate shortcuts')
    return result

def load_preferences(saved):
    language=saved.get('language','pt')
    if not isinstance(language,str) or language not in LANGUAGES:language='pt'
    try:hotkeys=validate_hotkeys(saved.get('hotkeys',{}))
    except ValueError:hotkeys=dict(DEFAULT_HOTKEYS)
    return {'language':language,'hotkeys':hotkeys}
