# Benchmark DB Pool

This project provides a FastAPI application with `asyncpg` for database interactions, demonstrating a benchmark setup for database connection pooling. It includes a PostgreSQL database with sample employee data and two API endpoints to query employee salaries and department-specific employee information.

## Setup and Running

To set up and run the project, ensure you have Docker and Docker Compose installed.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd benchmark-db-pool
    ```

2.  **Start the services using Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This command will:
    - Build the Docker image for the `api` service based on the `Dockerfile`.
    - Start the `postgres` service (PostgreSQL database).
    - Start the `api` service (FastAPI application).
    - Initialize the PostgreSQL database with data from `employees.sql.gz`.

    You can customize the PostgreSQL password, user, database name, and connection pool sizes using environment variables in a `.env` file or directly in the `docker-compose.yml`.

    **Environment Variables (can be set in a `.env` file):**
    - `POSTGRES_PASSWORD`: Password for the PostgreSQL user (default: `postgres`)
    - `POSTGRES_USER`: PostgreSQL username (default: `postgres`)
    - `POSTGRES_DB`: PostgreSQL database name (default: `postgres`)
    - `POOL_MIN_SIZE`: Minimum number of connections in the database pool (default: `3`)
    - `POOL_MAX_SIZE`: Maximum number of connections in the database pool (default: `10`)
    - `API_REPLICAS`: Number of API service replicas (default: `1`)

3.  **Access the API:**
    The FastAPI application will be accessible at `http://localhost:8000`.

    - **API Documentation (Swagger UI):
    - **Alternative API Documentation (ReDoc):** `http://localhost:8000/redoc`

## API Endpoints

### 1. Get Salaries

Retrieves salary information for employees within a specified date range.

-   **URL:** `/salaries`
-   **Method:** `GET`
-   **Query Parameters:**
    -   `from_date` (date, required): Start date for the salary range (e.g., `1999-01-01`).
    -   `to_date` (date, required): End date for the salary range (e.g., `1999-06-01`).
    -   `page` (integer, optional): Page number for pagination (default: `0`).
    -   `page_size` (integer, optional): Number of records per page (default: `50`).
-   **Response:** A JSON object containing a list of `Salary` objects.

    ```json
    {
      "salaries": [
        {
          "id": 10001,
          "first_name": "Georgi",
          "last_name": "Facello",
          "amount": 60117,
          "from_date": "1986-06-26",
          "to_date": "1987-06-26"
        }
      ]
    }
    ```

### 2. Get Employees by Department

Retrieves employee information for specified departments.

-   **URL:** `/employees`
-   **Method:** `GET`
-   **Query Parameters:**
    -   `department_ids` (array of strings, required): List of department IDs (e.g., `d004`, `d005`).
    -   `page` (integer, optional): Page number for pagination (default: `0`).
    -   `page_size` (integer, optional): Number of records per page (default: `50`).
-   **Response:** A JSON object containing a list of `EmployeeInfo` objects.

    ```json
    {
      "employees": [
        {
          "id": 10001,
          "first_name": "Georgi",
          "last_name": "Facello",
          "gender": "M",
          "title": "Senior Engineer",
          "dept_id": "d005",
          "dept_name": "Development"
        }
      ]
    }
    ```

## Dependencies

The project uses `uv` for dependency management. Key Python dependencies include:

-   `asyncpg`: PostgreSQL database adapter for `asyncio`.
-   `fastapi`: Web framework for building APIs.
-   `uvicorn`: ASGI server implementation for FastAPI.

## Development

If you want to run the application locally without Docker:

1.  **Install `uv`:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Run the FastAPI application:**
    ```bash
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 --no-access-log
    ```
    Ensure your PostgreSQL database is running and accessible at the `DATABASE_URL` specified in `main.py` or via environment variables.
