"""
Train Random Forest model using actual Salary Data.csv
This script trains the model with real job titles and education levels
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

print("=" * 60)
print("TRAINING SALARY PREDICTION MODEL WITH REAL DATA")
print("=" * 60)

# 1️⃣ Load the dataset
print("\n1️⃣ Loading Salary Data.csv...")
try:
    df = pd.read_csv('Salary Data.csv')
    print(f"   ✅ Loaded {len(df)} records")
except FileNotFoundError:
    print("   ❌ Error: 'Salary Data.csv' not found!")
    print("   Please ensure the file exists in the project directory")
    exit(1)

# 2️⃣ Data preprocessing
print("\n2️⃣ Preprocessing data...")
print(f"   Original records: {len(df)}")

# Remove rows with missing values
df = df.dropna()
print(f"   After removing nulls: {len(df)} records")

# Display column names
print(f"   Columns: {list(df.columns)}")

# 3️⃣ Create label encoders for categorical variables
print("\n3️⃣ Creating label encoders...")

encoders = {}

# Gender encoder
gender_encoder = LabelEncoder()
df['Gender_Encoded'] = gender_encoder.fit_transform(df['Gender'])
encoders['gender'] = gender_encoder
print(f"   Gender mapping: {dict(zip(gender_encoder.classes_, range(len(gender_encoder.classes_))))}")

# Education encoder
education_encoder = LabelEncoder()
df['Education_Encoded'] = education_encoder.fit_transform(df['Education Level'])
encoders['education'] = education_encoder
print(f"   Education mapping: {dict(zip(education_encoder.classes_, range(len(education_encoder.classes_))))}")

# Job Title encoder
job_title_encoder = LabelEncoder()
df['JobTitle_Encoded'] = job_title_encoder.fit_transform(df['Job Title'])
encoders['job_title'] = job_title_encoder
print(f"   Job Titles: {len(job_title_encoder.classes_)} unique titles encoded")

# 4️⃣ Prepare features and target
print("\n4️⃣ Preparing features and target...")

# Features: [Years of Experience, Age, Gender_Encoded, JobTitle_Encoded, Education_Encoded]
X = df[['Years of Experience', 'Age', 'Gender_Encoded', 'JobTitle_Encoded', 'Education_Encoded']].values
y = df['Salary'].values

print(f"   Features shape: {X.shape}")
print(f"   Target shape: {y.shape}")
print(f"   Salary range: ${y.min():,.0f} - ${y.max():,.0f}")
print(f"   Average salary: ${y.mean():,.2f}")

# 5️⃣ Split data
print("\n5️⃣ Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   Training set: {len(X_train)} samples")
print(f"   Testing set: {len(X_test)} samples")

# 6️⃣ Train the model
print("\n6️⃣ Training Random Forest model...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)
print("   ✅ Model training complete!")

# 7️⃣ Evaluate the model
print("\n7️⃣ Evaluating model performance...")
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)
print(f"Training R² Score:  {train_score:.4f} ({train_score*100:.2f}%)")
print(f"Testing R² Score:   {test_score:.4f} ({test_score*100:.2f}%)")
print("=" * 60)

# 8️⃣ Test predictions
print("\n8️⃣ Testing predictions with actual data:")

test_cases = [
    {
        'experience': 5,
        'age': 32,
        'gender': 'Male',
        'job_title': 'Software Engineer',
        'education': "Bachelor's"
    },
    {
        'experience': 8,
        'age': 35,
        'gender': 'Female',
        'job_title': 'Data Scientist',
        'education': "Master's"
    },
    {
        'experience': 15,
        'age': 45,
        'gender': 'Male',
        'job_title': 'Senior Manager',
        'education': "PhD"
    },
    {
        'experience': 20,
        'age': 50,
        'gender': 'Female',
        'job_title': 'Director',
        'education': "Master's"
    }
]

for case in test_cases:
    try:
        gender_enc = encoders['gender'].transform([case['gender']])[0]
        job_enc = encoders['job_title'].transform([case['job_title']])[0]
        edu_enc = encoders['education'].transform([case['education']])[0]
        
        features = np.array([[
            case['experience'],
            case['age'],
            gender_enc,
            job_enc,
            edu_enc
        ]])
        
        prediction = model.predict(features)[0]
        
        print(f"   {case['job_title']} | {case['education']} | {case['gender']} | {case['experience']}y exp | {case['age']}y old")
        print(f"   → Predicted Salary: ${prediction:,.2f}\n")
    except ValueError as e:
        print(f"   ⚠️ Skipping {case['job_title']}: {e}\n")

# 9️⃣ Save model and encoders
print("9️⃣ Saving model and encoders...")

# Save model
with open('model_rf.pkl', 'wb') as f:
    pickle.dump(model, f)
print("   ✅ Model saved to 'model_rf.pkl'")

# Save encoders
with open('encoders.pkl', 'wb') as f:
    pickle.dump(encoders, f)
print("   ✅ Encoders saved to 'encoders.pkl'")

# Save job titles list for frontend
job_titles = sorted(job_title_encoder.classes_.tolist())
with open('static/job_titles.txt', 'w') as f:
    f.write('\n'.join(job_titles))
print("   ✅ Job titles list saved")

# Save education levels list for frontend
education_levels = sorted(education_encoder.classes_.tolist())
with open('static/education_levels.txt', 'w') as f:
    f.write('\n'.join(education_levels))
print("   ✅ Education levels list saved")

print("\n" + "=" * 60)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 60)
print(f"Features: Years of Experience, Age, Gender, Job Title, Education")
print(f"Job Titles: {len(job_title_encoder.classes_)}")
print(f"Education Levels: {len(education_encoder.classes_)}")
print(f"Test R² Score: {test_score:.4f}")
print("=" * 60)
print("\n🚀 Ready to run: python3 run_server.py")
