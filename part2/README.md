# HBnB - BL and API (Part 2)

This repository contains the second part of the HBnB Evolution project, focusing on the development of the Business Logic (BL) and the implementation of a robust RESTful API. This project aims to simulate a vacation rental platform, similar to Airbnb, by providing a programmable interface for managing users, places, reviews, and amenities.

## Project Objectives (Part 2)

This part of the project aims to:

  * Establish a complete RESTful API allowing interaction with the HBnB platform's data.
  * Implement the business logic to manage the different entities (Users, Places, Reviews, Amenities).
  * Ensure data persistence through a database.
  * Provide a clear and modular architecture for easy maintenance and scalability.

## Key API Features

The HBnB Evolution API offers the following main functionalities:

  * **User Management:**
      * Registration of new users.
      * User authentication.
      * Retrieval, update, and deletion of user information.
  * **Place Management:**
      * Creation of new place listings.
      * Searching and retrieving places with filtering criteria.
      * Updating and deleting existing place listings.
  * **Review Management:**
      * Adding reviews for places.
      * Retrieval and deletion of reviews.
  * **Amenity Management:**
      * Creation, retrieval, update, and deletion of available amenities.

## Architecture

The project is structured around a multi-layered architecture, ensuring a clear separation of responsibilities:

  * **Presentation Layer:** Handles API endpoints (`api/v1/`) and interaction with HTTP requests and responses.
  * **Business Logic Layer:** Contains data models (`models/`) and associated business logic for each entity (User, Place, Review, Amenity).
  * **Persistence Layer:** Interacts with the database (`persistence/`) to store and retrieve data.

## Class Diagram

The class diagram below illustrates the relationships between the different entities in the system, their attributes, and key methods.

## Sequence Diagrams of Key Operations

These diagrams illustrate the flow of information and interactions between the different layers of the system for specific API operations.

### User Registration

### Place Creation

### Retrieving Places

### Review Creation

## Project Structure

```
.
├── App/
│   ├── api/
│   │   └── v1/
│   │       ├── amenities.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       └── users.py
│   ├── models/
│   │   ├── amenity.py
│   │   ├── base_model.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── user.py
│   ├── persistence/
│   │   └── repository.py
│   ├── services/
│   └── tests/
├── config.py
├── requirements.txt
└── run.py
```

## Technologies Used

  * **Python**
  * **Flask**: Micro-framework for building the API.
  * **Flask-RESTful**: Flask extension facilitating the creation of REST APIs.
  * **SQLAlchemy**: ORM (Object-Relational Mapper) for database interaction.
  * **mysql-connector-python**: Python connector for MySQL.
  * **python-dotenv**: For managing environment variables.
  * **jsonschema**: For validating API input data.

## Installation

Follow these steps to set up the project locally:

1.  **Clone the repository:**

    ```bash
    git clone [YOUR_FRIEND'S_REPO_URL]
    cd hbnb-bl-api/part2 # Or the path to the part2 folder if cloning into a parent directory
    ```

2.  **Create and activate a Python virtual environment:**

    ```bash
    python3 -m venv myenv # Or your chosen name
    source myenv/bin/activate # On Linux/macOS
    # or myenv\Scripts\activate # On Windows
    ```

3.  **Install dependencies:**
    Install all required libraries listed in `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

      * **Specific Dependencies:**
          * `Flask==3.0.3`
          * `Flask-RESTful==0.3.9`
          * `SQLAlchemy==2.0.29`
          * `mysql-connector-python==8.4.0`
          * `python-dotenv==1.0.1`
          * `Werkzeug==3.1.3`
          * `itsdangerous==2.2.0`
          * `Jinja2==3.1.4`
          * `MarkupSafe==2.1.5`
          * `click==8.1.7`
          * `packaging==24.0`
          * `rpds-py==0.18.0`
          * `typing_extensions==4.12.2`
          * `jsonschema==4.22.0`
          * `jsonschema-specifications==2023.12.1`
          * `referencing==0.35.0`
          * `attrs==23.2.0`
          * `rpds==0.18.0`
          * `blinker==1.8`
          * `aniso8601==10.0.0`
          * `pytz==2024.1`

4.  **Database and Application Configuration:**

      * This project uses MySQL. Ensure you have a running MySQL server.
      * The `config.py` file contains application settings such as `HOST`, `PORT`, and `DEBUG_MODE`. Adjust them as necessary for your environment.

## Usage

To start the API:

1.  **Ensure your virtual environment is activated.**
2.  **Run the `run.py` script:**
    ```bash
    python run.py
    ```
    This will start the Flask server, and the API will be accessible via the `HOST` and `PORT` defined in `config.py`.

## API Usage Examples

Once the API is running, you can use tools like `curl`, Postman, Insomnia, or an HTTP client to interact with the endpoints.

  * **Example (adapt with actual routes):**
      * `POST /users`: To register a new user.
      * `GET /places`: To retrieve a list of places.
      * `POST /places`: To create a new place.
      * `POST /reviews`: To add a review to a place.

## Tests

The `tests/` folder contains unit and integration tests to validate the proper functioning of the application and the API.

To run the tests:

```bash
python -m unittest discover tests
```

## Contribution

We welcome contributions to this project\! If you wish to improve or extend the HBnB API, please follow these steps:

1.  **Fork the repository:** Create your own copy of the repository on GitHub.
2.  **Clone your fork:**
    ```bash
    git clone https://github.com/YOUR_GITHUB_USERNAME/hbnb-bl-api.git
    cd hbnb-bl-api/part2 # Navigate to the project folder
    ```
3.  **Create a new branch:** Give your branch a descriptive name for the feature or fix you are implementing.
    ```bash
    git checkout -b feature/your-feature-name
    # or bugfix/your-bug-fix
    ```
4.  **Make your changes:** Code your additions or fixes.
5.  **Run tests:** Ensure all changes work correctly and do not break existing functionalities.
    ```bash
    python -m unittest discover tests
    ```
6.  **Build and run the application:** Verify that the API starts and behaves as expected with your changes.
    ```bash
    python run.py
    ```
7.  **Commit your changes:**
    ```bash
    git add .
    git commit -m "feat: Add new feature X"
    # or "fix: Fix bug Y"
    ```
8.  **Push your changes to your fork:**
    ```bash
    git push origin feature/your-feature-name
    ```
9.  **Open a Pull Request (PR):** Go to your fork's GitHub page and open a Pull Request to the `main` branch of the original repository. Clearly describe the changes you've made and why.

We will review your Pull Request as soon as possible. Thank you in advance for your contribution\!

## Group Members

  * Dirimo IRIARTE PEREZ
  * Nomen RATSIMBA
  * Partrice BOLIN

## License

This project is part of the Holberton School Software Engineering curriculum.

**Repository:** [holbertonschool-hbnb](https://github.com/Dirimo/holbertonschool-hbnb)
**Project:** HBnB Evolution - Part 2 (BL and API)
**School:** Holberton School

---
