<template>
  <div id="dchart" ref="dchart">
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
            clientHeight: 400
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
            //add a new field to store prev (for tooltip only)
            var prev = arr[0].BID;
            arr.map(function(a) {
                a.prev = prev;
                prev = a.BID;                
            })
            //plot only the top 50 entries desc
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
            //add a new field to store prev (for tooltip only)
            var post = 0;
            arr.map(function(a,i) {
                 
                if (i != arr.length - 1) {
                    post = arr[i+1].ASK;
                } else {
                    post = arr[49].ASK;
                }
                
                a.post = post;         
            })
            //plot only the top 50 entries asc
            return arr.slice(0,50); 
        },
        createChart(width, height) {
            const margin = {
                top:20,
                bottom:30,
                left:40,
                right:40
            };
            
            //draw responsive svg 
            const svg = d3.select('#dchart')
                        .append('div')
                        .classed("svg-container", true)
                        .append('svg')
                        .attr("preserveAspectRatio", "xMinYMin meet")
                        .attr("viewBox", "0 0 " + width + " " + height)
                        .classed("svg-content-responsive", true);

        
            var x = d3.scaleLinear()
                        .range([margin.left, width - margin.right])
                        .domain([this.getx0,this.getxend]);
            var y = d3.scaleLinear()
                        .range([height - margin.bottom, margin.top])
                        .domain([0, this.getyend]);
            var xAxis = d3.axisBottom(x);
            //append axes
            var gX = svg.append('g')
            .attr('class', 'axis axis-x')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x))
            .style("color","grey")
            svg.append('g')
            .attr('class','axis axis-y')
            .attr("transform",`translate(${margin.left},0)`)
            .call(d3.axisLeft(y))
            .style("color","grey")

            //append y-axis labeling
            // svg.append("text")
            //     .attr("class","y-label")
            //     .attr("text-anchor", "end")
            //     .attr("y", 6)
            //     .attr("dy", ".75em")
            //     .attr("transform", "rotate(-90)")
            //     .text("CUMULATIVE SIZE");

            //append grids
            var gXgrid = svg.append("g")			
                .attr("class", "grid")
                .attr("transform", `translate(0,${height - margin.bottom})`)
                .style("stroke-dasharray", "5 5")
                .call(d3.axisBottom(x)
                    .ticks(8)
                    .tickSizeInner(-height+margin.top+margin.bottom)
                    .tickFormat(""))
                .style("color","grey")
                .attr("opacity",0.3)
                //.attr("clip-path", "url(#clipd)")
            var gYgrid = svg.append("g")			
                .attr("class", "grid")
                .attr("transform", `translate(${margin.left},0)`)
                .style("stroke-dasharray", "5 5")
                .call(d3.axisLeft(y).ticks(9)
                .tickSizeInner(-width+margin.left+margin.right)
                .tickFormat(""))
                .style("color","grey")
                .attr("opacity",0.3)
                //.attr("clip-path", "url(#clipd)")

            //append tooltip and mouse line
            // var tooltipBID = d3.select("body")
            //             .append("div")
            //             .attr("class", "tooltipbid")
            //             .style("opacity",0)
            var tooltipBID = d3.select('.svg-container').append('g')
                        .attr("class", "tooltipbid")
                        .style("opacity",0)
            var tooltipASK = d3.select('.svg-container').append('g')
                        .append("div")
                        .attr("class", "tooltipask")
                        .style("opacity",0)

            var tooltipxb = d3.selectAll("body")
                            .append("div")
                            .attr("class","tooltipxb")
                            .style("opacity",0)
            var tooltipxa = d3.selectAll("body")
                            .append("div")
                            .attr("class","tooltipxa")
                            .style("opacity",0)
            var mouseG = svg.append("g")
                .attr("class", "mouse-over-effects");

                mouseG.append("path") // this is the black vertical line to follow mouse
                .attr("class", "mouse-line")
                .style("stroke", "grey")
                .style("stroke-width", "1px")
                .style("opacity", "0");
            //area generator
            const areaBID = d3.area()
                        .curve(d3.curveStep)
                        .x(d => x(d.BID))
                        .y0(y(0))
                        .y1(d => y(d.cumSIZE));
            const areaASK = d3.area()
                        .curve(d3.curveStep)
                        .x(d => x(d.ASK))
                        .y0(y(0))
                        .y1(d => y(d.cumSIZE));

            //line generator
            const lineBID = d3.line()
                        .curve(d3.curveStep)
                        .x(d => x(d.BID))
                        .y(d => y(d.cumSIZE));

            const lineASK = d3.line()
                        .curve(d3.curveStep)
                        .x(d => x(d.ASK))
                        .y(d => y(d.cumSIZE));

            //append lines 
            svg.append('path')
            .datum(this.BIDdata)
            .attr("class", 'bidline')
            .attr("fill", "none")
            .attr("d",lineBID)
            .attr("stroke","green")
            .attr("stroke-width",2.5)
            .attr("clip-path", "url(#clipd)")
            
            svg.append('path')
            .datum(this.ASKdata)
            .attr('class','askline')
            .attr("fill", "none")
            .attr("d",lineASK)
            .attr("stroke","#9e1818ce")
            .attr("stroke-width",2.5)
            .attr("clip-path", "url(#clipd)")

            //append area for shaded area under the line
            svg.append('path')
            .datum(this.BIDdata)
            .attr('class','bidarea')
            .attr("fill", "green")
            .attr("opacity",0.15)
            .attr("d",areaBID)
            .attr("clip-path", "url(#clipd)")
            svg.append('path')
            .datum(this.ASKdata)
            .attr('class','askarea')
            .attr("fill", "darkred")
            .attr("opacity",0.15)
            .attr("d",areaASK)
            .attr("clip-path", "url(#clipd)")

            //append tooltip hover box for bid (in that box show tooltip)
            svg.selectAll('rect.hover-box-bid')
            .data(this.BIDdata).enter()
            .append('rect')
            .style('opacity',0)
            .attr('class','hover-box-bid')
            .attr("clip-path", "url(#clipd)")
            //.attr('width', "1px")
            .attr('width', function(d) {return x(d.prev)-x(d.BID)})
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.BID)})
            .attr('y',function(_) {return y(_)})
            .on('mouseover', function() {
                tooltipBID.style("display", null);
                d3.select(".mouse-line").style("opacity", "1");
            })  
            .on('mousemove',function(d) {
                var mouse = d3.mouse(this);
                var svgdim = svg.node().getBoundingClientRect();
                tooltipBID.style("opacity", 1)
                tooltipBID.html("<strong>SUM:</strong> <span style='color:grey'>" + d.SUM.toFixed(4) + 
                              "</span><br/><strong>BID:</strong> <span style='color:grey'>" + d.BID.toFixed(4)+ 
                               "</span><br/><strong> CUMULATIVE SIZE: </strong> <span style='color:grey'>" + d.cumSIZE.toFixed(3))
                .style("left", (mouse[0]*svgdim.height/height+2) + "px")
                //.style("top", y(0)+ "px");
                .style("top", ( ((y(d.cumSIZE)-25)*svgdim.height/height)+ "px"))
                tooltipxb.style("opacity",1);
                tooltipxb.html(d.BID.toFixed(4))
                .style("left", (d3.event.clientX-28) + "px")
                .style("top", ((y(0)+margin.top+70)*(svgdim.height+120)/(height+120))+"px")
                
                mouse = d3.mouse(this);
                d3.select(".mouse-line")
                .attr("d", function() {
                    var d = "M" + mouse[0] + "," + (height-margin.bottom);
                    d += " " + mouse[0] + "," + 0;
                    //console.log(d);
                    return d;
                    });
            })
            .on("mouseout", function() {
                tooltipBID.style("opacity", 0);
                tooltipxb.style("opacity",0);
                d3.select(".mouse-line").style("opacity", "0");
            });

            //append tooltip hover box for ask(in that box show tooltip)
            svg.selectAll('rect.hover-box-ask')
            .data(this.ASKdata).enter()
            .append('rect')
            .style('opacity',0)
            .attr('class','hover-box-ask')
            .attr("clip-path", "url(#clipd)")
            .attr('width',function(d) {return x(d.post)-x(d.ASK)})
            .attr('height',height-margin.bottom)
            .attr('x', function(d) {return x(d.ASK)})
            .attr('y',function(_) {return y(_)})
            .on('mouseover',function()   {
                tooltipASK.style("display", null);
                d3.select(".mouse-line").style("opacity",1)})
            .on('mousemove',function(d) {
                var mouse = d3.mouse(this);
                 var svgdim = svg.node().getBoundingClientRect();
                tooltipASK.style("opacity", 1);
                tooltipASK.html("<strong>SUM:</strong> <span style='color:grey'>" + d.SUM.toFixed(4) + 
                                "</span><br/><strong>ASK:</strong> <span style='color:grey'>" + d.ASK.toFixed(4)+ 
                                "</span><br/><strong>CUMULATIVE SIZE: </strong> <span style='color:grey'>" + d.cumSIZE.toFixed(3) + "</span>")
                .style("left", ((mouse[0])*svgdim.height/height) - 144 + "px")
                .style("top", ((y(d.cumSIZE)-25)*svgdim.height/height)+ "px")
                tooltipxa.style("opacity",1);
                tooltipxa.html(d.ASK.toFixed(4))
                .style("left", (d3.event.clientX - 28) + "px")
                .style("top", ((y(0)+margin.top+70)*(svgdim.height+120)/(height+120))+"px")
                   mouse = d3.mouse(this);
                    d3.select(".mouse-line")
                    .attr("d", function() {
                    var d = "M" + mouse[0] + "," + (height - margin.bottom);
                    d += " " + mouse[0] + "," + margin.top;
                    return d;
                    });
            }).on("mouseout", function() {
                tooltipASK.style("opacity", 0);
                tooltipxa.style("opacity",0);
                d3.select(".mouse-line").style("opacity",0);
            });
            
            //define zoom area 
            svg.append("defs").append("clipPath")
            .attr("id", "clipd")
            .append("rect")
            .attr("width", width- margin.right - margin.left)
            .attr("height", height -margin.bottom - margin.top)
            .attr("transform",`translate(${margin.left},${margin.top})`)

            const extent = [[0, 0], [width,height]];
            //implement zoom 
            //axis
            var zoom = d3.zoom()
            .scaleExtent([1,80])
            .translateExtent(extent)
            .extent(extent)
            .on('zoom',function() {
                var t = d3.event.transform;
                var xt = t.rescaleX(x);
                var yt = t.rescaleY(y);
                gX.call(xAxis.scale(xt));
                //gY.call(yAxis.scale(yt));
                gXgrid.call(d3.axisBottom(x).scale(xt).ticks(8)
                    .tickSizeInner(-height+margin.top+margin.bottom)
                    .tickFormat(""));
                gYgrid.call(d3.axisLeft(y).scale(yt).ticks(8)
                    .tickSizeInner(-width+margin.left+margin.right)
                    .tickFormat(""));
                
            //zoom lines and area
            const areaBID = d3.area()
                        .curve(d3.curveStep)
                        .x(d => xt(d.BID))
                        .y0(y(0))
                        .y1(d => y(d.cumSIZE));
            const areaASK = d3.area()
                        .curve(d3.curveStep)
                        .x(d => xt(d.ASK))
                        .y0(y(0))
                        .y1(d => y(d.cumSIZE));
            const lineBID= d3.line()
                        .curve(d3.curveStep)
                        .x(d => xt(d.BID))
                        .y(d => y(d.cumSIZE));
            const lineASK = d3.line()
                        .curve(d3.curveStep)
                        .x(d => xt(d.ASK))
                        .y(d => y(d.cumSIZE));
            d3.selectAll('.bidline').attr("d", lineBID)
            d3.selectAll('.askline').attr("d", lineASK)
            d3.selectAll('.bidarea').attr("d", areaBID)
            d3.selectAll('.askarea').attr("d", areaASK) 

            //zoom hover bars
            d3.selectAll('.hover-box-bid').attr('width',function(d) {return xt(d.prev)-xt(d.BID)})
            .attr('x', function(d) {return xt(d.BID)})
            d3.selectAll('.hover-box-ask').attr('width',function(d) {return xt(d.post)-xt(d.ASK)})
            .attr('x', function(d) {return xt(d.ASK)})
        })

        svg.call(zoom);
        },

    }

}
</script>

<style>
.svg-container {
    display: inline-block;
    position: relative;
    width: 100%;
    padding-bottom: 47%; /* aspect ratio */
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

.tooltipbid{
    position: absolute;
    border: 2px solid green;
    text-align:left;
    width: 140px;
    height: 80px;
    padding: 5px;
    background :white;
    border-radius: 8px;
    pointer-events: none;
    font-size: 12px;
}

.tooltipask {
    position: absolute;
    border: 2px solid#9e1818ce;
    text-align:left;
    width: 140px;
    height: auto;
    padding: 5px;
    background :white;
    border-radius: 8px;
    pointer-events: none;
    font-size: 12px;
}
.tooltipbid::after {
  content: " ";
  position: absolute;
  top: 50%; /* At the right of the tooltip */
  right: 100%;
  margin-top: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent green transparent transparent;
}
.tooltipask::after {
  content: " ";
  position: absolute;
  top: 50%; /* At the right of the tooltip */
  left: 100%;
  margin-top: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent transparent #9e1818ce;
}

.tooltipxb{
    position: absolute;
    border: solid 0.5px gray;
    text-align:center;
    width: 50px;
    height: 15px;
    padding: 3px;
    background :white;
    pointer-events: none;
    font-size: 8px;
    opacity:0.5;
    border-radius: 3px;
}
.tooltipxb::after {
  content: " ";
  position: absolute;
  bottom: 100%; /* At the right of the tooltip */
  left: 50%;
  margin-top: -3px;
  border-width: 3px;
  border-style: solid;
  border-color: transparent transparent  rgb(2, 2, 2) transparent;
}
.tooltipxa{
    position: absolute;
    border: solid 0.5px gray;
    text-align:center;
    width: 50px;
    height: 15px;
    padding: 3px;
    background :white;
    pointer-events: none;
    font-size: 8px;
     opacity:0.5;
    border-radius: 3px;
}

.tooltipxa::after {
  content: " ";
  position: absolute;
  bottom: 100%; /* At the right of the tooltip */
  left: 50%;
  margin-top: -3px;
  border-width: 3px;
  border-style: solid;
  border-color: transparent transparent  rgb(2, 2, 2) transparent;
}
</style>


