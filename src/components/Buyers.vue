<template>
	<!-- table-->
  <div>
    <b-table 
      striped 
      hover 
      
      small  
      :per-page="perPage"
      :total-rows="getLen"
      :current-page="getCurrentPage"
      :items="getAll"
      :fields="fields"
      class="text-right"
      >
    <template slot="ASK" slot-scope="data">
      <a class="text-danger">
        {{data.value.toFixed(4)}}
      </a>
    </template>
        <template slot="SUM" slot-scope="data">
      <a>
        {{data.value.toFixed(4)}}
      </a>
    </template>
    <template slot="TOTAL" slot-scope="data">
      <a>
        {{data.value.toFixed(4)}}
      </a>
    </template>
    <template slot="SIZE" slot-scope="data">
      <a>
        {{data.value.toFixed(3)}}
      </a>
    </template>
  </b-table>
  <b-row class="text-secondary">
    <b-col class="text-left">{{totalASK}} USD</b-col>
    <b-col class="text-right">{{totalSize}} BTC</b-col>
  </b-row>
    <b-pagination
      align="center" 
      size="sm" 
      :total-rows="getLen" 
      v-model="currentPage" 
      :per-page="perPage">>
    </b-pagination>
  </div>
</template>

<script>
import list from '@/assets/ask.json'

export default {
  name: 'buys',
  data () {
     return {
         fields: [{
             key: 'ASK',
             label: 'ASK(USD)',  
         },
         {
             key: 'SIZE',
             label: 'SIZE(BTC)'
         }, 
         'TOTAL','SUM'],
        orders: list,
     } 
  },
  props: {
      perPage: Number,
      currentPage: Number,
    },
  computed: {
      getAll () {
        return this.orders;
      },
      getLen () {
          return this.orders.length
      },
      getPerPage () {
        return this.perPage
      },
      getCurrentPage () {
        return this.currentPage
      },
      totalSize () {
        return this.orders.reduce(function(a, c){return a + c.SIZE || 0},0).toFixed(3)
      },
      totalASK () {
        return this.orders.reduce(function(a, c){return a + c.ASK || 0},0).toFixed(3)
      }
  }
}
</script>

<style scoped>
</style>
