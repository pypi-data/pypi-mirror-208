mpld3.register_plugin('range_selector_buttons', RangeSelectorButtons);
RangeSelectorButtons.prototype = Object.create(mpld3.Plugin.prototype);
RangeSelectorButtons.prototype.constructor = RangeSelectorButtons;
RangeSelectorButtons.prototype.requiredProps = ['button_labels', 'line_ids', 'margin_right', 'fontsize'];
function RangeSelectorButtons(fig, props) {
    mpld3.Plugin.call(this, fig, props);
}
RangeSelectorButtons.prototype.draw = function () {
    var fig = this.fig;
    var ax = fig.axes[0];
    var buttonLabels = this.props.button_labels;
    var lineIds = this.props.line_ids;
    var marginRight = this.props.margin_right;
    var fontsize = this.props.fontsize;
    var x = 10;
    var y = 20;
    for (var i = 0; i < buttonLabels.length; i++) {
        if (x >= fig.width - marginRight) {
            break;
        }
        var button = new RangeButton(fig, ax, buttonLabels[i], fontsize, lineIds);
        button.setPosition(x, y);
        x += button.buttonWidth + 3;
    }
};
function setLowerLimit(xMin, xMax, number, unit) {
    switch (unit) {
        case 's':
            xMin.setSeconds(xMax.getSeconds() - number);
            break;
        case 'M':
            xMin.setMinutes(xMax.getDate() - number);
            break;
        case 'h':
            xMin.setHours(xMax.getHours() - number);
            break;
        case 'd':
            xMin.setDate(xMax.getDate() - number);
            break;
        case 'm':
            xMin.setMonth(xMax.getMonth() - number);
            break;
        case 'y':
            xMin.setFullYear(xMax.getFullYear() - number);
            break;
        default:
            throw new Error("Unrecognised unit '" + unit + "'");
    }
}
function mplToDate(value) {
    var date = new Date((value - 719163) * 86400000);
    date.setMinutes(date.getMinutes() + date.getTimezoneOffset());
    return date;
}
function getVisibleDomain(fig, lineIds) {
    if (!lineIds) {
        throw new Error('"lineIds" must be defined for the "fit" button to work');
    }
    var xMin;
    var xMax;
    var yMin;
    var yMax;
    lineIds.forEach(function (lineId) {
        var line = mpld3.get_element(lineId, fig);
        if (!line.props.isHidden) {
            var lineXMin = mplToDate(line.data[0][line.props.xindex]);
            var lineXMax = mplToDate(line.data[line.data.length - 1][line.props.xindex]);
            xMin = xMin ? (lineXMin < xMin ? lineXMin : xMin) : lineXMin;
            xMax = xMax ? (lineXMax > xMax ? lineXMax : xMax) : lineXMax;
            var _a = d3.extent(line.data.map(function (row) { return row[line.props.yindex]; })), lineYMin = _a[0], lineYMax = _a[1];
            yMin = yMin ? (lineYMin < yMin ? lineYMin : yMin) : lineYMin;
            yMax = yMax ? (lineYMax > yMax ? lineYMax : yMax) : lineYMax;
        }
    });
    if (yMin && yMax) {
        var padding = (yMax - yMin) / 100;
        yMin -= padding;
        yMax += padding;
    }
    return [xMin && xMax ? [xMin, xMax] : undefined, yMin && yMax ? [yMin, yMax] : undefined];
}
var RangeButton = (function () {
    function RangeButton(fig, ax, label, fontsize, lineIds) {
        this.xPadding = 6;
        this.yPadding = 4;
        this.fig = fig;
        this.ax = ax;
        this.label = label;
        this.fontsize = fontsize;
        this.lineIds = lineIds;
        this.number = Number.parseInt(label.substr(0, label.length - 1));
        if (this.number) {
            this.unit = label.charAt(label.length - 1);
        }
        else {
            this.unit = label;
        }
        var bgColour;
        switch (this.unit) {
            case 'fit':
                bgColour = '#bbe5bb';
                break;
            case 'reset':
                bgColour = '#e5bbbb';
                break;
            default:
                bgColour = '#e5e5e5';
        }
        this.box = fig.canvas
            .append('rect')
            .style('fill', bgColour)
            .attr('class', 'mpld3-range-selector-button-rect')
            .on('click', this.onClick.bind(this));
        this.text = fig.canvas
            .append('text')
            .style('fontsize', fontsize)
            .attr('class', 'mpld3-range-selector-button-text')
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
    RangeButton.prototype.setPosition = function (xLoc, yLoc) {
        this.box.attr('x', xLoc).attr('y', yLoc - this.buttonHeight / 2);
        this.text.attr('x', xLoc + this.buttonWidth / 2).attr('y', yLoc);
    };
    RangeButton.prototype.onClick = function () {
        var _a;
        var xLim;
        var yLim;
        var duration = 200;
        switch (this.unit) {
            case 'reset':
                this.ax.reset(duration, true);
                return;
            case 'fit':
                _a = getVisibleDomain(this.fig, this.lineIds), xLim = _a[0], yLim = _a[1];
                break;
            default:
                var xMax = this.ax.xdom.invert(this.ax.width);
                var newXMin = new Date(xMax.valueOf());
                if (this.unit === 'ytd') {
                    newXMin.setDate(1);
                    newXMin.setMonth(0);
                }
                else {
                    setLowerLimit(newXMin, xMax, this.number, this.unit);
                }
                xLim = [newXMin, xMax];
        }
        this.ax.set_axlim(xLim, yLim, duration, true);
    };
    return RangeButton;
}());
