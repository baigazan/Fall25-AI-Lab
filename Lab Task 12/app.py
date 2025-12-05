from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load the pre-trained model and encoders
MODEL_PATH = 'model_rf.pkl'
ENCODERS_PATH = 'encoders.pkl'

model = None
encoders = None

try:
    # Load the model
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
    
    # Load the encoders
    with open(ENCODERS_PATH, 'rb') as f:
        encoders = pickle.load(f)
    print(f"✅ Encoders loaded successfully from {ENCODERS_PATH}")
    print(f"   - Gender encoder: {list(encoders['gender'].classes_)}")
    print(f"   - Education encoder: {list(encoders['education'].classes_)}")
    print(f"   - Job Title encoder: {len(encoders['job_title'].classes_)} job titles")
    
except FileNotFoundError as e:
    print(f"❌ Error: File not found - {e}")
    print(f"   Please run: python train_with_real_data.py")
except Exception as e:
    print(f"❌ Error loading model/encoders: {e}")

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict salary based on input features
    Expected input: Experience_Years, Age, Gender, Job_Title, Education_Level
    """
    try:
        # Check if model and encoders are loaded
        if model is None or encoders is None:
            return jsonify({
                'error': 'Model or encoders not loaded. Please run: python train_with_real_data.py'
            }), 500
        
        # Get JSON data from request
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract features
        experience = data.get('experience_years')
        age = data.get('age')
        gender = data.get('gender')
        job_title = data.get('job_title')
        education = data.get('education_level')
        
        # Validate required fields
        if experience is None or age is None or gender is None or job_title is None or education is None:
            return jsonify({
                'error': 'Missing required fields: experience_years, age, gender, job_title, education_level'
            }), 400
        
        # Convert to appropriate types
        try:
            experience = float(experience)
            age = float(age)
        except ValueError:
            return jsonify({
                'error': 'Experience and Age must be numeric values'
            }), 400
        
        # Validate ranges
        if experience < 0 or experience > 50:
            return jsonify({
                'error': 'Experience years must be between 0 and 50'
            }), 400
        
        if age < 18 or age > 100:
            return jsonify({
                'error': 'Age must be between 18 and 100'
            }), 400
        
        # Encode gender using the trained encoder
        try:
            gender_encoded = encoders['gender'].transform([gender])[0]
            gender_display = gender
        except ValueError:
            return jsonify({
                'error': f'Invalid gender: {gender}. Must be one of: {list(encoders["gender"].classes_)}'
            }), 400
        
        # Encode job title using the trained encoder
        try:
            job_title_encoded = encoders['job_title'].transform([job_title])[0]
            job_title_display = job_title
        except ValueError:
            return jsonify({
                'error': f'Invalid job title: {job_title}. Please select a valid job title from the dropdown.'
            }), 400
        
        # Encode education level using the trained encoder
        try:
            education_encoded = encoders['education'].transform([education])[0]
            education_display = education
        except ValueError:
            return jsonify({
                'error': f'Invalid education level: {education}. Must be one of: {list(encoders["education"].classes_)}'
            }), 400
        
        # Prepare features for prediction
        # Feature order: experience, age, gender, job_title, education
        features = np.array([[experience, age, gender_encoded, job_title_encoded, education_encoded]])
        
        # Make prediction
        prediction = model.predict(features)
        predicted_salary = float(prediction[0])
        
        # Calculate statistics for visualization
        # These are example values - adjust based on your data
        avg_salary = 60000  # Example average
        min_salary = 30000  # Example minimum
        max_salary = 150000  # Example maximum
        
        # Calculate percentile (where does this prediction fall)
        percentile = min(100, max(0, ((predicted_salary - min_salary) / (max_salary - min_salary)) * 100))
        
        return jsonify({
            'success': True,
            'predicted_salary': round(predicted_salary, 2),
            'average_salary': avg_salary,
            'percentile': round(percentile, 1),
            'input_data': {
                'experience_years': experience,
                'age': age,
                'gender': gender_display,
                'job_title': job_title_display,
                'education_level': education_display
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Prediction error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
