"""Native settings with a preview rendered using the reviewer's actual CSS."""
from copy import deepcopy
from html import escape
from aqt.qt import (QCheckBox, QColor, QColorDialog, QComboBox, QDialog,
    QDialogButtonBox, QFormLayout, QGridLayout, QHBoxLayout, QInputDialog,
    QLabel, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget)
from aqt.webview import AnkiWebView
from .styles import LIMITS, PALETTES, ROLES, normalize, preset, stylesheet

class SettingsDialog(QDialog):
    def __init__(self, parent, module, refresh):
        super().__init__(parent)
        self.setWindowTitle('Button Colors')
        self.resize(640, 650)
        self.manager, self.module, self.refresh = parent.addonManager, module, refresh
        raw = self.manager.getConfig(module) or {}
        self.config = normalize(raw)
        saved = raw.get('custom_presets', {})
        self.saved = {name: normalize(value) for name, value in saved.items()
                      if isinstance(name, str) and isinstance(value, dict)} if isinstance(saved, dict) else {}
        self.loading = False
        layout = QVBoxLayout(self)
        title = QLabel('<h2>Make your review buttons yours.</h2>')
        layout.addWidget(title)
        row = QHBoxLayout()
        self.presets = QComboBox()
        self.populate_presets()
        row.addWidget(self.presets, 1)
        self.load_button = QPushButton('Load preset')
        self.load_button.setAutoDefault(False)
        self.load_button.clicked.connect(self.load_preset)
        row.addWidget(self.load_button)
        self.presets.currentIndexChanged.connect(self.update_preset_action)
        for label, callback in [('Save as…', self.save_preset), ('Delete saved', self.delete_preset)]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            row.addWidget(button)
        layout.addLayout(row)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        appearance = QWidget()
        form = QFormLayout(appearance)
        self.controls = {}
        mode = QComboBox()
        mode.addItems(['filled', 'outline', 'text'])
        mode.currentTextChanged.connect(self.changed)
        self.controls['mode'] = mode
        form.addRow('Style', mode)
        label_color = QComboBox()
        label_color.addItems(['white', 'black', 'auto'])
        label_color.currentTextChanged.connect(self.changed)
        self.controls['label_color'] = label_color
        form.addRow('Filled button text', label_color)
        labels = {'radius': 'Corner radius', 'padding': 'Vertical padding', 'min_width': 'Minimum width', 'font_size': 'Font size', 'border_width': 'Border width'}
        for key, limits in LIMITS.items():
            spin = QSpinBox()
            spin.setRange(*limits)
            spin.setSuffix(' px')
            spin.valueChanged.connect(self.changed)
            self.controls[key] = spin
            form.addRow(labels[key], spin)
        for key, label in [('enabled', 'Enable button styling'), ('bold', 'Bold labels'), ('color_intervals', 'Use palette colors for intervals'), ('style_show', 'Style Show Answer')]:
            check = QCheckBox(label)
            check.toggled.connect(self.changed)
            self.controls[key] = check
            form.addRow(check)
        tabs.addTab(appearance, 'Appearance')
        self.color_buttons = {}
        for theme in ('light', 'dark'):
            page = QWidget()
            grid = QGridLayout(page)
            for index, role in enumerate(ROLES):
                grid.addWidget(QLabel('Show Answer' if role == 'show' else role.title()), index, 0)
                button = QPushButton()
                button.clicked.connect(lambda _checked=False, t=theme, r=role: self.pick_color(t, r))
                self.color_buttons[theme, role] = button
                grid.addWidget(button, index, 1)
            tabs.addTab(page, f'{theme.title()} colors')
        self.preview_dark = QCheckBox('Preview dark mode')
        self.preview_dark.toggled.connect(self.update_preview)
        layout.addWidget(self.preview_dark)
        self.preview = AnkiWebView(parent=self)
        self.preview.setMinimumHeight(160)
        layout.addWidget(self.preview)
        note = QLabel('Changes apply when you save. Presets include both light and dark palettes.\nFilled text: white for consistency, black, or auto for strongest contrast.')
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        for index in range(self.presets.count()):
            kind, name = self.presets.itemData(index)
            candidate = preset(name) if kind == 'builtin' else self.saved[name]
            if candidate == self.config:
                self.presets.setCurrentIndex(index)
                break
        self.load_controls()

    def update_preset_action(self, *_args):
        data = self.presets.currentData()
        if not data:
            self.load_button.setEnabled(False)
            return
        kind, name = data
        candidate = preset(name) if kind == 'builtin' else self.saved[name]
        pending = candidate != self.config
        self.load_button.setEnabled(pending)
        self.load_button.setText(f'Load {name}' if pending else 'Loaded')
        self.load_button.setToolTip(
            f'Apply {name} to the editor. Press Save to keep changes.' if pending
            else 'This preset matches your current settings.')
        self.load_button.setStyleSheet(
            'QPushButton { background: #2563eb; color: white; border: 1px solid #60a5fa; border-radius: 5px; padding: 5px 12px; }'
            'QPushButton:hover { background: #1d4ed8; }'
            'QPushButton:pressed { background: #1e40af; }' if pending else '')

    def populate_presets(self):
        self.presets.clear()
        for name in PALETTES:
            self.presets.addItem(name, ('builtin', name))
        for name in sorted(self.saved):
            self.presets.addItem(f'Saved: {name}', ('saved', name))

    def load_controls(self):
        self.loading = True
        for key, widget in self.controls.items():
            if isinstance(widget, QCheckBox):
                widget.setChecked(self.config[key])
            elif isinstance(widget, QSpinBox):
                widget.setValue(self.config[key])
            else:
                widget.setCurrentText(self.config[key])
        for (theme, role), button in self.color_buttons.items():
            color = self.config[theme][role]
            button.setText(color)
            from .styles import foreground
            button.setStyleSheet(f'background-color: {color}; color: {foreground(color)}; padding: 6px;')
        self.loading = False
        self.update_preview()

    def changed(self, *_args):
        if self.loading:
            return
        for key, widget in self.controls.items():
            self.config[key] = widget.isChecked() if isinstance(widget, QCheckBox) else widget.value() if isinstance(widget, QSpinBox) else widget.currentText()
        self.update_preview()

    def pick_color(self, theme, role):
        color = QColorDialog.getColor(QColor(self.config[theme][role]), self, f'{role.title()} — {theme}')
        if color.isValid():
            self.config[theme][role] = color.name()
            self.load_controls()

    def load_preset(self):
        kind, name = self.presets.currentData()
        self.config = preset(name) if kind == 'builtin' else deepcopy(self.saved[name])
        self.load_controls()

    def save_preset(self):
        name, ok = QInputDialog.getText(self, 'Save preset', 'Preset name (same name replaces a saved preset):')
        if ok and name.strip():
            self.saved[name.strip()[:80]] = deepcopy(self.config)
            self.populate_presets()
            self.presets.setCurrentIndex(self.presets.findData(('saved', name.strip()[:80])))

    def delete_preset(self):
        data = self.presets.currentData()
        if data and data[0] == 'saved':
            del self.saved[data[1]]
            self.populate_presets()

    def update_preview(self, *_args):
        self.update_preset_action()
        dark = self.preview_dark.isChecked()
        background, text = ('#2c2c2c', '#fcfcfc') if dark else ('#f5f5f5', '#020202')
        css = stylesheet(self.config, dark)
        buttons = ''.join(
            f'<td align="center"><button data-ease="{i}">{escape(role.title())}'
            f'<span class="nobold">{interval}</span></button></td>'
            for i, role, interval in zip(range(1, 5), ROLES, ('1m', '6m', '10m', '5d'))
        )
        body = (
            '<div id="middle"><center><table cellpadding="0" cellspacing="0"><tr>'
            + buttons + '</tr></table></center></div>'
            '<p><button id="ansbut">Show Answer</button></p>'
        )
        # Use Anki's reviewer CSS for interval typography/positioning instead of
        # approximating it. Scope theme variables below the app's root theme.
        self.preview.stdHtml(
            body,
            css=['css/reviewer-bottom.css'],
            head=f"""<style>
body {{ --fg: {text}; --canvas: {background};
    color-scheme: {'dark' if dark else 'light'};
    background: {background}; color: {text}; text-align: center;
    padding-top: 16px;
}}
{css}
</style>""",
            context=self,
        )

    def save(self):
        self.manager.writeConfig(self.module, {**normalize(self.config), 'custom_presets': self.saved})
        self.refresh()
        self.accept()
