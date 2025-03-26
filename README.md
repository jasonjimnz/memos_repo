# Memos Flask Replica

This project is a Python/Flask-based replica aiming to emulate the core functionalities of the Memos application (originally built with Go and React).

It includes features like user authentication, memo creation/editing/deletion with Markdown support (via a WYSIWYG editor), file attachments, and database persistence.

## Features Implemented

* User Authentication (Signup, Login, Logout)
* Memo CRUD (Create, Read, Update, Delete)
* Markdown Rendering for Memo Content
* WYSIWYG Markdown Editor (EasyMDE)
* File Attachments (Multiple uploads per memo, separate deletion)
* Bootstrap 5 UI Styling
* Database Migrations (Flask-Migrate)
* Docker / Docker Compose Support

## Getting Started

You can run this application either using Docker (recommended for ease of setup and consistency) or locally using a Python virtual environment.

### Running with Docker (Recommended)

**Prerequisites:**

* **Git:** To clone the repository.
* **Docker:** Installed and running ([Download Docker](https://www.docker.com/products/docker-desktop/)).
* **Docker Compose:** Usually included with Docker Desktop.

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd memos-flask-replica # Or your repository directory name
    ```

2.  **Create Environment File (`.env`):**
    This file stores configuration secrets. Create a file named `.env` in the project root. Add a `SECRET_KEY`. You can generate one using:
    ```bash
    # Run this in your terminal (use 'python' if 'python3' doesn't work)
    python3 -c 'import secrets; print(f"SECRET_KEY={secrets.token_hex(24)}")'
    ```
    Copy the output into your `.env` file:
    ```dotenv
    # .env
    SECRET_KEY=your_generated_hex_string_here
    # DATABASE_URL is set in Dockerfile for SQLite inside the volume by default
    ```
    *(Ensure `.env` is listed in your `.gitignore`)*

3.  **Build and Run:**
    Make sure Docker is running. In the project root directory, run:
    ```bash
    docker-compose up --build
    ```
    * This command builds the Docker image (installs dependencies, runs migrations) and starts the web service container.
    * Data (database and uploads) will be persisted in a `./instance_data` folder on your host machine.
    * Add `-d` to run in detached mode: `docker-compose up --build -d`

4.  **Access the Application:**
    Open your web browser and go to: [http://localhost:5000](http://localhost:5000)

5.  **Stopping:**
    * Press `Ctrl+C` in the terminal where Compose is running.
    * Or, if detached or in another terminal, run: `docker-compose down` (preserves data in `./instance_data`).

### Running Locally (Without Docker)

**Prerequisites:**

* **Git:** To clone the repository.
* **Python:** Version 3.8 or newer recommended.
* **pip:** Python's package installer.

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd memos-flask-replica # Or your repository directory name
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    # Create (use 'python' if 'python3' doesn't work)
    python3 -m venv venv

    # Activate
    # macOS/Linux: source venv/bin/activate
    # Windows CMD: .\venv\Scripts\activate
    # Windows PowerShell: .\venv\Scripts\Activate.ps1
    ```
    *(Your prompt should show `(venv)`)*

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create Environment File (`.env`):**
    Create a `.env` file in the project root. Generate a `SECRET_KEY`:
    ```bash
    # Run this in your terminal (venv active or python3 available)
    python3 -c 'import secrets; print(f"SECRET_KEY={secrets.token_hex(24)}")'
    ```
    Paste the key into the `.env` file and ensure the `DATABASE_URL` points to your local SQLite database location:
    ```dotenv
    # .env
    SECRET_KEY=your_generated_hex_string_here
    DATABASE_URL='sqlite:///instance/app.db'
    ```
    *(Ensure `.env` is listed in your `.gitignore`)*

5.  **Set `FLASK_APP` Environment Variable:**
    Tell Flask where your application entry point is:
    ```bash
    # macOS/Linux:
    export FLASK_APP=run.py
    # Windows CMD:
    set FLASK_APP=run.py
    # Windows PowerShell:
    $env:FLASK_APP="run.py"
    ```
    *(Replace `run.py` if your script is named differently)*

6.  **Run Database Migrations:**
    Apply migrations to create/update your database schema:
    ```bash
    flask db upgrade
    ```
    *(This will create `instance/app.db` if it doesn't exist)*

7.  **Run the Development Server:**
    ```bash
    flask run
    ```

8.  **Access the Application:**
    Open your web browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000) (or the address shown in the terminal).

9.  **Stopping:**
    Press `Ctrl+C` in the terminal where `flask run` is executing.