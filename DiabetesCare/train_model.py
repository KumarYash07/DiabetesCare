import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

DATA_PATH = 'diabetes.csv'
MODEL_PATH = 'model.pkl'

def train_and_save_model():
    print("Training Random Forest model...")

    # Load dataset (Pima Indians Diabetes Dataset style)
    df = pd.read_csv(DATA_PATH, header=None)
    df.columns = [
        'Pregnancies',
        'Glucose',
        'BloodPressure',
        'SkinThickness',
        'Insulin',
        'BMI',
        'DiabetesPedigreeFunction',
        'Age',
        'Outcome'
    ]

    print(f"Dataset loaded with {len(df)} rows.")

    X = df.drop(columns=['Outcome'])
    y = df['Outcome']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Random Forest Model
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    # Train model
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    # Save model + accuracy
    with open(MODEL_PATH, 'wb') as file:
        pickle.dump((model, accuracy), file)

    print("Random Forest model and accuracy saved successfully.")

if __name__ == "__main__":
    train_and_save_model()
