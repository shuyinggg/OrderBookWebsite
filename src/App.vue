<template>
  <div id="app">
    <b-container  >
      <b-row>
        <b-col>
          <h>DEPTH CHART</h>
          <DepthChart></DepthChart>
        </b-col>
      </b-row>
      <b-row>
        <b-col><Sellers v-bind:perPage="getPage" :currentPage="getcurrPage"></Sellers></b-col>
        <b-col><Buyers v-bind:perPage="getPage" :currentPage="getcurrPage"></Buyers></b-col>
      </b-row>
      <b-row class="text-center">
        <b-col>
          <b-button-group size="sm">
            <b-button disabled class="outline-secondary">Order Book</b-button>
            <b-button class="text-primary bg-light" @click="changePages(10)">10</b-button>
            <b-button class="text-primary bg-light" @click="changePages(25)">25</b-button>
            <b-button class="text-primary bg-light" @click="changePages(50)">50</b-button>
            <b-button class="text-primary bg-light" @click="changePages(100)">100</b-button>
          </b-button-group>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import DepthChart from './components/DepthChart.vue'
import Sellers from './components/Sellers.vue'
import Buyers from './components/Buyers.vue'



export default {
  name: 'app',
  components: {
    Sellers,
    Buyers,
    DepthChart,
  },
  data () {
    return {
      perPage: 10,
    }
  },
  computed: {
    getPage () {
      return this.perPage
    },
    getcurrPage () {
      return 1
    }
  },
  methods: {
    changePages(num) {
      this.perPage = num
    }
  }
}
</script>

<style>
h {
  text-decoration: underline;
  font-size: 40px;
  color:gray;
}
</style>
