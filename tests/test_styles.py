import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('styles', Path(__file__).parents[1] / 'button_colors_plus/styles.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

class StylesTest(unittest.TestCase):
    def test_invalid_config_is_safe(self):
        for raw in (None, [], 'bad', {'light': None, 'radius': 'bad', 'mode': []}):
            self.assertEqual(s.normalize(raw), s.DEFAULT)

    def test_css_injection_is_rejected(self):
        config = s.normalize({'light': {'again': '</style><script>alert(1)</script>'}})
        self.assertEqual(config['light']['again'], s.DEFAULT['light']['again'])

    def test_numeric_bounds_and_bools(self):
        config = s.normalize({'radius': 999, 'padding': -1, 'font_size': True})
        self.assertEqual((config['radius'], config['padding'], config['font_size']), (24, 2, 13))

    def test_presets_are_independent(self):
        a = s.preset('Ocean'); a['light']['again'] = '#000000'
        self.assertNotEqual(a['light'], a['dark'])
        self.assertNotEqual(a['light'], s.preset('Ocean')['light'])

    def test_themes_and_disable(self):
        c = s.preset('Classic'); c['dark']['again'] = '#123456'
        self.assertIn('#123456', s.stylesheet(c, True))
        self.assertNotIn('#123456', s.stylesheet(c, False))
        c['enabled'] = False
        self.assertEqual(s.stylesheet(c), '')

    def test_selectors_and_modes(self):
        for mode in ('filled', 'outline', 'text'):
            c = {**s.DEFAULT, 'mode': mode, 'style_show': False}
            css = s.stylesheet(c)
            for ease in range(1, 5):
                self.assertIn(f'button[data-ease="{ease}"]', css)
            self.assertNotIn('#ansbut', css)
            self.assertNotIn('onclick', css)

    def test_intervals_use_canvas_foreground_not_button_foreground(self):
        for dark, expected in ((True, '#fcfcfc'), (False, '#020202')):
            for mode in ('filled', 'outline', 'text'):
                config = {**s.DEFAULT, 'mode': mode}
                css = s.stylesheet(config, dark)
                self.assertIn('button[data-ease="2"] .nobold { color: ' + expected + ' !important; }', css)
                config['color_intervals'] = True
                self.assertIn('button[data-ease="2"] .nobold { color: #ad6500 !important; }', s.stylesheet(config, dark))

    def test_filled_label_color_options(self):
        config = s.preset('Classic')
        config['light']['hard'] = '#b86600'
        self.assertIn('background: #b86600 !important; color: #ffffff', s.stylesheet(config))
        config['label_color'] = 'auto'
        self.assertIn('background: #b86600 !important; color: #000000', s.stylesheet(config))
        config['light']['hard'] = '#ad6500'  # white still clears AA here, so white wins
        self.assertIn('background: #ad6500 !important; color: #ffffff', s.stylesheet(config))
        config['label_color'] = 'black'
        self.assertIn('background: #c73545 !important; color: #000000', s.stylesheet(config))
        self.assertEqual(s.normalize({'label_color': 'invalid'})['label_color'], 'white')

    def test_foreground_contrast(self):
        self.assertEqual(s.foreground('#ffffff'), '#000000')
        self.assertEqual(s.foreground('#000000'), '#ffffff')
        for palette in s.PALETTES.values():
            for color in palette:
                values = [int(color[i:i+2], 16)/255 for i in (1,3,5)]
                lum = sum((v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4)*w for v,w in zip(values,(.2126,.7152,.0722)))
                ratio = (lum+.05)/.05 if s.foreground(color) == '#000000' else 1.05/(lum+.05)
                self.assertGreaterEqual(ratio, 4.5)

if __name__ == '__main__':
    unittest.main()
