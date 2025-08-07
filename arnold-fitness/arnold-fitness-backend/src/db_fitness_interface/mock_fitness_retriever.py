class MockFitnessRetriever:
    def __init__(self, collection_name=None):
        self.collection_name = collection_name or "arnold_fitness_chunks"
        self.mock_responses = {
            # BMI and Anthropometric assessments
            "bmi_anthropometric": {
                "question": "How do I calculate BMI and interpret anthropometric measurements?",
                "answer": """Step 1: Calculate BMI using the formula: BMI = weight (kg) / height (m)²

WHO BMI Classifications:
- Underweight: <18.5 kg/m²
- Normal weight: 18.5-24.9 kg/m²
- Overweight: 25.0-29.9 kg/m²
- Obesity Class I: 30.0-34.9 kg/m²
- Obesity Class II: 35.0-39.9 kg/m²
- Obesity Class III: ≥40.0 kg/m²

Additional anthropometric measures:
- Waist circumference: Men >102cm, Women >88cm indicates increased health risk
- Waist-to-hip ratio: Men >0.9, Women >0.85 indicates abdominal obesity
- Body fat percentage: Men 10-25%, Women 16-32% (varies by age)

Assessment protocol: Take measurements in the morning, fasted state, minimal clothing."""
            },

            # Weight Loss and Calorie Deficit
            "weight_loss_deficit": {
                "question": "How do I calculate calorie deficit for weight loss?",
                "answer": """Step 1: Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation:
- Men: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
- Women: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161

Step 2: Calculate Total Daily Energy Expenditure (TDEE):
- Sedentary (little/no exercise): BMR × 1.2
- Lightly active (light exercise 1-3 days/week): BMR × 1.375
- Moderately active (moderate exercise 3-5 days/week): BMR × 1.55
- Very active (hard exercise 6-7 days/week): BMR × 1.725
- Extremely active (very hard exercise, physical job): BMR × 1.9

Step 3: Create deficit:
- Safe deficit: 500-750 calories/day (1-1.5 lbs/week loss)
- Maximum deficit: 1000 calories/day (2 lbs/week loss)
- Target intake = TDEE - deficit

Monitor weekly and adjust as needed."""
            },

            # Resistance Training Programs
            "resistance_training": {
                "question": "What's an effective beginner resistance training program?",
                "answer": """Beginner 3-Day Full Body Program:

DAY 1 - Monday:
1. Squats: 3 sets × 8-10 reps
2. Bench Press/Push-ups: 3 sets × 8-10 reps
3. Bent-over Rows: 3 sets × 8-10 reps
4. Overhead Press: 3 sets × 8-10 reps
5. Romanian Deadlifts: 3 sets × 8-10 reps
6. Plank: 3 sets × 30-60 seconds

DAY 2 - Wednesday:
1. Deadlifts: 3 sets × 5-6 reps
2. Incline Dumbbell Press: 3 sets × 8-10 reps
3. Pull-ups/Lat Pulldowns: 3 sets × 8-10 reps
4. Lunges: 3 sets × 10 reps each leg
5. Dumbbell Shoulder Press: 3 sets × 8-10 reps
6. Russian Twists: 3 sets × 20 reps

DAY 3 - Friday:
1. Goblet Squats: 3 sets × 10-12 reps
2. Dumbbell Bench Press: 3 sets × 8-10 reps
3. Seated Cable Rows: 3 sets × 10-12 reps
4. Step-ups: 3 sets × 10 each leg
5. Lateral Raises: 3 sets × 12-15 reps
6. Dead Bugs: 3 sets × 10 each side

Progression: Increase weight by 2.5-5lbs when you can complete all sets with proper form."""
            },

            # Cardiovascular Training
            "cardio_training": {
                "question": "How should I structure cardiovascular training?",
                "answer": """Cardiovascular Training Guidelines:

BEGINNER PROTOCOL:
- Frequency: 3-4 days/week
- Duration: 20-30 minutes
- Intensity: 50-70% max heart rate
- Type: Walking, cycling, swimming

INTERMEDIATE PROTOCOL:
- Frequency: 4-5 days/week
- Duration: 30-45 minutes
- Intensity: 60-80% max heart rate
- Type: Mix of steady-state and interval training

HIIT Protocol (2-3x/week):
- Warm-up: 5 minutes easy pace
- Work intervals: 30 seconds high intensity (80-90% max HR)
- Rest intervals: 90 seconds low intensity (50-60% max HR)
- Repeat: 8-12 cycles
- Cool-down: 5 minutes easy pace

Max Heart Rate calculation: 220 - age
Target zones:
- Fat burning: 60-70% max HR
- Aerobic: 70-80% max HR
- Anaerobic: 80-90% max HR

Monitor RPE (Rate of Perceived Exertion) 1-10 scale alongside heart rate."""
            },

            # Nutrition and Macronutrients
            "nutrition_macros": {
                "question": "How do I calculate and track macronutrients?",
                "answer": """Macronutrient Guidelines:

CALORIE DISTRIBUTION:
- Protein: 4 calories/gram
- Carbohydrates: 4 calories/gram
- Fats: 9 calories/gram

MACRO RATIOS (% of total calories):

For Weight Loss:
- Protein: 25-30% (0.8-1.2g per lb bodyweight)
- Carbohydrates: 35-45%
- Fats: 25-35%

For Muscle Building:
- Protein: 20-25% (1.0-1.6g per lb bodyweight)
- Carbohydrates: 45-55%
- Fats: 20-30%

For Maintenance:
- Protein: 15-20% (0.8-1.0g per lb bodyweight)
- Carbohydrates: 45-55%
- Fats: 25-35%

CALCULATION EXAMPLE (150lb person, 2000 calories, weight loss):
- Protein: 30% × 2000 = 600 calories ÷ 4 = 150g protein
- Carbs: 40% × 2000 = 800 calories ÷ 4 = 200g carbs
- Fats: 30% × 2000 = 600 calories ÷ 9 = 67g fats

Track using apps like MyFitnessPal, Cronometer, or food diary."""
            },

            # Exercise Form and Technique
            "exercise_form": {
                "question": "What are the key points for proper exercise form?",
                "answer": """Fundamental Movement Patterns:

SQUAT TECHNIQUE:
- Feet shoulder-width apart, toes slightly out
- Core braced, chest up, neutral spine
- Initiate with hips back, knees track over toes
- Descend until thighs parallel or below
- Drive through heels to return to start

DEADLIFT TECHNIQUE:
- Bar over mid-foot, shins 1 inch from bar
- Hip-width stance, hands just outside legs
- Shoulders over bar, neutral spine
- Drive through heels, hips and shoulders rise together
- Full hip extension at top, controlled descent

PUSH-UP/BENCH PRESS:
- Hands slightly wider than shoulders
- Core tight, body in straight line
- Lower with control, chest to floor/bar to chest
- Press up explosively, full arm extension

PULL-UP/ROW:
- Full arm extension at bottom
- Pull shoulder blades back and down
- Lead with chest, elbows close to body
- Full range of motion, controlled tempo

GENERAL PRINCIPLES:
- Quality over quantity always
- Full range of motion
- Controlled tempo (2-1-2-1 eccentric-pause-concentric-pause)
- Proper breathing (exhale on exertion)
- Progressive overload"""
            },

            # Recovery and Sleep
            "recovery_sleep": {
                "question": "How important is recovery and sleep for fitness goals?",
                "answer": """Recovery and Sleep Optimization:

SLEEP REQUIREMENTS:
- Adults: 7-9 hours per night
- Athletes/Active individuals: 8-10 hours
- Sleep stages: 4-6 complete cycles per night
- Deep sleep: Critical for physical recovery
- REM sleep: Important for cognitive function

SLEEP HYGIENE:
- Consistent sleep/wake times (including weekends)
- Cool, dark, quiet environment (65-68°F)
- No screens 1-2 hours before bed
- Avoid caffeine 6+ hours before sleep
- No large meals 3 hours before bed

ACTIVE RECOVERY:
- Light walking, yoga, swimming
- Mobility/stretching sessions
- Massage, foam rolling
- Meditation, stress management

REST DAY FREQUENCY:
- Beginners: 2-3 rest days per week
- Intermediate: 1-2 rest days per week
- Advanced: 1 rest day per week minimum

RECOVERY INDICATORS:
- Heart rate variability (HRV)
- Resting heart rate trends
- Sleep quality scores
- Subjective energy levels
- Performance metrics

Poor recovery signs: Elevated resting HR, decreased HRV, persistent fatigue, mood changes, increased injury risk."""
            }
        }

    def search(self, query_text: str, limit=5, filters=None) -> list:
        """
        Mock search that returns relevant fitness guidance based on query keywords
        """
        query_lower = query_text.lower()
        
        # Determine which response to return based on keywords
        response_data = None
        
        if any(keyword in query_lower for keyword in ['bmi', 'anthropometric', 'body composition', 'measurements']):
            response_data = self.mock_responses["bmi_anthropometric"]
        elif any(keyword in query_lower for keyword in ['weight loss', 'deficit', 'calories', 'tdee', 'bmr']):
            response_data = self.mock_responses["weight_loss_deficit"]
        elif any(keyword in query_lower for keyword in ['resistance', 'strength', 'weights', 'lifting', 'muscle building']):
            response_data = self.mock_responses["resistance_training"]
        elif any(keyword in query_lower for keyword in ['cardio', 'cardiovascular', 'running', 'hiit', 'aerobic']):
            response_data = self.mock_responses["cardio_training"]
        elif any(keyword in query_lower for keyword in ['nutrition', 'macros', 'protein', 'diet', 'eating']):
            response_data = self.mock_responses["nutrition_macros"]
        elif any(keyword in query_lower for keyword in ['form', 'technique', 'exercise', 'movement', 'posture']):
            response_data = self.mock_responses["exercise_form"]
        elif any(keyword in query_lower for keyword in ['recovery', 'sleep', 'rest', 'fatigue']):
            response_data = self.mock_responses["recovery_sleep"]
        else:
            # Default general fitness response
            response_data = {
                "question": "General fitness guidance",
                "answer": """For comprehensive fitness success, focus on these key areas:

1. EXERCISE: Combine resistance training (2-3x/week) with cardiovascular exercise (3-4x/week)
2. NUTRITION: Maintain appropriate caloric intake with balanced macronutrients
3. RECOVERY: Prioritize 7-9 hours of quality sleep and rest days
4. PROGRESSION: Gradually increase exercise intensity and complexity
5. CONSISTENCY: Maintain regular habits over time for best results

Always consult healthcare providers before starting new fitness programs, especially if you have medical conditions or concerns."""
            }
        
        # Return mock response in the same format as Qdrant
        return [
            {
                "id": f"mock_fitness_doc_{i+1}",
                "score": 0.9 - (i * 0.1),  # Decreasing relevance scores
                "payload": response_data
            }
            for i in range(min(limit, 3))  # Return up to 3 identical responses with different IDs
        ]