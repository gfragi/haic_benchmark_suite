# frontend

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your unit tests
```
npm run test:unit
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).



## Project structure
```bash
src/
├── assets/                     # Static assets (images, fonts, etc.)
├── components/                 # Reusable Vue components
│   ├── ConfigForm.vue  # Form to create/edit evaluation configs
│   ├── EvaluationResultCard.vue  # Card to display a summary of an evaluation result
│   ├── LogIngestionForm.vue      # Form to upload or input logs
│   ├── NavigationBar.vue         # Top navigation bar
│   ├── Sidebar.vue               # Sidebar for navigation
│   ├── PlotlyChart.vue           # Reusable component for Plotly charts
│   └── ...
├── views/                      # Views (pages) of the application
│   ├── Home.vue                 # Home page with navigation to other pages
│   ├── ConfigList.vue # List and manage evaluation configs
│   ├── EvaluationResults.vue    # View and analyze evaluation results
│   ├── LogIngestion.vue         # Page for log ingestion
│   ├── Reports.vue              # Generate and download reports
│   └── ...
├── router/                     # Vue Router configuration
│   ├── index.js                # Router setup with routes
├── store/                      # Vuex store (if needed)
│   ├── index.js                # Store setup
├── App.vue                     # Main app component
└── main.js                     # Entry point for the Vue app
```

