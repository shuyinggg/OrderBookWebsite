# Order Book Website

This project uses [vue.js 2.0](https://vuejs.org/) and [bootstrap + vue](https://bootstrap-vue.js.org/).

The website displays three kinds of visualization of market data.
- Depth Chart (with [d3.js](https://d3js.org/))
- Candlestick Chart (with [d3.js](https://d3js.org/))
- Tables (Pagination)

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
        ├── trade.json            # via binance.com api
        ├── trade_mock.json       # randomly generated trade data 
│   ├── components                # vue components
        ├── DepthChart.vue        # depth chart based on sample data
        ├── MarketChart.vue       # candlestick chart based on generated data
│       ├── Sellers.vue           # left table
│       ├── Buyers.vue            # right table
│   ├── App.vue
│   ├── trade_history.py          # obtain historical trade data from binance.com
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

