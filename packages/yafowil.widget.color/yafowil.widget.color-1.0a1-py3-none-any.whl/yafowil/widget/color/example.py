# -*- coding: utf-8 -*-
from yafowil.base import factory


DOC_COLOR = """
Color widget
------------

This is the default hex color picker widget.

.. code-block:: python

    color = factory('color', name='colorwidget')
"""


def default_example():
    part = factory(u'fieldset', name='yafowil.widget.color.default')
    part['color'] = factory(
        '#field:color',
        props={
            'label': 'Default Color Picker'
        })
    return {
        'widget': part,
        'doc': DOC_COLOR,
        'title': 'Default Color Picker'
    }


DOC_WHEEL = """
Color Wheel
-----------

Instead of a box, the color widget can also be initialized with a color wheel.

Passing both 'box' and 'wheel' allows the user to switch between components.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        props={
            'label': 'Picker with wheel',
            'sliders': ['wheel', 'box', 'v']
        }
    )
"""


def wheel_example():
    part = factory(u'fieldset', name='yafowil.widget.color.wheel')
    part['color'] = factory(
        '#field:color',
        props={
            'label': 'Picker with wheel',
            'sliders': ['wheel', 'box', 'v']
        })
    return {
        'widget': part,
        'doc': DOC_WHEEL,
        'title': 'Color wheel'
    }


DOC_DIM = """
Custom dimensions
-----------------

Initialize the widget color box or wheel with custom dimensions.
The 'box_width' and 'box_height' properties change the width and height of
the color picker box, respectively.
Setting only one value on a box component produces a square color picker.

All values are defined in pixels.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        props={
            'label': 'Picker with custom dimensions',
            'box_width': 400,
            'box_height': 100
        }
    )
"""


def dim_example():
    part = factory(u'fieldset', name='yafowil.widget.color.dimensions')
    part['color'] = factory(
        '#field:color',
        props={
            'label': 'Picker with custom dimensions',
            'box_width': 400,
            'box_height': 100
        })
    return {
        'widget': part,
        'doc': DOC_DIM,
        'title': 'Custom dimensions'
    }


DOC_LENGTH = """
Slider dimensions
-----------------

'slider_size' defines the thickness of the slider, while 'slider_length'
defines the length of the entire slider.

All values are defined in pixels.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        props={
            'label': 'Sliders with custom length',
            'box_width': 200,
            'sliders': ['box', 'h', 'a'],
            'slider_size': 20,
            'slider_length': 100
        }
    )
"""


def length_example():
    part = factory(u'fieldset', name='yafowil.widget.color.length')
    part['color'] = factory(
        '#field:color',
        props={
            'label': 'Sliders with custom length',
            'box_width': 200,
            'sliders': ['box', 'h', 'a'],
            'slider_size': 20,
            'slider_length': 100
        })
    return {
        'widget': part,
        'doc': DOC_LENGTH,
        'title': 'Slider length'
    }


DOC_LAYOUT = """
Horizontal Layout
-----------------

The color picker can be initalized with horizontal layout direction
by setting 'layout_direction' to 'horizontal'.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        props={
            'label': 'Horizontal Layout',
            'sliders': ['wheel', 's', 'v', 'a'],
            'layout_direction': 'horizontal',
            'show_inputs': True,
            'show_labels': True,
            'locked_swatches': False
        }
    )
"""


def layout_example():
    part = factory(u'fieldset', name='yafowil.widget.color.horizontal')
    part['color'] = factory(
        '#field:color',
        props={
            'label': 'Horizontal Layout',
            'sliders': ['wheel', 's', 'v', 'a'],
            'layout_direction': 'horizontal',
            'show_inputs': True,
            'show_labels': True,
            'locked_swatches': False
        })
    return {
        'widget': part,
        'doc': DOC_LAYOUT,
        'title': 'Horizontal Layout'
    }


DOC_PREVIEW = """
Custom preview elements
-----------------------

Add your own optional preview element by adding a HTML string in the
'preview_elem' option.

The color of your element is set by css 'background-color' attribute.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        props={
            'label': 'Picker with custom preview',
            'sliders': ['box', 'h', 'a'],
            'preview_elem': '<div id="my-preview" style="border-radius: 50%; width:100px; height:100px; margin:20px; border: 1px solid gray;" />',
        }
    )
"""


def preview_example():
    part = factory(u'fieldset', name='yafowil.widget.color.preview')
    part['color'] = factory(
        '#field:color',
        props={
            'label': 'Picker with custom preview',
            'sliders': ['box', 'h', 'a'],
            'preview_elem': '<div id="my-preview" style="border-radius: 50%; width:100px; height:100px; margin:20px; border: 1px solid gray;" />',
        })
    return {
        'widget': part,
        'doc': DOC_PREVIEW,
        'title': 'Preview element'
    }


DOC_SWATCHES = """
Color swatches
--------------

Initialize the widget with custom swatches by passing an array of elements
in the 'swatches' option.

Enable/Disable locked swatches by setting the "locked_swatches" option to
True/False.

Enable/Disable user swatches by setting the "user_swatches" option to
True/False.

Supported formats (locked swatches):

- Number Array (will default to rgb / rgba value)
- rgb string
- rgba string
- hsl string
- hex string
- hsl dict
- rgb/rgba dict

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        value='#ff0000',
        props={
            'label': 'Picker with locked swatches',
            'sliders': ['h', 's', 'v', 'a'],
            'locked_swatches': [
                [255, 0, 0],            # default interpretation as rgb
                [255, 150, 0, 0.5],     # default interpretation as rgba
                'rgb(255,255,0)',       # rgb string
                'rgba(255,255,0,0.5)',  # rgba string
                'hsl(100, 100%, 50%)',  # hsl string
                '#00fff0',              # hex string
                {                       # hsl dict
                    'h': '200',
                    's': '100',
                    'l': '50'
                }, {                    # rgb[a] dict
                    'r': 150,
                    'g': 0,
                    'b': 255
                }
            ],
            'user_swatches': True
        }
    )
"""


def swatches_example():
    part = factory(u'fieldset', name='yafowil.widget.color.swatches')
    part['color'] = factory(
        '#field:color',
        value='#ff0000',
        props={
            'label': 'Picker with locked swatches',
            'sliders': ['h', 's', 'v', 'a'],
            'locked_swatches': [
                [255, 0, 0],            # default interpretation as rgb
                [255, 150, 0, 0.5],     # default interpretation as rgba
                'rgb(255,255,0)',       # rgb string
                'rgba(255,255,0,0.5)',  # rgba string
                'hsl(100, 100%, 50%)',  # hsl string
                '#00fff0',              # hex string
                {                       # hsl dict
                    'h': '200',
                    's': '100',
                    'l': '50'
                }, {                    # rgb[a] dict
                    'r': 150,
                    'g': 0,
                    'b': 255
                }
            ]
        })
    return {
        'widget': part,
        'doc': DOC_SWATCHES,
        'title': 'Locked swatches'
    }


DOC_INPUT = """
Enabling input/label fields
---------------------------

If you want to show input fields or labels next to your sliders, set the
'show_inputs' and/or 'show_labels' properties to True.

Input fields can be set as read-only with the 'disabled' property.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        props={
            'label': 'Picker with input fields',
            'sliders': ['h', 's', 'v'],
            'show_inputs' : True,
            'show_labels': True,
            # 'disabled': True,
            'format': 'hex'
        }
    )
"""


def input_example():
    part = factory(u'fieldset', name='yafowil.widget.color.inputs')
    part['color'] = factory(
        '#field:color',
        props={
            'label': 'Picker with input fields',
            'sliders': ['h', 's', 'v'],
            'show_inputs' : True,
            'show_labels': True,
            # 'disabled': True,
            'format': 'hex'
        })
    return {
        'widget': part,
        'doc': DOC_INPUT,
        'title': 'Input Fields'
    }


DOC_RGB = """
Example: RGB/RGBA color picker
------------------------------

The color picker widget can be used to edit and view RGB/RGBA values.
Single channel editing is also possible.

If editing a channel (for example, red), the corresponding blue and
green channels will be fixed at the initially passed color value.

Pass 'a' in the 'sliders' option to edit alpha channel value.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        value='rgba(100, 100, 255, .5)',
        props={
            'label': 'Example: RGBA Picker',
            'sliders': ['r', 'g', 'b', 'a'],
            'format': 'rgba',
            'show_labels': True,
            'show_inputs': True
        }
    )
"""


def rgb_example():
    part = factory(u'fieldset', name='yafowil.widget.color.rgb_example')
    part['color'] = factory(
        '#field:color',
        value='rgba(100, 100, 255, .5)',
        props={
            'label': 'Example: RGBA Picker',
            'sliders': ['r', 'g', 'b', 'a'],
            'format': 'rgba',
            'show_labels': True,
            'show_inputs': True
        })
    return {
        'widget': part,
        'doc': DOC_RGB,
        'title': 'Example: RGBA'
    }


DOC_HSV = """
Example: HSV color picker
-------------------------

Pass the following values to create a HSV/HSVA color picker.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        value='hsl(260, 100, 50)',
        props={
            'label': 'Example: HSV Picker',
            'sliders': ['h', 's', 'v'],
            'format': 'hsla',
            'show_labels': True
        }
    )
"""


def hsv_example():
    part = factory(u'fieldset', name='yafowil.widget.color.hsv_example')
    part['color'] = factory(
        '#field:color',
        value='hsl(260, 100, 50)',
        props={
            'label': 'Example: HSV Picker',
            'sliders': ['h', 's', 'v', 'a'],
            'format': 'hsla',
            'show_labels': True
        })
    return {
        'widget': part,
        'doc': DOC_HSV,
        'title': 'Example: HSV'
    }


DOC_KELVIN = """
Example: Temperature
--------------------

Pass 'k' in the 'sliders' option of your widget to create a color
temperature slider.

Slider Temperature defaults to 2000-12000K, if you want to override this
behaviour pass a dict with min and max values.

The possible kelvin temperature ranges from 1000 to 40000.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        value=5000,
        props={
            'label': 'Example: Temperature Picker',
            'sliders': ['k'],
            'slider_size': 30,
            'format': 'kelvin',
            'temperature': {'min': 4000, 'max': 8000},
            'locked_swatches': False,
            'user_swatches': False
        }
    )
"""


def kelvin_example():
    part = factory(u'fieldset', name='yafowil.widget.color.temperature_example')
    part['color'] = factory(
        '#field:color',
        value=5000,
        props={
            'label': 'Example: Temperature Picker',
            'sliders': ['k'],
            'slider_size': 30,
            'format': 'kelvin',
            'temperature': {'min': 4000, 'max': 8000},
            'locked_swatches': False,
            'user_swatches': False
        })
    return {
        'widget': part,
        'doc': DOC_KELVIN,
        'title': 'Example: Temperature'
    }


DOC_SWATCHES_ONLY = """
Swatch Widget
-------------

Pass False in the 'sliders' option of your widget to create a swatch only
widget.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        value='#ff0000',
        props={
            'label': 'Example: Swatch Widget',
            'sliders': False,
            'locked_swatches': [
                '#ff0000',
                '#aa2255',
                '#4287f5',
                '#06c7e5',
                '#a096d4',
                '#ecbd78',
                '#80dbad',
                '#f18a1e',
                '#9c171c',
                '#37e3a4',
                '#72d910'
            ],
            'user_swatches': False
        }
    )
"""


def swatches_only_example():
    part = factory(u'fieldset', name='yafowil.widget.color.swatches_only')
    part['color'] = factory(
        '#field:color',
        value='#80dbad',
        props={
            'label': 'Example: Swatch Widget',
            'sliders': False,
            'locked_swatches': [
                '#ff0000',
                '#aa2255',
                '#4287f5',
                '#06c7e5',
                '#a096d4',
                '#ecbd78',
                '#80dbad',
                '#f18a1e',
                '#9c171c',
                '#37e3a4',
                '#72d910'
            ],
            'user_swatches': False
        })
    return {
        'widget': part,
        'doc': DOC_SWATCHES_ONLY,
        'title': 'Example: Temperature'
    }


DOC_VALUE_CONVERSION = """
Value Conversion
----------------

In some cases, values need to be converted between different formats for
further use.

The Color Widget provides functionality to convert values to the following
formats:

- tuple (rgb/a and hsl/a only)
- list (rgb/a and hsl/a only)
- string (all formats)
- int (kelvin only)

The widget's 'datatype' property specifies the format to convert from/to, and
the 'datatype_range' property specifies the desired range, Either '0-1' or
'default' range for the specified format.

.. code-block:: python

    color = factory(
        'color',
        name='colorwidget',
        value=(.5, 0, 1, .5),
        props={
            'label': 'Example: Value Conversion',
            'format': 'rgba',
            'datatype': tuple,
            'datatype_range': '0-1'
        }
    )
"""


def value_conversion_example():
    part = factory(u'fieldset', name='yafowil.widget.color.value_conversion')
    part['color'] = factory(
        '#field:color',
        name='colorwidget',
        value=(.5, 0, 1, .5),
        props={
            'label': 'Example: Value Conversion',
            'format': 'rgba',
            'datatype': tuple,
            'datatype_range': '0-1'
        }
    )
    return {
        'widget': part,
        'doc': DOC_VALUE_CONVERSION,
        'title': 'Example: Value Conversion'
    }


def get_example():
    return [
        default_example(),
        wheel_example(),
        layout_example(),
        dim_example(),
        length_example(),
        input_example(),
        preview_example(),
        swatches_example(),
        swatches_only_example(),
        rgb_example(),
        hsv_example(),
        value_conversion_example(),
        kelvin_example(),
    ]
