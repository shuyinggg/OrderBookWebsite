<template>
  <div id="mchart">
    <b-button-group size = 'sm'>
      <b-button variant="light" @click = "changeTicks('d')">1 D</b-button>
      <b-button variant="light" @click = "changeTicks('h')">1 H</b-button>
    </b-button-group>
  </div>
</template>
<script>
import * as d3 from 'd3';
import trade from '@/assets/trade.json'

export default {
    name: 'mchart',
    data () {
        return {
            tradeHistory: this.parseData(trade),
            clientWidth: 900,
            clientHeight: 400,
            interval: 'd',
            margin:{
                top:20,
                bottom:20,
                left:40,
                right:20
            }
        }
    },
    mounted () {
        this.DrawChart();
    },
    // computed: {
    //     getx0 () {
    //         return d3.min(this.tradeHistory, d => d.parsedTime.getTime());
    //     },
    //     getxend () {
    //         return d3.max(this.tradeHistory, d => d.parsedTime.getTime());
    //     },
    // },
    methods: {
        getBandWidth() {
            return (this.clientWidth- this.margin.left - this.margin.right)/this.tradeHistory.length - 2;
        },
        getInterval(s) {
           this.interval = s;
        },
        parseData(jdata) {
            var arr = Object.keys(jdata).map(function(k) { return jdata[k]});
            var timeParser = d3.timeParse("%m/%d/%Y");
            arr.map(function(a) {
                a.parsedTime = timeParser(a.Time); //in standard time format
            })
            return arr; 
        },
        DrawChartBasics() {
            //////////////////////////INITIALIZE SVG////////////////////////////////////////////////////////////////////
            //draw responsive svg 
            const height = this.clientHeight;
            const width = this.clientWidth;
            const margin = this.margin;
            const svg = d3.select('#mchart')
                        .append('div')
                        .classed("svg-container", true)
                        .append('svg')
                        .attr("preserveAspectRatio", "xMinYMin meet")
                        .attr("viewBox", "0 0 " + width + " " + height)
                        .classed("svg-content-responsive", true);
            /////////////////////////////CLIP AREA////////////////////////////////////////////////////////////
            //append clip to keep all the elements inside svg when zooming : define strict svg area
            const bandwidth = this.getBandWidth();
            svg.append("defs").append("clipPath")
            .attr("id", "clipupper")
            .append("rect")
            .attr("width", width- margin.right - margin.left + bandwidth/2)
            .attr("height", height -margin.bottom - margin.top - 100)
            .attr("transform",`translate(${margin.left},${margin.top})`)

            svg.append("defs").append("clipPath")
            .attr("id", "cliplower")
            .append("rect")
            .attr("width", width- margin.right - margin.left + bandwidth/2)
            .attr("height", 90)
            .attr("transform",`translate(${margin.left},${height - margin.bottom - 90})`)
            return svg;
        },
        DrawChart() {
            ////////////////////////////////////////PARAMETERS///////////////////////////////////////////////
            const svg = this.DrawChartBasics();
            const margin = this.margin;
            const height = this.clientHeight;
            const width = this.clientWidth;
            const bandwidth = this.getBandWidth();
            ////////////////////////////AXES///////////////////////////////////////////////////////////////////
            //x y scale set up
            var x = d3.scaleTime()
                        .domain([d3.timeWeek(d3.min(this.tradeHistory,function(d) {return d.parsedTime})),
                        d3.max(this.tradeHistory,function(d) {return d.parsedTime})])
                        // .domain(d3.timeWeek(d3.extent(this.tradeHistory, function(d) {return d.parsedTime})))
                        .range([margin.left, width - margin.right]);
                        //.ticks()  zoom
            var y = d3.scaleLinear()
                    .domain(
                        [d3.min(this.tradeHistory,function(d) {return d.Low}),
                        d3.max(this.tradeHistory,function(d) {return d.High})]
                        )
                    .range([ height - margin.bottom-100,margin.top,])
            var ylower = d3.scaleLinear()
                    .domain(d3.extent(this.tradeHistory,function(d) {return d.Volume}))
                    .range([ height - margin.bottom, height - margin.bottom-90])
            
            var xAxis = d3.axisBottom(x);
            var yAxis = d3.axisLeft(y);
            var ylowerAxis = d3.axisLeft(ylower);
            xAxis.tickFormat(function(d) {
                         if( d3.timeMonth(d) < d) {
                             return d3.timeFormat("%m/%d")(d)
                         } else {
                            return d3.timeFormat("%M")(d)
                         }
                     })
            this.DrawAxes(svg,xAxis, yAxis, ylowerAxis)

            //////////////////////////////////CURSOR LINES///////////////////////////////////////////////////
            this.DrawCursorLines(svg);

            //////////////////////////////TOOLTIPS//////////////////////////////////////////////////////////////
            //append tooltip to display data in the top left corner
            var tooltip = d3.select('#mchart').select('.svg-container').append('g')
                            .attr("class","tooltip")
                            .style("opacity", 0)

            var tooltipx = d3.select('#mchart').select('.svg-container').append('g')
                            .attr("class","tooltip")
                            .attr("id","tooltipx")
                            .style("opacity", 0)
                            .style("border", "solid 0.5px gray")
                            .style("text-align","center")
                            .style("background","white")
                            .style("border-radius","3px")

            var tooltipy = d3.select('#mchart').select('.svg-container').append('g')
                            .attr("class","tooltip")
                            .attr("id","tooltipy")
                            .style("opacity", 0)
                            .style("border", "solid 0.5px gray")
                            .style("text-align","center")
                            .style("background","white")
                            .style("border-radius","3px")

            var tooltipylower = d3.select('#mchart').select('.svg-container').append('g')
                            .attr("class","tooltip")
                            .attr("id","tooltipylower")
                            .style("opacity", 0)
                            .style("border", "solid 0.5px gray")
                            .style("text-align","center")
                            .style("background","white")
                            .style("border-radius","3px")

            ////////////////////////////////SVG ELEMENTS////////////////////////////////////////////////////////////////
            //svg elements
            //draw lower bar charts: Volume
            this.DrawVolumes(svg,x,ylower);

            //draw high-low line
            this.DrawHighLow(svg,x,y);

            //draw open close rect
            this.DrawOpenClose(svg,x,y);
    
            
            //////////////////////////////////////////////ARROWS////////////////////////////////////////////////////
            //these are the arrows to indicate min and max values
            const miny = d3.min(this.tradeHistory, d => d.Low);
            const maxy = d3.max(this.tradeHistory, d => d.High);
            const minyx = this.tradeHistory.find( function(d) {
                return d.Low == miny;
            }).parsedTime;
            const maxyx = this.tradeHistory.find( function(d) {
                return d.High == maxy;
            }).parsedTime;
            this.DrawArrows(svg,x,y,miny,maxy,minyx,maxyx);

            /////////////////////////////////////////////CURSOR-RECTS/////////(SHOW-TOOLTIPS)//////////////////////////////////////
            //draw bars for cursor
            //upper vertical bars
            svg.selectAll('rect-hover-cursor')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',0)
            .attr('class','hover-cursor')
            .attr("clip-path", "url(#clipupper)")
            .attr('width', bandwidth)
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.parsedTime) - bandwidth/2})
            .attr('y',function(_) {return y(_)})
            .on('mouseover', function() {
                d3.select(".mouse-xline").style("opacity", 1);
                d3.select(".mouse-yline").style("opacity", 1);
            }) 
            .on('mousemove', function(l) {
                //cursor
                var mouse = d3.mouse(this);
                    d3.select(".mouse-xline")
                    .attr("d", function() {
                    var d = "M" + mouse[0] + "," + (height-margin.bottom);
                    d += " " + mouse[0] + "," + margin.top;
                    //console.log(d);
                    return d;
                    });
                    d3.select(".mouse-yline")
                    .attr("d", function() {
                    var d = "M" + margin.left + "," + mouse[1];
                    d += " " + (width-margin.right) + "," + mouse[1];
                    //console.log(d);
                    return d;
                    });
                //show tooltip x axis
                tooltipx.html("<font size = 1>" + l.Time + "</font>")//.attr("transform", "translate(" + coord[0] + "," + (coord[1] - 20) + ")");
                .style('top', (svg.node().getBoundingClientRect().height)+ 'px')
                .style('left', (mouse[0]*svg.node().getBoundingClientRect().height/height) - 25 + 'px')
                tooltipx.style("opacity",1)

                //show tooltip y axis
                tooltipy.html("<font size = 1>" + y.invert(mouse[1]).toFixed(0) + "</font>")//.attr("transform", "translate(" + coord[0] + "," + (coord[1] - 20) + ")");
                .style('top', (mouse[1]*svg.node().getBoundingClientRect().height/height)+ 'px')
                .style('left', 0 + 'px')
                tooltipy.style("opacity",1)
                //console.log(y.invert(mouse[1]))

                //information box top left
                tooltip.html(
                    '<font size = "-5"> O:' + l.Open.toFixed(4) + "  H:" + l.High.toFixed(4) + "  L:" + l.Low.toFixed(4) + "  C:" + l.Close.toFixed(4) + "  Volume:" + l.Volume.toFixed(4)+"</font>")
                .style("opacity", 1);
            })
            .on('mouseout', function() {
                d3.select(".mouse-xline").style("opacity", 0);
                d3.select(".mouse-yline").style("opacity", 0);
                tooltip.style('opacity',0)
                tooltipx.style('opacity',0);
                tooltipy.style('opacity',0);
                tooltipylower.style("opacity",0)
            })

            ///lower vertical bars
            // upper vertical bars
            svg.selectAll('rect-hover-cursor')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',0)
            .attr('class','hover-cursor')
            .attr("clip-path", "url(#cliplower)")
            .attr('width', bandwidth)
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.parsedTime) - bandwidth/2})
            .attr('y',function(_) {return y(_)})
            .on('mouseover', function() {
                d3.select(".mouse-xline").style("opacity", 1);
                d3.select(".mouse-yline").style("opacity", 1);
            }) 
            .on('mousemove', function(l) {
                //cursor
                var mouse = d3.mouse(this);
                    d3.select(".mouse-xline")
                    .attr("d", function() {
                    var d = "M" + mouse[0] + "," + (height-margin.bottom);
                    d += " " + mouse[0] + "," + margin.top;
                    //console.log(d);
                    return d;
                    });
                    d3.select(".mouse-yline")
                    .attr("d", function() {
                    var d = "M" + margin.left + "," + mouse[1];
                    d += " " + (width-margin.right) + "," + mouse[1];
                    //console.log(d);
                    return d;
                    });
                //show tooltip x axis
                tooltipx.html("<font size = 1>" + l.Time + "</font>")//.attr("transform", "translate(" + coord[0] + "," + (coord[1] - 20) + ")");
                .style('top', (svg.node().getBoundingClientRect().height)+ 'px')
                .style('left', (mouse[0]*svg.node().getBoundingClientRect().height/height) - 25 + 'px')
                tooltipx.style("opacity",1)

                //show tooltip ylower
                tooltipylower.html("<font size = 1>" + ylower.invert(mouse[1]).toFixed(0) + "</font>")//.attr("transform", "translate(" + coord[0] + "," + (coord[1] - 20) + ")");
                .style('top', (mouse[1]*svg.node().getBoundingClientRect().height/height)+ 'px')
                .style('left', 0 + 'px')
                tooltipylower.style("opacity",1)

                //information box top left
                tooltip.html(
                    '<font size = "-5"> O:' + l.Open.toFixed(4) + "  H:" + l.High.toFixed(4) + "  L:" + l.Low.toFixed(4) + "  C:" + l.Close.toFixed(4) + "  Volume:" + l.Volume.toFixed(4)+"</font>")
                .style("opacity", 1);
            })
            .on('mouseout', function() {
                d3.select(".mouse-xline").style("opacity", 0);
                d3.select(".mouse-yline").style("opacity", 0);
                tooltipylower.style("opacity",0)
            })

            ///////////////////////////////////////////ZOOM////////////////////////////////////////////////////////////////
            const extent = [[0, 0], [width,height]];
            const gX = d3.select('.axis axis-x') ;
            //implement zoom
            var zoom = d3.zoom()
            .scaleExtent([1,10])
            .translateExtent(extent)
            .extent(extent)
            .on('zoom',function() {
                var t = d3.event.transform;
                var xt = t.rescaleX(x);
                gX.call(xAxis.scale(xt)
                .tickFormat(function(d) {
                         if(d3.timeYear(d) < d) {
                             return d3.timeFormat("%m/%d")(d)
                         } else {
                            return d3.timeFormat("%M")(d)
                }})
                )
           
                d3.selectAll('.volume').attr("x", function(d) {return xt(d.parsedTime)- bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
                d3.selectAll('.open-close').attr("x", function(d) {return xt(d.parsedTime) - bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
                d3.selectAll('.hover-cursor').attr("x", function(d) {return xt(d.parsedTime) - bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
                d3.selectAll('.high-low')
                                    .attr("d", function(l) {
                                        var d = "M" + xt(l.parsedTime) + "," + y(l.High);
                                        d += " " + xt(l.parsedTime) + "," + y(l.Low);
                                        return d;
                                    })
                d3.selectAll('.min-arrow').attr('x1', function() {return xt(minyx) - 15})
                                      .attr('x2', function() {return xt(minyx)})

                d3.selectAll('.max-arrow').attr('x1', function() {return xt(maxyx) - 15})
                                      .attr('x2', function() {return xt(maxyx)})
                
            })
            svg.call(zoom);
    },
    DrawCursorLines(svg) {
        /////////////////////////////CURSOR LINE////////////////////////////////////////////////////////////
            //append cursor lines x and y
            var mouseX = svg.append("g")
                .attr("class", "mouse-over-effects");

                mouseX.append("path") // this is the black vertical line to follow mouse
                .attr("class", "mouse-xline")
                .style("stroke", "grey")
                .style("stroke-width", "1px")
                .style("opacity", 0);

            var mouseY = svg.append("g")
                .attr("class", "mouse-over-effects");

                mouseY.append("path") // this is the black vertical line to follow mouse
                .attr("class", "mouse-yline")
                .style("stroke", "grey")
                .style("stroke-width", "1px")
                .style("opacity", 0);

    },
    DrawAxes(svg, xAxis, yAxis, ylowerAxis) {
        //parameters
        const margin = this.margin;
        const height = this.clientHeight;
        //draw x axis
        svg.append('g')
        .attr('class', 'axis axis-x')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(xAxis)
        .style("color","grey")

        //draw upper y
        svg.append('g')
        .attr('class','axis axis-y')
        .attr("transform",`translate(${margin.left},0)`)
        .call(yAxis)
        .style("color","grey")
        .style("font-size","8px")
        //draw lower y
        svg.append('g')
        .attr('class','axis axis-y')
        .attr("transform",`translate(${margin.left},0)`)
        .call(ylowerAxis)
        .style("color","grey")
        .style("font-size","8px")
    },
    DrawArrows(svg,x,y,miny,maxy,minyx,maxyx) {
        //draw arrows to indicate min max
            svg.append("svg:defs").append("svg:marker")
            .attr("id", "marker-end")
            .attr("refX", 6)
            .attr("refY", 6)
            .attr("markerWidth", 30)
            .attr("markerHeight", 30)
            .attr("markerUnits","userSpaceOnUse")
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M 0 0 6 6 0 12 3 6")
            .style("fill", "black");
            //min line             
            svg.append('g')
                .append("line")
                .attr('class','min-arrow')
                .attr("x1",  x(minyx) - 15)
                .attr("y1", y(miny))
                .attr("x2", x(minyx))
                .attr("y2", y(miny))
                .attr("stroke-width", 1)
                .attr("stroke", "black")
                .attr("marker-end", "url(#marker-end)");
            //max line
            svg.append('g')
                .append("line")
                .attr('class','max-arrow')
                .attr("x1",  x(maxyx) - 15)
                .attr("y1", y(maxy))
                .attr("x2", x(maxyx))
                .attr("y2", y(maxy))
                .attr("stroke-width", 1)
                .attr("stroke", "black")
                .attr("marker-end", "url(#marker-end)");
    },
    DrawVolumes(svg,x,ylower) {
        //parameters
        const margin = this.margin;
        const height = this.clientHeight;
        const bandwidth = this.getBandWidth();
        //draw
        svg.append('g')
            .selectAll('rect-volume')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',0.7)
            .attr("clip-path", "url(#cliplower)")
            .attr('class','volume')
            .attr('width', bandwidth)
            .attr('height',function(d) {return height-margin.bottom-ylower(d.Volume)})
            .attr('x', function(d) {return x(d.parsedTime) - bandwidth/2})
            .attr('y',function(d) {return ylower(d.Volume)})
            .attr("fill", d => (d.Open === d.Close) ? "silver" : (d.Open > d.Close) ? "#9e1818ce" : "green")
    },
    DrawHighLow(svg,x,y) {
        svg.append('g')
            .selectAll('.line high-low')
            .data(this.tradeHistory).enter()
            .append('path')
            .attr('class','high-low')
            .attr("clip-path", "url(#clipupper)")
            .attr("d", function(l) {
                    var d = "M" + x(l.parsedTime) + "," + y(l.High);
                    d += " " + x(l.parsedTime) + "," + y(l.Low);
                    //console.log(d);
                    return d;
            })
            .style("stroke", d => (d.Open === d.Close) ? "silver" : (d.Open > d.Close) ? "#9e1818ce" : "green")
            .style("stroke-width", "1px")
    },
    DrawOpenClose(svg,x,y) {
        //parameters
        const bandwidth = this.getBandWidth();
        //draw
        svg.append('g')
            .selectAll('rect-open-close')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',1)
            .attr('class','open-close')
            .attr("clip-path", "url(#clipupper)")
            .attr('width', bandwidth)
            .attr('height',function(d) {
                if (d.Open < d.Close) {
                    return y(d.Open) - y(d.Close);
                } else {
                    return y(d.Close) - y(d.Open);
                }
            })
            .attr('x', function(d) {return x(d.parsedTime) - bandwidth/2})
            .attr('y',function(d) {
                if (d.Open < d.Close) {
                    return y(d.Close)
                } else {
                    return y(d.Open)
                }
            })
            .attr("fill", d => (d.Open === d.Close) ? "silver" : (d.Open > d.Close) ? "#9e1818ce" : "green")
    },
        
            
    }
}
</script>

<style scoped>
.svg-container {
    display: inline-block;
    position: relative;
    width: 100%;
    padding-bottom: 70%; /* aspect ratio */
    vertical-align: top;
    overflow: hidden;
    background: rgba(219, 218, 218, 0.377);
    top: 0px;
}
.svg-content-responsive {
    display: inline-block;
    position: absolute;
    top: 10px;
    left: 0;
}
#tooltipx {
    position: relative;
    padding: 2px;
    border-radius: 2px;
    font-size: 8px;
}
.svg-container #tooltipx::after {
  content: " ";
  position: relative;
  bottom: 100%; 
  left: 50%;
  margin-top: -3px;
  border-width: 3px;
  border-style: solid;
  border-color: transparent transparent  rgb(2, 2, 2) transparent;
}
.svg-container #tooltipy {
    position: relative;
    padding: 2px;
    border-radius: 2px;
    font-size: 8px;
}
.svg-container #tooltipylower {
    position: relative;
    padding: 2px;
    border-radius: 2px;
    font-size: 8px;
}
</style>


