mpld3.register_plugin('save_image_buttons', SaveImageButtons);
SaveImageButtons.prototype = Object.create(mpld3.Plugin.prototype);
SaveImageButtons.prototype.constructor = SaveImageButtons;
SaveImageButtons.prototype.requiredProps = ['button_labels', 'fontsize'];
function SaveImageButtons(fig, props) {
    mpld3.Plugin.call(this, fig, props);
}
SaveImageButtons.prototype.draw = function () {
    var fig = this.fig;
    var ax = fig.axes[0];
    var buttonLabels = this.props.button_labels;
    var fontsize = this.props.fontsize;
    var x = fig.width - 2;
    var y = 20;
    for (var i = 0; i < buttonLabels.length; i++) {
        var button = new SaveButton(fig, ax, buttonLabels[i], fontsize);
        button.setPosition(x, y);
        x -= button.buttonWidth + 3;
    }
};
var SaveButton = (function () {
    function SaveButton(fig, ax, label, fontsize) {
        this.xPadding = 6;
        this.yPadding = 4;
        this.fig = fig;
        this.ax = ax;
        this.label = label;
        this.fontsize = fontsize;
        var bgColour = '#bbdde5';
        this.box = fig.canvas
            .append('rect')
            .style('fill', bgColour)
            .attr('class', 'mpld3-save-button-rect')
            .on('click', this.onClick.bind(this));
        this.text = fig.canvas
            .append('text')
            .style('fontsize', fontsize)
            .attr('class', 'mpld3-save-button-text')
            .attr('dominant-baseline', 'central')
            .attr('text-anchor', 'middle')
            .text(this.label)
            .on('click', this.onClick.bind(this));
        var textWidth = this.text.node().getBBox().width;
        this.buttonHeight = this.fontsize + this.yPadding * 2;
        this.buttonWidth = textWidth + this.xPadding * 2;
        this.box
            .attr('height', this.buttonHeight)
            .attr('width', this.buttonWidth)
            .attr('rx', this.buttonHeight / 6);
    }
    SaveButton.prototype.setPosition = function (xLoc, yLoc) {
        this.box.attr('x', xLoc - this.buttonWidth).attr('y', yLoc - this.buttonHeight / 2);
        this.text.attr('x', xLoc - this.buttonWidth / 2).attr('y', yLoc);
    };
    SaveButton.prototype.onClick = function () {
        var _a = figToSVG(this.fig, this.ax), svgString = _a.svgString, svgWidth = _a.svgWidth, svgHeight = _a.svgHeight;
        var imgSource = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));
        var callback = function (dataUrl) {
            var sessionKey = 'autoplot_image_data_url';
            sessionStorage.setItem(sessionKey, dataUrl);
            var event = new CustomEvent('autoplot-embed-image', { detail: { sessionKey: sessionKey } });
            document.dispatchEvent(event);
        };
        switch (this.label.toLowerCase()) {
            case 'svg':
                callback(imgSource);
                break;
            case 'png':
                svgToPNG(imgSource, svgWidth, svgHeight, callback);
                break;
            default:
                throw new Error("Unrecognised save button label " + this.label);
        }
    };
    return SaveButton;
}());
function figToSVG(fig, ax) {
    var svgElement = fig.canvas.node().cloneNode(true);
    svgElement.setAttribute('xlink', 'http://www.w3.org/1999/xlink');
    addElementCSS(ax, svgElement);
    var viewBox = [0, 0, fig.width, fig.height];
    svgElement.setAttribute('viewBox', viewBox.join(' '));
    svgElement.setAttribute('width', "" + viewBox[2]);
    svgElement.setAttribute('height', "" + viewBox[3]);
    var serializer = new XMLSerializer();
    var svgString = serializer.serializeToString(svgElement);
    svgString = svgString.replace(/(\w+)?:?xlink=/g, 'xmlns:xlink=');
    svgString = svgString.replace(/NS\d+:href/g, 'xlink:href');
    return { svgString: svgString, svgWidth: viewBox[2], svgHeight: viewBox[3] };
}
function svgToPNG(imgSource, width, height, callback) {
    var scaleFactor = 3;
    var scaledWidth = width * scaleFactor;
    var scaledHeight = height * scaleFactor;
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    canvas.width = scaledWidth;
    canvas.height = scaledHeight;
    var image = new Image();
    image.onload = function () {
        context.fillStyle = 'white';
        context.fillRect(0, 0, scaledWidth, scaledHeight);
        context.drawImage(image, 0, 0, scaledWidth, scaledHeight);
        callback(canvas.toDataURL('image/png'));
    };
    image.src = imgSource;
}
function addElementCSS(ax, svgElement) {
    addMissingCSS(ax, svgElement);
    hidePlugins(svgElement);
    addMissingLegendCSS(svgElement);
}
function addAttributesToAll(elements, attributes) {
    var _loop_1 = function (i) {
        Object.keys(attributes).forEach(function (prop) { return elements.item(i).setAttribute(prop, attributes[prop]); });
    };
    for (var i = 0; i < elements.length; i++) {
        _loop_1(i);
    }
}
function addMissingCSS(ax, svgElement) {
    ax.elements.forEach(function (element) {
        var cssClass = element.cssclass;
        if (!cssClass) {
            return;
        }
        var tickStyles = {};
        var pathStyles = {};
        var textStyles = {};
        switch (cssClass) {
            case 'mpld3-xaxis':
            case 'mpld3-yaxis':
                pathStyles = {
                    'shape-rendering': 'crispEdges',
                    stroke: element.props.axiscolor,
                    fill: 'none',
                };
                textStyles = {
                    'font-family': 'sans-serif',
                    'font-size': element.props.fontsize + "px",
                    fill: element.props.fontcolor,
                    stroke: 'none',
                };
                break;
            case 'mpld3-xgrid':
            case 'mpld3-ygrid':
                tickStyles = {
                    stroke: element.props.color,
                    'stroke-dasharray': element.props.dasharray,
                    'stroke-opacity': "" + element.props.alpha,
                };
                break;
        }
        var svgElementsByClass = svgElement.getElementsByClassName(cssClass);
        function applyStyles(styles, child) {
            if (!child.class && !child.tag) {
                addAttributesToAll(svgElementsByClass, styles);
                return;
            }
            for (var i = 0; i < svgElementsByClass.length; i++) {
                var children = child.class
                    ? svgElementsByClass.item(i).getElementsByClassName(child.class)
                    : svgElementsByClass.item(i).getElementsByTagName(child.tag);
                addAttributesToAll(children, styles);
            }
        }
        applyStyles(pathStyles, {});
        applyStyles(tickStyles, { class: 'tick' });
        applyStyles(textStyles, { tag: 'text' });
    });
}
function hidePlugins(svgElement) {
    var pluginClasses = [
        'mpld3-time-series-tooltip-rect',
        'mpld3-time-series-tooltip-text',
        'mpld3-time-series-tooltip-circle',
        'mpld3-range-selector-button-rect',
        'mpld3-range-selector-button-text',
        'mpld3-save-button-text',
        'mpld3-save-button-rect',
        'mpld3-resetbutton',
        'mpld3-zoombutton',
        'mpld3-boxzoombutton',
    ];
    pluginClasses.forEach(function (pluginClass) {
        var elements = svgElement.getElementsByClassName(pluginClass);
        addAttributesToAll(elements, { display: 'none' });
    });
}
function addMissingLegendCSS(svgElement) {
    var elements = svgElement.getElementsByClassName('mpld3-interactive-legend-text');
    addAttributesToAll(elements, { 'font-family': 'sans-serif' });
}
