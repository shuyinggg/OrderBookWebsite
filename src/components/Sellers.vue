<template>
	<!-- table-->
  <div id="app">
    <b-table 
      striped 
      hover 
      dark
      small  
      :per-page="getPerPage"
      :total-rows="getLen"
      :current-page="getCurrentPage"
      :items="getAll"
      :fields="fields"
      class="text-right"
      >
    <!-- fix display styles, like color and precision -->
    <template slot="BID" slot-scope="data">
      <a class="text-success">
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
      <b-col class="text-left">{{total1}} BTC</b-col>
      <b-col class="text-right">{{total2}} USD</b-col>
  </b-row>
  <b-pagination align="center" size="sm" :total-rows="getLen" v-model="currentPage" :per-page="perPage" />
  </div>
</template>

<script>
import list from '@/assets/bid.json'

export default {
  name: 'Sells',
  data () {
     return {
         fields: [
           'SUM',
           'TOTAL',
           {
             key: 'SIZE',
             label: 'SIZE(BTC)'
           },
          {
             key: 'BID',
             label: 'BID(USD)',  
         }],
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

      getCurrentPage() {
        return this.currentPage
      },
      total1 () {
        return this.orders.reduce(function(a, c){return a + c.SIZE || 0},0).toFixed(3)
      },
      total2 () {
        return this.orders.reduce(function(a, c){return a + c.BID || 0},0).toFixed(3)
      }
  }
}

</script>

<style scoped>

</style>
