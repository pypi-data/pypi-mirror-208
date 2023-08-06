# -*- coding: utf-8 -*-
from yafowil.base import ExtractionError
from yafowil.base import factory
from yafowil.common import generic_extractor
from yafowil.common import generic_required_extractor
from yafowil.common import input_attributes_common
from yafowil.datatypes import DatatypeConverter
from yafowil.datatypes import generic_emptyvalue_extractor
from yafowil.tsf import TSF
from yafowil.utils import attr_value
from yafowil.utils import data_attrs_helper
from yafowil.utils import managedprops


_ = TSF('yafowil.widget.color')


class ColorDatatypeConverter(DatatypeConverter):
    """Datatype Converter for Color Formats."""

    def __init__(self, type_=None, format=None, range='default'):
        self.type_ = type_
        self.format = format
        self.range = range

    def to_value(self, value):
        if isinstance(value, str):
            # XXX: more checks if value is correct type
            if self.type_ == str:
                return value
            elif self.type_ == int and self.format == 'kelvin':
                return int(value)
            elif self.type_ in [list, tuple]:
                if self.format == 'rgba':
                    value = value[5:-1].split(', ')
                    value[0] = int(value[0])
                    value[1] = int(value[1])
                    value[2] = int(value[2])
                    value[3] = float(value[3])
                    if self.range == '0-1':
                        value[0] = value[0] / 255
                        value[1] = value[1] / 255
                        value[2] = value[2] / 255
                elif self.format == 'rgb':
                    if self.type_ in [list, tuple]:
                        value = value[4:-1].split(', ')
                        if self.range == '0-1':
                            value = [int(channel) / 255 for channel in value]
                        else:
                            value = [int(channel) for channel in value]
                elif self.format == 'hsl':
                    if self.type_ in [list, tuple]:
                        value = value[4:-1].replace('%', '').split(', ')
                        value = [int(channel) for channel in value]
                        if self.range == '0-1':
                            value[0] = value[0] / 360
                            value[1] = value[1] / 100
                            value[2] = value[2] / 100
                elif self.format == 'hsla':
                    if self.type_ in [list, tuple]:
                        value = value[5:-1].replace('%', '').split(', ')
                        value[0] = int(value[0])
                        value[1] = int(value[1])
                        value[2] = int(value[2])
                        value[3] = float(value[3])
                        if self.range == '0-1':
                            value[0] = value[0] / 360
                            value[1] = value[1] / 100
                            value[2] = value[2] / 100
            if isinstance(value, list) and self.type_ == tuple:
                return tuple(value)
            return value
        elif isinstance(value, int) and self.format == 'kelvin':
            if self.type_ == int:
                return value
            return str(value)
        else:
            raise TypeError(
                'Not supported type: {}'
                .format(type(value).__name__)
            )

    def to_form(self, value):
        type_name = type(value).__name__
        accepted_formats = [
            'hex',
            'hex8',
            'hsl',
            'hsla',
            'rgb',
            'rgba',
            'kelvin'
        ]

        if not self.format in accepted_formats:
            raise TypeError(
                'Not supported format: {}'.format(self.format)
            )
        if not value:
            return value
        if isinstance(value, (tuple, list)):
            length = len(value)

            if isinstance(value, tuple):
                value = list(value)

            if self.format == 'rgba':
                if length != 4:
                    raise ValueError(
                        '{} must contain 4 items, contains: {}'
                        .format(type_name, length)
                    )
                for item in value:
                    index = value.index(item)
                    if self.range == '0-1' and index < 3:
                        if item < 0 or item > 1:
                            raise ValueError((
                                'Value out of bounds at index {}. '
                                '0-1 expected value between 0 and 1, value is: {}'
                            ).format(index, item))
                        value[index] = item * 255
                    elif value.index(item) == 3:
                        if item < 0 or item > 1:
                            raise ValueError((
                                'Value out of bounds at index {}. '
                                'Expected value between 0 and 1, value is: {}'
                            ).format(value.index(item), item))
                    elif item < 0 or item > 255:
                        raise ValueError((
                            'Value out of bounds at index {}. '
                            'Expected value between 0 and 255, value is: {}'
                        ).format(value.index(item), item))
                return 'rgba({}, {}, {}, {})'.format(
                    value[0],
                    value[1],
                    value[2],
                    value[3]
                )
            elif self.format == 'rgb':
                if length != 3:
                    raise ValueError(
                        '{} must contain 3 items, contains: {}'
                        .format(type_name, length)
                    )
                for item in value:
                    index = value.index(item)
                    if self.range == '0-1':
                        if item < 0 or item > 1:
                            raise ValueError((
                                'Value out of bounds at index {}. '
                                '0-1 expected value between 0 and 1, value is: {}'
                            ).format(value.index(item), item))
                        value[index] = item * 255
                    elif item < 0 or item > 255:
                        raise ValueError((
                            'Value out of bounds at index {}. '
                            'Expected value between 0 and 255, value is: {}'
                        ).format(value.index(item), item))
                return 'rgb({}, {}, {})'.format(value[0], value[1], value[2])
            elif self.format == 'hsl':
                if length != 3:
                    raise ValueError(
                        '{} must contain 3 items, contains: {}'
                        .format(type_name, length)
                    )
                for item in value:
                    index = value.index(item)
                    if self.range == '0-1':
                        if item < 0 or item > 1:
                            raise ValueError((
                                'Value out of bounds at index {}. '
                                '0-1 expected value between 0 and 1, value is: {}'
                            ).format(value.index(item), item))
                        if index == 0:
                            value[index] = item * 360
                        else:
                            value[index] = item * 100
                    if index == 0 and item < 0 or item > 360:
                        raise ValueError((
                            'Value out of bounds at index {}. '
                            'Expected Hue value between 0 and 360, value is: {}'
                        ).format(index, item))
                    if (index == 1 or index == 2) and (item < 0 or item > 100):
                        raise ValueError((
                            'Value out of bounds at index {}. '
                            'Expected value between 0 and 100, value is: {}'
                        ).format(index, item))
                return 'hsl({}, {}%, {}%)'.format(value[0], value[1], value[2])
            elif self.format == 'hsla':
                if length != 4:
                    raise ValueError(
                        '{} must contain 4 items, contains: {}'
                        .format(type_name, length)
                    )
                for item in value:
                    index = value.index(item)
                    if self.range == '0-1':
                        if item < 0 or item > 1:
                            raise ValueError((
                                'Value out of bounds at index {}. '
                                '0-1 expected value between 0 and 1, value is: {}'
                            ).format(value.index(item), item))
                        if index == 0:
                            value[index] = item * 360
                        elif index < 3:
                            value[index] = item * 100
                    if index == 0 and (item < 0 or item > 360):
                        raise ValueError((
                            'Value out of bounds at index {}. '
                            'Expected Hue value between 0 and 360, value is: {}'
                        ).format(index, item))
                    if index == 1 and (item < 0 or item > 100):
                        raise ValueError((
                            'Value out of bounds at index {}. '
                            'Expected Saturation value between 0 and 100, value is: {}'
                        ).format(index, item))
                    if index == 2 and (item < 0 or item > 100):
                        raise ValueError((
                            'Value out of bounds at index {}. '
                            'Expected Lightness value between 0 and 100, value is: {}'
                        ).format(index, item))
                    if index == 3 and (item < 0 or item > 1):
                        raise ValueError(
                            'Value out of bounds at index {}. '
                             'Expected Alpha value between 0 and 1, value is: {}'
                             .format(index, item)
                        )
                return 'hsla({}, {}%, {}%, {})'.format(
                    value[0],
                    value[1],
                    value[2],
                    value[3]
                )
            elif self.format == 'hex' or self.format == 'hex8':
                raise ValueError(
                    'Format {} does not accept type {}, accepted type: string'
                     .format(self.format, type_name)
                )
            elif self.format == 'kelvin':
                raise ValueError(
                    'Format {} does not accept type {}, accepted type: string | number'
                     .format(self.format, type_name)
                )
        elif isinstance(value, str):
            return value
        elif isinstance(value, int):
            if self.format == 'kelvin':
                return value
            else:
                raise ValueError(
                    'Format {} does not accept type {}, accepted type: string'
                     .format(self.format, type_name)
                )
        else:
            raise ValueError(
                'Unsupported value type: {}'
                 .format(type_name)
            )


def color_builder(widget, factory):
    datatype = widget.attrs['datatype']
    if not datatype:
        return
    format = widget.attrs['format']
    range_ = widget.attrs['datatype_range']
    if datatype in [tuple, list]:
        if not format in ['rgb', 'rgba', 'hsl', 'hsla']:
            raise ValueError(
                'Format {} does not support datatype {}' \
                .format(format, datatype.__name__)
            )
    elif datatype == int:
        if format != 'kelvin':
            raise ValueError(
                'Format {} does not support datatype {}' \
                .format(format, datatype.__name__)
            )
    elif datatype != str:
        raise ValueError(
            'Not supported value datatype: {}' \
            .format(datatype.__name__)
        )
    widget.attrs['datatype'] = ColorDatatypeConverter(datatype, format, range_)


@managedprops('format', 'datatype')
def color_extractor(widget, data):
    extracted = data.extracted
    if not extracted:
        return extracted
    format = attr_value('format', widget, data)
    formats = ', '.join(
        [
            'hex',
            'hex8',
            'hsl',
            'hsla',
            'rgb',
            'rgba',
            'kelvin'
        ]
    )

    # hex
    if format == 'hex' or format == 'hex8':
        if (not extracted.startswith('#')):
            msg = _(
                'unknown_color_format',
                default='Unknown Format. Supported formats: ${formats}',
                mapping={'formats':formats}
            )
            raise ExtractionError(msg)
        elif format == 'hex' and len(extracted) != 7:
            msg = _(
                'incorrect_hex_length',
                default='Incorrect hex Color String length: string length must be 7'
            )
            raise ExtractionError(msg)
        elif format == 'hex8' and len(extracted) != 9:
            msg = _(
                'incorrect_hex8_length',
                default='Incorrect hex8 Color String length: string length must be 9'
            )
            raise ExtractionError(msg)
        color = extracted[1:]
        r = color[0:2]
        g = color[2:4]
        b = color[4:6]
        if format == 'hex8':
            a = color[6:8]
        try:
            r = int(r, 16)
            g = int(g, 16)
            b = int(b, 16)
            if format == 'hex8':
                a = int(a, 16)
        except Exception as e:
            args = ', '.join(e.args)
            msg = _(
                'incorrect_hex_value',
                default='Incorrect Hex Value: ${args}',
                mapping={'args':args}
            )
            raise ExtractionError(msg)
    # hsl
    elif format == 'hsl' or format == 'hsla':
        hsl_format = 'hsl([0-360], [0-100]%, [0-100]%)'
        hsla_format = 'hsla([0-360], [0-100]%, [0-100]%, [0-1])'

        if not extracted.endswith(')'):
            raise ExtractionError(_(
                'unclosed_brace',
                default='Incorrect Color String:  Unclosed bracket.'
            ))
        elif format == 'hsl' and not extracted.startswith('hsl('):
            raise ExtractionError(_(
                'hsl_str_start',
                default="Incorrect Color String: String must start with 'hsl'"
            ))
        elif format == 'hsla' and not extracted.startswith('hsla('):
            raise ExtractionError(_(
                'hsla_str_start',
                default="Incorrect Color String: String must start with 'hsla'"
            ))
        length = 3 if format == 'hsl' else 4
        color = extracted[length + 1:-1]
        color = [channel.strip() for channel in color.split(',')]

        if format == 'hsl' and len(color) != 3:
            raise ExtractionError(_(
                'hsl_str_length',
                default='Incorrect Color String: expected format: ${hsl_format}',
                mapping={'hsl_format':hsl_format}
            ))
        if format == 'hsla' and len(color) != 4:
            raise ExtractionError(_(
                'hsla_str_length',
                default='Incorrect Color String: expected format: ${hsla_format}',
                mapping={'hsla_format':hsla_format}
            ))

        h = color[0]
        s = color[1]
        l = color[2]
        a = color[3] if format == 'hsla' else False

        if int(h) < 0 or int(h) > 360:
            raise ExtractionError(_(
                'incorrect_hue_value',
                default=(
                    'Incorrect Color String: value for hue must be between 0 and 360.'
                )
            ))
        elif not s.endswith('%') or int(s[0:-1]) not in range(0, 101):
            raise ExtractionError(_(
                'incorrect_saturation_value',
                default=(
                    'Incorrect Color String: value for saturation must be '
                    'between 0 and 100 followed by "%".'
                )
            ))
        elif not l.endswith('%') or int(l[0:-1]) not in range(0, 101):
            raise ExtractionError(_(
                'incorrect_lightness_value',
                default=(
                    'Incorrect Color String: value for lightness must be '
                    'between 0 and 100 followed by "%".'
                )
            ))
        elif a and float(a) < 0 or float(a) > 1:
            raise ExtractionError(_(
                'incorrect_alpha_value',
                default='Incorrect Color String: Alpha value must be between 0 and 1.'
            ))
    # rgb
    elif format == 'rgb' or format == 'rgba':
        rgb_format = 'rgb([0-255], [0-255], [0-255])'
        rgba_format = 'rgba([0-255], [0-255], [0-255], [0-1])'

        if not extracted.endswith(')'):
            raise ExtractionError(_(
                'unclosed_brace',
                default='Incorrect Color String: Unclosed bracket.'
            ))
        elif format == 'rgb' and not extracted.startswith('rgb('):
            raise ExtractionError(_(
                'rgb_str_start',
                default="Incorrect Color String: String must start with 'rgb'"
            ))
        elif format == 'rgba' and not extracted.startswith('rgba('):
            raise ExtractionError(_(
                'rgba_str_start',
                default="Incorrect Color String: String must start with 'rgba'"
            ))
        length = 3 if format == 'rgb' else 4
        color = extracted[length + 1:-1]
        color = [channel.strip() for channel in color.split(',')]

        if format == 'rgb' and len(color) != 3:
            raise ExtractionError(_(
                'rgb_str_length',
                default='Incorrect Color String: expected format: ${rgb_format}',
                mapping={'rgb_format':rgb_format}
            ))
        elif format == 'rgba' and len(color) != 4:
            raise ExtractionError(_(
                'rgba_str_length',
                default='Incorrect Color String: expected format: ${rgba_format}',
                mapping={'rgba_format':rgba_format}
            ))
        r = color[0]
        g = color[1]
        b = color[2]
        a = color[3] if format == 'rgba' else False

        if int(r) < 0 or int(r) > 255:
            raise ExtractionError(_(
                'incorrect_red_value',
                default='Incorrect Color String: value for red must be between 0 and 255.'
            ))
        elif int(g) < 0 or int(g) > 255:
            raise ExtractionError(_(
                'incorrect_green_value',
                default='Incorrect Color String: value for green must be between 0 and 255.'
            ))
        elif int(b) < 0 or int(b) > 255:
            raise ExtractionError(_(
                'incorrect_blue_value',
                default='Incorrect Color String: value for blue must be between 0 and 255.'
            ))
        elif a and float(a) < 0 or float(a) > 1:
            raise ExtractionError(_(
                'incorrect_alpha_value',
                default='Incorrect Color String: Alpha value must be between 0 and 1.'
            ))
    # kelvin
    elif format == 'kelvin':
        try:
            color = int(extracted)
        except ValueError:
            raise ExtractionError(_(
                'incorrect_kelvin_format',
                default='Unknown Format, expected format: int(1000 - 40000) or str(1000 - 40000)'
            ))
        if color < 1000 or color > 40000:
            raise ExtractionError(_(
                'incorrect_kelvin_number',
                default='Kelvin Temperature out of range (1000-40000)'
            ))
    # other
    else:
        raise ExtractionError(_(
            'unknown_color_format',
            default='Unknown Format. Supported formats: ${formats}',
            mapping={'formats':formats}
        ))

    converter = widget.attrs['datatype']
    if converter:
        extracted = converter.to_value(extracted)
    return extracted


color_options = [
    'preview_elem',
    'sliders',
    'box_width',
    'box_height',
    'slider_size',
    'locked_swatches',
    'user_swatches',
    'temperature',
    'format',
    'disabled',
    'show_inputs',
    'show_labels',
    'slider_length',
    'layout_direction',
    'open_on_focus'
]


format_mapping = {
    'hex': 'hexString',
    'hex8': 'hex8String',
    'hsl': 'hslString',
    'hsla': 'hslaString',
    'rgb': 'rgbString',
    'rgba': 'rgbaString',
    'kelvin': 'kelvin'
}


@managedprops(*color_options)
def color_edit_renderer(widget, data):
    input_attrs = input_attributes_common(widget, data)
    custom_attrs = data_attrs_helper(widget, data, color_options)
    format = custom_attrs['data-format']
    custom_attrs['data-format'] = format_mapping[format]
    input_attrs.update(custom_attrs)
    input_attrs['type'] = 'text'
    input_attrs['data-color'] = input_attrs['value']
    return data.tag('input', **input_attrs)


def color_display_renderer(widget, data):
    pass


factory.register(
    'color',
    extractors=[
        generic_extractor,
        generic_required_extractor,
        generic_emptyvalue_extractor,
        color_extractor
    ],
    edit_renderers=[
        color_edit_renderer
    ],
    display_renderers=[
        color_display_renderer
    ],
    builders=[color_builder]
)


factory.doc['blueprint']['color'] = """\
Add-on blueprint
`yafowil.widget.color <http://github.com/conestack/yafowil.widget.color/>`_ .
"""

factory.defaults['color.class'] = 'color-picker'
factory.doc['props']['color.class'] = """\
CSS classes for color widget wrapper DOM element.
"""

factory.doc['props']['color.emptyvalue'] = """\
If color value empty, return as extracted value.
"""

factory.defaults['color.format'] = 'hex'
factory.doc['props']['color.format'] = """\
Specify the output format of the color picker color.
Values: [Str].

Available options:
- hex
- hex8
- hsl
- hsla
- rgb
- rgba
- kelvin
"""

factory.defaults['color.preview_elem'] = None
factory.doc['props']['color.preview_elem'] = """\
Add an optional preview elem.
Values: [True|False|None (default)].
"""

factory.defaults['color.box_width'] = 250
factory.doc['props']['color.box_width'] = """\
Set the initial width of the color box (in pixels).
Values: [px].
"""

factory.defaults['color.box_height'] = None
factory.doc['props']['color.box_height'] = """\
Set the initial height of the color box (in pixels).
Values: [px].
"""

factory.defaults['color.sliders'] = ['box', 'h']
factory.doc['props']['color.sliders'] = """\
Add additional sliders to layout.
Values: [List(Str)|None].

Available options:
- box
- r (red)
- g (green)
- b (blue)
- h (hue)
- s (saturation)
- v (value)
- a (alpha)
- k (kelvin)
"""

factory.defaults['color.slider_size'] = 10
factory.doc['props']['color.slider_size'] = """\
Set the height of slider elements (in pixels).
Values: [px].
"""

factory.defaults['color.locked_swatches'] = None
factory.doc['props']['color.locked_swatches'] = """\
Swatches to be initialized.
Given swatches can't be deleted in the widget.
Values: [Array(Dict)].
"""

factory.defaults['color.user_swatches'] = True
factory.doc['props']['color.user_swatches'] = """\
Flag whether the user can add and remove swatches.
Values: [Array(Dict)].
"""

factory.defaults['color.temperature'] = {'min': 2000, 'max': 12000}
factory.doc['props']['color.temperature'] = """\
Set the minimum and maximum kelvin temperature.
Values: [Dict('min': 2200-11000, 'max': 2200-11000)].
"""

factory.defaults['color.disabled'] = False
factory.doc['props']['color.disabled'] = """\
Disable or enable input field editing.
Values: [True | False].
"""

factory.defaults['color.show_inputs'] = False
factory.doc['props']['color.show_inputs'] = """\
Show or hide slider input elements.
Values: [True|False(Default)].
"""

factory.defaults['color.show_labels'] = False
factory.doc['props']['color.show_labels'] = """\
Show or hide slider label elements.
Values: [True|False(Default)].
"""

factory.defaults['color.slider_length'] = None
factory.doc['props']['color.slider_length'] = """\
Slider length prop
Values: [True|False(Default)].
"""

factory.defaults['color.layout_direction'] = 'vertical'
factory.doc['props']['color.layout_direction'] = """\
Direction of the entire layout.
Values: ['vertical'|'horizontal'].
"""

factory.defaults['color.open_on_focus'] = True
factory.doc['props']['color.open_on_focus'] = """\
Flag whether the picker dropdown opens on input focus.
Values: [True | False].
"""

factory.defaults['color.datatype'] = None
factory.doc['props']['color.datatype'] = """\
Datatype for extraction.
Values: [str|int|tuple|list].
"""

factory.defaults['color.datatype_range'] = 'default'
factory.doc['props']['color.datatype'] = """\
Datatype range for extraction.
'default': default number range for given format
'0-1': range 0 - 1
Values: ['default'|'0-1'].
"""
