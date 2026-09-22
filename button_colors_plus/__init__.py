"""Button Colors: presentation-only reviewer styling."""
import json
from aqt import gui_hooks, mw
from aqt.qt import QAction
from aqt.reviewer import ReviewerBottomBar
from aqt.theme import theme_manager
from .styles import stylesheet

STYLE_ID = 'button-colors-plus'

def current_css():
    return stylesheet(mw.addonManager.getConfig(__name__), theme_manager.night_mode)

def inject(web_content, context):
    if isinstance(context, ReviewerBottomBar):
        web_content.head += f'<style id="{STYLE_ID}">{current_css()}</style>'

def refresh(*_args):
    if mw.state == 'review':
        mw.reviewer.bottom.web.eval('''(() => {
const id = %s;
let style = document.getElementById(id);
if (!style) { style = document.createElement('style'); style.id = id; document.head.append(style); }
style.textContent = %s;
})()''' % (json.dumps(STYLE_ID), json.dumps(current_css())))

def configure():
    from .settings import SettingsDialog
    SettingsDialog(mw, __name__, refresh).exec()

mw.addonManager.setConfigAction(__name__, configure)
mw.addonManager.setConfigUpdatedAction(__name__, refresh)
gui_hooks.webview_will_set_content.append(inject)
gui_hooks.theme_did_change.append(refresh)
action = QAction('Button Colors…', mw)
action.triggered.connect(configure)
mw.form.menuTools.addAction(action)
