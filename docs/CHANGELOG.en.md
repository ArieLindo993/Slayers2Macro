# Version history

[Português](../CHANGELOG.md) · **English** · [Español](CHANGELOG.es.md) · [User guide](README.en.md)

Older entries below summarize the documented releases. The [Portuguese changelog](../CHANGELOG.md) includes the detailed investigations and validation notes. Recorded-frame and automated tests do not guarantee uninterrupted live gameplay.

## [Beta 0.0.41](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.41-beta)

### Continuous capture, first rewards and complete bar calibration

- Notification capture and calibration now continue while an earlier scene scan is busy. A bounded queue preserves original frames, timestamps and cycle ownership; late results update the correct catch without double counting.
- OCR enlarges small text regions instead of enlarging the entire scene fourfold and stops after a validated reward. Compact recorded frames recognized Metal Scraps, Crustadon, Krathulon and OuwFish; latency depends on the frame and computer load.
- First acquisitions can show a yellow NEW! badge instead of ×1. It is accepted only beside an aligned known item name. Collect prompts or names alone do not confirm a catch.
- Calibration rejects targets cut by crop edges and prefers the enclosing rail over inner contours. Once the independent fishing indicator confirms the minigame, marker overlap with scenery does not re-enable the stricter new-bar localization filter.
- Adds a native compact Collect reference while retaining the 0.80 threshold. Detector revision 5 renews old automatic profiles and preserves manual settings.
- Logs every OCR outcome with frame age, queue size and detection counts. Starting a new history clears pending frames from the previous session.
- Validation includes automated tests, local 800×599 recorded-frame replay and the compiled executable. Offline replay does not establish long-session live control reliability. `tools/replay_video.py` accepts local recordings without publishing them.

## [Beta 0.0.40](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.40-beta)

### Compact tracking and reward labels over the character

- The 800×599 recording showed the minigame’s “Exit” button scoring 0.823, below the 0.83 cutoff. Detection now accepts it from 0.78 while retaining the existing distinct-frame confirmation.
- Over the green island, the target outline turns lime green in some frames instead of yellow. Detection now pairs the two saturated outlines (yellow or lime green) without treating the large green map area as the target band.
- The obtained item appears as a small label over the character. In the real capture OCR read “OuwFish” and “X” because the `1` in `x1` is tiny. The reader accepts that case only when X aligns with a known item name; a lone X cannot confirm an item.
- The supplied frames now recover bar readings in five consecutive moments over the island, and OCR reads “OuwFish × 1” from the compact frame. Tests also cover the exit-button margin and reject frames without a bar or an aligned item name.

## [Beta 0.0.39](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.39-beta)

### Compact resolution, collection and tracking over green scenery

- The 800×599 log completed 16 cycles without a confirmed catch. The review found a coordinate mismatch: the badge was located in Roblox client coordinates, while OCR cropped a centered 1920×1080 canvas; the old conversion shifted the crop, especially vertically. OCR now uses the client position plus its canvas offset, separate from the scaled coordinates used for item icons.
- A weak badge match can guide another OCR attempt from a score of 0.50. It cannot confirm a reward: the existing item-name and quantity checks still apply. The compact fallback crop now comes from the center of the captured game view.
- Collection and fishing indicators are matched at scales proportional to the current Roblox window. The side panel explicitly displays the active resolution.
- The green target is first located by its paired yellow edges, independent of fill color. This keeps tracking alive when a green map area merges with the target, including narrow crops from small windows. The detector revision changes so old automatic profiles are recalibrated.
- All 129 automated tests cover collection and fishing indicators at 800×599/1280×720, centered-canvas crop coordinates, blank-frame rejection and a yellow target over green scenery. The diagnostic captures that failed now produce valid readings; a fresh live Roblox session is still needed to confirm gameplay behavior.

## [Beta 0.0.38](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.38-beta)

### Reward reading in small windows

- In the compact cycle from the supplied log, the macro detected the minigame and rod item, pressed T, and saw the notice disappear, but OCR found neither a name nor a quantity. The session then switched to fullscreen after that single compact cycle; it does not show repeated failures across compact cycles.
- Compact captures now preserve their original scale instead of stretching to 1920×1080 before OCR. Recognition also tries an independent crop in the upper central area, even if a weak badge match points elsewhere.
- Validation still requires both an item name and a quantity. Item disappearance alone does not count as a confirmed catch.
- 125 automated tests cover compact geometry, fallback crops, cycle attribution and recovery. They verify logic with simulated OCR; another live 800×599 Roblox session is still needed to verify the result in-game.

## [Beta 0.0.37](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.37-beta)

### OCR scan and window stabilization

- The latest log showed six completed cycles without a reward reading; the best badge matches scored 0.71–0.77, below the 0.91 confirmation threshold. Beta 0.0.36's wider search did not account for the badge scaling down in compact windows.
- Matches the badge at multiple aspect-preserving scales. A weak match can guide the OCR crop, but it cannot confirm a reward or lower visual validation.
- The same log recorded about 35 consecutive recoveries while the reported geometry remained 800×599. Position or HWND changes at the same size now update the active window without restarting the cycle; an actual resolution change must stay stable for 250 ms and triggers one recovery.
- OCR logs now include crop dimensions, OCR box counts, best numeric confidence values and window scale/position data, without saving screenshots or raw OCR text.
- Automated tests cover small and weak notices, plus HWND/position fluctuations. A new live Roblox session is still needed to confirm reward reading.

## [Beta 0.0.36](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.36-beta)

### Reward notices at different positions

- The latest log showed the search starting below the notice in 800×599 windows: 0/10 compact notices and 8/10 fullscreen notices were detected, despite all 20 cycles completing.
- Expands reward search for both fixed-size and scaled UI layouts.
- Makes the OCR crop taller so it includes notices above the fullscreen reference position.
- Adds a regression case for a notice above the old search band.
- Real-session confirmation at both resolutions is still needed; the geometry fix alone does not prove perfect operation.

## [Beta 0.0.35](https://github.com/ArieLindo993/Slayers2Macro/releases/tag/v0.0.35-beta)

### Small-window collection fix

- Widens the reward crop to include the full notice in smaller windows and when name and quantity share one line.
- OCR results that finish before a cycle is written to history are retained and attached to that collection once it is recorded.
- Notices still on screen while waiting for the next bite are no longer assigned to the new cycle.
- Latest-log diagnosis: none of the 10 catches in the 800×599 window had a detected notice; 8/10 in fullscreen did. Names were read for detected notices, while the other catches were marked unconfirmed. This addresses missed reading and cycle attribution.
- Keeps name validation and support for empty catches.

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
