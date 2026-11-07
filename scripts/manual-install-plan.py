#!/usr/bin/env python3
"""Print a manual-install plan. This process never connects, signs, installs or reads secrets."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFUSED = {'--execute', '--connect', '--install', '--launch', '--sign', '--uninstall'}


def main():
    requested = REFUSED.intersection(sys.argv[1:])
    if requested:
        raise SystemExit('Refusing ' + ', '.join(sorted(requested)) + '. This planner has no device or signing action. Read docs/ls03b-manual-install.md.')
    signing = ROOT / '.local/signing.json'
    device = ROOT / '.local/device.json'
    print('CleanFrame manual-install plan: dry run')
    print('Scope: print only. No SDB connection, certificate wizard, package signing, install, launch or uninstall.')
    print('Target notes: 2022 Samsung The Frame LS03B, Tizen 6.5, ARM32. Those values are owner-supplied and were not read from a television in this planner.')
    print('Package identity: NZsRORBcn0')
    print('Application identity: NZsRORBcn0.WesleyCleanFrame')
    print('required_version stays 5.0. Do not replace it with a project-wizard 2.3 value.')
    print('Build the unsigned payload with: npm run export:owner')
    print('On the owner Mac, unzip the web payload and sign with: tizen package -t wgt -s WesleyFrame -- <build-dir>')
    print('A later install uses the official tizen install command only.')
    print('Do not use the repository TV installer or the native Home helper.')
    print('Local signing file: ' + ('present, contents not read' if signing.exists() else 'absent'))
    print('Local device file: ' + ('present, contents not read' if device.exists() else 'absent'))
    print('Do not put a DUID, address, certificate, password or installed-app inventory in the repository.')
    print('Home, startup and Art Mode routing are unchanged by this planner.')
    print('Next stage is on the owner Mac with the official Samsung TV SDK, TV Extension and Certificate Extension, after a separate approval to connect.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
