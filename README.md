# Order Book Website

This project uses [vue.js 2.0](https://vuejs.org/) and [bootstrap + vue](https://bootstrap-vue.js.org/).

The website displays two kinds of visualization of order book data.
- Depth Chart (with [d3.js](https://d3js.org/))
- Tables 

## Project Setup

```
npm install
npm i bootstrap-vue
npm install d3
```

## Code Structure
```
.
├── public                   
├── src
│   ├── assets 
│       ├── bid.json              # sample data in the table from sellers
        ├── ask.json              # sample data in the table from buyers
│   ├── components                # vue components
        ├── DepthChart.vue        # depth chart based on sample data
│       ├── Sellers.vue           # left table
│       ├── Buyers.vue            # right table
│   ├── App.vue
│   └── main.js                               
├── .gitignore
├── babel.config.js
├── package-lock.json
├── package.json
└── README.md
```

## Usage

In terminal, 

### Compiles and hot-reloads for development
```
npm run serve
```
Then navigate to the localhost shown in the terminal, usually [http://localhost:8080/](http://localhost:8080/).

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

