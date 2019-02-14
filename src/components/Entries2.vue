<template>
	<!-- table-->
  <div>
    <b-table 
      striped 
      hover 
      dark
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
        {{data.value}}
      </a>
    </template>
  </b-table>
  <b-row class="text-secondary">
    <b-col class="text-left">{{total2}} USD</b-col>
    <b-col class="text-right">{{total1}} BTC</b-col>
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
import list from '@/assets/list2.json'

export default {
  name: 'Entries',
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
        entry: list,
     } 
  },
  props: {
      perPage: Number,
      currentPage: Number,
    },
  computed: {
      getAll () {
        return this.entry;
      },
      getLen () {
          return this.entry.length
      },
      getPerPage () {
        return this.perPage
      },
       getCurrentPage() {
        return this.currentPage
      },
      total1 () {
        return this.entry.reduce(function(a, c){return a + c.SIZE || 0},0).toFixed(3)
      },
      total2 () {
        return this.entry.reduce(function(a, c){return a + c.ASK || 0},0).toFixed(3)
      }
  }
}
</script>

<style scoped>
</style>
