mpld3.register_plugin('time_series_tooltip', TimeSeriesTooltip);
TimeSeriesTooltip.prototype = Object.create(mpld3.Plugin.prototype);
TimeSeriesTooltip.prototype.constructor = TimeSeriesTooltip;
TimeSeriesTooltip.prototype.requiredProps = ['line_ids', 'fontsize'];
function TimeSeriesTooltip(fig, props) {
    mpld3.Plugin.call(this, fig, props);
}
TimeSeriesTooltip.prototype.draw = function () {
    var fig = this.fig;
    var ax = fig.axes[0];
    var xTooltip = new XTooltip(fig, ax, this.props.fontsize);
    var yTooltips = new YTooltips(fig, ax, this.props.line_ids, this.props.fontsize);
    function setTooltipLocation(xLoc) {
        xLoc = Math.min(ax.position[0] + ax.width, Math.max(ax.position[0], xLoc));
        var xValue = xLocationToValue(xLoc, ax);
        xTooltip.setValue(xValue);
        xTooltip.setLocation(xLoc);
        yTooltips.setLocationsAndValues(xValue);
    }
    function updateTooltips() {
        var _a = d3.mouse(fig.canvas.node()), xLoc = _a[0], yLoc = _a[1];
        if (ax.position[1] <= yLoc && yLoc <= ax.position[1] + ax.height) {
            setTooltipLocation(xLoc);
        }
    }
    xTooltip.show();
    setTooltipLocation(Number.MAX_SAFE_INTEGER);
    fig.canvas.on('mousedown', function () {
        updateTooltips();
        fig.canvas.on('mousemove', updateTooltips);
        fig.canvas.on('mouseup', function () {
            fig.canvas.on('mousemove', function () { return null; }).on('mouseup', function () { return null; });
        });
        d3.event.preventDefault();
    });
};
function xValueToLocation(xValue, ax) {
    return ax.x(xValue) + ax.position[0];
}
function yValueToLocation(yValue, ax) {
    return ax.y(yValue) + ax.position[1];
}
function xLocationToValue(xLoc, ax) {
    return ax.xdom.invert(xLoc - ax.position[0]);
}
function getXRange(ax) {
    return Math.abs(ax.xdom.invert(ax.width).getTime() - ax.xdom.invert(0).getTime()) / (24 * 3600 * 1000);
}
function getClosestIndex(xValue, line) {
    var offset = xValue.getTimezoneOffset() / (24 * 60);
    var x = xValue.getTime() / (1000 * 3600 * 24) + 719163 - offset;
    var traceLength = line.data.length;
    var lineWidth = 1000;
    try {
        lineWidth = d3.select(line.path[0][0]).node().getBBox().width;
    }
    catch (_a) { }
    var x0 = getX(line, 0);
    var x1 = getX(line, traceLength - 1);
    var xMin = Math.min(x0, x1);
    var xMax = Math.max(x0, x1);
    var buffer = (20 * (xMax - xMin)) / lineWidth;
    if (x < xMin) {
        if (xMin - x > buffer) {
            return null;
        }
        return { closestX: xMin, closestIndex: 0 };
    }
    else if (x > xMax) {
        if (x - xMax > buffer) {
            return null;
        }
        return { closestX: xMax, closestIndex: traceLength - 1 };
    }
    var precision = Math.floor(traceLength / 2);
    var closestIndex = Math.floor(traceLength / 2);
    var closestX = getX(line, closestIndex);
    var bestDistance = Math.abs(x - closestX);
    while (precision >= 1) {
        var i1 = closestIndex - precision;
        var x1_1 = getX(line, i1);
        if (x1_1) {
            var d1 = Math.abs(x - x1_1);
            if (d1 < bestDistance) {
                closestX = x1_1;
                closestIndex = i1;
                bestDistance = d1;
                continue;
            }
        }
        var i2 = closestIndex + precision;
        var x2 = getX(line, i2);
        if (x2) {
            var d2 = Math.abs(x - x2);
            if (d2 < bestDistance) {
                closestX = x2;
                closestIndex = i2;
                bestDistance = d2;
                continue;
            }
        }
        precision = Math.floor(precision / 2);
    }
    return { closestIndex: closestIndex, closestX: closestX };
}
function getLine(lineId, fig) {
    return mpld3.get_element(lineId, fig);
}
function getValue(line, i, j) {
    return 0 <= i && i < line.data.length ? line.data[i][j] : null;
}
function getX(line, index) {
    return getValue(line, index, line.props.xindex);
}
function getY(line, index) {
    return getValue(line, index, line.props.yindex);
}
function getDateFormatter(xRange) {
    if (xRange >= 30) {
        return d3.time.format('%Y-%m-%d');
    }
    if (xRange >= 5) {
        return d3.time.format('%m-%d %H:00');
    }
    if (xRange >= 0.25) {
        return d3.time.format('%m-%d %H:%M');
    }
    return d3.time.format('%d - %H:%M:%S');
}
function getNumberFormatter(yValue) {
    var abs = Math.abs(yValue);
    if (abs < 0.001 || abs >= 1000000) {
        return d3.format('.5s');
    }
    if (abs < 1) {
        return d3.format('.5f');
    }
    if (abs < 10000) {
        return d3.format('.5r');
    }
    return d3.format(',.0f');
}
var XTooltip = (function () {
    function XTooltip(fig, ax, fontsize) {
        this.xPadding = 4;
        this.yPadding = 2;
        this.fig = fig;
        this.ax = ax;
        this.fontsize = fontsize;
        var boxHeight = this.fontsize + this.yPadding * 2;
        this.boxWidth = 0;
        var yLoc = ax.position[1] + ax.height + boxHeight;
        this.background = this.fig.canvas
            .insert('rect')
            .attr('class', 'mpld3-time-series-tooltip-rect')
            .style('visibility', 'hidden')
            .attr('y', yLoc - boxHeight / 2)
            .attr('height', boxHeight)
            .style('fill', 'gray');
        this.label = this.fig.canvas
            .insert('text')
            .attr('class', 'mpld3-time-series-tooltip-text')
            .style('visibility', 'hidden')
            .style('text-anchor', 'middle')
            .attr('dominant-baseline', 'central')
            .style('font-size', this.fontsize)
            .style('fill', 'white')
            .attr('y', yLoc);
        this.xRange = getXRange(this.ax);
        this.formatter = getDateFormatter(this.xRange);
    }
    XTooltip.prototype.updateFormatter = function () {
        var newXRange = getXRange(this.ax);
        if (this.xRange !== newXRange) {
            this.xRange = newXRange;
            this.formatter = getDateFormatter(this.xRange);
        }
    };
    XTooltip.prototype.show = function () {
        this.background.style('visibility', 'visible');
        this.label.style('visibility', 'visible');
    };
    XTooltip.prototype.setValue = function (value) {
        this.updateFormatter();
        this.label.text(this.formatter(value));
        var textWidth = this.label.node().getBBox().width;
        this.boxWidth = textWidth + this.xPadding * 2;
        this.background.attr('width', this.boxWidth);
    };
    XTooltip.prototype.setLocation = function (xLoc) {
        this.background.attr('x', xLoc - this.boxWidth / 2);
        this.label.attr('x', xLoc);
    };
    return XTooltip;
}());
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var YTooltips = (function () {
    function YTooltips(fig, ax, lineIds, fontsize) {
        this.fig = fig;
        this.ax = ax;
        this.tooltips = lineIds.reduce(function (obj, lineId) {
            var _a;
            return (__assign(__assign({}, obj), (_a = {}, _a[lineId] = new YTooltip(fig, ax, lineId, fontsize), _a)));
        }, {});
    }
    YTooltips.prototype.setLocationsAndValues = function (xValue) {
        var _this = this;
        var lineIdLocations = [];
        Object.keys(this.tooltips).forEach(function (lineId) {
            var line = getLine(lineId, _this.fig);
            if (line.props.isHidden) {
                _this.tooltips[lineId].hide();
                return;
            }
            var result = getClosestIndex(xValue, line);
            if (!result) {
                _this.tooltips[lineId].hide();
                return;
            }
            var closestIndex = result.closestIndex, closestX = result.closestX;
            var xLoc = xValueToLocation(closestX, _this.ax);
            if (xLoc < 0 + _this.ax.position[0] || xLoc > _this.ax.width + _this.ax.position[0]) {
                _this.tooltips[lineId].hide();
                return;
            }
            var yValue = getY(line, closestIndex);
            if (!Number.isFinite(yValue) ||
                yValue < _this.ax.ydom.invert(_this.ax.height) ||
                yValue > _this.ax.ydom.invert(0)) {
                _this.tooltips[lineId].hide();
                return;
            }
            var yLoc = yValueToLocation(yValue, _this.ax);
            _this.tooltips[lineId].show();
            _this.tooltips[lineId].setValue(yValue);
            lineIdLocations.push([lineId, xLoc, yLoc]);
        });
        var prevYLoc = Number.MIN_SAFE_INTEGER;
        lineIdLocations
            .sort(function (a, b) { return a[2] - b[2]; })
            .forEach(function (tup) {
            prevYLoc = _this.tooltips[tup[0]].setLocation(tup[1], tup[2], prevYLoc);
        });
    };
    return YTooltips;
}());
var YTooltip = (function () {
    function YTooltip(fig, ax, lineId, fontsize) {
        this.xPadding = 2;
        this.yPadding = 2;
        var xLoc = ax.position[0] + ax.width + 3;
        this.fontsize = fontsize;
        this.boxHeight = this.fontsize + this.yPadding * 2;
        this.background = fig.canvas
            .insert('rect')
            .attr('class', 'mpld3-time-series-tooltip-rect')
            .style('visibility', 'hidden')
            .attr('x', xLoc)
            .attr('height', this.boxHeight)
            .style('fill', getLine(lineId, fig).props.edgecolor);
        this.label = fig.canvas
            .insert('text')
            .attr('class', 'mpld3-time-series-tooltip-text')
            .style('visibility', 'hidden')
            .style('text-anchor', 'left')
            .attr('dominant-baseline', 'central')
            .style('font-size', this.fontsize)
            .style('fill', 'white')
            .attr('x', xLoc + this.xPadding);
        this.circle = fig.canvas
            .insert('circle')
            .attr('class', 'mpld3-time-series-tooltip-circle')
            .style('visibility', 'hidden')
            .attr('r', 3)
            .attr('pointer-events', 'none')
            .style('fill', getLine(lineId, fig).props.edgecolor);
    }
    YTooltip.prototype.show = function () {
        this.background.style('visibility', 'visible');
        this.label.style('visibility', 'visible');
        this.circle.style('visibility', 'visible');
    };
    YTooltip.prototype.hide = function () {
        this.background.style('visibility', 'hidden');
        this.label.style('visibility', 'hidden');
        this.circle.style('visibility', 'hidden');
    };
    YTooltip.prototype.setValue = function (value) {
        this.label.text(getNumberFormatter(value)(value));
        var textWidth = this.label.node().getBBox().width;
        this.background.attr('width', textWidth + this.xPadding * 2);
    };
    YTooltip.prototype.setLocation = function (xLoc, yLoc, prevYLoc) {
        this.circle.attr('cx', xLoc).attr('cy', yLoc);
        if (yLoc < prevYLoc + this.boxHeight) {
            yLoc = prevYLoc + this.boxHeight;
        }
        this.background.attr('y', yLoc - this.boxHeight / 2);
        this.label.attr('y', yLoc);
        return yLoc;
    };
    return YTooltip;
}());
