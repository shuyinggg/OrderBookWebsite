<template>
  <div id="app">
    <b-container class="bg-dark" >
      <b-row>
        <b-col><Entries1 v-bind:perPage="getPage" currentPage=1></Entries1></b-col>
        <b-col><Entries2 v-bind:perPage="getPage" currentPage=1></Entries2></b-col>
      </b-row>
      <b-row class="text-center">
        <b-col>
          <b-button-group size="sm">
            <b-button disabled class="outline-dark">Order Book</b-button>
            <b-button class="bg-dark" @click="changePages(10)">10</b-button>
            <b-button class="bg-dark" @click="changePages(25)">25</b-button>
            <b-button class="bg-dark" @click="changePages(50)">50</b-button>
            <b-button class="bg-dark" @click="changePages(100)">100</b-button>
          </b-button-group>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import Entries1 from './components/Entries1.vue'
import Entries2 from './components/Entries2.vue'
export default {
  name: 'app',
  components: {
    Entries1,
    Entries2,
  },
  data () {
    return {
      perPage: 10,
    }
  },
  computed: {
    getPage () {
      return this.perPage
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

</style>
