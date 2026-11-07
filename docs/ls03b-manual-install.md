# 2022 Frame LS03B — browser preset and manual install

Prepared for an independent public checkout. This is a cloud and browser record. It did not connect to a television, sign a package, or change Home, startup or Art Mode.

Use it at your own risk. The installation floor in `config.xml` is Tizen 5.0. That admits a Tizen 6.5 package attempt. It does not prove rendering, launching, Art Mode, HDMI or remote behaviour on a 2022 LS03B.

## What this checkout changes

A fresh Home uses the seven-streaming preset, in this order:

| Home label | Service | Candidate `tizen.application.launch` ID | On this LS03B |
| --- | --- | --- | --- |
| Apple TV | Apple TV | `com.samsung.tv.aria-video` | Untested |
| Hulu | Hulu | `LBUAQX1exg.Hulu` | Untested |
| Netflix | Netflix | `org.tizen.netflix-app` | Untested |
| Prime Video | Amazon Prime Video | `org.tizen.primevideo` | Untested |
| Paramount+ | Paramount+ | `rJyOSqC6Up.CBSAllAccess` | Untested |
| YouTube | YouTube | `9Ur5IzDKqV.TizenYouTube` | Untested |
| Disney+ | Disney+ | `MCmYXNxgcu.DisneyPlus` | Untested |

A saved Home order is left alone, including an older nine-app order. The editor can still hold one to nine apps.

These IDs are application IDs already present in this repository and in public installed-app listings, including the [tizen-app-id dump](https://github.com/arlogilbert/tizen-app-id) and the QE49Q85T listing that names the same Apple TV, Prime Video, Disney+ and YouTube application IDs. Samsung’s [Application API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/application-api.html) launches by that application ID. `getAppsInfo()` is the API that returns the ID installed on a particular TV. The reference LS03D record confirms only Netflix (`org.tizen.netflix-app`) and YouTube (`9Ur5IzDKqV.TizenYouTube`) by a physical launch. It does not confirm the other five, and it is a different model.

The Paramount+ row keeps the application ID `rJyOSqC6Up.CBSAllAccess`. Public listings label that installed application Paramount+. The package name still says CBS All Access, which is the earlier service name. Treat a mismatch on the TV as a missed shortcut, then pin the application `getAppsInfo()` actually returns.

These are not launch targets:

- Numeric Samsung content or WebSocket IDs, including `3201710014981` and `3202110025305` for Paramount+ and `3201601007625` for Hulu.
- Dummy packages such as `org.tizen.primevideo-dummy` and `com.samsung.tv.aria-dummy`. The catalogue already drops IDs ending in `-dummy`.
- `MCmYXNxgcu.DisneyPlusService`, which is a service entry beside Disney+, not the player.
- `com.samsung.tv.cobalt-yt`, which remains excluded as a duplicate YouTube component. It is not a silent fallback.

The browser preview states that launching apps and Art Mode need the TV, and that the photograph is the launcher wallpaper. Wallpaper selection does not call `org.tizen.art-app`. Art Mode still sends the existing application control and was not retargeted.

## Evidence already recorded for other Tizen 6.5 sets

[Compatibility](compatibility.md) includes owner reports for other Tizen 6.5 televisions, including two Frame LS03B reports (QA75LS03BASXNZ and QN43LS03BAFXZA) and a Chromium 85 note on some Tizen 6.5 sets. Those reports are not this television, not this build, and not a native Home result for this task. The reference television remains the LS03D on Tizen 9. This run’s browser checks use current Chromium, not Chromium 85. Runtime JavaScript stays ES5, and the CSS check still rejects `inset` and flex `gap`.

No speed, cold-boot or full-reversibility claim is made here. Nothing in this run was timed on a television.

## Manual open, without Home or startup changes

Installing a signed widget and assigning the system Home button are separate steps. Stop after the app is listed and can be opened from Apps. Do not run `scripts/native-home/`, do not change Home or startup keys, and do not treat an app inventory as a settings or data backup.

This television uses the official `tizen package` and `tizen install` commands. Do not use the repository TV installer or the native Home helper. If the official install fails, stop and record the command and response. Do not switch to another transport. A file upload alone is not an installation.

`python3 scripts/manual-install-plan.py` only prints this boundary. Flags such as `--install` and `--connect` are refused. It does not read `.local/signing.json` or `.local/device.json`.

## macOS signing checklist

Do this on the owner’s Mac, with a separate approval before the first device connection. Apple Silicon compatibility is not assumed: confirm the current official Tizen Studio, TV Extension and Certificate Extension builds against that Mac’s CPU before installing them. Complete Samsung account sign-in yourself.

1. Read [AGENTS.md](../AGENTS.md), [the setup guide](agent-tv-setup-guide.md) and [development](development.md). Keep DUID, addresses, certificates, passwords and the installed-app inventory in ignored `.local/` only.
2. Install the official [Samsung TV SDK](https://developer.samsung.com/smarttv/develop/getting-started/setting-up-sdk/installing-tv-sdk.html) with the TV Extension and the Samsung Certificate Extension. Record the SDK and SDB paths. Do not reuse the maintainer SDK profile name `FrameHome` unless Certificate Manager actually created that profile for this owner.
3. On the TV, record the model and full firmware string from Settings → Support → About This TV. Enable Developer Mode with Apps → App Settings → 12345, enter the computer’s local address, and restart as the TV instructs. Connection steps are [Samsung’s device guide](https://developer.samsung.com/smarttv/develop/getting-started/using-sdk/tv-device.html).
4. Create a new certificate profile: author certificate plus a distributor certificate that contains this TV’s DUID. Use [Certificate Manager](https://developer.samsung.com/smarttv/develop/getting-started/setting-up-sdk/creating-certificates.html). Back up the author certificate. An emulator certificate does not cover this television.
5. The official project wizard already supplied package `NZsRORBcn0` and application `NZsRORBcn0.WesleyCleanFrame`. Those are the tracked manifest and runtime self-filter values. Keep `required_version` at `5.0`. Do not copy a scaffold value of `2.3`, and do not put the reference package back into the manifest. The local certificate profile name for the next command is `WesleyFrame`.
6. From this checkout, run `npm run export:owner`. It writes an unsigned widget and a web-payload zip under `dist/`. Copy the payload zip to the Mac. Unzip it into an empty directory. That directory is the build input. It contains no signature files and no certificates.
7. On the Mac, in that directory’s parent, run `tizen package -t wgt -s WesleyFrame -- <build-dir>`. Inspect the signed widget’s `config.xml` and confirm package `NZsRORBcn0`, application `NZsRORBcn0.WesleyCleanFrame`, and `required_version` `5.0`. Do not sign the payload with a test or reference certificate.
8. Install and launch only with the official `tizen install` command, after announcing it. Permit installation for the selected device in Device Manager. Confirm the installed application ID is `NZsRORBcn0.WesleyCleanFrame`, then open CleanFrame from Apps. See [Samsung’s command-line guide](https://developer.samsung.com/smarttv/develop/getting-started/using-sdk/command-line-interface.html). Do not use the repository TV installer or the native Home helper.
9. On the TV, open All apps and compare the seven shortcuts with `getAppsInfo()`. Replace any shortcut whose candidate ID is absent. Launch each installed service with the remote. Account sign-in stays inside those apps.
10. Confirm Art Mode separately from the wallpaper. The expected call is still `org.tizen.art-app` with fullscreen mode. A successful callback is not visual proof. Personal Art Mode photos are Samsung’s, not the launcher wallpapers.

## Return and the Samsung Home control

Version 0.7.3 adds a Samsung Home control beside Art Mode, All apps and Settings. OK launches `com.samsung.tv.csfs` and does not close CleanFrame first. If the television refuses the launch, CleanFrame remains on the error. This is the same launch already used from Settings. It does not change the physical Home button.

Return pressed while YouTube is in front is handled by YouTube and the television. This package cannot send that key back to CleanFrame. The supported checks are in [interaction behaviour](interaction-behaviour.md).

## Rollback of the manual package

Uninstalling this package is not a system Home restore. Because Home and startup were not changed, there is no native Home value to roll back. Still confirm on the television that Apps → CleanFrame is the owner’s package before removing it.

The exact uninstall command must be taken from the installed SDK and checked against package `NZsRORBcn0` inside the signed widget. This repository does not ship a verified uninstall mapping for the LS03B. Removing the app from the TV’s Apps screen, then checking that `NZsRORBcn0.WesleyCleanFrame` is gone and Samsung Home is unchanged, is the manual check. That check has not been done.

Keep the author certificate if you want a later in-place update of the same identity. Changing the application ID creates a different app.

## Unsigned export

`npm run export:owner` writes `dist/WesleyCleanFrame-unsigned.wgt` and `dist/WesleyCleanFrame-web-payload.zip`. Both are offline, public-font and unsigned. The widget is for inspection. The web payload is the directory input for `tizen package -t wgt -s WesleyFrame -- <build-dir>`. Neither file is signed, and neither should be installed as it is. The script prints the sha256 of each file. It does not read certificates or contact a television.

## Open checks before any device claim

- Model, full firmware string, Tizen version and CPU, read from this television.
- Whether Device Manager can install when `sdb shell` and general app commands are disabled.
- Visible launch of each of the seven services, or an honest missing-app error.
- Visible Art Mode and the usual wake path, recorded separately from the launcher wallpaper.
- Remote focus, type and public fonts on the set.
- The uninstall command or Apps-screen removal, matched to the owner package ID, with Samsung Home still the system Home.
