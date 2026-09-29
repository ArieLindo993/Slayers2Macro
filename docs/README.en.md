# Fishing Macro

[Português](../README.md) · **English** · [Español](README.es.md)

A Windows fishing macro for **Slayers 2 on Roblox**, with automatic calibration, session history and local diagnostics. The product name is generic; the current game profile is specific to Slayers 2.

**[Download updater](https://github.com/ArieLindo993/Slayers2Macro/releases/latest/download/Atualizador.zip)** · **[Releases and downloads](https://github.com/ArieLindo993/Slayers2Macro/releases)** · **[Changelog](CHANGELOG.en.md)**

**Beta 0.0.34:** Improves reward notice detection across window sizes and OCR for small text.

## Install and start

Windows and Roblox are required. You do not need Python, Git or AutoHotkey. Internet access is needed to download updates and play Roblox.

1. Download **Atualizador.zip**, right-click it and choose **Extract All**. Keep the extracted folder somewhere writable. GitHub's **Code → Download ZIP** is source code, not the ready-to-run application.
2. Open the extracted folder and double-click **Atualizar.cmd**. Keep `Atualizar.ps1` and the other scripts together. Do not launch them inside the ZIP.
3. Wait for the download, integrity check and extraction. When asked **Abrir agora? (S/N)**, enter **S** to open the macro. The updater scripts still use Portuguese prompts and filenames.
4. In the macro, open **Configurar → Idioma e atalhos**, select **English**, then click **Salvar e fechar**. After this, the settings are labeled **Settings → Language and shortcuts → Save and close**.

For manual installation, download **Slayers2Macro.zip**, extract everything, and run **Slayers2Macro.exe** with its companion files in place. The `.sha256` file is a download checksum, not an application. The updater checks it automatically.

## First fishing session

1. Enter Slayers 2, equip your fishing rod and stand near the water.
2. Keep Roblox in the foreground, point the mouse at a valid water location, and press **F8** to save the casting point.
3. Leave automatic calibration enabled and press **F4**.
4. The macro casts, waits for the minigame, tracks the marker, and holds **T** to collect the reward. Watch the first round using the preview and status message.
5. Press **F10** to stop. Losing focus pauses the macro and releases inputs; return to Roblox and use **F4** to resume.

Roblox must remain visible and in the foreground. The macro uses the mouse and keyboard while active. Unsuccessful casts and catches without rewards are handled automatically. There are up to three casts per round and five collection attempts, with early completion when evidence allows. An item disappearing alone does not count as a confirmed reward. If no item is identified in the first two collection attempts, absence is checked before fishing resumes.

## Language and shortcuts

Open **Settings → Language and shortcuts**. Choose **Português**, **English** or **Español**, set the keys, then **Save and close**. Changes apply immediately, without resetting the session history or counters, and are saved locally for future launches and updates.

| Default | Action |
| --- | --- |
| F8 | Mark water / save the casting point |
| F4 | Start or pause |
| F6 | Calibrate manually / select the bar |
| F7 | Alternate manual calibration shortcut |
| F10 | Stop and release inputs |

Use F1–F12, letters or digits. **T is reserved for in-game collection**. All actions need different keys; duplicates cannot be saved. **Restore defaults** resets the shortcut fields; save to apply. Shortcuts do not start fishing while settings are open. In manual selection, **Enter** saves, **Esc** cancels, and your configured stop key also cancels.

On-screen instructions show your selected keys. References to F4/F8/F6/F10 in this guide describe factory defaults. Game mouse clicks and collection with T retain their current behavior.

Menus, status messages, history, manual selection and manually exported CSV are translated. Item names remain as shown in the game. Diagnostic logs, JSON and automatically saved CSV retain a stable format. Changing the macro's language does not change Roblox's language.

## Calibration and tracking

**Automatic:** the macro checks the bar on every catch. Three consistent observations are needed to confirm its location. Reliable rounds refine the display profile, but improvement on every attempt is not guaranteed. The location is checked periodically even after confirmation. When tracking is lost, the search expands from the current region to nearby areas and the game screen. After 120 seconds without the marker, automatic recovery begins instead of stopping permanently.

**Manual:** show the minigame and press F6. On the frozen screenshot, drag around the entire vertical bar and save. This enables manual mode. Return to Roblox and press F4. You can re-enable automatic calibration in the main window.

Display profiles separate calibration by window size, borders and Windows scaling. Blue marks the analyzed area, green the target, and pink the marker. The time-inside-target metric measures valid tracking intervals, not the percentage of catches won.

## Fishing settings

Open **Settings → Fishing**, adjust the values and save.

| Setting | Default | Allowed range |
| --- | --- | --- |
| Click duration | 0.25 s | 0.08–1 s |
| Hold T | 3 s | 0.2–5 s |
| Wait before retrying a cast | 20 s | 10–60 s |
| Wait for item after fishing | 2 s | 0.5–20 s |

Updates preserve existing preferences except documented migrations. An older T duration, such as 1.5 seconds, must be changed manually if you want 3 seconds. The old 12-second item wait migrates once to 2 seconds. **Observe only** shows detection without sending game input.

## History and diagnostics

**Items obtained** opens a summary and a chronological history. OCR may fail; “Unidentified name” is a placeholder. Late reward recognition can correct the original cycle and confirmed count without duplication. Known variants such as “Clown” and “Clown F” are grouped as **Clown Fish**. Older session files are not rewritten.

Reward thumbnails come from the game's reward notification. They are reused per recognized item name, stored in the local JSON, and limited to 256 distinct thumbnails per session. Missing images show a dash; there is no online icon catalogue or retroactive recovery of old images. CSV contains text only. **Clear list / new session** starts a fresh list while preserving the previous files on disk.

**Open records** opens the local data folder. Optional diagnostic snapshots are limited to 20 image/record pairs. The snapshot setting does not disable text logs or item thumbnails.

**Open text logs** opens timestamped session logs. They record launches, starts, pauses, fishing, calibration, collection attempts, recognized rewards, recovery and errors. Each line includes date, time and local timezone. A periodic snapshot is logged every 30 seconds. These are event logs, not a video of every frame. Abrupt termination may leave only the last completed entries. The separate `runtime.json` keeps up to 200 recent events and refreshes its state every five seconds.

Vision, calibration, OCR and diagnostic tasks run in bounded worker processes. Stalled tasks are restarted. Three unconfirmed casts trigger recovery with a 15–60-second delay; recognized fishing or an item takes priority over recasting. Resizing the same Roblox window triggers adjustment. Manual pauses and focus loss still require you to resume; recovery does not reconnect Roblox or change the saved water point.

## Update, rollback and troubleshooting

Close the macro before updating. Keep the updater's hidden `.install` folder.

| Script | Purpose |
| --- | --- |
| Atualizar.cmd | Check GitHub, install the latest version, offer to launch it |
| Iniciar.cmd | Launch the installed version without checking for updates |
| Voltar-versao.cmd | Switch to the previous version installed by this updater |

To update the updater itself, extract a new **Atualizador.zip** into the same folder, replacing its files while preserving `.install`. Rollback requires an earlier version installed by the same updater. After rollback, use **Iniciar.cmd** to avoid immediately updating again.

If a command window appears idle, allow time for downloading and extracting. If scripts are missing, extract the entire ZIP. Close the macro if the updater reports it is running. Retry failed network or integrity checks. If fishing does not start, put Roblox in the foreground, equip the rod and mark water. If tracking fails, inspect the preview and try manual calibration. Include the version, status text and steps when reporting a problem; review logs or images before sharing.

## Local data and development

Settings, profiles, history and diagnostics are stored in `%LOCALAPPDATA%\FishingMacro`, separate from installation. There is no telemetry or automatic upload of these files. The updater contacts GitHub for releases. Personal videos, configurations, histories and logs are not included in the repository or distribution. Diagnostic images contain the selected region; an incorrect selection may include other visible elements.

The repository and downloads are public. The application currently has no payment, license-key activation, customer authentication or copy restrictions. Distributed game visuals are indicator crops and the icon from the [Slayers 2 Roblox page](https://www.roblox.com/games/16205713724/Slayers-2).

For development, use Windows and Python 3.12 in a virtual environment:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python audit.py
python src/macro.py
```

`python build.py` creates the packages and tests executable startup. A `v*` tag runs the Windows release workflow. Keep the tag, `src/product.py` version and changelogs aligned. UI translations are in `src/i18n.py`; preference validation is in `src/preferences.py`. Built packages include library notices in `THIRD_PARTY`. Automated checks and recorded-frame tests do not replace a long live-game session; game UI changes may require detection updates.
