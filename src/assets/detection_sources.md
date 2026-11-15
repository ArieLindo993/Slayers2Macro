The compact `Collect` and `NEW!` references contain only small game-interface
glyphs. They contain no player name, character image, desktop, recording path,
or session data. Recordings and diagnostic captures used for local validation
are not included in the repository or release.

The `circle_*` references and `tests/fixtures/circular_ui.png` were derived from
user-provided recordings of the November 2026 circular fishing UI. They contain
only the ring/glyphs and the immediately surrounding game background, without
player names, character images or local file paths. The circular reader is
connected to the application input loop starting with Beta 0.0.42. The
`claim_*` references and `tests/fixtures/circular_key_a.png` likewise contain
only game-interface glyphs and their immediate background.

The `tests/fixtures/splash_*_masks.npz` regression samples retain only binary
cyan-particle masks, normalized water coordinates and frame geometry. They
exclude the original RGB images, UI text, player names, recording paths and
audio. They cover the November 15 animated fishing zone and earlier bites
inside/outside fishing zones. Raw recordings remain local.

Starting with Beta 0.0.44, `circle_mouse_*` contains rotation-normalized binary
green/right and red/left chevrons from those recordings. The older white
`circle_hold`/`circle_release` glyphs remain only as negative test references;
the production reader no longer uses them as mouse instructions. The RGB
`circular_green_cue`/`circular_red_cue` fixtures contain only the circular UI and
its adjacent game background, excluding characters, player names and paths.

The Beta 0.0.45 `splash_small_blue_*` and `splash_zone_blue_*` NPZ fixtures
preserve only filtered cyan/blue RGB pixels inside the marked water circle,
plus frame geometry and sampling rate. All other pixels are zeroed. They do
not include recording names, paths, audio, player names or character images.
They cover the three user-confirmed small bursts, a zone-only control, lower
capture rates and a resized variant. Original recordings remain local.
