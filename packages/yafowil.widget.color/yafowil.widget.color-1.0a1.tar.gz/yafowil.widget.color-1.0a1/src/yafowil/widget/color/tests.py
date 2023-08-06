from .widget import ColorDatatypeConverter
from .widget import color_builder
from importlib import reload
from node.utils import UNSET
from yafowil.base import ExtractionError
from yafowil.base import factory
from yafowil.tests import YafowilTestCase
import os
import unittest


def np(path):
    return path.replace('/', os.path.sep)


class TestColorWidget(YafowilTestCase):

    def setUp(self):
        super(TestColorWidget, self).setUp()
        from yafowil.widget import color
        from yafowil.widget.color import widget
        reload(widget)
        color.register()

    def test_edit_renderer(self):
        # Render widget
        widget = factory(
            'color',
            name='colorwidget'
        )
        self.checkOutput("""
        <input class="color-picker" data-box_width='250' data-disabled='false'
        data-format='hexString' data-layout_direction='vertical'
        data-open_on_focus='true' data-show_inputs='false'
        data-show_labels='false' data-slider_size='10'
        data-sliders='["box", "h"]' data-temperature='{...}'
        data-user_swatches='true' id="input-colorwidget" name="colorwidget"
        type="text" />
        """, widget())

        # Render with JS config properties
        widget = factory(
            'color',
            name='colorwidget',
            props={
                'color': 'rgba(255, 255, 0, 1)',
                'format': 'rgba',
                'show_inputs': True,
                'show_labels': True,
                'slider_size': 50,
                'layout_direction': 'horizontal',
                'open_on_focus': False
            })
        self.checkOutput("""
        <input class="color-picker" data-box_width='250' data-disabled='false'
        data-format='rgbaString' data-layout_direction='horizontal'
        data-open_on_focus='false' data-show_inputs='true'
        data-show_labels='true' data-slider_size='50'
        data-sliders='["box", "h"]' data-temperature='{...}'
        data-user_swatches='true' id="input-colorwidget" name="colorwidget"
        type="text" />
        """, widget())

    def test_display_renderer(self):
        pass

    def test_color_extractor(self):
        # empty value
        color = UNSET
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'hex',
                'color': UNSET
            })
        data = widget.extract({})
        self.assertEqual(data.value, UNSET)
        # initial value
        color = '#ffffff'
        widget = factory(
            'color',
            name='colorwidget',
            value=color,
            props={
                'format': 'hex',
                'color': color
            })
        data = widget.extract({})
        self.assertEqual(data.value, '#ffffff')
        # unknown format
        color = '#ff0000'
        widget = factory(
            'color',
            name='colorwidget',
            value=color,
            props={
                'format': 'unknown_format_type',
                'color': color
            })
        request = {'colorwidget': 'abc'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Unknown Format. Supported formats: hex, hex8, '
                'hsl, hsla, rgb, rgba, kelvin'
            )]
        )

    def test_color_extractor_hexString(self):
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'hex'
            })
        # not startswith '#'
        request = {'colorwidget': 'ff0000'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors, 
            [ExtractionError(
                'Unknown Format. Supported formats: hex, hex8, '
                'hsl, hsla, rgb, rgba, kelvin'
            )]
        )
        # too short
        request = {'colorwidget': '#ff000'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors, 
            [ExtractionError(
                'Incorrect hex Color String length: string length must be 7'
            )]
        )
        # incorrect hex value
        request = {'colorwidget': '#ffxx00'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                "Incorrect Hex Value: invalid literal for int() with base 16: 'xx'"
            )]
        )

    def test_color_extractor_hex8String(self):
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'hex8'
            })
        # not startswith '#'
        request = {'colorwidget': 'ff000000'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors, 
            [ExtractionError(
                'Unknown Format. Supported formats: hex, hex8, '
                'hsl, hsla, rgb, rgba, kelvin'
            )]
        )
        # too short
        request = {'colorwidget': '#ff0000'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect hex8 Color String length: string length must be 9'
            )]
        )
        # incorrect hex value
        request = {'colorwidget': '#ff00bbxc'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                "Incorrect Hex Value: invalid literal for int() with base 16: 'xc'"
            )]
        )
        # correct hex value
        request = {'colorwidget': '#ff00bbcc'}
        data = widget.extract(request)
        self.assertEqual(data.errors, [])

    def test_color_extractor_hslString(self):
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'hsl'
            })
        # not startswith hsl(
        request = {'colorwidget': 'rgb(360, 122, 122)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                "Incorrect Color String: String must start with 'hsl'"
            )]
        )
        # not endswith )
        request = {'colorwidget': 'hsl(360, 100%, 88%'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError("Incorrect Color String:  Unclosed bracket.")]
        )
        # hsl+alpha string
        request = {'colorwidget': 'hsl(360, 100%, 88%, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: expected format: hsl([0-360], '
                '[0-100]%, [0-100]%)'
            )]
        )
        # Incorrect Hue Value
        request = {'colorwidget': 'hsl(380, 100%, 88%)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for hue must be between 0 and 360.'
            )]
        )
        # Incorrect Saturation Value
        request = {'colorwidget': 'hsl(360, 102%, 88%)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors, 
            [ExtractionError(
                'Incorrect Color String: value for saturation must be between 0 '
                'and 100 followed by "%".'
            )]
        )
        # Incorrect Lightness Value
        request = {'colorwidget': 'hsl(360, 100%, 88)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for lightness must be between 0 '
                'and 100 followed by "%".'
            )]
        )
        # correct value
        request = {'colorwidget': 'hsl(360, 100%, 88%)'}
        data = widget.extract(request)
        self.assertEqual(data.errors, [])

    def test_color_extractor_hslaString(self):
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'hsla'
            })
        # not startswith hsla(
        request = {'colorwidget': 'hsl(360, 122, 122)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                "Incorrect Color String: String must start with 'hsla'"
            )]
        )
        # not endswith )
        request = {'colorwidget': 'hsla(360, 100%, 88%, 0.5'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError('Incorrect Color String:  Unclosed bracket.')]
        )
        # no alpha channel
        request = {'colorwidget': 'hsla(360, 100%, 88%)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: expected format: hsla([0-360], '
                '[0-100]%, [0-100]%, [0-1])'
            )]
        )
        # Incorrect Hue Value
        request = {'colorwidget': 'hsla(380, 100%, 88%, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for hue must be between 0 and 360.'
            )]
        )
        # Incorrect Saturation Value
        request = {'colorwidget': 'hsla(360, 102%, 88%, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for saturation must be between 0 '
                'and 100 followed by "%".'
            )]
        )
        # Incorrect Lightness Value
        request = {'colorwidget': 'hsla(360, 100%, 88, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for lightness must be between 0 '
                'and 100 followed by "%".'
            )]
        )
        # Incorrect Alpha Value
        request = {'colorwidget': 'hsla(360, 100%, 88%, 1.8)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: Alpha value must be between 0 and 1.'
            )]
        )
        # correct value
        request = {'colorwidget': 'hsla(360, 100%, 88%, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(data.errors, [])

    def test_color_extractor_rgbString(self):
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'rgb'
            })
        # not startswith rgb(
        request = {'colorwidget': 'rgba(122, 122, 122)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                "Incorrect Color String: String must start with 'rgb'"
            )]
        )
        # not endswith )
        request = {'colorwidget': 'rgb(122, 122, 122'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError('Incorrect Color String: Unclosed bracket.')]
        )
        # alpha channel
        request = {'colorwidget': 'rgb(122, 122, 122, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: expected format: rgb([0-255], [0-255], '
                '[0-255])'
            )]
        )
        # Incorrect Red Channel Value
        request = {'colorwidget': 'rgb(-1, 122, 122)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for red must be between 0 and 255.'
            )]
        )
        # Incorrect Green Channel Value
        request = {'colorwidget': 'rgb(122, 300, 122)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for green must be between 0 and 255.'
            ,)]
        )
        # Incorrect Blue Channel Value
        request = {'colorwidget': 'rgb(122, 122, 300)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for blue must be between 0 and 255.'
            )]
        )
        # correct value
        request = {'colorwidget': 'rgb(255, 255, 255)'}
        data = widget.extract(request)
        self.assertEqual(data.errors, [])

    def test_color_extractor_rgbaString(self):
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'rgba'
            })
        # not startswith rgba(
        request = {'colorwidget': 'rgb(122, 122, 122, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                "Incorrect Color String: String must start with 'rgba'"
            )]
        )
        # not endswith )
        request = {'colorwidget': 'rgba(122, 122, 122, 0.5'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError('Incorrect Color String: Unclosed bracket.')]
        )
        # no alpha channel
        request = {'colorwidget': 'rgba(122, 122, 122)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: expected format: '
                'rgba([0-255], [0-255], [0-255], [0-1])'
            )]
        )
        # Incorrect Red Channel Value
        request = {'colorwidget': 'rgba(-1, 122, 122, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for red must be between 0 and 255.'
            )]
        )
        # Incorrect Green Channel Value
        request = {'colorwidget': 'rgba(122, 300, 122, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for green must be between 0 and 255.'
            )]
        )
        # Incorrect Blue Channel Value
        request = {'colorwidget': 'rgba(122, 122, 300, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: value for blue must be between 0 and 255.'
            )]
        )
        # Incorrect Alpha Channel Value
        request = {'colorwidget': 'rgba(122, 122, 122, 1.5)'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Incorrect Color String: Alpha value must be between 0 and 1.'
            )]
        )
        # correct value
        request = {'colorwidget': 'rgba(255, 255, 255, 0.5)'}
        data = widget.extract(request)
        self.assertEqual(data.errors, [])

    def test_color_extractor_kelvin(self):
        widget = factory(
            'color',
            name='colorwidget',
            value=UNSET,
            props={
                'format': 'kelvin'
            })
        # not a number / convertable string
        request = {'colorwidget': '4000K'}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError(
                'Unknown Format, expected format: int(1000 - 40000) or '
                'str(1000 - 40000)'
            )]
        )
        # Temperature not in range
        request = {'colorwidget': 80000}
        data = widget.extract(request)
        self.assertEqual(
            data.errors,
            [ExtractionError('Kelvin Temperature out of range (1000-40000)')]
        )
        # number / convertable string
        request = {'colorwidget': '4000'}
        data = widget.extract(request)
        self.assertEqual(data.errors, [])
        request = {'colorwidget': 4000}
        data = widget.extract(request)
        self.assertEqual(data.errors, [])

    def test_color_convertor_to_value_hexString(self):
        convertor = ColorDatatypeConverter()
        convertor.type_ = str
        # hexString
        convertor.format = 'hex'
        res = convertor.to_value('#ff0000')
        self.assertEqual(res, '#ff0000')
        # hex8String
        convertor.format = 'hex8'
        res = convertor.to_value('#66000000')
        self.assertEqual(res, '#66000000')
        # unsupported type
        val = {'foo': 'bar'}
        self.assertRaises(TypeError, convertor.to_value, val)

    def test_color_convertor_to_value_rgb_rgba(self):
        convertor = ColorDatatypeConverter()
        convertor.type_ = list
        # rgbaString
        convertor.format = 'rgba'
        res = convertor.to_value('rgba(255, 255, 0, 0.5)')
        self.assertEqual(res, [255, 255, 0, 0.5])
        # rgbaString to tuple
        convertor.type_ = tuple
        res = convertor.to_value('rgba(255, 255, 0, 0.5)')
        self.assertEqual(res, (255, 255, 0, 0.5))
        # rgbaString 0-1
        convertor.range = '0-1'
        res = convertor.to_value('rgba(255, 255, 0, 0.5)')
        self.assertEqual(res, (1, 1, 0, 0.5))
        # rgbString
        convertor.format = 'rgb'
        convertor.type_ = list
        convertor.range = 'default'
        res = convertor.to_value('rgb(125, 125, 5)')
        self.assertEqual(res, [125, 125, 5])
        # rgbString 0-1
        convertor.range = '0-1'
        res = convertor.to_value('rgb(125, 125, 5)')
        self.assertEqual(round(res[0], 2), 0.49)
        self.assertEqual(round(res[1], 2), 0.49)
        self.assertEqual(round(res[2], 2), 0.02)

    def test_color_convertor_to_value_hsl_hsla(self):
        convertor = ColorDatatypeConverter()
        convertor.type_ = list
        # hslString
        convertor.format = 'hsl'
        convertor.range = 'default'
        res = convertor.to_value('hsl(360, 100, 50)')
        self.assertEqual(res, [360, 100, 50])
        convertor.range = '0-1'
        res = convertor.to_value('hsl(360, 100, 50)')
        self.assertEqual(res, [1, 1, 0.5])
        # hslaString
        convertor.format = 'hsla'
        convertor.range = 'default'
        res = convertor.to_value('hsla(360, 100, 50, 0.3)')
        self.assertEqual(res, [360, 100, 50, 0.3])
        convertor.range = '0-1'
        res = convertor.to_value('hsla(360, 100, 50, 0.3)')
        self.assertEqual(res, [1, 1, 0.5, 0.3])

    def test_color_convertor_to_value_kelvin(self):
        convertor = ColorDatatypeConverter()
        # int to str
        convertor.type_ = str
        convertor.format = 'kelvin'
        res = convertor.to_value(4500)
        self.assertEqual(res, '4500')
        # str to str
        convertor.format = 'kelvin'
        res = convertor.to_value('8000')
        self.assertEqual(res, '8000')
        # int to int
        convertor.type_ = int
        convertor.format = 'kelvin'
        res = convertor.to_value(4500)
        self.assertEqual(res, 4500)
        # str to int
        convertor.format = 'kelvin'
        res = convertor.to_value('2000')
        self.assertEqual(res, 2000)

    def test_color_convertor_to_form_hexString(self):
        convertor = ColorDatatypeConverter()
        # not in accepted formats
        convertor.format = 'someString'
        self.assertRaises(TypeError, convertor.to_form, '')
        # type None
        convertor.format = 'hex'
        res = convertor.to_form(None)
        self.assertEqual(res, None)
        # hexString
        res = convertor.to_form('#ff0000')
        self.assertEqual(res, '#ff0000')

    def test_color_convertor_to_form_unsupported_types(self):
        convertor = ColorDatatypeConverter()
        convertor.format = 'hex'
        # unsupported value type
        self.assertRaises(ValueError, convertor.to_form, {'a': 'b'})
        # hexString to tuple
        convertor.type_ = tuple
        convertor.format = 'hex'
        self.assertRaises(ValueError, convertor.to_form, (100, 100, 50))
        # hex8String to tuple
        convertor.format = 'hex8'
        self.assertRaises(ValueError, convertor.to_form, (100, 100, 50))
        # kelvin to tuple
        convertor.format = 'kelvin'
        self.assertRaises(ValueError, convertor.to_form, (100, 100, 50))

    def test_color_convertor_to_form_rgb_rgba(self):
        convertor = ColorDatatypeConverter()

        # to tuple - range default correct
        convertor.format = 'rgb'
        res = convertor.to_form((255, 255, 0))
        self.assertEqual(res, 'rgb(255, 255, 0)')
        # to tuple - range default incorrect
        self.assertRaises(ValueError, convertor.to_form, (360, 255, 0.5))
        self.assertEqual(res, 'rgb(255, 255, 0)')
        # to tuple - range 0-1 correct
        convertor.range = '0-1'
        res = convertor.to_form((0, 1, 0))
        self.assertEqual(res, 'rgb(0, 255, 0)')
        # to tuple - range 0-1 incorrect
        self.assertRaises(ValueError, convertor.to_form, (0, 22, 1))
        # wrong length
        convertor.range = 'default'
        self.assertRaises(ValueError, convertor.to_form, (255, 255, 255, 1))

        # rgbaString - range default correct
        convertor.format = 'rgba'
        res = convertor.to_form((255, 255, 0, 1))
        self.assertEqual(res, 'rgba(255, 255, 0, 1)')
        # rgbaString - range default incorrect
        convertor.format = 'rgba'
        self.assertRaises(ValueError, convertor.to_form, (255, 255, 0, 5))
        self.assertRaises(ValueError, convertor.to_form, (300, 255, 0, 1))
        # to tuple - range 0-1 correct
        convertor.range = '0-1'
        res = convertor.to_form((0, 1, 0, 0.5))
        self.assertEqual(res, 'rgba(0, 255, 0, 0.5)')
        # to tuple - range 0-1 incorrect
        self.assertRaises(ValueError, convertor.to_form, (0, 22, 1, 1))
        # wrong length
        convertor.range = 'default'
        self.assertRaises(ValueError, convertor.to_form, (255, 255, 255))

    def test_color_convertor_to_form_hsl_hsla(self):
        convertor = ColorDatatypeConverter()

        # to tuple - range default correct
        convertor.format = 'hsl'
        res = convertor.to_form((360, 100, 0))
        self.assertEqual(res, 'hsl(360, 100%, 0%)')
        # to tuple - range default incorrect
        self.assertRaises(ValueError, convertor.to_form, (360, 255, 0.5))
        self.assertRaises(ValueError, convertor.to_form, (500, 100, 0.5))
        # to tuple - range 0-1 correct
        convertor.range = '0-1'
        res = convertor.to_form((0, 1, 0))
        self.assertEqual(res, 'hsl(0, 100%, 0%)')
        # to tuple - range 0-1 incorrect
        self.assertRaises(ValueError, convertor.to_form, (0, 22, 1))
        # wrong length
        convertor.range = 'default'
        self.assertRaises(ValueError, convertor.to_form, (360, 50, 50, 1))

        # to tuple - range default correct
        convertor.format = 'hsla'
        res = convertor.to_form((360, 100, 0, 0.5))
        self.assertEqual(res, 'hsla(360, 100%, 0%, 0.5)')
        # to tuple - range default incorrect
        self.assertRaises(ValueError, convertor.to_form, (361, 100, 100, 0.5))
        self.assertRaises(ValueError, convertor.to_form, (360, 500, 100, 0.5))
        self.assertRaises(ValueError, convertor.to_form, (360, 50, 500, 0.5))
        self.assertRaises(ValueError, convertor.to_form, (360, 50, 50, -1))
        # to tuple - range 0-1 correct
        convertor.range = '0-1'
        res = convertor.to_form((0, 1, 0, 0.3))
        self.assertEqual(res, 'hsla(0, 100%, 0%, 0.3)')
        # to tuple - range 0-1 incorrect
        self.assertRaises(ValueError, convertor.to_form, (0, 22, 1, 0.3))
        # wrong length
        convertor.range = 'default'
        self.assertRaises(ValueError, convertor.to_form, (360, 50, 50))

    def test_color_convertor_to_form_kelvin(self):
        convertor = ColorDatatypeConverter()
        # wrong format
        convertor.format = 'rgba'
        self.assertRaises(ValueError, convertor.to_form, 3500)
        # correct format
        convertor.format = 'kelvin'
        res = convertor.to_form(3000)
        self.assertEqual(res, 3000)

    def test_color_builder(self):
        class MockWidget:
            attrs = {
                'format': 'rgb',
                'datatype': tuple,
                'datatype_range': 'default'
            }
        widget = MockWidget
        color_builder(widget, None)
        datatype = widget.attrs['datatype']
        # XXX: compare class names. Does not work due to import
        self.assertEqual(datatype.type_, tuple)
        self.assertEqual(datatype.format, 'rgb')
        self.assertEqual(datatype.range, 'default')
        # not supported format for datatype tuple
        widget.attrs['format'] = 'hex'
        widget.attrs['datatype'] = tuple
        self.assertRaises(ValueError, color_builder, widget, None)
        # datatype int, format not kelvin
        widget.attrs['datatype'] = int
        self.assertRaises(ValueError, color_builder, widget, None)
        # not supported datatype
        widget.attrs['format'] = 'hex'
        widget.attrs['datatype'] = object
        self.assertRaises(ValueError, color_builder, widget, None)

    def test_resources(self):
        factory.theme = 'default'
        resources = factory.get_resources('yafowil.widget.color')
        self.assertTrue(resources.directory.endswith(np('/color/resources')))
        self.assertEqual(resources.name, 'yafowil.widget.color')
        self.assertEqual(resources.path, 'yafowil-color')

        scripts = resources.scripts
        self.assertEqual(len(scripts), 2)

        self.assertTrue(
            scripts[0].directory.endswith(np('/color/resources/iro'))
        )
        self.assertEqual(scripts[0].path, 'yafowil-color/iro')
        self.assertEqual(scripts[0].file_name, 'iro.min.js')
        self.assertTrue(os.path.exists(scripts[0].file_path))

        self.assertTrue(scripts[1].directory.endswith(np('/color/resources')))
        self.assertEqual(scripts[1].path, 'yafowil-color')
        self.assertEqual(scripts[1].file_name, 'widget.min.js')
        self.assertTrue(os.path.exists(scripts[1].file_path))

        styles = resources.styles
        self.assertEqual(len(styles), 1)

        self.assertTrue(styles[0].directory.endswith(np('/color/resources')))
        self.assertEqual(styles[0].path, 'yafowil-color')
        self.assertEqual(styles[0].file_name, 'widget.css')
        self.assertTrue(os.path.exists(styles[0].file_path))


if __name__ == '__main__':
    unittest.main()
