# DiabetesCare Web Application

This is a Flask-based web application designed to mimic the structure of the American Diabetes Association website, providing informational content and a diabetes risk prediction tool.

## Project Structure

The project follows the structure you requested:

```
DiabetesCare/
│
├── app.py                 # Main Flask application with all routes (Home, Info, Auth, Prediction)
├── model.pkl              # The trained machine learning model (currently a simple rule-based function)
├── diabetes.csv           # The Pima Indian Diabetes dataset used for the model
├── model_logic.py         # Contains the simple_rule_model function to resolve pickling issues
├── train_model.py         # Script to "train" and save the model.pkl file
│
├── static/
│   ├── css/
│   │   └── style.css      # Comprehensive, responsive CSS styling
│   ├── images/
│   │   └── hero.jpg       # Placeholder image
│
└── templates/
    ├── base.html          # Base template with the dual navigation bar structure
    ├── index.html         # Home page
    ├── about.html         # Informational page
    ├── prevention.html    # Informational page
    ├── causes.html        # Informational page
    ├── login.html         # User login form
    ├── register.html      # User registration form
    ├── risk_test.html     # Multi-step form for prediction input
    └── result.html        # Prediction result page
```

## How to Run the Application

1.  **Navigate to the project directory:**
    ```bash
    cd DiabetesCare
    ```

2.  **Install Dependencies:**
    The application requires `Flask`, `pandas`, and `numpy`.
    ```bash
    pip3 install flask pandas numpy
    ```

3.  **Run the Application:**
    ```bash
    python3.11 app.py
    ```
    The application will start on `http://127.0.0.1:5000`.

## Key Features

*   **Dual Navigation Bar:** A utility bar for account/search and a main bar for content navigation.
*   **User Authentication:** Simple in-memory login/register functionality (for demonstration).
    *   **Test User:** Email: `test@example.com`, Password: `password123`
*   **Informational Pages:** Pages for "Causes of Diabetes" and "Diabetes Prevention."
*   **Diabetes Risk Test:** A multi-step form, inspired by the reference image, that collects 8 features for prediction.
*   **Custom ML Model:** The prediction uses a custom, non-API-dependent model (`model.pkl`) trained on the `diabetes.csv` dataset. The model is a simple rule-based function for demonstration purposes, as the full `scikit-learn` library could not be installed in the environment.

### Prediction Input Fields (Pima Indian Diabetes Dataset Features)

To test the prediction feature, you will need to input values for the following 8 features:

1.  **Pregnancies** (Number of times pregnant)
2.  **Glucose** (Plasma glucose concentration a 2 hours in an oral glucose tolerance test)
3.  **BloodPressure** (Diastolic blood pressure (mm Hg))
4.  **SkinThickness** (Triceps skin fold thickness (mm))
5.  **Insulin** (2-Hour serum insulin (mu U/ml))
6.  **BMI** (Body mass index (weight in kg/(height in m)^2))
7.  **DPF** (Diabetes Pedigree Function)
8.  **Age** (Age in years)

**Example for High Risk (Prediction = 1):**
*   Glucose: `180`
*   BMI: `35`
*   Other fields can be any valid number.

**Example for Low Risk (Prediction = 0):**
*   Glucose: `100`
*   BMI: `25`
*   Other fields can be any valid number.
