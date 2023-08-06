mpld3.register_plugin('interactive_legend', InteractiveLegend);
InteractiveLegend.prototype = Object.create(mpld3.Plugin.prototype);
InteractiveLegend.prototype.constructor = InteractiveLegend;
InteractiveLegend.prototype.requiredProps = ['line_ids', 'labels', 'alpha_visible', 'alpha_hidden', 'fontsize'];
function InteractiveLegend(fig, props) {
    mpld3.Plugin.call(this, fig, props);
}
InteractiveLegend.prototype.draw = function () {
    var fig = this.fig;
    var ax = fig.axes[0];
    var alphaVisible = this.props.alpha_visible;
    var alphaHidden = this.props.alpha_hidden;
    var lineIds = this.props.line_ids;
    var fontsize = this.props.fontsize;
    var labels = this.props.labels;
    var legendItems = [];
    for (var i = 0; i < labels.length; i++) {
        var label = labels[i];
        var line = mpld3.get_element(lineIds[i], fig);
        var hidden = isHidden(label);
        var legendItem = new LegendItem(label, line, hidden, alphaVisible, alphaHidden);
        legendItems.push(legendItem);
    }
    new Legend(fig, ax, legendItems, fontsize, onClickItem);
};
var LegendItem = (function () {
    function LegendItem(label, line, hidden, alphaVisible, alphaHidden) {
        this.label = label;
        this.line = line;
        this.alphaVisible = alphaVisible;
        this.alphaHidden = alphaHidden;
        if (hidden) {
            this.hide();
        }
        else {
            this.show();
        }
    }
    LegendItem.prototype.show = function () {
        this.line.props.isHidden = false;
        d3.select(this.line.path[0][0]).style('stroke-opacity', this.alphaVisible);
        saveVisible(this.label);
    };
    LegendItem.prototype.hide = function () {
        this.line.props.isHidden = true;
        d3.select(this.line.path[0][0]).style('stroke-opacity', this.alphaHidden);
        saveHidden(this.label);
    };
    LegendItem.prototype.getLabel = function () {
        return this.label;
    };
    LegendItem.prototype.isHidden = function () {
        return this.line.props.isHidden;
    };
    LegendItem.prototype.getColour = function () {
        return this.line.props.edgecolor;
    };
    return LegendItem;
}());
var Legend = (function () {
    function Legend(fig, ax, items, fontsize, onClickItem) {
        this.xPadding = 12;
        this.yPadding = 5;
        this.fig = fig;
        this.ax = ax;
        this.items = items;
        this.fontsize = fontsize;
        this.boxWidth = 1.6 * this.fontsize;
        this.boxHeight = 0.7 * this.fontsize;
        this.legend = fig.canvas.append('svg:g').attr('class', 'legend');
        this.boxes = [];
        this.labels = [];
        for (var i = 0; i < items.length; i++) {
            this.boxes.push(this.legend
                .data([items[i]])
                .append('rect')
                .attr('class', 'mpld3-interactive-legend-rect')
                .attr('height', this.boxHeight)
                .attr('width', this.boxWidth)
                .attr('stroke', function (d) { return d.getColour(); })
                .style('fill', function (d) { return (d.isHidden() ? 'white' : d.getColour()); })
                .on('click', onClickItem));
            this.labels.push(this.legend
                .data([items[i]])
                .append('text')
                .attr('class', 'mpld3-interactive-legend-text')
                .attr('font-size', this.fontsize)
                .attr('dominant-baseline', 'central')
                .text(function (d) { return d.getLabel(); }));
        }
        this.setPositions();
    }
    Legend.prototype.setPositions = function () {
        function warnWithToast(message) {
            document.dispatchEvent(new CustomEvent('autoplot-toast', { detail: { type: 'warning', message: message } }));
            console.warn(message);
        }
        var x = this.ax.position[0];
        var y = this.ax.position[1] + this.ax.height + 35;
        var newLine = true;
        var notEnoughSpace = false;
        for (var i = 0; i < this.boxes.length; i++) {
            if (notEnoughSpace) {
                this.boxes[i].attr('visibility', 'hidden');
                this.labels[i].attr('visibility', 'hidden');
                continue;
            }
            this.boxes[i].attr('x', x).attr('y', y - this.boxHeight / 2);
            x += this.boxWidth + this.fontsize / 3;
            this.labels[i].attr('x', x).attr('y', y);
            x += this.labels[i].node().getBBox().width + this.xPadding;
            if (x > this.fig.width) {
                if (newLine) {
                    var name_1 = this.items[i].getLabel();
                    warnWithToast("Legend label '" + name_1 + "' is very long and may cause issues with the layout.");
                    newLine = false;
                }
                else {
                    i -= 1;
                    y += this.fontsize + this.yPadding;
                    x = this.ax.position[0];
                    newLine = true;
                    if (y + this.fontsize > this.fig.height) {
                        warnWithToast("The legend labels can't all fit below the figure.");
                        notEnoughSpace = true;
                    }
                }
            }
            else {
                newLine = false;
            }
        }
    };
    return Legend;
}());
function onClickItem(d) {
    if (d.isHidden()) {
        d.show();
        d3.select(this).style('fill', d.getColour());
    }
    else {
        d.hide();
        d3.select(this).style('fill', 'white');
    }
}
function saveVisible(label) {
    window.sessionStorage.removeItem("autoplot-legend-" + label);
}
function saveHidden(label) {
    window.sessionStorage.setItem("autoplot-legend-" + label, 'hidden');
}
function isHidden(label) {
    return window.sessionStorage.getItem("autoplot-legend-" + label) === 'hidden';
}
