"""Validated configuration and CSS generation, independent of Anki/Qt."""
from copy import deepcopy
import re

ROLES = ('again', 'hard', 'good', 'easy', 'show')
PALETTES = {
    'Classic': ('#c73545', '#ad6500', '#23834b', '#286dcc', '#7656c4'),
    'Ocean': ('#bf4664', '#9c7017', '#008477', '#266ac4', '#5069b8'),
    'Pastel': ('#f2a0ad', '#efd191', '#a1d8b5', '#a9c9f4', '#cab8ec'),
    'Colorblind friendly': ('#cc79a7', '#d55e00', '#009e73', '#0072b2', '#8064b5'),
    'Monochrome': ('#64748b', '#64748b', '#64748b', '#64748b', '#64748b'),
}
LIMITS = {'radius': (0, 24), 'padding': (2, 12), 'min_width': (40, 130), 'font_size': (10, 20), 'border_width': (1, 4)}

def preset(name):
    colors = dict(zip(ROLES, PALETTES[name]))
    return {'enabled': True, 'mode': 'filled', 'label_color': 'white', 'radius': 8, 'padding': 6,
            'min_width': 70, 'font_size': 13, 'border_width': 2,
            'bold': True, 'color_intervals': False, 'style_show': True,
            'light': colors, 'dark': deepcopy(colors)}

DEFAULT = preset('Classic')

def normalize(raw):
    result = deepcopy(DEFAULT)
    if not isinstance(raw, dict):
        return result
    for key in ('enabled', 'bold', 'color_intervals', 'style_show'):
        if isinstance(raw.get(key), bool):
            result[key] = raw[key]
    if raw.get('mode') in ('filled', 'outline', 'text'):
        result['mode'] = raw['mode']
    if raw.get('label_color') in ('auto', 'white', 'black'):
        result['label_color'] = raw['label_color']
    for key, (low, high) in LIMITS.items():
        value = raw.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            result[key] = max(low, min(high, value))
    for theme in ('light', 'dark'):
        colors = raw.get(theme, {})
        if isinstance(colors, dict):
            for role in ROLES:
                value = colors.get(role)
                if isinstance(value, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', value):
                    result[theme][role] = value.lower()
    return result

def foreground(color):
    channels = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    luminance = sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))
    # Prefer white; fall back to black only where white drops below 4.5:1 (WCAG AA).
    # ponytail: picking the *strongest* contrast instead flips saturated mid-darks
    # like #ad6500 to black on a hair's-width margin, which reads wrong on a button.
    return '#ffffff' if 1.05 / (luminance + .05) >= 4.5 else '#000000'

def stylesheet(raw, dark=False):
    c = normalize(raw)
    if not c['enabled']:
        return ''
    rules = []
    for index, role in enumerate(ROLES, 1):
        if role == 'show' and not c['style_show']:
            continue
        selector = '#ansbut' if role == 'show' else f'button[data-ease="{index}"]'
        color = c['dark' if dark else 'light'][role]
        bg = color if c['mode'] == 'filled' else 'transparent'
        filled_fg = foreground(color) if c['label_color'] == 'auto' else ('#ffffff' if c['label_color'] == 'white' else '#000000')
        fg = filled_fg if c['mode'] == 'filled' else color
        border = color if c['mode'] != 'text' else 'transparent'
        rules.append(f'''{selector} {{
 background: {bg} !important; color: {fg} !important;
 border: {c['border_width']}px solid {border} !important;
 border-radius: {c['radius']}px !important;
 padding: {c['padding']}px 10px !important;
 min-width: {c['min_width']}px !important;
 font-size: {c['font_size']}px !important;
 font-weight: {700 if c['bold'] else 400} !important;
 box-shadow: none !important;
}}
{selector}:hover {{ filter: brightness({'1.15' if dark else '.92'}); }}
{selector}:focus-visible {{ outline: 3px solid {fg}; outline-offset: 2px; }}
{selector}:active {{ filter: brightness(.85); }}''')
        if role != 'show':
            rules.append(f'{selector} .nobold {{ color: {color if c["color_intervals"] else ("#fcfcfc" if dark else "#020202")} !important; }}')
    return '\n'.join(rules)
