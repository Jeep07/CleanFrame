# Interaction behaviour — 0.7.0

## Home

- Dock: Left/Right scrolls the apps without wrapping. Up enters the top-right controls, starting with Art Mode or the last selected control. Left/Right moves between Art Mode, All apps, Settings, Home and Samsung Home. Down or Back returns to the selected app. The clock is at the top left.
- List: Up/Down scrolls the apps without wrapping. Right enters the bottom-right controls, aligned with the clock above. Up/Down moves between Art Mode, All apps, Settings, Home and Samsung Home. Left or Back returns to the selected app. The list fades at both ends as it scrolls.
- Home returns to CleanFrame’s own launcher. It closes All apps, the editor, Settings and an appearance group, and it does not rewrite the saved app order. An uncommitted editor move is dropped the same way Back drops it. Samsung Home remains the separate control that asks the television to open `com.samsung.tv.csfs`.
- OK opens the selected item. Focus alone never launches an app.
- Icons-only apps and controls reveal their names when focused. App presentation and control presentation are independent.
- Back from the app list or Dock opens a choice to stay or open Samsung Home.
- A panel keeps focus within its own controls. Back closes one panel at a time.
- Returning to the running launcher keeps the selected app or panel item. There is no auto-return timer. Held OK and Back keys act once until the key is released.

## Settings and appearance

Settings opens a grouped overview: Background, Layout, Typography, Focus, Apps on Home and Samsung. OK opens a group. Appearance groups use a two-pane screen with visible choices on the left and the committed Home preview on the right.

| Group | Choices |
| --- | --- |
| Background | Photo, Light, Dark; Wallpaper and Rotation when Photo is active |
| Layout | List or Dock; independent Text, Icons or Both choices for apps and Home controls |
| Typography | Manrope, Neue Montreal, Mori, Pangram Sans, Geist and Newsreader, when available |
| Focus | Type or Glass; Soft, Frost or Clear tint material |
| Apps on Home | Membership and arrangement editor |
| Samsung | Samsung Home, TV settings and Inputs |

Up/Down moves between rows. Left/Right moves between choices in a horizontal row. Focus alone changes neither the preview nor saved preferences in these appearance groups. Wallpaper has its own temporary photo preview, described below. OK applies the focused value. A checkmark identifies the applied value; the filled plate identifies remote focus. Applying the current value does not write again.

Material applies to a photographic Dock, or Glass focus on a photographic List. Inactive material choices remain visible with an explanation and are skipped during navigation. Their stored value is retained. Wallpaper and rotation are also inactive on flat backgrounds.

A font or photo change applies only after its resources are ready and storage succeeds. A load or storage failure keeps the previous appearance and checkmark, with a Try again action. Back cancels a pending change, leaves the group and keeps completed changes. Late load callbacks cannot apply a cancelled choice. There is no Save button. Returning to a group restores its last choice focus; returning to Settings restores its category focus. Rotation is nested within Background, and Back returns to its Rotation row.

The selected font applies to Home app names, the clock and Home controls, including Newsreader. Settings, All apps, the Home editor and status text retain Manrope. The preview shows the committed Home appearance and its clock continues to update. Pangram faces are available in Nathan's private build when the local files are present; their binaries are not included in the public source. An unavailable optional face is omitted. If the baseline font is slow or missing, Home remains usable with a local fallback and can recover when the font loads.

## Streaming apps

A fresh Home uses the seven-streaming preset: Apple TV, Hulu, Netflix, Prime Video, Paramount+, YouTube and Disney+. Saved orders, including an older nine-app Home, stay as they were. Other installed consumer apps can also be added. Launching uses the public `tizen.application.launch` API with a candidate native application ID. Those IDs are recorded in [the LS03B manual-install notes](ls03b-manual-install.md) and are not confirmed on every television. Numeric Samsung content IDs and packages ending in `-dummy` are not launch targets. Missing apps and denied launches produce a real error. No web player, placeholder success page or account credential is embedded.

## All apps

The panel reads `tizen.application.getAppsInfo` on entry and shows the filtered consumer apps alphabetically. Samsung's visibility flag alone also exposes system utilities, so EP packages, background services, ad players, account utilities, placeholders and duplicates are omitted. Known brands use bundled marks. Other apps use their local installed icon, with initials as a fallback.

The five-column grid scrolls with remote focus. OK launches an app; its On Home badge shows membership. Up from the first row reaches Apps on Home, which opens the editor. An API failure shows a retry and keeps saved Home choices. Browser previews report that installed-app discovery and launching require the TV.

## Apps on Home

Open the editor from Settings or All apps. On Home shows the current order on the left. Not on Home shows Recently removed first, followed by other installed apps on the right. Home holds one to nine apps.

- Reorder: OK on an app name picks it up. Up/Down moves it. OK places it and saves the order. Back puts an unplaced app back without saving that move.
- Remove: Right from an app name reaches Remove from Home. OK saves the removal and moves focus to the same app in Recently removed. The app stays installed.
- Add: OK on an app in Not on Home adds it and saves. A recently removed app returns to its previous position within the editing session; another app is added at the end. Focus follows the app to its Remove from Home control, so another OK can reverse the addition.
- Undo reverses a completed addition, removal or reorder from the current editing session. Done or Back closes the editor and keeps completed changes. Undo history ends when the editor closes.

Removing the last Home app or adding a tenth app is prevented. A failed storage write keeps the committed choices and order, with a retry message. Saved native app IDs and names survive a restart or a failed catalogue refresh.

## Art Mode and Samsung screens

Art Mode sends an application control to the installed `org.tizen.art-app`, with `mode=fullscreen` and `requester=mobile`. This aims to enter native Art Mode with its current artwork, without toggling power or changing the selected artwork.

This mode comes from [research on Samsung's Art app](https://github.com/TheFab21/ha-samsungtv-smart/blob/master/notes/QN55LS03FAFXZA/ART_MODE_DECOMPILED.md), on another Tizen 9 Frame model. It is an internal Samsung contract, not a documented public Art API. Its visible behaviour on this exact firmware must be confirmed on the TV.

Samsung Home, both in the top-row control and in Settings → Samsung, launches `com.samsung.tv.csfs` with `tizen.application.launch`. The same call is used by the Dock or List Back choice. CleanFrame does not call `hide()` or `exit()` before that launch, so a refused launch leaves CleanFrame visible and shows the error. The success callback means the television accepted the request. It is not visual proof that Samsung Home appeared. This does not change the remote’s physical Home button, startup, autostart, or any native Home assignment. The earlier `com.samsung.tv.coba.newhome` component did not open Smart Hub visibly and is no longer the escape target. There is no blind power-key fallback.

Settings → Samsung → TV settings is not the Inputs path. Inputs reads `VIDEOSOURCE`, calls `tvwindow.setSource`, then launches `org.tizen.tv-viewer`. TV settings in 0.7.3 called `tizen.application.launch('com.samsung.tv.coba.setting')` and treated the accept callback as finished, with no message. On this LS03B that button did not open Samsung TV settings, while Inputs did. A working input handoff does not identify the settings application.

On other Tizen 6.5 sets, a plain launch of `com.samsung.tv.coba.setting` is reported to be accepted while no Settings screen appears. That is the same OS generation, not a reading of this television’s installed-app list. This package does not contain that list, and 0.7.4 does not launch `com.samsung.tv.coba.setting`. It asks `getAppsInfo()` for `org.tizen.menu`. When that id is present, it sends `launchAppControl` with operation `http://tizen.org/appcontrol/operation/default` and no URI or extra data. One 2022 Q60B report opened Settings with that application id plus an ATSC `menu.json` path and `__K_EX_FORCE_BOOST`. Those extras are one region’s filesystem path. They are not attached here, because this LS03B’s menu file has not been read. The accept callback is shown as “Settings on screen is not confirmed.” If `org.tizen.menu` is absent, or the control is refused, CleanFrame stays on the error and does not try another id. The call does not change a television setting or switch an input.

## Return inside another app

Back while CleanFrame is visible moves inside CleanFrame: it closes one panel, or from the Dock or List opens the choice to stay or open Samsung Home. That key handling stops when another application is in front.

A normal signed web app cannot make YouTube’s Return key open CleanFrame. Samsung delivers remote keys, including Return, to the focused application. `tizen.application.launch` does not install a return-to-caller contract. `launchAppControl` delivers a result only when the launched application calls `replyResult()` or `replyFailure()`. YouTube does not send that reply. `GROUP` requests a launch into the caller’s subgroup, and a `SINGLE` value in the launched application’s manifest overrides the request. Tizen’s application-group guide says applications in one group are hidden and exited together, and resuming the caller shows the subgroup again. That is not a Return path back to CleanFrame. The television’s own Home behaviour is what shows Samsung Home after Return inside YouTube. CleanFrame does not register a global key, poll in the background, or relaunch itself to change that. Doing so would require a Home reassignment or another system change, which this build does not make.

## Sources for that limit

- [Samsung multitasking](https://developer.samsung.com/smarttv/develop/guides/fundamentals/multitasking.html): another application hides this one and pauses its JavaScript. `visibilitychange` reports the change. It does not say that the other app’s Return resumes the caller.
- [Samsung terminating applications](https://developer.samsung.com/smarttv/develop/guides/fundamentals/terminating-applications.html) and [common certification checks](https://developer.samsung.com/smarttv/develop/development-checklist/common.html), case CO-US-05: Return on an application’s own home page closes that application and shows Smart Hub, or the TV channel on some models since 2016. A launch from the Apps screen returns to Smart Hub. That policy is implemented by the foreground app.
- [Samsung Application API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/application-api.html): `launch`, `launchAppControl`, `replyResult`, and `ApplicationControlLaunchMode` (`SINGLE` or `GROUP`). A `SINGLE` manifest value overrides `GROUP`.
- [Tizen application controls](https://docs.tizen.org/application/web/guides/app-management/app-controls/): the launched application must call `replyResult()` or `replyFailure()` before the caller receives a result.
- [Tizen application groups](https://developer.tizen.org/development/guides/web-application/application-management/application-groups): applications in one group are hidden and exited together. Resuming the caller shows the subgroup again.

All calls have bounded response handling. A failure leaves CleanFrame usable. No simulated device success views remain. Browser validation cannot confirm the visible Samsung destination.

Installed-app discovery allows up to 20 seconds for large TV catalogues; launch controls retain an 8-second limit. Opening All apps or the editor refreshes the catalogue while retaining saved Home choices. No discovery polling runs during hidden startup.

## HDMI inputs

Settings → Samsung → Inputs opens the HDMI chooser. The adapter reads the TV’s actual connected and disconnected source records, including sleeping devices that may be listed as disconnected. It does not guess a universal port count or add a fourth default Home control. Missing APIs, denied access and discovery failure produce an unavailable/error state rather than invented ports. The active source comes from the synchronous `tvwindow.getSource()` return value.

Up/Down selects an input. OK requests that exact source; Back returns to Samsung Settings. Retry after a failed load rereads the available sources. A routing error remains an error, and a failed handoff leaves the launcher usable. Timed-out or cancelled requests cannot start a later routing or viewer action; a native request already sent to the TV may itself be uncancellable.

Selecting a source, opening Samsung’s viewer, seeing the expected HDMI picture and waking a CEC device are separate results. The portable implementation does not import firmware-specific viewer payloads or claim to wake a sleeping device. No input discovery or polling runs during hidden startup.

## Preferences and wallpaper

The launcher stores appearance, Home order, recently removed apps, the last launched Home app, wallpaper and rotation locally. List and Dock share these preferences. The existing `cleanframe.home.v1` key is retained, with a fallback read from `cleanframe.shore.v1`. Legacy List maps to Dark + List + Type; Glass Dock and Glass Grid map to Photo + Dock + Glass. App order, wallpaper, rotation and the last Home app are preserved.

The gallery contains 15 bundled wallpapers. Settings → Background → Wallpaper keeps the two-pane Settings frame. Up/Down browses a vertical thumbnail list without wrapping; the right-hand Home preview shows the candidate while the surrounding Settings backdrop stays on the applied photo. OK applies the focused photo and stays in Wallpaper. The tick marks the applied photo and preview status distinguishes unsaved browsing. Back restores the latest applied photo, cancels pending loading and returns to Background’s Wallpaper row. Photo and material assets change as one complete bundle; a failed load restores the applied preview and offers retry. Preview loading waits briefly for remote focus to settle. OK during loading queues application for that photo; another browse move or Back cancels it. Browsing never saves, and repeated OK on the applied photo does not write again.

Settings → Background → Rotation offers Fixed, Each time Home opens, Every 5 minutes, Every 15 minutes and Every hour. Each time Home opens advances once when the launcher loads; a return to the already-running launcher does not advance it. Timed rotation counts only visible Photo Home time in either List or Dock. Panels, flat backgrounds and time spent in other apps pause the cycle. Changing the photo or rotation mode starts a new interval.

Launcher wallpaper is separate from native Art Mode. Runtime photos, materials and available fonts are local assets; they do not require the Mac or a network download.

## Sources

- [Samsung Application API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/application-api.html): installed-app discovery and application control.
- [Samsung application termination guide](https://developer.samsung.com/smarttv/develop/guides/fundamentals/terminating-applications.html): exiting is not treated as a deterministic Samsung Home route.

The native Home operation and startup configuration from 19 October remain separate from this app update. Home from Netflix was confirmed for that configuration; power-on after Netflix remains provisional. Streaming apps retain their own Back navigation. Netflix did not exit on repeated Back in the observed test, so there was no app-exit destination to verify. No global Back interception or key-filter hook was installed. See [TV status](tv-status.md) for device evidence; this behaviour specification is not an installation or visual-verification record for 0.6.0.

## Clock and rendering

Both layouts show the TV's local time in 12-hour format, without AM/PM or seconds. It updates at the minute boundary and on return to the launcher. No date or clock panel is shown.

Photographic materials and blurred panel backgrounds are generated before packaging and stay aligned with the full-screen image. Photo colour and contrast metadata are also prepared offline. Navigation does not sample image pixels, run an optics engine or apply live backdrop blur. Flat backgrounds use matching light or dark panel colours. Focus feedback uses transforms and opacity; reduced motion removes animated scaling and movement while retaining opacity feedback.

Hidden prelaunch can install a fully loaded wallpaper bundle without waiting for an animation frame. A valid loaded image remains usable if detached-image decoding rejects. A failed startup bundle retries when the launcher becomes visible; an active wallpaper preview keeps its candidate. Font recovery clears fallback measurements and cached markup. This readiness fallback uses a completed load and nonzero image dimensions; it does not prove a TV has painted the image, and an accepted bundle is not automatically decoded again on return. These paths have browser regression coverage; physical cold-boot behaviour still needs owner observation.
