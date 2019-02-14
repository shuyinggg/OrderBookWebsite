<template>
        <div id="chart" ref="chart">
        </div>
</template>

<script>
import  * as d3 from 'd3'
import list1 from '@/assets/list1.json'
import list2 from '@/assets/list2.json'
import d3Tip from "d3-tip"

export default {
    name: 'chart',
    data() {
        return {
            a1: this.parseData(list1),
            a2: this.parseData(list2),
            clientWidth: 900,
            clientHeight: 600
        }
    },
    mounted () {
                this.createChart(this.clientWidth,this.clientHeight)
    },
    methods: {
        parseData(jdata) {
            var arr = Object.keys(jdata).map(function(k) { return jdata[k] });
            arr = arr.sort((a,b)=>(a.SUM > b.SUM? 1:-1));
            return arr; 
        },
        createChart(width, height) {
            const margin = {
                top:10,
                bottom:20,
                left:30,
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
                        .domain([d3.min(this.a1, d => d.BID),d3.max(this.a2, d => d.ASK)]);
            const y = d3.scaleLinear()
                        .range([height - margin.bottom, margin.top])
                        .domain([d3.min(this.a1,d=>d.SUM/d.BID), 800]);
            
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

            //tooltip generator with d3.tip
            const tip1 = d3Tip()
                    .attr('class','d3-tip')
                    .offset([-10,0])
                    .html(function(d) {
                        return "<strong>SUM:</strong> <span style='color:grey'>" + d.SUM + "</span><br/><strong>BID:</strong> <span style='color:grey'>" + d.BID+ "</span><br/><strong>Volumn:</strong> <span style='color:grey'>" + d.SUM/d.BID + "</span>";
                    })

            const tip2 = d3Tip()
                    .attr('class','d3-tip')
                    .offset([-10,0])
                    .html(function(d) {
                        return "<strong>SUM:</strong> <span style='color:grey'>" + d.SUM + "</span><br/><strong>ASK:</strong> <span style='color:grey'>" + d.ASK+ "</span><br/><strong>Volumn:</strong> <span style='color:grey'>" + d.SUM/d.ASK + "</span>";
                    });
            svg.call(tip1);
            svg.call(tip2);

            //area generator
            const area1 = d3.area()
                        .x(d => x(d.BID))
                        .y0(y(0))
                        .y1(d => y(d.SUM/d.BID));
            const area2 = d3.area()
                        .x(d => x(d.ASK))
                        .y0(y(0))
                        .y1(d => y(d.SUM/d.ASK));

            //line generator
            const line1 = d3.line()
                        .x(d => x(d.BID))
                        .y(d => y(d.SUM/d.BID));

            const line2 = d3.line()
                        .x(d => x(d.ASK))
                        .y(d => y(d.SUM/d.ASK));
            //append lines
            svg.append('path')
            .datum(this.a1)
            .attr("fill", "none")
            .attr("d",line1)
            .attr("stroke","green")
            .attr("stroke-width",3)
            svg.append('path')
            .datum(this.a2)
            .attr("fill", "none")
            .attr("d",line2)
            .attr("stroke","red")
            .attr("stroke-width",3)

            //append area for shaded area under the line
            svg.append('path')
            .datum(this.a1)
            .attr("fill", "green")
            .attr("opacity",0.2)
            .attr("d",area1)
            svg.append('path')
            .datum(this.a2)
            .attr("fill", "red")
            .attr("opacity",0.2)
            .attr("d",area2)

            //append circles for tooltip use
            svg.selectAll("dot")
            .data(this.a1)
            .enter().append('circle')
            .attr("fill","#fff")
            .attr("opacity",0)
            .attr("r",3)
            .attr("cx",function(d) {return x(d.BID)})
            .attr("cy",function(d) {return y(d.SUM/d.BID)})
            .on('mouseover',tip1.show)
            .on('mouseout',tip1.hide)
            svg.selectAll("dot")
            .data(this.a2)
            .enter().append('circle')
            .attr("fill","#fff")
            .attr("opacity",0)
            .attr("r",3)
            .attr("cx",function(d) {return x(d.ASK)})
            .attr("cy",function(d) {return y(d.SUM/d.ASK)})
            .on('mouseover',tip2.show)
            .on('mouseout',tip2.hide)
        },

    }

}
</script>

<style>
.svg-container {
    display: inline-block;
    position: relative;
    width: 100%;
    padding-bottom: 70%; /* aspect ratio */
    vertical-align: top;
    overflow: hidden;
}
.svg-content-responsive {
    display: inline-block;
    position: absolute;
    top: 10px;
    left: 0;
}

.d3-tip {
  line-height: 1;
  font-weight: bold;
  padding: 12px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  border-radius: 2px;
}

/* Creates a small triangle extender for the tooltip */
.d3-tip:after {
  box-sizing: border-box;
  display: inline;
  font-size: 10px;
  line-height: 1;
  color: rgba(0, 0, 0, 0.8);
  content: "\25BC";
  position: absolute;
  text-align: center;
}

/* Style northward tooltips differently */
.d3-tip.n:after {
  margin: -1px 0 0 0;
  top: 100%;
  left: 0;
}
</style>


