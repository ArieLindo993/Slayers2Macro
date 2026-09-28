"""Updater integration tests with local downloads; no real executable is launched."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


@unittest.skipUnless(sys.platform == 'win32', 'Windows updater')
class UpdateIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='update-integrity-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.script = self.base / 'Atualizar.ps1'
        shutil.copy2(Path(__file__).resolve().parents[1] / 'Atualizar.ps1', self.script)
        self.install = self.base / '.install'
        self.install.mkdir()
        self.archive = self.base / 'fixture.zip'
        with zipfile.ZipFile(self.archive, 'w') as bundle:
            bundle.writestr('Slayers2Macro.exe', b'new placeholder; never executed')
            bundle.writestr('_internal/runtime.dat', b'complete dependency')
        self.checksum = self.base / 'fixture.sha256'
        self.checksum.write_text(hashlib.sha256(self.archive.read_bytes()).hexdigest())
        self.downloads = self.base / 'downloads.txt'
        self.environment = dict(os.environ, LOCALAPPDATA=str(self.base / 'appdata'),
                                UPDATER_SCRIPT=str(self.script), UPDATE_ZIP=str(self.archive),
                                UPDATE_HASH=str(self.checksum), UPDATE_DOWNLOADS=str(self.downloads))

    def legacy(self, version):
        directory = self.install / version
        directory.mkdir()
        (directory / 'Slayers2Macro.exe').write_bytes(b'legacy placeholder; never executed')
        return directory

    def run_updater(self, extra='', arguments='-NaoAbrir'):
        wrapper = self.base / 'run-fixture.ps1'
        wrapper.write_text(r'''
$ErrorActionPreference = 'Stop'
Import-Module Microsoft.PowerShell.Utility
Import-Module Microsoft.PowerShell.Archive
function Get-Process { [CmdletBinding()]param([string]$Name) }
# Keep PowerShell command/module discovery intact. Intercept only GitHub's CLI
# so this fixture never reads the user's credentials or contacts the service.
function gh { $global:LASTEXITCODE = 0 }
function Invoke-RestMethod {
    param($Uri, $Headers, $TimeoutSec)
    return [pscustomobject]@{ id = 2; tag_name = 'test'; assets = @(
        [pscustomobject]@{ name = 'Slayers2Macro.zip'; url = 'local-zip'; size = 100 },
        [pscustomobject]@{ name = 'Slayers2Macro.zip.sha256'; url = 'local-hash' }
    ) }
}
function Invoke-WebRequest {
    param([switch]$UseBasicParsing, $Uri, $Headers, $OutFile, $TimeoutSec)
    Add-Content -LiteralPath $env:UPDATE_DOWNLOADS -Value $Uri
    $source = if ($Uri -eq 'local-zip') { $env:UPDATE_ZIP } else { $env:UPDATE_HASH }
    Copy-Item -LiteralPath $source -Destination $OutFile
}
''' + extra + '\n& $env:UPDATER_SCRIPT ' + arguments + '\nexit $LASTEXITCODE\n', encoding='utf-8')
        return subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                               '-File', str(wrapper)], env=self.environment,
                              text=True, capture_output=True, timeout=45)

    def test_partial_or_legacy_same_version_is_repaired_and_then_reused(self):
        current = self.legacy('2')
        (current / 'config.json').write_text('{"cast":[0.4,0.5]}')
        (current / 'historico').mkdir()
        (current / 'historico' / 'session.json').write_text('{"items":7}')
        (self.install / 'current.txt').write_text('2')
        result = self.run_updater()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((current / '_internal/runtime.dat').read_bytes(), b'complete dependency')
        self.assertEqual((current / 'installation.complete').read_text().strip(), '2')
        self.assertEqual((current / 'historico/session.json').read_text(), '{"items":7}')
        self.assertEqual((current / 'config.json').read_text(), '{"cast":[0.4,0.5]}')
        self.assertEqual(self.downloads.read_text().splitlines(), ['local-zip', 'local-hash'])
        result = self.run_updater()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(self.downloads.read_text().splitlines()), 2)

    def test_interrupted_extraction_preserves_old_install_and_retry_succeeds(self):
        old = self.legacy('1')
        (self.install / 'current.txt').write_text('1')
        result = self.run_updater(r'''
function Expand-Archive {
    param($LiteralPath, $DestinationPath)
    New-Item -ItemType Directory -Path $DestinationPath | Out-Null
    Set-Content -LiteralPath (Join-Path $DestinationPath 'Slayers2Macro.exe') -Value 'partial'
    throw 'simulated interrupted extraction'
}
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('simulated interrupted extraction',result.stdout)
        self.assertEqual((self.install / 'current.txt').read_text().strip(), '1')
        self.assertEqual((old / 'Slayers2Macro.exe').read_bytes(), b'legacy placeholder; never executed')
        self.assertFalse((self.install / '2').exists())
        self.assertFalse(list(self.install.glob('staging-*/package/installation.complete')))
        result = self.run_updater()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.install / 'current.txt').read_text().strip(), '2')
        self.assertEqual((self.install / 'previous.txt').read_text().strip(), '1')

    def test_incomplete_extraction_returning_success_is_rejected(self):
        self.legacy('1')
        (self.install / 'current.txt').write_text('1')
        result = self.run_updater(r'''
function Expand-Archive {
    param($LiteralPath, $DestinationPath)
    New-Item -ItemType Directory -Path $DestinationPath | Out-Null
    Set-Content -LiteralPath (Join-Path $DestinationPath 'Slayers2Macro.exe') -Value 'partial'
}
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Extracao incompleta',result.stdout)
        self.assertEqual((self.install / 'current.txt').read_text().strip(), '1')
        self.assertFalse((self.install / '2').exists())

    def test_corrupted_archive_is_rejected_before_extraction(self):
        self.legacy('1');(self.install/'current.txt').write_text('1')
        self.archive.write_bytes(self.archive.read_bytes()+b'corrupted download')
        result=self.run_updater()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('checksum incorreto',result.stdout)
        self.assertFalse((self.install/'2').exists())
        self.assertEqual((self.install/'current.txt').read_text().strip(),'1')

    def test_legacy_offline_start_and_rollback_still_work(self):
        self.legacy('1')
        self.legacy('2')
        (self.install / 'current.txt').write_text('2')
        (self.install / 'previous.txt').write_text('1')
        for arguments in ('-Iniciar -NaoAbrir', '-Voltar -NaoAbrir'):
            result = self.run_updater(arguments=arguments)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.install / 'current.txt').read_text().strip(), '1')
        self.assertEqual((self.install / 'previous.txt').read_text().strip(), '2')
        self.assertFalse(self.downloads.exists())

    def test_running_macro_is_rejected_before_download_or_replacement(self):
        old=self.legacy('1');(self.install/'current.txt').write_text('1')
        result=self.run_updater("function Get-Process { param($Name); return [pscustomobject]@{ Id = 99 } }")
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Feche o macro',result.stdout)
        self.assertFalse(self.downloads.exists())
        self.assertEqual((old/'Slayers2Macro.exe').read_bytes(),b'legacy placeholder; never executed')


if __name__ == '__main__':
    unittest.main()
