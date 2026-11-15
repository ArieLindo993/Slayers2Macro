# Fishing Macro

[Português](../README.md) · **English** · [Español](README.es.md)

A visual Windows fishing macro for **Slayers 2 on Roblox**. **Beta 0.0.47** integrates November's circular minigame, splash hook click, held/released mouse, A/D taps and T collection.

**[Download updater](https://github.com/ArieLindo993/Slayers2Macro/releases/latest/download/Atualizador.zip)** · **[Downloads](https://github.com/ArieLindo993/Slayers2Macro/releases)** · **[Changelog](CHANGELOG.en.md)**

## Install

1. Download **Atualizador.zip**, right-click and choose **Extract All**. Keep the folder somewhere writable. GitHub's Code → Download ZIP contains sources.
2. Open **Atualizar.cmd** in the extracted folder. Wait for download, checksum verification and extraction. Enter **S** at **Abrir agora? (S/N)** to open the app.
3. Open **Configurar → Idioma e atalhos**, choose **English**, then **Salvar e fechar**.

Windows and Roblox are required; Python, Git and AutoHotkey are not needed for the packaged app. Keep Atualizar.ps1 next to the .cmd files and preserve .install. If the script is missing, extract the whole ZIP again; if it disappears after extraction, check quarantine and the package source. Do not run shortcuts inside the ZIP. Iniciar.cmd opens the local install; Atualizar.cmd updates; Voltar-versao.cmd restores the available previous version. Updater prompts remain Portuguese.

For manual installation, extract **Slayers2Macro.zip** and run **Slayers2Macro.exe** with companion files. The .sha256 file is an integrity checksum.

## Fish

1. Equip the rod near water and keep the camera fixed. Point where the line will land and the splash will appear; press **F8**.
2. Leave automatic calibration enabled and press **F4** with Roblox in the foreground.
3. The macro casts and lets the line settle. The default guard is **3 seconds**, including a quiet check. After recognizing a splash, it waits **0.18 second (180 ms)** before clicking. Adjust **Post-cast protection (s)** and **Hook delay (s)** to suit the flight and game response.
4. The goal is to **keep the needle inside the green arc**. The [minigame guide](https://www.youtube.com/watch?v=BO6waB_XXhY&t=90s) specifies **green right arrow = hold right mouse; red left arrow = hold left mouse**. The macro releases the previous button before switching. Near the green edge in the pulling direction, it eases off both buttons and resumes within a safer margin. A/D remains independent. A dedicated leap response still needs a confirmed visual cue; edge relief is a separate control.
5. Active A/D side cards request one or two taps according to their dots, independently of mouse control.
6. After the result, the macro holds **T for three seconds** by default, checks Claim/name/weight and resumes fishing. Watch the first rounds in the preview.

Roblox must remain visible and focused. Losing focus pauses and releases inputs; return and resume with F4. Moving the camera or character requires marking the water again. Splash detection searches around that marked point.

| Default | Action |
| --- | --- |
| F4 | Start / pause |
| F8 | Mark water / splash search area |
| F6 / F7 | Select the entire circle on a frozen image; Enter saves, Esc cancels |
| F10 | Stop / release inputs |

Use **Settings → Language and shortcuts** to select Portuguese, English or Spanish and customize keys. A, D and T are reserved for gameplay; conflicting old bindings return to defaults. Changes preserve session history. Hints show selected keys.

Automatic mode searches for the segmented ring on each round and reacquires it even if the marker leaves the green arc. Manual mode fixes the selected full circle; side keys are read beside it. Circular profiles are isolated by client size, borders and DPI; old vertical selections are not reused. Active Roblox resolution is visible. **Observe only** inspects without sending input.

## History and support

History groups quantities by validated names and shows collection time, weight when read and notification icons when available. New names require two distinct high-confidence images. CSV export preserves history; local JSON also records weight and confirmation source.

A name on Claim does not confirm acquisition. A reward notification confirms it; without one, persistent Claim absence after a full T hold can **infer** collection. JSON distinguishes claim_after_hold from reward_notification. Physics or UI changes may still affect this inference.

Local text logs record timestamps, stages, splash, input transitions and outcomes. **Help and support** opens logs or copies a basic summary without username, personal paths, images or log contents. Nothing is sent automatically. Personal recordings, settings, captures and histories are excluded from the public repository and packages. The window can be resized.

## Validation

Automated checks cover the integrated flow, concurrent inputs, key release, profiles, history and recognition. Local video replay includes the two-tap A prompt and sends no game input. Replaying a recording cannot prove a live win; long live sessions and real compact-window recordings with the new UI remain unverified. Resized frames also exercise scaling.

[Beta numbering and previous versions](VERSIONING.en.md) · [Changelog](CHANGELOG.en.md)

The product name is generic; the available profile is specific to Slayers 2. Sources and downloads are public. Payments, activation keys, customer authentication and copy restrictions are not implemented. Development uses Python 3.12, requirements.txt and build.py. Replay tools additionally require imageio-ffmpeg.
