"""Run with Anki's Python environment; does not touch a user collection."""
import importlib.util
from pathlib import Path
import sys
import types
from aqt.qt import QApplication, QMainWindow, QWidget
import aqt.webview

root = Path(__file__).parents[1] / 'button_colors_plus'
pkg = types.ModuleType('button_colors_plus')
pkg.__path__ = [str(root)]
sys.modules[pkg.__name__] = pkg

class Preview(QWidget):
    def stdHtml(self, body, **kwargs):
        self.html = body + kwargs['head']
        self.css = kwargs.get('css', [])

# Exercise native controls without starting Anki's collection/media server.
aqt.webview.AnkiWebView = Preview
from button_colors_plus.settings import SettingsDialog
from button_colors_plus.styles import DEFAULT

class Manager:
    def getConfig(self, module):
        return DEFAULT
    def writeConfig(self, module, value):
        self.result = value

app = QApplication(['button-colors-plus-test'])
parent = QMainWindow()
parent.addonManager = Manager()
refreshes = []
dialog = SettingsDialog(parent, 'button_colors_plus', lambda: refreshes.append(True))
assert dialog.preview.css == ['css/reviewer-bottom.css']
assert dialog.load_button.text() == 'Loaded'
assert not dialog.load_button.isEnabled()
dialog.presets.setCurrentIndex(1)
assert dialog.load_button.text() == 'Load Ocean'
assert dialog.load_button.isEnabled()
assert dialog.config == DEFAULT  # Selecting does not overwrite edits.
dialog.load_button.click()
assert dialog.load_button.text() == 'Loaded'
assert not dialog.load_button.isEnabled()
dialog.controls['radius'].setValue(12)
assert dialog.load_button.isEnabled()
dialog.controls['mode'].setCurrentText('outline')
dialog.preview_dark.setChecked(True)
assert 'border-radius: 12px' in dialog.preview.html
assert 'background: transparent' in dialog.preview.html
dialog.presets.setCurrentIndex(2)
dialog.load_preset()
assert dialog.config['light']['again'] == '#f2a0ad'
dialog.saved['My palette'] = dialog.config.copy()
dialog.populate_presets()
dialog.save()
assert 'My palette' in parent.addonManager.result['custom_presets']
assert refreshes == [True]
print('Qt settings smoke test passed: controls, presets, preview HTML, persistence.')
import aqt
from aqt import gui_hooks
from aqt.qt import QMenu
from aqt.reviewer import ReviewerBottomBar
parent.addonManager.setConfigAction = lambda module, callback: None
parent.addonManager.setConfigUpdatedAction = lambda module, callback: None
parent.form = types.SimpleNamespace(menuTools=QMenu(parent))
parent.state = 'review'
evaluations = []
parent.reviewer = types.SimpleNamespace(bottom=types.SimpleNamespace(web=types.SimpleNamespace(eval=evaluations.append)))
aqt.mw = parent
spec = importlib.util.spec_from_file_location('button_colors_plus', root / '__init__.py', submodule_search_locations=[str(root)])
addon = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = addon
spec.loader.exec_module(addon)
content = types.SimpleNamespace(head='')
addon.inject(content, object())
assert content.head == ''
addon.inject(content, ReviewerBottomBar(parent.reviewer))
assert 'button-colors-plus' in content.head
addon.refresh()
assert len(evaluations) == 1
parent.state = 'deckBrowser'
addon.refresh()
assert len(evaluations) == 1
hook_content = types.SimpleNamespace(head='')
gui_hooks.webview_will_set_content(hook_content, ReviewerBottomBar(parent.reviewer))
assert 'button-colors-plus' in hook_content.head
print('Anki hook smoke test passed: reviewer scope, registration, live refresh.')
