# Order Book Website

This projects uses [vue.js 2.0](https://vuejs.org/) and [bootstrap + vue](https://bootstrap-vue.js.org/).

It displays a depth graph of order book using [d3.js](https://github.com/d3/d3) and the two tables contain all the sample order book.


## Project Setup

```
npm install
npm i bootstrap-vue
npm install d3
npm install d3-tip 
```
[d3-tip](https://github.com/Caged/d3-tip) adds tooltips for d3.js visualization.

## Code Structure
```
.
├── public                   
├── src
│   ├── assets 
│       ├── list1.json              # sample data in the table from sellers
        ├── list2.json              # sample data in the table from buyers
│   ├── components                  # vue components
        ├── DepthChart.vue          # depth chart based on sample data
│       ├── Entries1.vue            # left table
│       ├── Entries2.vue            # right table
│   ├── App.vue
│   └── main.js                               
├── .gitignore
├── babel.config.js
├── package-lock.json
├── package.json
└── README.md
```

## Usage
### Compiles and hot-reloads for development
```
npm run serve
```
Then navigate to the localcost shown in the terminal, usually [http://localhost:8080/](http://localhost:8080/).

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

