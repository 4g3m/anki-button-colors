# Button Colors

<img width="640" height="753" alt="image" src="https://github.com/user-attachments/assets/6d9f3d11-798a-4d15-b5af-fb7c257446d4" />


A new Anki Desktop add-on inspired by [teaqu/anki-button-colours](https://github.com/teaqu/anki-button-colours), implemented independently using reviewer CSS rather than adding font markup to labels. No original source code is incorporated.

Install from the official [Button Colors page on AnkiWeb](https://ankiweb.net/shared/info/747344205), or download the packaged `.ankiaddon` file from this repository.

Supports **Anki 2.1.55 and newer**, including the current 26.x releases. The minimum is based on the first release that provides all APIs used by the add-on, including `theme_did_change`. The add-on uses `ReviewerBottomBar`, `webview_will_set_content`, and `data-ease` button attributes. It does not replace reviewer methods or change scheduling, labels, keyboard shortcuts, or answer actions. Desktop only; AnkiMobile and AnkiDroid do not load desktop add-ons.

## Install

1. Download or locate `dist/button-colors.ankiaddon`.
2. In Anki, open **Tools → Add-ons → Install from file…** and select it.
3. Disable the old Button Colours add-on, or other add-ons that restyle review buttons, to avoid conflicting styles.
4. Restart Anki, then open **Tools → Button Colors…** (also available through the add-on's Config button).

## Customize

- Five built-in presets: Classic, Ocean, Pastel, Colorblind friendly, Monochrome.
- Independent light/dark colors for Again, Hard, Good, Easy, and Show Answer.
- Filled, outline, or text-only styling.
- Corner radius, vertical padding, minimum width, font size, border thickness, bold labels, and interval colors.
- Optional Show Answer styling and a master enable switch.
- A live HTML preview with a dark-mode toggle.
- Save, load, and delete named personal presets.

Press **Load preset** to apply the selectaned preset to the editor. **Save as…** captures your current editor settings. Press **Save** to commit everything and update an active review; **Cancel** discards the editing session. Presets include appearance settings and both palettes. Settings are installation-wide and do not sync through AnkiWeb.

Intervals above buttons use Anki’s theme foreground by default; optional interval coloring uses the palette color.

Filled styles default to consistent white labels. The Filled button text option also offers black or automatic contrast. Auto selects black or white text with at least 4.5:1 contrast; fixed white/black may have lower contrast on some palettes. Outline and text styles depend on the selected color and background; inspect both previews. Anki retains its native labels, so colors are not the sole indication of rating. Large widths may need reducing on narrow windows. Add-ons that replace the entire review toolbar may not be compatible.

## Verification

- Nine automated tests cover invalid configurations, CSS injection rejection, numeric bounds, independent presets, theme selection, selectors, and filled-text contrast.
- Native Qt controls, preview HTML generation, preset loading, persistence, hook registration, reviewer-only injection, and refresh are smoke-tested with the available Anki 25.09.4 Python runtime. The preview webview is stubbed in this test to avoid opening a collection/media server.
- Integration APIs and selectors were checked against the official **2.1.55** and **26.09.2** release sources. The settings UI and hooks were smoke-tested with Anki 25.09.4. A full live review on the minimum version has **not** been run in this workspace.

Build: `python3 build.py`. Tests: `python3 -m unittest discover -s tests -v`.
Run `tests/qt_smoke.py` with an Anki Python environment to exercise Qt controls and hooks.

Before release, manually verify a question/answer cycle, ratings 1–4, Space, theme switching, saving while reviewing, Cancel, and a narrow review window in Anki 2.1.55 and the latest Anki release.

References: [Anki 2.1.55 hooks](https://github.com/ankitects/anki/blob/2.1.55/qt/tools/genhooks_gui.py), [Anki 26.09.2 reviewer](https://github.com/ankitects/anki/blob/26.09.2/qt/aqt/reviewer.py), [add-on hooks guide](https://addon-docs.ankiweb.net/hooks-and-filters.html).
