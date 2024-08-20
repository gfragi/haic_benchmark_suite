# Human-AI Benchmark Suite

An application to evaluate Human-AI collaboration by logging interactions, configurations, and evaluations. This suite includes both a backend, built with FastAPI, and a frontend, built with Vue 3 and Vuetify.

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Frontend Components](#frontend-components)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Project Structure
```bash
human-ai-benchmark-suite/
├── backend/
│ ├── alembic/
│ ├── app/
│ ├── assets/
│ ├── docker-compose.yml
│ ├── docs/
│ ├── minio-data/
│ ├── pg-data/
│ ├── README.md
│ ├── requirements.txt
│ ├── templates/
│ └── tests/
└── frontend/
├── node_modules/
├── public/
├── src/
├── .browserslistrc
├── .eslintrc.js
├── babel.config.js
├── jest.config.js
├── jsconfig.json
├── package.json
├── README.md
├── vue.config.js
```


## Installation

### Prerequisites

- **Backend**: Python 3.9+, Docker, and Docker Compose
- **Frontend**: Node.js 14+, npm or yarn

## Backend Setup

1. **Clone the Repository**

    ```bash
    git clone https://github.com/gfragi/haic_benchmark_suite.git
    cd haic_benchmark_suite/backend
    ```

2. **Create a Virtual Environment**

    ```bash
    python3 -m venv bench-env
    source bench-env/bin/activate  # On Windows use `bench-env\Scripts\activate`
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run Migrations**

    ```bash
    alembic upgrade head
    ```

5. **Start the Backend Server**

    ```bash
    uvicorn app.main:app --reload
    ```

    The backend server will be available at `http://localhost:8000`.

## Frontend Setup

1. **Navigate to the Frontend Directory**

    ```bash
    cd ../frontend
    ```

2. **Install Dependencies**

    ```bash
    npm install
    ```

3. **Run the Frontend Development Server**

    ```bash
    npm run serve
    ```

    The frontend server will be available at `http://localhost:8080`.

## Running the Application

- **Backend**: Runs on `http://localhost:8000`
- **Frontend**: Runs on `http://localhost:8080`

Ensure both the backend and frontend are running simultaneously to fully use the application.

## API Endpoints

### Evaluation Config

- **GET /evaluation/config** - Get all evaluation configs
- **POST /evaluation/config** - Create a new evaluation config
- **GET /evaluation/config/{config_id}** - Get an evaluation config by ID

### Logs

- **POST /logs/** - Ingest a new log entry

### Evaluation Result

- **POST /results/** - Create a new evaluation result
- **GET /results/{result_id}** - Get an evaluation result by ID
- **GET /results/list** - Get all evaluation results

### Reporting

- **GET /reporting/aggregate-by-date** - Get aggregated results by date
- **GET /reporting/time-series-data** - Get time-series data for evaluations
- **GET /reporting/generate-report** - Generate a PDF report

## Frontend Components

### Components

- **HeaderComponent.vue** - The header for all pages, includes a toggle for the sidebar.
- **FooterComponent.vue** - The footer for all pages.
- **AppSidebar.vue** - The sidebar containing navigation links.
- **EvaluationConfigForm.vue** - Form for creating/editing evaluation configurations.
- **EvaluationConfigList.vue** - Displays a list of evaluation configurations.
- **LogIngestionForm.vue** - Form to ingest logs.

### Views

- **HomeView.vue** - The home page, providing an overview and navigation.
- **EvaluationConfigList.vue** - View for listing and managing evaluation configurations.
- **EvaluationReports.vue** - View for generating and viewing reports.
- **EvaluationResults.vue** - View for viewing evaluation results.
- **LogIngestion.vue** - View for ingesting log data.

## Usage

1. **Create an Evaluation Config**: Use the frontend to navigate to the "New Configuration" page, fill out the form, and save the configuration.
2. **Ingest Logs**: Use the "Log Ingestion" page to upload log data that will be associated with an evaluation config.
3. **Run Evaluations**: Automatically triggered upon log ingestion, generating evaluation results based on predefined metrics.
4. **View Results**: Navigate to the "Evaluation Results" page to view historical data.
5. **Generate Reports**: Use the "Reports" page to aggregate data and generate PDF reports.

## Testing

### Backend

Run backend tests using `pytest`:

```bash
cd backend
pytest
```

### Frontend

Run frontend tests using jest:
```bash
cd frontend
npm run test:unit
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a feature branch (git checkout -b feature/your-feature).
3. Commit your changes (git commit -am 'Add some feature').
4. Push to the branch (git push origin feature/your-feature).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

