
import time


import json
from flask import Flask, render_template, request, jsonify

from groq import Groq
apikey= "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"
app = Flask(__name__)

@app.route('/queens_college')
def index():
    return render_template('queens_college.html')
@app.route('/columbia')
def history_page():
    return render_template('columbia.html')
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/queens_college')
def queens_college_page():
    # Load the JSON data
    with open('data/queens_cs_course.json', 'r') as file:
        courses = json.load(file)
    # Pass the courses to the template
    return render_template('queens_college.html', courses=courses)
@app.route('/plan_schedule')
def plan_schedule():
    return render_template('plan_schedule.html')

@app.route('/submit_schedule', methods=['POST'])
def submit_schedule():
    year = request.form['year']
    num_courses = request.form['num_courses']
    taken_courses = request.form.getlist('taken_courses')

    # You can now process this data, for example, print it or store it for later use
    print(f"Year: {year}")
    print(f"Number of courses: {num_courses}")
    print(f"Courses already taken: {', '.join(taken_courses)}")

    # Redirect back to a thank you page or show the result
    return redirect(url_for('thank_you'))


@app.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    data = request.get_json()
    year = data['year']
    semester = data['semester']
    completed_courses = data['completedCourses']
    queens_courses = load_queens_courses()

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
        I am a {year} student in the {semester} semester at Queens College.
        I have already completed the following courses: {', '.join(completed_courses)}.
        Please generate a semester-by-semester course schedule for me considering prerequisites, graduation requirements, and electives.
        Here are the courses and their prerequisites: {json.dumps(queens_courses, indent=2)}. Please just give the schedule no additional info.
        """,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    schedule = chat_completion.choices[0].message.content

    return jsonify({"schedule": schedule})

    
# @app.route('/plan_schedule', methods=['POST'])
# def plan_schedule():
#     # Extract form data
#     year = request.form['year']
#     num_courses = request.form['num_courses']
#     taken_courses = request.form.getlist('taken_courses[]')

#     # Prepare the prompt for OpenAI
#     prompt = generate_schedule_prompt(year, num_courses, taken_courses)

#     # Call OpenAI API with the prepared prompt
#     response = openai.Completion.create(
#         engine="text-davinci-003",  # Use the appropriate model
#         prompt=prompt,
#         max_tokens=500,  # Limit response length
#         temperature=0.7,  # Control randomness
#     )

#     # Extract the response from OpenAI
#     schedule_plan = response.choices[0].text.strip()

#     return jsonify({"schedule_plan": schedule_plan})

# def generate_schedule_prompt(year, num_courses, taken_courses):
#     # Construct a detailed prompt to send to OpenAI
#     prompt = f"""
#     I am a student in {year} year. I want to take {num_courses} computer science courses per semester.
#     Here are the courses I have already taken: {', '.join(taken_courses)}.
#     Based on this information, plan a schedule for me considering the prerequisites and available electives.
#     Please provide a detailed semester-by-semester schedule.
#     """
#     return prompt

if __name__ == '__main__':
    app.run(debug=True)

