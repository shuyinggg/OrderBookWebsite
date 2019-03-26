<template>
  <div id="mchart">
    <b-button-group size = 'sm'>
      <b-button variant="light" @click = "RedrawWeekly">1 W</b-button>
      <b-button variant="light" @click = "RedrawDaily">1 D</b-button>
      <b-button variant="light" @click = "RedrawHourly">1 H</b-button>
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
                left:60,
                right:20
            }
        }
    },
    mounted () {
        this.DrawChart('h');
    },
    methods: {
        getBandWidth() {
            const len = this.tradeHistory.length;
            if (len > 100) {
                return (this.clientWidth - this.margin.left - this.margin.right)/this.tradeHistory.length-0.5;
            } else {
                return (this.clientWidth - this.margin.left - this.margin.right)/this.tradeHistory.length-2;
            }
            
        },
        getInterval(s) {
           this.interval = s;
        },
        parseData(jdata) {
            var arr = Object.keys(jdata).map(function(k) { return jdata[k]});
            var timeParser = d3.timeParse("%Q");
            arr.map(function(a) {
                a.parsedTime = timeParser(a.open_time); //in standard time format
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
                        .classed("svg-container-m", true)
                        .append('svg')
                        .attr("preserveAspectRatio", "xMinYMin meet")
                        .attr("viewBox", "0 0 " + width + " " + height)
                        .classed("svg-content-responsive-m", true);
            /////////////////////////////CLIP AREA////////////////////////////////////////////////////////////
            //append clip to keep all the elements inside svg when zooming : define strict svg area
            svg.append("defs").append("clipPath")
            .attr("id", "clipupper")
            .append("rect")
            .attr("width", width- margin.right - margin.left)
            .attr("height", height -margin.bottom - margin.top - 100)
            .attr("transform",`translate(${margin.left},${margin.top})`)

            svg.append("defs").append("clipPath")
            .attr("id", "cliplower")
            .append("rect")
            .attr("width", width- margin.right - margin.left)
            .attr("height", 90)
            .attr("transform",`translate(${margin.left},${height - margin.bottom - 90})`)

            svg.append("defs").append("clipPath")
            .attr("id", "clipwhole")
            .append("rect")
            .attr("width", width- margin.right - margin.left)
            .attr("height", height - margin.top - margin.bottom)
            .attr("transform",`translate(${margin.left},0)`)
            return svg;
        },
        DrawChart(interval) {
            ////////////////////////////////////////PARAMETERS///////////////////////////////////////////////
            const svg = this.DrawChartBasics();
            const margin = this.margin;
            const height = this.clientHeight;
            const width = this.clientWidth;
            const bandwidth = this.getBandWidth();
            ////////////////////////////AXES///////////////////////////////////////////////////////////////////
            //x y scale set up
            var x = d3.scaleTime()
                        .domain([d3.timeDay.offset((d3.min(this.tradeHistory,function(d) {return d.parsedTime})),0),
                        d3.timeDay.offset(d3.max(this.tradeHistory,function(d) {return d.parsedTime}),1)])
                        // .domain(d3.timeWeek(d3.extent(this.tradeHistory, function(d) {return d.parsedTime})))
                        .range([margin.left, width - margin.right]);
                        //.ticks()  zoom
            var y = d3.scaleLinear()
                    .domain(
                        [d3.min(this.tradeHistory,function(d) {return d.l}),
                        d3.max(this.tradeHistory,function(d) {return d.h})]
                        )
                    .range([ height - margin.bottom-100,margin.top,])
            var ylower = d3.scaleLinear()
                    .domain([0, d3.max(this.tradeHistory, function(d) {return +d.v})])
                    .range([ height - margin.bottom, height - margin.bottom-90])
            var xAxis = d3.axisBottom(x);
            var yAxis = d3.axisLeft(y);
            var ylowerAxis = d3.axisLeft(ylower);
            ///////////////////////////////////////////DIFFERENT TICKS/////////////////////////////////////////
            var formatMillisecond = d3.timeFormat(".%L"),
                formatSecond = d3.timeFormat(":%S"),
                formatMinute = d3.timeFormat("%I:%M"),
                formatHour = d3.timeFormat("%I %p"),
                formatDay = d3.timeFormat("%a %d"),
                formatWeek = d3.timeFormat("%b %d"),
                formatMonth = d3.timeFormat("%B"),
                formatYear = d3.timeFormat("%Y");
            if (interval == 'w') {
                xAxis.ticks(d3.timeWeek);
            } else if (interval == 'd') {
                xAxis.ticks(d3.timeDay.every(2));
            } else {
                xAxis.tickFormat(function(d) { 
                    return (d3.timeSecond(d) < d ? formatMillisecond
                                    : d3.timeMinute(d) < d ? formatSecond
                                    : d3.timeHour(d) < d ? formatMinute
                                    : d3.timeDay(d) < d ? formatHour
                                    : d3.timeMonth(d) < d ? (d3.timeWeek(d) < d ? formatDay : formatWeek)
                                    : d3.timeYear(d) < d ? formatMonth
                                    : formatYear)(d)});
            }
            //draw x axis
            var gX = svg.append('g')
                    .attr('class', 'axis axis-x')
                    .attr('transform', `translate(0,${height - margin.bottom})`)
                    .call(xAxis)
                    .style("color","grey");
            //draw y and ylower
            this.DrawAxes(svg, yAxis, ylowerAxis)
            //draw y grid
            svg.append("g")			
                .attr("class", "grid")
                .attr("transform", `translate(${margin.left},0)`)
                .style("stroke-dasharray", "5 5")
                .call(yAxis.ticks(9)
                .tickSize(-width+margin.left+margin.right)
                .tickFormat(""))
                .style("color","grey")
                .attr("opacity",0.3)
            //////////////////////////////////CURSOR LINES///////////////////////////////////////////////////
            this.DrawCursorLines(svg);

            //////////////////////////////TOOLTIPS//////////////////////////////////////////////////////////////
            //append tooltip to display data in the top left corner
            var tooltip = d3.select('#mchart').select('.svg-container').append('g')
                            .attr("class","tooltip")
                            .style("opacity", 0)

            var tooltipx = d3.select("body").append('div')
                            //d3.select('#mchart').select('.svg-container-m').append('g').append('div')
                            .attr("class","tooltipxt")
                            //.attr("id","tooltip")
                            .style("opacity", 0)
                            // .style("border", "solid 0.5px gray")
                            // .style("text-align","center")
                            // .style("background","white")
                            // .style("border-radius","3px")

            var tooltipy = d3.select("body").append('div')
            //d3.select('#mchart').select('.svg-container-m').append('g')
                            .attr("class","tooltipyupper")
                            .style("opacity", 0)
                            // .style("border", "solid 0.5px gray")
                            // .style("text-align","center")
                            // .style("background","white")
                            // .style("border-radius","3px")

            var tooltipylower = d3.select("body").append('div')
            //d3.select('#mchart').select('.svg-container-m').append('g')
                            .attr("class","tooltipylower")
                            .style("opacity", 0)
                            // .style("border", "solid 0.5px gray")
                            // .style("text-align","center")
                            // .style("background","white")
                            // .style("border-radius","3px")

            // var tooltipv = d3.select('#mchart').select('.svg-container-m').append('g')
            //                 .attr("class","tooltip")
            //                 .attr("id","tooltipv")
            //                 .style("opacity", 0)
            //                 .style("text-align","center")
            //                 .style("border-radius","3px")

            ////////////////////////////////SVG ELEMENTS////////////////////////////////////////////////////////////////
            //svg elements
            //draw lower bar charts: v
            this.DrawVolumes(svg,x,ylower);

            //draw h-l line
            this.DrawHighLow(svg,x,y);

            //draw o c rect
            this.DrawOpenClose(svg,x,y);
    
            
            //////////////////////////////////////////////ARROWS////////////////////////////////////////////////////
            //these are the arrows to indicate min and max values
            const miny = d3.min(this.tradeHistory, d => d.l);
            const maxy = d3.max(this.tradeHistory, d => d.h);
            const minyx = this.tradeHistory.find( function(d) {
                return d.l == miny;
            }).parsedTime;
            const maxyx = this.tradeHistory.find( function(d) {
                return d.h == maxy;
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
                const timeFormatter = d3.timeFormat("%Y-%m-%d %H:%M");
                tooltipx.html(timeFormatter(l.parsedTime))
                .style('top', svg.node().getBoundingClientRect().height + 100 + 'px')
                .style('left', d3.event.clientX - 52+ 'px');
                tooltipx.style("opacity",1);
                //show tooltip y axis
                tooltipy.html("<font size = 1>" + y.invert(mouse[1]).toFixed(4) + "</font>")//.attr("transform", "translate(" + coord[0] + "," + (coord[1] - 20) + ")");
                .style('top', d3.event.clientY - 8+ 'px')
                .style('left', (document.body.offsetWidth - svg.node().getBoundingClientRect().width)/2 + 'px')
                tooltipy.style("opacity",1)

                //information box top left
                tooltip.html(
                    '<font size = "-5"> O:' + l.o + "  H:" + l.h + "  L:" + l.l + "  C:" + l.c + "  v:" + l.v+"</font>")
                .style("opacity", 1);

                // //Volume information for lower y
                // tooltipv.html(
                //     '<font size = "-5"> Volume:' + l.v+"</font>")
                //         .style("top", height - margin.bottom - 100 + 'px')
                //         .style('left', 0 + 'px');
                // tooltipv.style("opacity", 1);
            })
            .on('mouseout', function() {
                d3.select(".mouse-xline").style("opacity", 0);
                d3.select(".mouse-yline").style("opacity", 0);
                tooltip.style('opacity',0)
                tooltipx.style('opacity',0);
                tooltipy.style('opacity',0);
                tooltipylower.style("opacity",0)
                //tooltipv.style("opacity",0)
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
                //console.log(mouse)
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
                const timeFormatter = d3.timeFormat("%Y-%m-%d %H:%M");
                tooltipx.html(timeFormatter(l.parsedTime) )
                .style('top', svg.node().getBoundingClientRect().height + 100+ 'px')
                .style('left', d3.event.clientX - 52+ 'px');
                tooltipx.style("opacity",1)

                //show tooltip ylower
                tooltipylower.html("<font size = 1>" + ylower.invert(mouse[1]).toFixed(0) + "</font>")//.attr("transform", "translate(" + coord[0] + "," + (coord[1] - 20) + ")");
                .style('top', d3.event.clientY - 8 + 'px')
                .style('left', (document.body.offsetWidth - svg.node().getBoundingClientRect().width)/2 + 'px')
                tooltipylower.style("opacity",1)

                //information box top left
                tooltip.html(
                    '<font size = "-5"> O:' + l.o + "  H:" + l.h + "  L:" + l.l + "  C:" + l.c + "  v:" + l.v +"</font>")
                .style("opacity", 1);

                // tooltipv.html(
                //     '<font size = "-5"> Volume:' + l.v+"</font>")
                // .style("opacity", 1);
            })
            .on('mouseout', function() {
                d3.select(".mouse-xline").style("opacity", 0);
                d3.select(".mouse-yline").style("opacity", 0);
                tooltipylower.style("opacity",0);
                //tooltipv.style("opacity",0);
            })

            ///////////////////////////////////////////ZOOM////////////////////////////////////////////////////////////////
            const extent = [[0, 0], [width,height]];
            //const gX = d3.select('.axis axis-x') ;
            //implement zoom
            var zoom = d3.zoom()
            .scaleExtent([1,10])
            .translateExtent(extent)
            .extent(extent)
            .on('zoom',function() {
                var t = d3.event.transform;
                var xt = t.rescaleX(x);
                gX.call(xAxis.scale(xt)
                // .tickFormat(function(d) {
                //          if(d3.timeYear(d) < d) {
                //              return d3.timeFormat("%m/%d")(d)
                //          } else {
                //             return d3.timeFormat("%M")(d)
                // }})
                )
           
                d3.selectAll('.v').attr("x", function(d) {return xt(d.parsedTime)- bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
                d3.selectAll('.o-c').attr("x", function(d) {return xt(d.parsedTime) - bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
                d3.selectAll('.hover-cursor').attr("x", function(d) {return xt(d.parsedTime) - bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
                d3.selectAll('.h-l')
                                    .attr("d", function(l) {
                                        var d = "M" + xt(l.parsedTime) + "," + y(l.h);
                                        d += " " + xt(l.parsedTime) + "," + y(l.l);
                                        return d;
                                    })
                d3.selectAll('.min-arrow').attr('x1', function() {return xt(minyx) - 15})
                                      .attr('x2', function() {return xt(minyx)})

                d3.selectAll('.max-arrow').attr('x1', function() {return xt(maxyx) - 15})
                                      .attr('x2', function() {return xt(maxyx)})
                
            })
            if (interval == 'h') {
                svg.call(zoom)
                svg.call(zoom.transform, d3.zoomIdentity.scale(8,1));
            } else {
                svg.call(zoom);
            }
            
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
        DrawAxes(svg, yAxis, ylowerAxis) {
            //parameters
            const margin = this.margin;

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
                .attr("marker-end", "url(#marker-end)")
                .attr("clip-path", "url(#clipwhole)");
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
                .attr("marker-end", "url(#marker-end)")
                .attr("clip-path", "url(#clipwhole)");
    },
    DrawVolumes(svg,x,ylower) {
        //parameters
        const margin = this.margin;
        const height = this.clientHeight;
        const bandwidth = this.getBandWidth();
        //draw
        svg.append('g')
            .selectAll('rect-v')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',0.7)
            .attr("clip-path", "url(#cliplower)")
            .attr('class','v')
            .attr('width', bandwidth)
            .attr('height',function(d) {return height-margin.bottom-ylower(d.v)})
            .attr('x', function(d) {return x(d.parsedTime)- bandwidth/2})
            .attr('y',function(d) {return ylower(d.v)})
            .attr("fill", d => (d.o === d.c) ? "silver" : (d.o > d.c) ? "#9e1818ce" : "green")
    },
    DrawHighLow(svg,x,y) {
        svg.append('g')
            .selectAll('.line h-l')
            .data(this.tradeHistory).enter()
            .append('path')
            .attr('class','h-l')
            .attr("clip-path", "url(#clipupper)")
            .attr("d", function(l) {
                    var d = "M" + x(l.parsedTime) + "," + y(l.h);
                    d += " " + x(l.parsedTime) + "," + y(l.l);
                    //console.log(d);
                    return d;
            })
            .style("stroke", d => (d.o === d.c) ? "silver" : (d.o > d.c) ? "#9e1818ce" : "green")
            .style("stroke-width", "1px")
    },
    DrawOpenClose(svg,x,y) {
        //parameters
        const bandwidth = this.getBandWidth();
        //draw
        svg.append('g')
            .selectAll('rect-o-c')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',1)
            .attr('class','o-c')
            .attr("clip-path", "url(#clipupper)")
            .attr('width', bandwidth)
            .attr('height',function(d) {
                if (d.o < d.c) {
                    return y(d.o) - y(d.c);
                } else {
                    return y(d.c) - y(d.o);
                }
            })
            .attr('x', function(d) {return x(d.parsedTime) - bandwidth/2})
            .attr('y',function(d) {
                if (d.o < d.c) {
                    return y(d.c)
                } else {
                    return y(d.o)
                }
            })
            .attr("fill", d => (d.o === d.c) ? "silver" : (d.o > d.c) ? "#9e1818ce" : "green")
        },
        RedrawWeekly() {
            this.tradeHistory = this.parseData(trade);
            const arr = this.tradeHistory;
            const weekData = arr.filter(function(a,i) {
            return !i || d3.timeWeek(a.parsedTime).getTime() != d3.timeWeek(arr[i-1].parsedTime).getTime();  
            })
            weekData[0].parsedTime = d3.timeWeek.offset(weekData[1].parsedTime,-1);
            this.tradeHistory = weekData;
            d3.select('#mchart').select('.svg-container-m').remove();
            this.DrawChart('w');
        },
        RedrawDaily() {
            this.tradeHistory = this.parseData(trade);
            const arr = this.tradeHistory;
            const dayData = arr.filter(function(a,i) {
            return !i || d3.timeDay(a.parsedTime).getTime() != d3.timeDay(arr[i-1].parsedTime).getTime();  
            })
            dayData[0].parsedTime = d3.timeDay.offset(dayData[1].parsedTime,-1);
            this.tradeHistory = dayData;
            d3.select('#mchart').select('.svg-container-m').remove();
            this.DrawChart('d');
        },
        RedrawHourly() {
            this.tradeHistory = this.parseData(trade);
            d3.select('#mchart').select('.svg-container-m').remove();
            this.DrawChart('h');
        }
     
    }
}
</script>

<style>
.svg-container-m {
    display: inline-block;
    position: relative;
    width: 100%;
    padding-bottom: 47%; /* aspect ratio */
    vertical-align: top;
    overflow: hidden;
    background: rgba(219, 218, 218, 0.377);
    top: 0px;
}
.svg-content-responsive-m {
    display: inline-block;
    position: absolute;
    top: 10px;
    left: 0;
}
.tooltipxt {
    position: absolute;
    border: solid 0.5px gray;
    text-align:center;
    width: 100px;
    height: 17px;
    padding: 3px;
    background :white;
    pointer-events: none;
    font-size: 8px;
    opacity:0.5;
    border-radius: 3px; 
}
.tooltipxt::after {
  content: " ";
  position: absolute;
  bottom: 100%; /* At the right of the tooltip */
  left: 50%;
  margin-top: -3px;
  border-width: 3px;
  border-style: solid;
  border-color: transparent transparent  rgb(2, 2, 2) transparent;
}
.tooltipyupper {
    position: absolute;
    border: solid 0.5px gray;
    text-align:center;
    width: 50px;
    height: 17px;
    padding: 3px;
    background :white;
    pointer-events: none;
    font-size: 8px;
    opacity:0.5;
    border-radius: 3px; 
}
.tooltipyupper::after {
  content: " ";
  position: absolute;
  top: 50%; /* At the right of the tooltip */
  left: 100%;
  margin-top: -3px;
  border-width: 3px;
  border-style: solid;
  border-color: transparent transparent transparent  rgb(2, 2, 2);
}
.tooltipylower {
    position: absolute;
    border: solid 0.5px gray;
    text-align:center;
    width: 50px;
    height: 17px;
    padding: 3px;
    background :white;
    pointer-events: none;
    font-size: 8px;
    opacity:0.5;
    border-radius: 3px; 
}
.tooltipylower::after {
  content: " ";
  position: absolute;
  top: 50%; /* At the right of the tooltip */
  left: 100%;
  margin-top: -3px;
  border-width: 3px;
  border-style: solid;
  border-color: transparent transparent transparent  rgb(2, 2, 2);
}
</style>


