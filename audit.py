"""Impede publicar diretórios pessoais e dados de execução por engano."""
from pathlib import Path
import re,subprocess
root=Path(__file__).resolve().parent
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
for name in filter(None,tracked):
    p=root/name
    assert p.name not in ('runtime.json','runtime.tmp','config.json','profiles.json'),name
    assert not any(x in p.parts for x in ('historico','diagnostics','.install')),name
    assert p.suffix.lower() not in ('.mp4','.pem','.zip'),name
    if p.suffix.lower() in ('.py','.md','.txt','.ps1','.yml','.cmd'):
        text=p.read_text('utf-8')
        assert not re.search(r'[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/]',text),name
        assert not re.search(r'/(?:home|Users)/[A-Za-z0-9_-]+/',text),name
print('PASS: arquivos versionados sem caminhos pessoais ou dados de execução.')
