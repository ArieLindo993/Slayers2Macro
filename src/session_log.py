"""Log textual local por execução; não apaga sessões anteriores."""
from datetime import datetime
from pathlib import Path
import re

class SessionLog:
    def __init__(self,directory):
        stamp=datetime.now().astimezone().strftime('%Y%m%d-%H%M%S-%f')
        self.path=Path(directory)/f'sessao-{stamp}.txt';self.error=False

    @staticmethod
    def clean(value):
        text=' '.join(str(value).split())
        text=re.sub(r'[A-Za-z]:[\\/][^|]*','[caminho local omitido]',text)
        return ''.join(c for c in text if c.isprintable())[:500]

    def event(self,event,**details):
        timestamp=datetime.now().astimezone().isoformat(timespec='milliseconds')
        fields=' | '.join(f'{self.clean(k)}={self.clean(v)}' for k,v in details.items() if v is not None)
        line=f'[{timestamp}] {self.clean(event)}'+(' | '+fields if fields else '')+'\n'
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open('a',encoding='utf-8') as stream:stream.write(line)
            self.error=False;return True
        except OSError:
            self.error=True;return False
