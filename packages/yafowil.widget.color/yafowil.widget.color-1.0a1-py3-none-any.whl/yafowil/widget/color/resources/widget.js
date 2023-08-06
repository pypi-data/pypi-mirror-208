var yafowil_color = (function (exports, $) {
    'use strict';

    class ColorSwatch {
        constructor(widget, container, color, kelvin = false, locked = false) {
            this.widget = widget;
            this.container = container;
            this.color = color;
            this.locked = locked;
            this.selected = false;
            this.kelvin = kelvin;
            this.destroy = this.destroy.bind(this);
            if (kelvin && !this.widget.type_kelvin ||
                this.widget.type_kelvin && !kelvin ||
                !this.widget.type_alpha && color.alpha < 1) {
                    this.invalid = true;
                    return;
            }
            if (kelvin && this.widget.type_kelvin &&
                (color.kelvin < this.widget.min ||
                 color.kelvin > this.widget.max)) {
                    this.invalid = true;
                    return;
            }
            this.elem = $('<div />')
                .addClass('color-swatch layer-transparent')
                .appendTo(this.container);
            this.color_layer = $('<div />')
                .addClass('layer-color')
                .css('background-color', this.color.rgbaString)
                .appendTo(this.elem);
            if (locked) {
                this.elem
                    .addClass('locked')
                    .append($('<div class="swatch-mark" />'));
            }
            if (this.widget.color_equals(color)) {
                this.selected = true;
            }
            this.select = this.select.bind(this);
            this.elem.on('click', this.select);
        }
        get selected() {
            return this._selected;
        }
        set selected(selected) {
            if (selected) {
                $('div.color-swatch', this.widget.dropdown_elem)
                .removeClass('selected');
                this.elem.addClass('selected');
                this.widget.picker.color.set(this.color);
            } else if (this.elem) {
                this.elem.removeClass('selected');
            }
            this._selected = selected;
        }
        destroy() {
            this.widget.active_swatch = null;
            if (this.locked || this.invalid) {
                return;
            }
            this.elem.off('click', this.select);
            this.elem.remove();
        }
        select(e) {
            if (this.widget.active_swatch !== this) {
                let previous = this.widget.picker.color.clone();
                this.previous_color = previous.rgbaString;
                this.widget.active_swatch = this;
            } else if (this.widget.active_swatch == this) {
                this.widget.active_swatch = null;
                this.selected = false;
                this.widget.picker.color.set(this.previous_color);
            }
        }
    }
    class LockedSwatchesContainer {
        constructor (widget, swatches = []) {
            this.widget = widget;
            this.elem = $('<div />')
                .addClass('color-picker-recent')
                .appendTo(widget.dropdown_elem);
            this.swatches = [];
            this.init_swatches(swatches);
        }
        parse_swatch(swatch) {
            let color,
                kelvin = false,
                valid_type = typeof swatch === 'string' || typeof swatch === 'object';
            if (swatch instanceof Array) {
                color = {
                    r: swatch[0],
                    g: swatch[1],
                    b: swatch[2]
                };
                if (swatch[3]) {
                    color.a = swatch[3];
                }
            } else if (is_kelvin(swatch)) {
                color = iro.Color.kelvinToRgb(swatch.toString());
                kelvin = true;
            } else if (valid_type) {
                color = swatch;
            } else {
                console.log(`ERROR: not supported color format at ${swatch}`);
                return;
            }
            return {'color': new iro.Color(color), 'kelvin': kelvin};
        }
        init_swatches(swatches) {
            if (!swatches || !swatches.length) {
                this.elem.hide();
                return;
            }
            for (let swatch of swatches) {
                let swatch_color = this.parse_swatch(swatch);
                this.swatches.push(
                    new ColorSwatch(
                        this.widget,
                        this.elem,
                        swatch_color.color,
                        swatch_color.kelvin,
                        true
                    )
                );
                this.elem.show();
            }
        }
    }
    class UserSwatchesContainer {
        constructor (widget) {
            this.widget = widget;
            this.elem = $('<div />')
                .addClass('color-picker-recent')
                .appendTo(widget.dropdown_elem);
            this.add_color_btn = $('<button />')
                .addClass('add_color')
                .text('+ Add');
            this.remove_color_btn = $('<button />')
                .addClass('remove_color')
                .text('- Remove')
                .hide();
            this.buttons = $('<div />')
                .addClass('buttons')
                .append(this.add_color_btn)
                .append(this.remove_color_btn)
                .appendTo(widget.dropdown_elem);
            this.swatches = [];
            this.init_swatches();
            this.create_swatch = this.create_swatch.bind(this);
            this.add_color_btn.on('click', this.create_swatch);
            this.remove_swatch = this.remove_swatch.bind(this);
            this.remove_color_btn.on('click', this.remove_swatch);
            this.init_swatches = this.init_swatches.bind(this);
            widget.elem.on('yafowil-color-swatches:changed', this.init_swatches);
        }
        init_swatches(e) {
            let json_str = localStorage.getItem('yafowil-color-swatches');
            for (let swatch of this.swatches) {
                swatch.destroy();
            }
            this.swatches = [];
            if (json_str) {
                this.elem.show();
                this.remove_color_btn.show();
                let colors = JSON.parse(json_str);
                for (let color_elem of colors) {
                    let iro_color = new iro.Color(color_elem.color);
                    this.swatches.push(new ColorSwatch(
                        this.widget,
                        this.elem,
                        iro_color,
                        color_elem.kelvin
                    ));
                }
                if (this.swatches.length > 10) {
                    this.swatches[0].destroy();
                    this.swatches.shift();
                }
            } else {
                this.remove_color_btn.hide();
            }
        }
        create_swatch(e) {
            if (e && e.type === 'click') {
                e.preventDefault();
            }
            if (this.widget.locked_swatches) {
                for (let swatch of this.widget.locked_swatches.swatches) {
                    if (this.widget.color_equals(swatch.color)) {
                        return;
                    }
                }
            }
            for (let swatch of this.swatches) {
                if (this.widget.color_equals(swatch.color)) {
                    return;
                }
            }
            let swatch = new ColorSwatch(
                this.widget,
                this.elem,
                this.widget.picker.color.clone(),
                this.widget.type_kelvin
            );
            this.swatches.push(swatch);
            this.set_swatches();
        }
        remove_swatch(e) {
            if (e && e.type === 'click') {
                e.preventDefault();
            }
            if (!this.widget.active_swatch || this.widget.active_swatch.locked) {
                return;
            }
            let index = this.swatches.indexOf(this.widget.active_swatch);
            this.widget.active_swatch.destroy();
            this.swatches.splice(index, 1);
            if (!this.swatches.length) {
                this.elem.hide();
                this.remove_color_btn.hide();
                this.widget.picker.color.reset();
            }
            this.elem.hide();
            this.remove_color_btn.hide();
            this.widget.picker.color.reset();
            this.set_swatches();
        }
        set_swatches() {
            let swatches = [];
            for (let swatch of this.swatches) {
                swatches.push({color: swatch.color.hsva, kelvin: swatch.kelvin});
            }
            if (swatches.length) {
                localStorage.setItem('yafowil-color-swatches', JSON.stringify(swatches));
            } else {
                localStorage.removeItem('yafowil-color-swatches');
            }
            let evt = new $.Event('yafowil-color-swatches:changed', {origin: this});
            $('input.color-picker').trigger(evt);
        }
    }
    class InputElement {
        constructor(widget, elem, color, format, temperature = {min: 1000, max:40000}) {
            this.widget = widget;
            this.elem = elem;
            this.elem.attr('spellcheck', 'false');
            this.elem.addClass('form-control');
            this.format = format || 'hexString';
            if (this.format === 'hexString') {
                this.elem.attr('maxlength', 7);
            } else if (this.format === 'hex8String') {
                this.elem.attr('maxlength', 9);
            }
            this.temperature = temperature;
            this.color = color;
            if (this.color) {
                this.update_color(color);
            }
            this.on_input = this.on_input.bind(this);
            this.elem.on('input', this.on_input);
            this.on_focusout = this.on_focusout.bind(this);
            this.elem.on('focusout', this.on_focusout);
            this.update_color = this.update_color.bind(this);
        }
        on_input(e) {
            let val = this.elem.val();
            this._color = val;
        }
        on_focusout() {
            let color = this._color;
            if (color) {
                if (this.format === 'kelvin') {
                    if (parseInt(color) < this.temperature.min) {
                        color = this.temperature.min;
                    } else if (parseInt(color) > this.temperature.max) {
                        color = this.temperature.max;
                    }
                    this.widget.color_picker.picker.color.kelvin = color;
                    this.elem.val(color);
                } else {
                    this.widget.color_picker.picker.color.set(color);
                }
                this._color = null;
            }
        }
        update_color(color) {
            if (this.format === 'kelvin') {
                this.elem.val(color.kelvin);
            } else {
                this.elem.val(color[this.format]);
            }
        }
    }
    class PreviewElement {
        constructor(widget, elem, color) {
            this.widget = widget;
            this.layer = $('<div />')
                .addClass('layer-color');
            this.elem = elem
                .addClass('layer-transparent')
                .append(this.layer)
                .insertAfter(this.widget.elem);
            this.color = color ? color.rgbaString : undefined;
            this.on_click = this.on_click.bind(this);
            this.elem.on('click', this.on_click);
        }
        get color() {
            return this._color;
        }
        set color(color) {
            this.layer.css('background-color', color);
            this._color = color;
        }
        on_click() {
            this.widget.open();
        }
    }
    const slider_components = {
        box: 'box',
        wheel: 'wheel',
        r: 'red',
        g: 'green',
        b: 'blue',
        a: 'alpha',
        h: 'hue',
        s: 'saturation',
        v: 'value',
        k: 'kelvin'
    };
    function is_kelvin(value) {
        return ((typeof value === 'string' && !value.startsWith('#') &&
                parseInt(value) == value) || (typeof value == 'number'));
    }

    function lookup_callback(path) {
        if (!path) {
            return null;
        }
        let source = path.split('.'),
            cb = window,
            name;
        for (const idx in source) {
            name = source[idx];
            if (cb[name] === undefined) {
                throw "'" + name + "' not found.";
            }
            cb = cb[name];
        }
        return cb;
    }
    class ColorPicker {
        constructor(elem, options) {
            this.elem = elem;
            if (options.on_update) {
                this.elem.on('color_update', options.on_update);
            }
            if (options.on_close) {
                this.elem.on('color_close', options.on_close);
            }
            this.dropdown_elem = $('<div />')
                .addClass('color-picker-wrapper')
                .css('top', this.elem.outerHeight())
                .insertAfter(this.elem);
            this.picker_container = $('<div />')
                .addClass('color-picker-container')
                .appendTo(this.dropdown_elem);
            this.close_btn = $('<button />')
                .addClass('close-button')
                .text('✕')
                .appendTo(this.dropdown_elem);
            this.slider_size = options.slider_size;
            let iro_opts = this.init_opts(options);
            this.picker = new iro.ColorPicker(this.picker_container.get(0), iro_opts);
            let sliders = options.sliders;
            if (sliders && sliders.includes('box') && sliders.includes('wheel')) {
                if (sliders.indexOf('box') < sliders.indexOf('wheel')) {
                    $('div.IroWheel', this.picker_container).hide();
                } else {
                    $('div.IroBox', this.picker_container).hide();
                }
                this.switch_btn = $('<button />')
                    .addClass('iro-switch-toggle')
                    .append($('<i class="glyphicon glyphicon-refresh" />'))
                    .appendTo(this.dropdown_elem);
                this.switch_btn.on('click', (e) => {
                    e.preventDefault();
                    $('div.IroWheel', this.picker_container).toggle();
                    $('div.IroBox', this.picker_container).toggle();
                });
            } else if (!sliders) {
                this.picker_container.hide();
            }
            this.type_kelvin = options.format === 'kelvin';
            if (this.type_kelvin) {
                this.min = options.temperature.min;
                this.max = options.temperature.max;
            }
            let alpha_types = ['rgbaString', 'hex8String', 'hslaString'];
            this.type_alpha = alpha_types.includes(options.format);
            if (!options.locked_swatches && !options.user_swatches) {
                this.picker_container.css('margin-bottom', 0);
            }
            if (options.color) {
                this.color = this.picker.color.clone();
            } else {
                this.color = null;
            }
            if (options.locked_swatches) {
                this.locked_swatches = new LockedSwatchesContainer(
                    this,
                    options.locked_swatches
                );
            }
            if (options.user_swatches) {
                this.user_swatches = new UserSwatchesContainer(this);
            }
            let prev_elem;
            if (options.preview_elem) {
                prev_elem = $(options.preview_elem)
                    .addClass('yafowil-color-picker-preview');
            } else {
                let elem_width = this.elem.outerWidth();
                prev_elem = $('<span />')
                    .addClass('yafowil-color-picker-color layer-transparent')
                    .css('left', `${elem_width}px`);
            }
            this.preview = new PreviewElement(this, prev_elem, this.color);
            this.open = this.open.bind(this);
            this.update_color = this.update_color.bind(this);
            this.picker.on('color:change', this.update_color);
            this.close = this.close.bind(this);
            this.close_btn.on('click', this.close);
            this.on_keydown = this.on_keydown.bind(this);
            this.on_click = this.on_click.bind(this);
        }
        get active_swatch() {
            return this._active_swatch;
        }
        set active_swatch(swatch) {
            if (swatch) {
                swatch.selected = true;
                this._active_swatch = swatch;
            } else {
                this._active_swatch = null;
            }
        }
        init_opts(opts) {
            let iro_opts = {
                width: opts.box_width,
                boxHeight: opts.box_height || opts.box_width,
                layoutDirection: opts.layout_direction || 'vertical',
                layout: []
            };
            if (opts.format === 'kelvin') {
                iro_opts.color = iro.Color.kelvinToRgb(opts.color);
            } else {
                iro_opts.color = opts.color ? opts.color : '#fff';
            }
            const sliders = opts.sliders || [];
            sliders.forEach(name => {
                let type = slider_components[name];
                if (type === 'box') {
                    iro_opts.layout.push({
                        component: iro.ui.Box,
                        options: {}
                    });
                } else if (type === 'wheel') {
                    iro_opts.layout.push({
                        component: iro.ui.Wheel,
                        options: {}
                    });
                } else {
                    iro_opts.layout.push({
                        component: iro.ui.Slider,
                        options: {
                            sliderType: type,
                            sliderSize: opts.slider_size,
                            sliderLength: opts.slider_length,
                            minTemperature: opts.temperature ? opts.temperature.min : undefined,
                            maxTemperature: opts.temperature ? opts.temperature.max : undefined,
                            disabled: opts.disabled,
                            showInput: opts.show_inputs,
                            showLabel: opts.show_labels
                        }
                    });
                }
            });
            return iro_opts;
        }
        update_color() {
            this.color = this.picker.color.clone();
            this.preview.color = this.color.rgbaString;
            let evt = new $.Event('color_update', {origin: this});
            this.elem.trigger(evt);
        }
        open(evt) {
            if (this.dropdown_elem.css('display') === 'none') {
                this.dropdown_elem.show();
                $(window).on('keydown', this.on_keydown);
                $(window).on('mousedown', this.on_click);
            } else {
                this.close();
            }
        }
        on_keydown(e) {
            if (e.key === 'Enter' || e.key === 'Escape') {
                e.preventDefault();
                this.close();
            } else if (e.key === 'Delete') {
                e.preventDefault();
                if (this.user_swatches) {
                    this.user_swatches.remove_swatch();
                }
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                if ((!this.locked_swatches && !this.user_swatches ) ||
                    !this.active_swatch) {
                    return;
                }
                let swatch = this.active_swatch,
                    user_swatches = Boolean(this.user_swatches),
                    locked_swatches = Boolean(this.locked_swatches),
                    valid_user_swatches,
                    valid_locked_swatches;
                if (user_swatches) {
                    valid_user_swatches = this.user_swatches.swatches.filter(el => {
                        return !el.invalid;
                    });
                }
                if (locked_swatches) {
                    valid_locked_swatches = this.locked_swatches.swatches.filter(el => {
                        return !el.invalid;
                    });
                }
                const ctx = swatch.locked ? valid_locked_swatches : valid_user_swatches;
                let index = ctx.indexOf(swatch);
                index = e.key === 'ArrowLeft' ? index - 1 : index + 1;
                if (index < 0) {
                    if (!swatch.locked
                        && locked_swatches
                        && valid_locked_swatches.length) {
                        this.active_swatch = valid_locked_swatches[valid_locked_swatches.length -1];
                    }
                } else if (index >= ctx.length) {
                    if (swatch.locked
                        && user_swatches
                        && valid_user_swatches.length) {
                            this.active_swatch = valid_user_swatches[0];
                    }
                } else {
                    this.active_swatch = ctx[index];
                }
            }
        }
        on_click(e) {
            let target = this.dropdown_elem;
            if (!target.is(e.target) &&
                target.has(e.target).length === 0 &&
                !this.preview.elem.is(e.target) &&
                target.css('display') === 'block')
            {
                this.close();
            }
        }
        close(e) {
            if (e) {
                e.preventDefault();
            }
            this.dropdown_elem.hide();
            $(window).off('keydown', this.on_keydown);
            $(window).off('mousedown', this.on_click);
            let evt = new $.Event('color_close', {origin: this});
            this.elem.trigger(evt);
        }
        color_equals(color) {
            if (this.color &&
                (color instanceof iro.Color) &&
                color.hsva.h === this.color.hsva.h &&
                color.hsva.s === this.color.hsva.s &&
                color.hsva.v === this.color.hsva.v &&
                color.hsva.a === this.color.hsva.a) {
                return true;
            }
        }
    }
    class ColorWidget {
        static initialize(context) {
            $('input.color-picker', context).each(function() {
                let elem = $(this);
                if (window.yafowil_array !== undefined &&
                    window.yafowil_array.inside_template(elem)) {
                    return;
                }
                let options = {
                    format: elem.data('format'),
                    preview_elem: elem.data('preview_elem'),
                    sliders: elem.data('sliders'),
                    box_width: elem.data('box_width'),
                    box_height: elem.data('box_height'),
                    slider_size: elem.data('slider_size'),
                    color: elem.val(),
                    locked_swatches: elem.data('locked_swatches'),
                    user_swatches: elem.data('user_swatches'),
                    temperature: elem.data('temperature'),
                    disabled: elem.data('disabled'),
                    show_inputs: elem.data('show_inputs'),
                    show_labels: elem.data('show_labels'),
                    slider_length: elem.data('slider_length'),
                    layout_direction: elem.data('layout_direction'),
                    open_on_focus: elem.data('open_on_focus'),
                    on_update: lookup_callback(elem.data('on_update')),
                    on_close: lookup_callback(elem.data('on_close'))
                };
                new ColorWidget(elem, options);
            });
        }
        constructor(elem, options) {
            elem.data('yafowil-color', this);
            this.elem = elem;
            this.color_picker = new ColorPicker(elem, options);
            this.temp = options.temperature || {min: 2000, max: 11000};
            this.input_elem = new InputElement(
                this, this.elem, this.color_picker.color, options.format, this.temp
            );
            if (options.open_on_focus) {
                this.elem.on('focus', this.color_picker.open);
            }
            this.elem.on('color_update', (e) => {
                this.input_elem.update_color(this.color_picker.color);
            });
            this.elem.on('color_close', (e) => {
                this.elem.blur();
            });
        }
    }
    function color_on_array_add(inst, context) {
        ColorWidget.initialize(context);
    }
    function register_array_subscribers() {
        if (window.yafowil_array === undefined) {
            return;
        }
        window.yafowil_array.on_array_event('on_add', color_on_array_add);
    }

    $(function() {
        if (window.ts !== undefined) {
            ts.ajax.register(ColorWidget.initialize, true);
        } else if (window.bdajax !== undefined) {
            bdajax.register(ColorWidget.initialize, true);
        } else {
            ColorWidget.initialize();
        }
        register_array_subscribers();
    });

    exports.ColorPicker = ColorPicker;
    exports.ColorWidget = ColorWidget;
    exports.lookup_callback = lookup_callback;
    exports.register_array_subscribers = register_array_subscribers;

    Object.defineProperty(exports, '__esModule', { value: true });


    window.yafowil = window.yafowil || {};
    window.yafowil.color = exports;


    return exports;

})({}, jQuery);
