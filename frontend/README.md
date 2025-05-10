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

## Running the Frontend Locally
1. Make sure you have Node.js and npm installed.
2. Clone the repository:
   ```bash
   git clone
    cd frontend
    ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm run serve
   ```
5. Open your browser and navigate to `http://localhost:8080` (or the port specified in the terminal).
6. You should see the application running locally.
7. Make changes to the code and see them reflected in real-time in your browser.

### Running under Docker Compose
1. Make sure you have Docker and Docker Compose installed.
2. Clone the repository:
   ```bash
   git clone
    cd frontend
    ```
3. Create a `.env` file in the root directory of the project with the following content:
    ```bash
    # .env
    VUE_APP_BACKEND_URL=http://localhost:8000
    ```
    This file is used to set environment variables for the Docker container.
4. In the keycloak.js file, set the following environment variables:
    ```javascript
    const keycloak = new Keycloak({
      url: process.env.VUE_APP_KEYCLOAK_URL,
      realm: process.env.VUE_APP_KEYCLOAK_REALM,
      clientId: process.env.VUE_APP_KEYCLOAK_CLIENT_ID,
    });
    ```
3. Build and run the Docker container:
   ```bash
   docker-compose build frontend
    docker-compose up frontend
   ```
4. Open your browser and navigate to `http://localhost:8080` (or the port specified in the terminal).
5. You should see the application running locally.