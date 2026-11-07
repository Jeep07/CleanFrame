# Google Photos as CleanFrame launcher wallpaper

Design review only. Written 7 November 2026 from official Google and Samsung documents and from the packaged app in this repo. No Google project was created, no OAuth client or photo account was used, no request was sent to a Google API, and no companion service was deployed. No television, Mac, or private network was contacted.

This describes a future owner-run path for showing a small set of stills, chosen by the owner in Google Photos, as CleanFrame launcher wallpaper. It leaves Samsung Art Mode, SmartThings, native Home, and startup behaviour alone. Launcher wallpaper and native Art Mode stay separate, as they are today.

Implementation waits on the blockers in [Stages](#stages). The first build, when approved, is still not a hosted CleanFrame service.

## Verdict

A household Frame can show owner-selected Google Photos stills only if selection and Google sign-in happen in a normal phone or desktop browser, and an owner-run companion on that computer downloads the bytes before they expire. The television then stores those stills locally and displays them through the existing wallpaper path.

The television cannot be the OAuth client. Google’s limited-input device flow does not list any Photos scope. The packaged widget has no HTTPS redirect Google will accept, and Google forbids sending the OAuth consent page to an embedded user-agent. A public PKCE client is a supported desktop configuration. It is not a supported configuration inside this Tizen widget.

There is no official API that returns “photos of this person.” Face labels stay inside Google Photos. The owner can gather a family album there, then search that album title in Google’s picker. CleanFrame must not promise person filtering.

## Current app, and the boundary to keep

CleanFrame already shows fifteen bundled photographs as launcher wallpaper. `app/main.js` owns the wallpaper list, preview, preference key `cleanframe.home.v1`, and rotation timer. `app/assets/wallpapers/catalog.js` is the bundled gallery. `app/device.js` is the only place that should call Tizen. `docs/assets.md` requires glass and blur to be baked ahead of time; the television does not sample pixels or blur on the animation path. `docs/interaction-behaviour.md` states that launcher wallpaper is separate from native Art Mode, and that runtime photos are local assets.

`app/config.xml` requests application launch, application info, TV input, and the TV window. It does not request internet, download, or filesystem privileges. Its widget id is `https://local.frame-home/app`. That value identifies the package. It is not a hostname Google can redirect to. The manifest sets `encryption="disable"`.

The stated target for a later device test is a 2022 Frame on Tizen 6.5, 32-bit ARM. This repo’s reference notes describe a different television. Nothing in this document claims that a Tizen 6.5 web engine has been retested for this feature.

## What the Photos APIs allow

Sources and their own “last updated” dates are listed at the end. Pages were read on 7 November 2026. Where a page and another official page disagree, that disagreement is marked.

### Library API: existing family albums are out of reach

Google’s Photos API update took effect on 31 March 2025. After that date the Library API can list, search, and retrieve only albums and media items the app itself created. These scopes were removed: `photoslibrary.readonly`, `photoslibrary.sharing`, and `photoslibrary`. Calls that depend on them return `403 PERMISSION_DENIED`. Shared-album methods were removed with them.

Scopes that remain are `photoslibrary.appendonly`, `photoslibrary.readonly.appcreateddata`, and `photoslibrary.edit.appcreateddata`. Those scopes read and write media the app uploaded. They do not read the owner’s existing library, shared albums, or face groups.

The release notes record that this restriction shipped on 1 April 2025. The updates page and release notes, as fetched for this review, do not describe a later reversal.

Uploading the family’s pictures through the app, then reading them back, would only show copies the app had just uploaded. It would not open the library the owner already labelled. It still needs OAuth, and those Library scopes are also absent from the TV device-flow allowlist below. That path is not the design.

### Picker API: the supported selection path

The Photos Picker API is the documented way for a user to choose items from the whole library and hand those items to an app. The scope is:

`https://www.googleapis.com/auth/photospicker.mediaitems.readonly`

It authorises session create, get, and delete, and listing the media items picked in that session. Service accounts are not supported. The user has to complete OAuth as themselves.

Official flow:

1. The companion holds a valid access token for that scope.
2. `POST https://photospicker.googleapis.com/v1/sessions`, with optional `pickingConfig.maxItemCount`.
3. Google returns `pickerUri`. The user opens it in a real browser, signed into the same Google account. The picker cannot be placed in an iframe. For a browser tab on the same computer, `/autoclose` may be appended. Google advises against `/autoclose` when the user arrives by QR code from another device.
4. The companion polls `GET https://photospicker.googleapis.com/v1/sessions/{sessionId}` until `mediaItemsSet` is true, using `pollingConfig.pollInterval` and stopping at `pollingConfig.timeoutIn`.
5. `GET https://photospicker.googleapis.com/v1/mediaItems?sessionId=...` returns the pick. `pageSize` above 100 is coerced to 100.
6. The companion downloads bytes from each `baseUrl`, then calls `sessions.delete`.

`PickingConfig` documents one client field: `maxItemCount`. The default cap is 2000. There is no documented parameter for person, album id, date, or media type. A CleanFrame session should send `maxItemCount` of `"15"`, matching the size of the bundled gallery and keeping the export small.

**Documentation inconsistency.** The REST resource and the media-item methods use `https://photospicker.googleapis.com`. The session guide’s polling example still shows `GET https://photoslibrary.googleapis.com/v1/sessions/{sessionId}`. The guide was last updated 6 October 2025. Implementers follow the REST host, `photospicker.googleapis.com`, and check the guide again before coding. This review did not send either request.

Session `expireTime` is part of the resource. The public pages do not state how long a session lives. After expiry, `sessions.get` returns `PERMISSION_DENIED`. **Uncertainty:** a picked item id must not be treated as a durable Library API id. The Library API would only resolve app-created items anyway. The companion downloads during the open session and does not plan a later refresh of the same session.

`sessions.create` returns `FAILED_PRECONDITION` when the account has no Google Photos library, and `RESOURCE_EXHAUSTED` if session limits are hit. Clients delete sessions when finished, including abandoned test sessions whose ids were stored.

### Face labels

The owner’s face labels are real inside Google Photos. They are not an API CleanFrame can call.

- Library `mediaItems.search` can filter `contentFilter` category `PEOPLE`, meaning “a picture that contains a person.” The same method’s other filters are dates, media type, features, and archived state. There is no person id, face id, or named-cluster field. Search now returns only app-created media.
- The Photos user-data policy says not to use the Photos APIs to produce face clusters. Facial clustering is reserved for people organising their own memories.
- Picker configuration cannot pre-select a person. The picking-experience page says the picker opens on recent photos. Albums, favourites, and other common categories are not shown as entry points. Documented search criteria are keywords, dates, locations, and album titles.

**Uncertainty:** that page does not say whether typing a face-group name works as a keyword. Do not promise it. The documented gesture is: in the Google Photos app, the owner uses the existing face labels to put the family in an album; in the picker, the owner searches that album title. Prompt copy should say “search for your family album,” not “we will filter by person.”

### baseUrl lifetime, EXIF, and CORS

Picker `baseUrl` values stay valid for 60 minutes and can die sooner if the user revokes the app. A request for Picker bytes must send `Authorization: Bearer` with the same scope. Width and height are mandatory unless the download parameter is used. Sizes must be in the range 1–16383.

| Parameter | Official effect | CleanFrame use |
| --- | --- | --- |
| `=w1920-h1080` | Scaled image, aspect ratio preserved, no wider than 1920 and no taller than 1080 | The bytes the companion requests for a 1920×1080 stage |
| `=w96-h54-c` | Exact crop | Optional thumbnail, same idea as the bundled 96×54 thumbs |
| `=d` | Original image with EXIF retained except location metadata | Do not request. It is the parameter that keeps EXIF |

**Uncertainty:** the docs do not say that `w`/`h` responses are free of all EXIF. The companion re-encodes to a baseline JPEG, maximum edge 1920, and drops metadata, including GPS, before anything is stored or sent to the television. Videos and other non-image MIME types are skipped and reported to the owner. Motion-photo video (`dv`) is out of scope.

The best-practices page says “For the Library API only” that temporary media should not be cached longer than 60 minutes, and that Library `baseUrl` values should not be stored. Picker access is different and narrower: the session expires, and there is no documented way to turn a picked id into a fresh `baseUrl` later. An offline frame therefore has to keep a local copy of the re-encoded stills. That copy is a user-initiated export of a capped set, which the companion explains before Google’s consent screen. It is also the point on which the policy blocker below turns.

Official Picker docs do not mention `Access-Control-Allow-Origin` on `baseUrl`. An older public issue (118662029) asked Google to add that header on Library media URLs; the thread did not record a fix. **Uncertainty:** whether a 2026 Picker `baseUrl` response allows browser `fetch` from a non-Google origin. The design does not depend on it. An `<img>` element also cannot attach the required `Authorization` header, so a raw `baseUrl` is not a wallpaper `src`. The companion downloads on the server side of its own process, where CORS does not apply.

## OAuth: which clients can actually hold the scope

### TV and limited-input device flow

Google’s device-code flow, last updated 16 October 2026, supports only these scopes:

- `email`, `openid`, `profile`
- `https://www.googleapis.com/auth/drive.appdata`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/youtube`
- `https://www.googleapis.com/auth/youtube.readonly`

`photospicker.mediaitems.readonly` is not in that list. Neither are the remaining Library scopes. A 2018 issue on the old Library scope was answered by Google with no plan to add Photos scopes to this flow. The 2026 allowlist is the evidence for the Picker scope: it is absent, so the design treats device authorization as unable to obtain it. This review did not POST to `https://oauth2.googleapis.com/device/code`. A later live check, only after the owner has a client id, would expect `invalid_scope` and should be recorded before anyone revisits this conclusion.

Drive’s `drive.file` scope is on the allowlist and still does not read the Google Photos library. It is not a substitute.

### Embedded user-agents and redirect URIs

OAuth 2.0 policies, last modified 5 August 2026, require:

- One registered client per platform, of the matching client type. A web client is not a stand-in for a native client, and a desktop client is not a stand-in for the television.
- Web clients use HTTPS JavaScript origins and HTTPS redirect URIs on domains the owner controls. Google may reject an origin that is not a secure context.
- Consent must be sent to a browser where the user can see the Google host and the certificate. Developers must not send the OAuth request to an embedded user-agent they control. Embedded user-agents include libraries that can inject scripts, change routing, or read session cookies. The failure users see is `disallowed_useragent`.

The installed-app guide’s redirect section says custom URI schemes are no longer supported, because another app can impersonate the scheme. An earlier parameter table on the same guide still shows a custom-scheme example. Treat the “no longer supported” note as the rule. Loopback remains the documented desktop method: a Desktop-app client, PKCE, and `http://127.0.0.1:<port>` or `http://[::1]:<port>`, with a listener on that machine. Loopback is deprecated for Android, Chrome-app, and iOS client types. The out-of-band copy/paste redirect is no longer supported.

The Tizen widget fails those rules together:

- Its id, `https://local.frame-home/app`, is not a domain the owner can verify, and the page is served from the package rather than from that host.
- `file://` and a widget origin are not HTTPS redirect URIs Google documents for a web client.
- A custom scheme back into the widget is the redirect method Google has withdrawn.
- The widget has no documented way to bind a loopback HTTP port and receive Google’s redirect. Adding a native listener would be a new privileged helper, which this work does not include.
- Loading Google’s consent page or `pickerUri` inside the TV webview is an embedded user-agent and, for the picker, an iframe-style embed. Both are prohibited. The Samsung browser on the television is not something this design will claim is a “secure browser” Google accepts. **Uncertainty:** only a later, owner-approved experiment could show the television browser’s user-agent result, and that experiment is not a proposed path.

Public PKCE on the television therefore has nowhere legal to land the authorization code. PKCE protects a code on a supported public client. It does not create a redirect.

### Desktop PKCE versus a confidential web companion

| | Desktop companion | HTTPS web companion | OAuth inside the widget |
| --- | --- | --- | --- |
| Client type | Desktop app, public client | Web application on a hostname the owner controls | No matching client type |
| Secret | Console may display one. Desktop apps are public clients and cannot keep a secret. Token exchange marks `client_secret` optional. PKCE is required. Leave any secret out of the widget and the repo. | Secret stays in the host’s secret store, never in Git or on the TV | Would require a secret or a fake client type |
| Redirect | Loopback on the owner’s computer | Exact `https` callback on that host | No supported URI |
| Where the refresh token lives | The owner’s computer, encrypted at rest, outside the repo | That host, encrypted at rest | Would be the TV |
| What this run does | Describes it | Describes it, only if the owner later chooses to run one | Rejects it |

The recommended client is the desktop companion. It matches “the computer where the owner can open a normal browser,” it needs no public website, and this project does not deploy it. A confidential web companion is the alternative when the owner already has an HTTPS name they control and wants the token off the desktop disk. Standing that service up is a separate, explicit hosting decision. It is not part of this review.

Google’s installed-app guide says a refresh token is always returned for a desktop client. Incremental authorization is not supported for installed apps, so the consent request should ask for the single Picker scope and nothing else.

## Policy blocker

The Photos API User Data and Developer Policy, effective with the 31 March 2025 change, allows Photos scopes for apps that store, edit, print, export, or share images and videos and that add something to Google Photos rather than recreating it. It disallows a substitute for Google Photos, and gives “a general purpose photo gallery app” as the example. It also disallows face clustering, broad library access except a user-initiated export, and use of the API as a CDN or as training data.

A rotating set of library photos sits close to that prohibited example. A capped, user-picked set shown only as launcher wallpaper, with no library browser, no search, no face clusters, and no second share, is the narrow reading this design uses. **This is not clearance.** Google assigns scope sensitivity in the Cloud Console, and the public scope page does not label `photospicker.mediaitems.readonly` as sensitive or restricted. **Uncertainty:** if the console classifies it as restricted, production use can require a Cloud Application Security Assessment and a third-party letter. The Photos authorization page also says an app that accesses the Photos APIs must pass OAuth verification before the unverified-app screen is removed.

OAuth policy separates personal use from production. Personal use means the app is not shared, or is used by fewer than 100 people the owner knows. Verification requirements called out for production apps are not automatically waived by the Photos page’s verification sentence. Until the owner reads both and decides, implementation stays stopped.

Consequences the design accepts if the owner continues:

- Publishing status stays **Testing**. Only allowlisted test users can consent. The cap is 100 test users.
- Any non-basic scope in Testing expires the grant, and the refresh token, seven days after consent. The Picker scope is not the basic identity exception (`openid`, `email`, `profile`).
- The companion treats `invalid_grant` as “sign in again,” and sends the owner through the system browser. An unattended frame will stop being able to fetch new picks after a week until that happens. Already downloaded stills can remain until the owner removes them.
- The consent screen shows Google’s testing warning.
- The companion shows its own disclosure immediately before consent: what is read (stills the owner picks), that a re-encoded copy is stored on the owner’s computer and television, that face data is not requested, and that “Remove family photos” deletes the copies. A link states that Photos API data use follows the Google user-data policy, including Limited Use. The privacy policy is the owner’s, on a site they control, if the console requires the URL.
- No CleanFrame cloud, advertising, or model training sees the pictures.
- The feature is not offered as a public integration until verification and the gallery-policy question are resolved. A public release that shipped this against an unverified consent screen would hit Google’s user cap and warning UI.

Required token handling from the OAuth and Photos policies: encrypt access and refresh tokens at rest, transmit them only over a modern secure protocol, and revoke and delete them when the feature is removed. Restricted-scope guidance also talks about hardware-backed key management and a security assessment. A household desktop and a Frame do not meet a formal assessment. **Uncertainty / gap:** OS keychain or an encrypted file outside the repo is the practical control for a personal Testing client. It is not a claim of certification. If the owner needs certified compliance, this feature stops.

## Token and photo threat model

The television is a shared living-room device. App localStorage is readable by anyone who can open the widget’s storage, and the manifest does not encrypt the package. A refresh token there would let a later holder mint access tokens until revocation. A client secret there would be extractable from the package. Neither value is placed on the TV or in Git.

| Asset | Where it may live | Where it must not live |
| --- | --- | --- |
| OAuth client id of a Desktop public client | Owner’s computer, ignored local config | TV package, Git, screenshots |
| Client secret, if one exists | Nowhere for the desktop path. Secret store only for a future web companion | TV, Git, command-line history |
| Refresh token and access token | Companion memory; refresh token encrypted at rest on that computer | TV localStorage, Tizen files, logs, Git |
| `baseUrl` and session id | Companion memory until download and `sessions.delete` finish | Preferences, logs, Git |
| Re-encoded JPEG stills | Companion cache outside the repo; TV app-private storage after a successful transfer | Git, bundled `app/assets`, public exports |
| Companion address, pairing code, device credential | TV local setting and companion memory | Git. A LAN address or code is private to the household |

The TV’s device credential, once pairing exists, authorises only “list and download the already re-encoded set” and “forget this TV.” It is not a Google token. It should be random, single-purpose, and expire within a day, with a new pair required after that. localStorage is acceptable for that short credential and is not acceptable for a Google refresh token. **Uncertainty:** a Tizen key manager API exists on some profiles and has not been shown on this Frame. The design does not depend on it.

Revocation has three layers, and any one of them must be enough to stop a new fetch:

1. The owner removes the app at Google Account → Third-party access. Google can also revoke. The next Picker or token call fails. Picker docs say a `baseUrl` can expire immediately on revoke. The companion deletes its cache and its tokens, and calls `https://oauth2.googleapis.com/revoke` when it still holds a token. Revocation covers every client in the same Google Cloud project.
2. The owner chooses disconnect in the companion. Same local deletion, plus revoke.
3. On the TV, “Remove family photos” deletes the local files and the device credential even when the companion is offline. The next successful contact tells the companion to drop that TV. If the companion answers 401 or “revoked,” the TV deletes local files without waiting for a settings visit.

Pictures already on the TV stay until that local delete or an uninstall. `wgt-private` is removed when the app is uninstalled. `documents` and `downloads` are not, so they are the wrong destination. The manifest’s `encryption="disable"` means those private files are not documented as encrypted. Another process with filesystem access, or a debug session, may be able to read them. That gap is accepted only for the owner’s own Testing use, and it is a blocker for any wider install.

EXIF and privacy on the wire: the companion re-encodes, so the TV never receives the original file. The TV does not run pixel analysis, face detection, or a blur pass. Logs record item counts and failures, not image bytes, names of people, or URLs that contain access tokens.

## Companion and television architecture

```text
Phone or desktop browser          Owner's computer (companion)           Frame (CleanFrame)
------------------------          ----------------------------           ------------------
Google consent in the             Desktop OAuth client, PKCE,            Shows launcher wallpaper
system browser                    loopback redirect                       from local files
        |                         Refresh token stays here
        v                         Creates picker session
Google Photos picker    <------   Shows pickerUri
Owner searches a family           Polls with pollingConfig
album title and picks             Downloads with Authorization
up to 15 stills                   Re-encodes JPEG, strips metadata
                                  Deletes the session
                                        |
                                        |  TLS, TV calls out
                                        v
                                  Serves the still set
                                  to a paired TV only
                                                                        Stores files in
                                                                        app-private storage
                                                                        Rotates them with the
                                                                        existing wallpaper timer
```

The companion is a program the owner runs. It is not a CleanFrame server, and this change does not add one.

Pairing, when a later stage builds it:

1. The owner starts the companion and completes Google consent in the system browser. The companion listens on loopback for that redirect only.
2. The companion serves the still set over TLS on the household network. The certificate is generated on that computer and kept outside the repo. The television dials out. The television does not accept an inbound connection.
3. One time, the owner enters the companion host in CleanFrame settings. That host is stored only on the TV. A private address must not be committed.
4. The TV shows a short code. The owner types that code on the companion. The companion then accepts a poll from the TV that presents the same code. The code expires in about ten minutes and works once. The TV receives the short-lived device credential.
5. The owner confirms the certificate fingerprint shown on both screens before the first picture is transferred.
6. Later “Update family photos” on the TV asks the companion for the current set. The companion does not call Google on the television’s clock minute. Google’s own best-practices page warns that calls aligned to the minute look like synchronised traffic. Picker polling stays on the companion and follows `pollInterval`.

**Uncertainty:** Tizen 6.5 may reject a private certificate. The Download API is optional on the TV profile and may be missing on a 2022 Frame. A page `fetch` from the widget often uses a `null` or `file` origin, which browsers will not expose across origins. Those three facts are why the network path has to be proven on the television before the feature depends on it, under a separate device task. If the television cannot complete TLS to the companion, the companion can write the same re-encoded files for the owner to bring across on removable media. That fallback still uses the picker on the computer, still keeps Google tokens off the TV, and still does not need a public server.

The television displays the files the way it displays bundled wallpapers: an `<img>` pointed at a local file, inside the existing stage. Family stills ship with a fixed, readable scrim chosen so clock and labels stay legible. They do not select Glass, Frost, or Clear, and they do not run `adaptive-ink` or the material builder on the TV. A later owner-side bake can add materials; until that review exists, Glass stays on the bundled fifteen. `docs/assets.md` already requires that review before new photographic metadata is accepted.

Preferences gain a new version of `cleanframe.home.v1`. The migration keeps the existing wallpaper id, rotation, layout, and app order. Family entries are local ids only. A missing file falls back to the last bundled wallpaper and offers retry. Rotation uses the existing rules: visible Photo Home time only, paused while a panel is open or the app is hidden. The family set is included in that rotation only while its files are present. Choosing a family still does not call `org.tizen.art-app`.

### Synthetic settings copy

This copy is a proposal for a later UI review. It is not implemented, and it is not evidence that an API call succeeded.

- Row label: Family photos
- Explanation: Choose stills in Google Photos on your phone or computer. CleanFrame keeps a copy on this TV and shows it as launcher wallpaper. Art Mode is unchanged.
- Empty state: No family photos on this TV.
- Pairing: Connect the computer that is signed in to Google, then enter the code shown here.
- Update: Check for the stills you picked.
- Remove: Remove family photos from this TV.

## Owner’s Google Cloud configuration

The owner does this later, in their own project. No secret is required to review this document, and none should be pasted into the repo, a pull request, or a screenshot.

1. Create a Google Cloud project used only for this personal Testing client. OAuth policy asks for separate projects per environment. Leave it out of any future public project.
2. User type **External**. Publishing status **Testing**. Add the owner’s Google account as a test user. Leave the app unpublished.
3. OAuth consent screen: app name, user support email, developer contact. Add a privacy-policy URL if the console requires it. The homepage and domain verification required for a production app can wait while the app stays personal and in Testing.
4. Enable the Google Photos Picker API. Do not enable a flow that requests `photoslibrary.readonly`, `photoslibrary`, or `photoslibrary.sharing`.
5. Create an OAuth client of type **Desktop app**. Use the loopback redirect the Desktop client wizard provides. Register `http://127.0.0.1` and `http://[::1]` in the form the console accepts, including the port if the console demands an exact port. Confirm the saved redirect before coding. **Uncertainty:** Google’s desktop guide both requires an exact redirect match and tells the app to bind a free port. The console’s current Desktop fields decide which of those is true.
6. Do not register `https://local.frame-home/app`, a `file://` URI, a custom scheme, or the television’s address.
7. Scope on the consent screen and in the authorization request: `https://www.googleapis.com/auth/photospicker.mediaitems.readonly` only. Read the classification the console shows. If it says restricted, stop and return to the policy blocker.
8. Put the client id in an ignored local file outside `app/`. Do not commit it. Do not copy a client secret into that file for the desktop path.
9. Expect a testing warning, a seven-day refresh-token lifetime, and the need to sign in again after `invalid_grant`. Access-token lifetime comes from `expires_in` on each token response. Do not hard-code an hour.
10. Verification, a public homepage, and brand review apply when the owner wants any Google account beyond the test-user list, or when they move the consent screen to production. Budget a Google review cycle and a demonstration of the picker before that. Do not start it from this design.

## Stages

### Stage 0 — this document

Review the verdict, the policy blocker, and the desktop-companion shape. No application code, privileges, Google project, or device work.

### Stage 1 — owner decisions, still no product code

The owner accepts or rejects the policy reading, chooses desktop PKCE rather than a hosted companion, and, only if they accept, creates the Testing project above. Record the console’s sensitive/restricted label. Do not paste credentials into the issue or the pull request.

### Stage 2 — companion on the owner’s computer

A later change can add the companion outside the widget, with fixture tests and no CI use of live credentials. A live pick happens only when the owner runs it. Tokens stay in ignored local storage. This stage still does not change `app/config.xml` or install anything on the television.

### Stage 3 — browser UI with synthetic files

Add the Family photos row and preference migration. Tests feed local fixture JPEGs, clearly synthetic, never a real library. Bundled wallpaper navigation, rotation, and Art Mode’s existing control stay as they are. Run `npm run check`, `npm run check:tools`, and `CLEANFRAME_PUBLIC_FONTS=1 npm run check:browser`.

### Stage 4 — television, only under a new explicit device task

Add the smallest privileges and `<access>` origins a Tizen 6.5 test shows are required for the companion origin. Announce any install or launch. Confirm the pictures are visible as launcher wallpaper, that Art Mode still opens Samsung’s Art app, and that Home and startup were not written. Keep private addresses, DUIDs, serials, certificates, and photos out of the repo and the status notes.

## Blockers

| Blocker | Why it stops the next stage |
| --- | --- |
| Gallery-policy reading | A wallpaper rotation can be judged a photo-gallery substitute. Stage 2 waits for the owner’s decision. |
| Scope classified restricted, or verification demanded for this personal project | CASA and a public review are a different project. Stay in Testing or stop. |
| Seven-day Testing refresh | Accepted for a household that can sign in again. Not acceptable for an unattended public frame. |
| No TV OAuth redirect, and device flow omits the scope | Direct PKCE on the TV is not an implementation option. |
| Companion TLS or Download API fails on the 2022 Frame | Stage 4 stops or falls back to removable media. Browser preview cannot prove this. |
| TV storage is unencrypted | Acceptable only for the owner’s own test. Blocker for any other install. |
| Glass materials for new photos | Family stills use a fixed scrim until an offline material review exists. |

The manual path that avoids the API entirely remains available: export stills from Google Photos, prepare them with the existing wallpaper tools, and keep them as local assets. That path has no OAuth and no picker. It also has no automatic update. It is the fallback if Stage 1 rejects the API, not a silent change to the bundled Unsplash gallery.

## Future source touchpoints

No file below is modified by this design.

| File | Later change |
| --- | --- |
| `app/config.xml` | Privileges and `<access>` origins for the companion only, after a device test. No Google origins while the TV never calls Google. Leave `encryption` as it is until a separate review. |
| `app/device.js` | Companion fetch, private-file save, and delete. Tizen calls stay in this adapter. Browser preview reports that pairing needs the television. |
| `app/main.js` | Preference version bump and migration. Family ids beside the bundled list. Rotation and preview reuse the current wallpaper behaviour. No token fields. |
| `app/index.html`, `app/style.css` | Family row inside the current Settings frame, only if the existing wallpaper markup cannot express it. Keep remote focus, ES5, and the CSS limits in `docs/development.md`. |
| `app/assets/wallpapers/catalog.js` | Unchanged. Family stills are runtime files, not new bundled entries. |
| `app/assets/adaptive-ink.js`, material scripts | Unchanged on the television. Offline bake is a separate asset review. |
| `docs/interaction-behaviour.md`, `docs/development.md`, `docs/testing.md` | Update when the behaviour actually changes. |
| Companion program | New, owner-run, introduced in Stage 2. Configuration under ignored `.local/` or an equivalent untracked file. |
| `scripts/native-home/` | Untouched. No Home, Art, or startup helper. |

## Tests and acceptance

This document’s check is editorial: `scripts/private_files.py` secret patterns do not match it, and it contains no certificate, token, photo, serial, or private address.

Later stages add tests. None of them call Google.

- Fixture of a `PickingSession` with `mediaItemsSet` false, then true. The companion waits `pollInterval`, stops at `timeoutIn`, and deletes the session after a successful save.
- Fixture `baseUrl` older than 60 minutes, and a revoke error. The companion does not store the URL and does not serve the file.
- Non-image MIME type is skipped. Re-encoded output has no EXIF segment in the fixture.
- Preference migration from the current `cleanframe.home.v1` keeps the wallpaper id and writes no token, `baseUrl`, or Google account id.
- Browser, public fonts: synthetic family JPEGs appear in the wallpaper list; Up, Down, OK, and Back match the current picker; a missing file restores the bundled wallpaper and offers retry; rotation pauses while Settings is open; the Art Mode control still reports that the television is required.
- `npm run check` ES5 lint, and `npm run check:performance` if the wallpaper render path changes.
- A source check fails the build if `app/` contains a Google token endpoint, a `googleusercontent` media URL, or a client secret.
- Stage 4 acceptance is visual and is recorded by the owner. SDK success alone is not acceptance.

Acceptance for the feature, when all four stages are done:

- The owner picks up to 15 stills in Google’s picker, in a normal browser, after searching an album they created with Google Photos’ own tools.
- Those stills rotate as launcher wallpaper on the existing intervals and survive a restart without a network.
- The television package and localStorage contain no Google refresh token and no client secret.
- Revoking the Google app, disconnecting the companion, or choosing “Remove family photos” leaves no family image files on the TV and the launcher returns to a bundled wallpaper.
- Art Mode, native Home, and startup settings are unchanged.
- The fifteen bundled wallpapers, List and Dock focus, and panel Back behaviour still pass the browser checks.
- The public repo and the pull request contain no family photos, tokens, certificates, or household addresses.

## Uncertainties gathered

| Topic | What is known | What is not claimed |
| --- | --- | --- |
| Library restriction after 31 March 2025 | Official updates and the 1 April 2025 release note | A reversal published after those pages’ last update and missed by this review |
| Picker session length | `expireTime` exists; expired access is `PERMISSION_DENIED` | A numeric lifetime, or reuse of picker ids through the Library API |
| Person search | No API field; policy forbids producing face clusters; picker documents album-title search | That the picker search box resolves a face-group name |
| `w`/`h` and EXIF | `=d` keeps EXIF except location | That `w`/`h` already strips everything. Re-encode anyway |
| `baseUrl` CORS | Authorization header is required; historical Library CORS gap | That the 2026 media host sends `Access-Control-Allow-Origin` |
| Device flow | 16 October 2026 allowlist omits every Photos scope | A hidden exception. No live `invalid_scope` probe was sent |
| Scope sensitivity | Photos pages require verification to clear an unverified screen | Whether this scope is sensitive or restricted until the console says so |
| Desktop redirect port | Exact match is required, and a free port is also described | Which form the current Desktop wizard saves |
| Tizen 6.5 download, private CA, and file-origin CORS | Download API is optional on TV; `wgt-private` is removed on uninstall | That this Frame can download from the companion |
| Policy fit of a wallpaper rotation | Picker is the documented limited export | That Google will accept the feature as distinct from a gallery app |

## Sources

Read 7 November 2026.

- [Updates to the Google Photos APIs](https://developers.google.com/photos/support/updates), last updated 28 August 2025. Library restriction and removed scopes, effective 31 March 2025.
- [Photos API release notes](https://developers.google.com/photos/support/release-notes). 1 April 2025 entry records the restriction taking effect. 16 September 2024 entry introduces the Picker.
- [Photos API User Data and Developer Policy](https://developers.google.com/photos/support/api-policy), last updated 28 August 2025.
- [Authorization scopes](https://developers.google.com/photos/overview/authorization), last updated 28 August 2025.
- [Configure your app](https://developers.google.com/photos/overview/configure-your-app).
- [Picker get started](https://developers.google.com/photos/picker/guides/get-started-picker), last updated 6 October 2025.
- [Picker sessions guide](https://developers.google.com/photos/picker/guides/sessions), last updated 6 October 2025. Polling example host disagrees with the REST reference.
- [REST Resource: sessions](https://developers.google.com/photos/picker/reference/rest/v1/sessions), last updated 6 October 2025.
- [Photo picking: what users see](https://developers.google.com/photos/picker/guides/picking-experience), last updated 6 October 2025.
- [List and retrieve picked media](https://developers.google.com/photos/picker/guides/media-items), last updated 28 August 2025. `baseUrl`, authorization header, `w`/`h`/`d`.
- [mediaItems.list](https://developers.google.com/photos/picker/reference/rest/v1/mediaItems/list).
- [Library search filters](https://developers.google.com/photos/library/guides/apply-filters) and [mediaItems.search](https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search). `PEOPLE` is a content category on app-created media.
- [Photos API best practices](https://developers.google.com/photos/overview/best-practices), last updated 28 August 2025. Library-only caching note.
- [OAuth 2.0 for TV and limited-input devices](https://developers.google.com/identity/protocols/oauth2/limited-input-device), last updated 16 October 2026. Allowed scopes.
- [OAuth 2.0 policies](https://developers.google.com/identity/protocols/oauth2/policies), last modified 5 August 2026. Embedded user-agents, HTTPS redirects, token storage.
- [OAuth 2.0 for desktop apps](https://developers.google.com/identity/protocols/oauth2/native-app). PKCE, loopback, custom schemes withdrawn.
- [Using OAuth 2.0 to access Google APIs](https://developers.google.com/identity/protocols/oauth2). Seven-day refresh tokens for External Testing projects.
- [OAuth consent screen](https://support.google.com/cloud/answer/10311615) and [sensitive-scope verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification).
- [OAuth app state](https://developers.google.com/identity/protocols/oauth2/production-readiness/overview).
- Samsung [Download API](https://developer.samsung.com/smarttv/develop/api-references/tizen-web-device-api-references/download-api.html) and [file operations](https://developer.samsung.com/smarttv/develop/guides/data-handling/managing-file-operations.html). Tizen’s download guide notes the API is optional on TV profiles.
- Issue 118662029, historical request for CORS on media `baseUrl` responses. Not a statement of current behaviour.
