<template>
  <div id="mchart">
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
            clientHeight: 400
        }
    },
    mounted () {
        this.createChart(this.clientWidth,this.clientHeight)
    },
    computed: {
        getx0 () {
            return d3.min(this.tradeHistory, d => d.parsedTime.getTime());
        },
        getxend () {
            return d3.max(this.tradeHistory, d => d.parsedTime.getTime());
        },
        // getyend () {
        //     return d3.max([d3.max(this.BIDdata, d => d.cumSIZE),d3.max(this.ASKdata, d => d.cumSIZE)]);
        // }
    },
    methods: {
        parseData(jdata) {
            var arr = Object.keys(jdata).map(function(k) { return jdata[k]});
            var timeParser = d3.timeParse("%m/%d/%Y");
            arr.map(function(a) {
                a.parsedTime = timeParser(a.Time); //in Standard time format
            })
            return arr; 
        },
        createChart(width, height) {
            const margin = {
                top:20,
                bottom:30,
                left:40,
                right:20
            };
            
            //draw responsive svg 
            const svg = d3.select('#mchart')
                        .append('div')
                        .classed("svg-container", true)
                        .append('svg')
                        .attr("preserveAspectRatio", "xMinYMin meet")
                        .attr("viewBox", "0 0 " + width + " " + height)
                        .classed("svg-content-responsive", true);

            //let dates = this.tradeHistory.map(a => a.parsedTime);
            //x scale 
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
            //console.log(d3.extent(this.tradeHistory, function(d) { return d.parsedTime;}));
            
            var xAxis = d3.axisBottom(x);
            var yAxis = d3.axisLeft(y);
            var ylowerAxis = d3.axisLeft(ylower);
            //draw x axis
            var gX = svg.append('g')
            .attr('class', 'axis axis-x')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(xAxis
            .tickFormat(function(d) {
                         if(d3.timeYear(d) < d) {
                             return d3.timeFormat("%m/%d")(d)
                         } else {
                            return d3.timeFormat("%M")(d)
                         }
                     })
            )
            .style("color","grey")

            //draw upper y
            var gY = svg.append('g')
            .attr('class','axis axis-y')
            .attr("transform",`translate(${margin.left},0)`)
            .call(yAxis)
            .style("color","grey")
            .style("font-size","8px")
            //draw lower y
            var gYlower = svg.append('g')
            .attr('class','axis axis-y')
            .attr("transform",`translate(${margin.left},0)`)
            .call(ylowerAxis)
            .style("color","grey")
            .style("font-size","8px")

            //append clip to keep all the elements inside svg when zooming
            const bandwidth = (width - margin.left - margin.right)/this.tradeHistory.length - 2;
            svg.append("defs").append("clipPath")
            .attr("id", "clip")
            .append("rect")
            .attr("width", width- margin.right - margin.left + bandwidth/2)
            .attr("height", height -margin.bottom)
            .attr("transform",`translate(${margin.left},${margin.top})`)

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
            //append tooltip to display data in the top left corner
            var tooltip = d3.select('#mchart').select('.svg-container').append('g')
                            .attr("class","tooltip")
                            .style("opacity", 0)

            //draw lower bar charts
            svg.append('g')
            .selectAll('rect-volume')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',0.7)
            .attr("clip-path", "url(#clip)")
            .attr('class','volume')
            .attr('width', bandwidth)
            .attr('height',function(d) {return height-margin.bottom-ylower(d.Volume)})
            .attr('x', function(d) {return x(d.parsedTime) - bandwidth/2})
            .attr('y',function(d) {return ylower(d.Volume)})
            .attr("fill", d => (d.Open === d.Close) ? "silver" : (d.Open > d.Close) ? "#9e1818ce" : "green")

            //draw high-low line
            svg.append('g')
            .selectAll('.line high-low')
            .data(this.tradeHistory).enter()
            .append('path')
            .attr('class','high-low')
            .attr("clip-path", "url(#clip)")
            .attr("d", function(l) {
                    var d = "M" + x(l.parsedTime) + "," + y(l.High);
                    d += " " + x(l.parsedTime) + "," + y(l.Low);
                    //console.log(d);
                    return d;
            })
            .style("stroke", d => (d.Open === d.Close) ? "silver" : (d.Open > d.Close) ? "#9e1818ce" : "green")
            .style("stroke-width", "1px")

            //draw open close rect
            svg.append('g')
            .selectAll('rect-open-close')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',1)
            .attr('class','open-close')
            .attr("clip-path", "url(#clip)")
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

            //draw bars for cursor
            svg.selectAll('rect-hover-cursor')
            .data(this.tradeHistory).enter()
            .append('rect')
            .style('opacity',0)
            .attr('class','hover-cursor')
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

                //show tooltip to display data
                tooltip.html(
                    '<font size = "-5"> O:' + l.Open.toFixed(4) + "  H:" + l.High.toFixed(4) + "  L:" + l.Low.toFixed(4) + "  C:" + l.Close.toFixed(4) + "  Volume:" + l.Volume.toFixed(4)+"</font>")
                .style("opacity", 1);
            })
            .on('mouseout', function() {
                d3.select(".mouse-xline").style("opacity", 0);
                d3.select(".mouse-yline").style("opacity", 0);
            })
            
            const extent = [[0, 0], [width,height]];
            //implement zoom
            var zoom = d3.zoom()
            .scaleExtent([1,80])
            .translateExtent(extent)
            .extent(extent)
            .on('zoom',function() {
                var t = d3.event.transform;
                var xt = t.rescaleX(x);
                var yt = t.rescaleY(y);
                var ylowert = t.rescaleY(ylower);
                gX.call(xAxis.scale(xt)
                .tickFormat(function(d) {
                         if(d3.timeYear(d) < d) {
                             return d3.timeFormat("%m/%d")(d)
                         } else {
                            return d3.timeFormat("%M")(d)
                }})
                )
                gY.call(yAxis.scale(yt))
                gYlower.call(ylowerAxis.scale(ylowert))
           
            d3.selectAll('.volume').attr("x", function(d) {return xt(d.parsedTime)- bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
            d3.selectAll('.open-close').attr("x", function(d) {return xt(d.parsedTime) - bandwidth * t.k/2})
                                    .attr("width", function() {return bandwidth * t.k})
                
            d3.selectAll('.high-low')
                .attr("d", function(l) {
                    var d = "M" + xt(l.parsedTime) + "," + y(l.High);
                    d += " " + xt(l.parsedTime) + "," + y(l.Low);
                    return d;
            })
                
        })

        svg.call(zoom);
        }
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
.tooltip {
    position: absolute;
    padding: 2px;
    border-radius: 2px;
    font-size: 8px;
}
</style>


