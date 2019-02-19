<template>
        <div id="chart" ref="chart">
        </div>
</template>

<script>
import  * as d3 from 'd3'
import bid from '@/assets/bid.json'
import ask from '@/assets/ask.json'

export default {
    name: 'chart',
    data() {
        return {
            //BIDdata and ASKdata only have length 50
            BIDdata: this.parseBID(bid),
            ASKdata: this.parseASK(ask),
            clientWidth: 900,
            clientHeight: 500
        }
    },
    mounted () {
                this.createChart(this.clientWidth,this.clientHeight)
    },
    computed: {
        getx0 () {
            return d3.min(this.BIDdata, d => d.BID);
        },
        getxend () {
            return d3.max(this.ASKdata, d => d.ASK);
        },
        getyend () {
            return d3.max([d3.max(this.BIDdata, d => d.cumSIZE),d3.max(this.ASKdata, d => d.cumSIZE)]);
        }
    },
    methods: {
        parseBID(jdata) {
            var arr = Object.keys(jdata).map(function(k) { return jdata[k]});
            arr = arr.sort((a,b)=>(a.BID > b.BID? -1:1)); //descend
            //add a new field in json array to store the cumulative size
            var sum = 0;
            arr.map(function(a) {
                a.cumSIZE = sum + a.SIZE;
                sum = a.cumSIZE;
            })
            //plot only the top 50 entries
            return arr.slice(0,50); 
        },
        parseASK(jdata) {
            var arr = Object.keys(jdata).map(function(k) { return jdata[k]});
            arr = arr.sort((a,b)=>(a.ASK > b.ASK? 1:-1)); //ascend
            //add a new field in json array to store the cumulative size
            var sum = 0;
            arr.map(function(a) {
                a.cumSIZE = sum + a.SIZE;
                sum = a.cumSIZE;
            })
            //plot only the top 50 entries
            return arr.slice(0,50); 
        },
        createChart(width, height) {
            const margin = {
                top:20,
                bottom:30,
                left:40,
                right:20
            };
            
            //draw responsive svg 
            const svg = d3.select('#chart')
                        .append('div')
                        .classed("svg-container", true)
                        .append('svg')
                        .attr("preserveAspectRatio", "xMinYMin meet")
                        .attr("viewBox", "0 0 " + width + " " + height)
                        .classed("svg-content-responsive", true); 
            const x = d3.scaleLinear()
                        .range([margin.left, width - margin.right])
                        .domain([this.getx0,this.getxend]);
            const y = d3.scaleLinear()
                        .range([height - margin.bottom, margin.top])
                        .domain([0, this.getyend]);
            
            //append axes
            svg.append('g')
            .attr('class', 'axis axis-x')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x))
            .style("color","grey")
            svg.append('g')
            .attr('class','axis axis-y')
            .attr("transform",`translate(${margin.left},0)`)
            .call(d3.axisLeft(y))
            .style("color","grey")

            //append grids
            svg.append("g")			
                .attr("class", "grid")
                .attr("transform", `translate(0,${height - margin.bottom})`)
                .style("stroke-dasharray", "5 5")
                .call(d3.axisBottom(x)
                    .ticks(8)
                    .tickSize(-height)
                    .tickFormat(""))
                .style("color","grey")
                .attr("opacity",0.3)
            svg.append("g")			
                .attr("class", "grid")
                .attr("transform", `translate(${margin.left},0)`)
                .style("stroke-dasharray", "5 5")
                .call(d3.axisLeft(y).ticks(6)
                .tickSizeInner(-width)
                .tickFormat(""))
                .style("color","grey")
                .attr("opacity",0.3)

            //append tooltip
            var tooltipBID = d3.select("body")
                        .append("div")
                        .attr("class", "tooltipbid")
                        .style("opacity",0)
                        .style("position","absolute")
                        .style("text-align", "left")
                        .style("width", "160px")
                        .style("height", "auto")
                        .style("padding", "5px")
                        .style("background", "beige")
                        .style("border-radius","8px")
                        .style("pointer-events", "none");
            var tooltipASK = d3.select("body")
                        .append("div")
                        .attr("class", "tooltipask")
                        .style("opacity",0)
                        .style("position","absolute")
                        .style("text-align", "left")
                        .style("width", "160px")
                        .style("height", "auto")
                        .style("padding", "5px")
                        .style("background", "beige")
                        .style("border-radius","8px")
                        .style("pointer-events", "none");

            //area generator
            const areaBID = d3.area()
                        .x(d => x(d.BID))
                        .y0(y(0))
                        .y1(d => y(d.cumSIZE));
            const areaASK = d3.area()
                        .x(d => x(d.ASK))
                        .y0(y(0))
                        .y1(d => y(d.cumSIZE));

            //line generator
            const lineBID = d3.line()
                        .x(d => x(d.BID))
                        .y(d => y(d.cumSIZE));

            const lineASK = d3.line()
                        .x(d => x(d.ASK))
                        .y(d => y(d.cumSIZE));
            //append lines 
            svg.append('path')
            .datum(this.BIDdata)
            .attr("fill", "none")
            .attr("d",lineBID)
            .attr("stroke","green")
            .attr("stroke-width",2.5)
            svg.append('path')
            .datum(this.ASKdata)
            .attr("fill", "none")
            .attr("d",lineASK)
            .attr("stroke","darkred")
            .attr("stroke-width",2.5)

            //append area for shaded area under the line
            svg.append('path')
            .datum(this.BIDdata)
            .attr("fill", "green")
            .attr("opacity",0.15)
            .attr("d",areaBID)
            svg.append('path')
            .datum(this.ASKdata)
            .attr("fill", "darkred")
            .attr("opacity",0.15)
            .attr("d",areaASK)

            //append tooltip cursor (the vertical line) for bid
            const bandwidth = width/100;
            svg.selectAll('rect.hover-line-bid')
            .data(this.BIDdata).enter()
            .append('rect')
            .attr('id',function(d,i) {
                return 'bline-'+i;
            })
            .attr('class','hover-line-bid')
            .style('opacity',0)
            .attr('width',1)
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.BID)})
            .attr('y',function(_) {return y(_)})
            .style('fill',"white")
            //append tooltip hover box for bid (in that box show tooltip)
            svg.selectAll('rect.hover-box-bid')
            .data(this.BIDdata).enter()
            .append('rect')
            .style('opacity',0)
            .attr('class','hover-box-bid')
            .attr('width',bandwidth)
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.BID)})
            .attr('y',function(_) {return y(_)})
            .on('mouseover',function(d,i) {
                const currLine = '#bline-'+i;
                d3.select(currLine).style('opacity',0.5);
                tooltipBID.style("opacity", 0.7);
                tooltipBID.html("<strong>SUM:</strong> <span style='color:grey'>" + d.SUM.toFixed(4) + "</span><br/><strong>BID:</strong> <span style='color:grey'>" + d.BID.toFixed(4)+ "</span><br/><strong>SIZE: </strong> <span style='color:grey'>" + d.SIZE.toFixed(3) + "</span>")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            }).on("mouseout", function(d,i) {
                tooltipBID.style("opacity", 0);
                // hover line
                const currentLine = '#bline-' + i;
                d3.select(currentLine).style('opacity', 0);
            });

            //append tooltip cursor (the vertical line) for ask
            svg.selectAll('rect.hover-line-ask')
            .data(this.ASKdata).enter()
            .append('rect')
            .attr('id',function(d,i) {
                return 'aline-'+i;
            })
            .attr('class','hover-line-ask')
            .style('opacity',0)
            .attr('width',1)
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.ASK)})
            .attr('y',function(_) {return y(_)})
            .style('fill',"white")
            //append tooltip hover box for bid (in that box show tooltip)
            svg.selectAll('rect.hover-box-ask')
            .data(this.ASKdata).enter()
            .append('rect')
            .style('opacity',0)
            .attr('class','hover-box-ask')
            .attr('width',bandwidth)
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.ASK)})
            .attr('y',function(_) {return y(_)})
            .on('mouseover',function(d,i) {
                const currLine = '#aline-'+i;
                d3.select(currLine).style('opacity',0.5);
                tooltipASK.style("opacity", 0.7);
                tooltipASK.html("<strong>SUM:</strong> <span style='color:grey'>" + d.SUM.toFixed(4) + "</span><br/><strong>BID:</strong> <span style='color:grey'>" + d.ASK.toFixed(4)+ "</span><br/><strong>SIZE: </strong> <span style='color:grey'>" + d.SIZE.toFixed(3) + "</span>")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            }).on("mouseout", function(d,i) {
                tooltipASK.style("opacity", 0);
                // hover line
                const currentLine = '#aline-' + i;
                d3.select(currentLine).style('opacity', 0);
            });
        },

    }

}
</script>

<style>
.svg-container {
    display: inline-block;
    position: relative;
    width: 100%;
    padding-bottom: 60%; /* aspect ratio */
    vertical-align: top;
    overflow: hidden;
    background: rgba(24, 23, 23, 0.8);
    top: 10px;
}
.svg-content-responsive {
    display: inline-block;
    position: absolute;
    top: 10px;
    left: 0;
}
.tooltip {
    position: absolute;
    z-index: 10;
}
/* .d3-tip {
  line-height: 1;
  font-weight: bold;
  padding: 12px;
  background: rgba(61, 60, 60, 0.8);
  color: #fff;
  border-radius: 2px;
} */

/* Creates a small triangle extender for the tooltip */
/* .d3-tip:after {
  box-sizing: border-box;
  display: inline;
  font-size: 10px;
  line-height: 1;
  color: rgba(0, 0, 0, 0.8);
  content: "\25BC";
  position: absolute;
  text-align: center;
} */

/* Style northward tooltips differently */
/* .d3-tip.n:after {
  margin: -1px 0 0 0;
  top: 100%;
  left: 0;
} */ 
</style>


