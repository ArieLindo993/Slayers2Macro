# Version history

[Português](../CHANGELOG.md) · **English** · [Español](CHANGELOG.es.md) · [User guide](README.en.md)

Older entries below summarize the documented releases. The [Portuguese changelog](../CHANGELOG.md) includes the detailed investigations and validation notes. Recorded-frame and automated tests do not guarantee uninterrupted live gameplay.

## [Beta 0.0.34](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.34-beta)

### Notification recovery and OCR

- Detects reward notices with fixed-size UI and UI that scales with the game window, and chooses the matching crop geometry.
- If the normal read cannot separate small or partly faded text, retries with locally enhanced contrast. Existing name and quantity validation remains in place.
- Logs the selected geometry, visual match score, and whether OCR found reward text.
- Local evidence: the previous log recorded 9 cycles with no item indicator or notice, then identified Crustadon x1 when a notice appeared; another notice was detected, but Roblox lost focus before OCR finished.
- Validation: all 112 tests and packaging audit passed, including 5 geometry checks. A continuous live session still needs confirmation.

## [Beta 0.0.33](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.33-beta)

### Stricter item name validation

- Observed-name catalogue and explicit corrections for Golden Fish, Clown Fish, Crustadon, Coral, Sea Horse and other variants. Distinct items such as OuwFish/OuwFwesh and Refinement Ore/Mythic Refinement Ore stay separate.
- Fragments such as Fish, a Fish and Ore, border-clipped words and suspected near-name errors remain **Unidentified name**, preserving reward quantities.
- New names require matching high-confidence readings from two different images. Reprocessing the same image cannot confirm a new name; suspicious near-matches are not learned as new species.
- Later conflicting readings cannot overwrite a validated name. Late identification does not duplicate collection counts; pending-name memory is bounded.
- Pending names and conflicts are logged. Older files are preserved; validation applies to new entries.
- Includes the clearer thumbnails and direct inventory rewards from Beta 0.0.32.
- Validation: 107 tests, local replay of a real history with totals preserved, and OCR of real OuwFish/Metal Scraps frames. Personal data was not published.

## [Beta 0.0.32](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.32-beta)

### Clearer icons and direct inventory rewards

- Reward notifications are checked during quick minigame scans too. A new notification can confirm an item sent directly to inventory, without a Collect prompt or pressing T.
- Notifications overlapping the last minigame frame are retained until fishing ends. Preexisting or lingering previous-round notifications are not counted again.
- OCR uses the same captured frame and original cycle as notification detection; text reading also starts when the bar disappears.
- Thumbnails are selected across distinct frames using notification contrast and icon detail. Faint frames are rejected; a better image replaces the earlier thumbnail, without a fade-out downgrade. Shared item thumbnails improve across the current session. Old files are not reprocessed; a dash remains when no suitable frame exists.
- Notification and icon-update events are logged.
- Validation: 99 automated tests and a real recorded reward sequence. Direct inventory collection was simulated and still needs live-game confirmation.

## [Beta 0.0.31](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.31-beta)

### Beta numbering from the beginning

- Every version is classified as beta, from Beta 0.0.0 to Beta 0.0.31, including pre-Git packages, intermediate variants and the AutoHotkey prototype.
- The [version mapping](VERSIONING.en.md) records old identifiers, local package hashes and preserved tags. No versions are invented for attempts without artifacts.
- The title and interface show Beta 0.0.31; logs identify 0.0.31-beta. Older GitHub release names and descriptions are updated; original historical packages are preserved.
- The updater displays the public release name and still installs by release ID. The download channel is preserved; settings, shortcuts and languages are not reset.
- Naming, documentation and distribution changes only; fishing mechanics preserved.

## [Beta 0.0.30](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.4.0)

- Portuguese (default), English and Spanish interface, selectable in **Settings → Language and shortcuts**. Saving applies the language immediately without losing session history or counters.
- Translated main window, fishing status messages, settings, history, manual selection and manually exported CSV. Game item names and technical log/data formats remain stable.
- Configurable start/pause, water, main/alternate calibration and stop shortcuts. Defaults remain F4, F8, F6, F7 and F10 respectively.
- Supports F1–F12, letters and digits; T is reserved for collection. Duplicate-key validation, restore-defaults button and on-screen hints showing the chosen keys.
- Settings pause fishing and suppress shortcuts while editing. The configured stop key cancels manual selection; Enter and Esc remain available.
- Preferences persist locally, separately from display profiles. Old or invalid preferences use defaults. No changes to the fishing controller, timings or in-game T input.
- Guides and version histories in three languages, linked from GitHub and bundled with downloads. Updater scripts remain in Portuguese.
- 88 automated tests cover translation placeholders, custom shortcuts, conflicts, persistence, CSV export and preserved session data, alongside previous fishing and stability checks and visual inspection.

## [Beta 0.0.29](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.1)

- Late reward recognition corrects the original history entry and confirmed count once, including delayed first-use OCR. Preparing the next cast allows additional reading attempts.
- Expanded reward crop and joined words on the same line. Known Clown Fish name fragments and case differences share totals and icons, without fuzzy merging of distinct species. Old session files are preserved.
- 81 automated tests; recorded OuwFish and Metal Scraps rewards checked. The specific first-discovery notification still requires live-game verification; missing evidence is not invented.

## [Beta 0.0.28](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.3.0)

- Real reward thumbnails in Summary and History, associated with their capture and original cycle, including late results. Images are reused per recognized name and stored in local JSON; CSV remains textual.
- Maximum 256 distinct thumbnails per session; missing images do not block fishing. 77 tests and visual inspection using real reward frames.

## [Beta 0.0.27](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.2.2)

- Fixed recovery getting stuck when briefly aged observations repeatedly reset evidence. Independent ordered captures and processing latency are handled explicitly.
- Losing the marker for 120 seconds now enters recovery. Bounded isolated worker processes recover from hangs; transient capture errors and same-window resizing are handled. Manual pauses remain manual.
- Expanded diagnostic events, endurance and recovery tests; updater integrity, staging and rollback fixes. Live overnight stability is not guaranteed by simulated tests.

## [Beta 0.0.24](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.1)

- Replaced the hook icon with the Slayers 2 game-page icon and removed green checkerboard decoration. Bundled offline image; visual change only.

## [Beta 0.0.23](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.1.0)

- Dark blue and jade fishing/anime-inspired theme, reorganized 900 × 720 main window, consistent settings/history/manual-selection styling and clearer start/stop controls. Fishing mechanics and settings unchanged.

## [Beta 0.0.22](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.9)

- Default post-minigame wait reduced from 12 to 2 seconds with a one-time default migration; custom values preserved. Absence verification uses two independent frames spanning at least 0.6 seconds. Retry interval reduced to 0.6 seconds; T remains 3 seconds.

## [Beta 0.0.21](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.8)

- Preserved collection-absence evidence across short processing gaps. Only valid ordered frames count; reappearance, active fishing or gaps over three seconds reset verification. Added detailed post-T observation logs. Disappearance alone remains unconfirmed.

## [Beta 0.0.20](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.7)

- Three unconfirmed casts start automatic recovery rather than a permanent pause, with waits increasing from 15 to 60 seconds. Fresh observations are required before recasting; active fishing or an item takes priority. Counters/history preserved; no Roblox reconnection.

## [Beta 0.0.19](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.6)

- Per-launch text logs with date, milliseconds and local timezone; fishing, collection, OCR, calibration, pause, recovery and error events; periodic 30-second state. Prior logs are kept locally, separate from the bounded runtime journal.

## [Beta 0.0.18](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.5)

- Stricter marker geometry and independent recent minigame evidence prevent learning text as the bar. Old automatic profiles reset; manual selection and user settings retained.
- Added bounded `runtime.json`, periodic state and previous-interruption detection, local records button and publication checks excluding runtime files.

## [Beta 0.0.17](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.4)

- Detection improved for translucent/yellow targets and darkened markers outside the target. Real-video and synthetic checks added; successful frame readings are not a catch win rate.

## [Beta 0.0.16](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.3)

- Periodic bar relocalization, handling of white overlap and continued search during active fishing. Confirmed rewards end collection early; persistent absence or two no-item attempts can end the sequence after independent observations. Unconfirmed outcomes remain separate.

## [Beta 0.0.15](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.2)

- Default T hold increased from 1.5 to 3 seconds, preserving saved preferences. Updater progress messages and a 30-second release-query timeout added.

## [Beta 0.0.14](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.1)

- Smaller preview and per-display preservation/restoration of manual versus automatic calibration, including the corresponding UI option.

## [Beta 0.0.13](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v7.0.0)

- Generic Fishing Macro branding; annotated preview, tracking metrics, progressive bar search, display profiles, bounded local diagnostics and launch/rollback scripts.
- User data separated from executable files, additive migration, repository privacy audit and third-party library notices.

## [Beta 0.0.12](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v6.1.0)

- First version recorded in this repository: F8 water marking, F4 start/pause, F10 stop, F6 manual bar selection, automatic calibration, minigame control, held-T collection, bounded retries, focus-loss pause, OCR history and Windows executable/updater with SHA-256 verification.
- The separate updater ZIP was packaged after this tag, before Beta 0.0.13. Earlier prototypes have no repository tags to substantiate a precise version-by-version history.
