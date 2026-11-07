#!/usr/bin/env python3
"""Write the unsigned owner web payload. No certificates, signing, network or TV access."""
from pathlib import Path
import hashlib
import zipfile

from font_assets import ROOT, write_widget_archive
from local_config import manifest_identity

PACKAGE = 'NZsRORBcn0'
APP = 'NZsRORBcn0.WesleyCleanFrame'
BLOCKED_SUFFIXES = ('.p12', '.pfx', '.pem', '.key', '.crt')
BLOCKED_NAMES = {'author-signature.xml', 'signature1.xml', 'author-signature.xml.sec'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config_path = ROOT / 'app/config.xml'
    device_path = ROOT / 'app/device.js'
    config = config_path.read_bytes()
    device = device_path.read_bytes()
    identity = manifest_identity(config)
    if identity != {'package_id': PACKAGE, 'app_id': APP}:
        raise SystemExit('Refusing export: manifest identity is not the owner application.')
    if b'required_version="5.0"' not in config or b'required_version="2.3"' in config:
        raise SystemExit('Refusing export: required_version must stay 5.0.')
    if b'nClrkHome1' in config or b'nClrkHome1' in device:
        raise SystemExit('Refusing export: the reference package is still a runtime identity.')
    if b"var SELF = 'NZsRORBcn0.WesleyCleanFrame';" not in device:
        raise SystemExit('Refusing export: runtime self-filter does not use the owner application ID.')

    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    unsigned = out / 'WesleyCleanFrame-unsigned.wgt'
    payload = out / 'WesleyCleanFrame-web-payload.zip'
    write_widget_archive(unsigned, include_private=False)
    with zipfile.ZipFile(unsigned, 'a', zipfile.ZIP_DEFLATED) as archive:
        for notice in ['LICENSE', 'THIRD_PARTY_NOTICES.md']:
            archive.write(ROOT / notice, notice)

    with zipfile.ZipFile(unsigned) as source, zipfile.ZipFile(payload, 'w', zipfile.ZIP_DEFLATED) as target:
        names = source.namelist()
        if len(names) != len(set(names)):
            raise SystemExit('Refusing export: duplicate archive entry.')
        for name in names:
            base = Path(name).name
            if base in BLOCKED_NAMES or name.endswith(BLOCKED_SUFFIXES) or 'signature' in base.lower():
                raise SystemExit('Refusing export: signing material in payload: ' + name)
            data = source.read(name)
            if b'nClrkHome1' in data:
                raise SystemExit('Refusing export: reference package remains in ' + name)
            target.writestr(name, data)
        manifest = manifest_identity(source.read('config.xml'))
        if manifest != {'package_id': PACKAGE, 'app_id': APP}:
            raise SystemExit('Refusing export: packaged manifest identity drifted.')
        packaged = source.read('config.xml')
        if b'required_version="5.0"' not in packaged:
            raise SystemExit('Refusing export: packaged required_version is not 5.0.')
        for privilege in [b'application.launch', b'application.info', b'tv.inputdevice', b'tv.window']:
            if privilege not in packaged:
                raise SystemExit('Refusing export: missing reviewed privilege ' + privilege.decode())
        if b'tv-samsung' not in packaged:
            raise SystemExit('Refusing export: missing the Samsung TV profile.')

    print('Unsigned widget: ' + str(unsigned.relative_to(ROOT)))
    print('sha256 ' + digest(unsigned))
    print('bytes ' + str(unsigned.stat().st_size))
    print('Web payload: ' + str(payload.relative_to(ROOT)))
    print('sha256 ' + digest(payload))
    print('bytes ' + str(payload.stat().st_size))
    print('Identity ' + PACKAGE + ' / ' + APP + '; required_version 5.0; unsigned; no TV or certificate used.')
    print('On the owner Mac, unzip the web payload and run: tizen package -t wgt -s WesleyFrame -- <build-dir>')


if __name__ == '__main__':
    main()
