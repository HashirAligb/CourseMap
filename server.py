import time

import requests
import fitz 
import json
from flask import Flask, render_template, request, jsonify
import os


from groq import Groq
apikey= "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"
app = Flask(__name__)



client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
def load_queens_courses():
    with open("data/queens_cs_course.json", "r", encoding="utf-8") as file:
        return json.load(file)

def load_columbia_courses():
    with open("data/columbia_cs_courses.json", "r", encoding="utf-8") as file:
        return json.load(file)
# Load Columbia CS courses from JSON file
def get_columbia_courses():
    try:
        with open("data/columbia_cs_courses.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            
            courses = []

            # Extract from core courses
            if "core_courses" in data:
                courses.extend([course["course"] for course in data["core_courses"]])

            # Extract from math requirements (course and alternatives)
            if "math_requirements" in data:
                for item in data["math_requirements"]:
                    courses.append(item["course"])
                    courses.extend(item.get("alternatives", []))  # Include alternative courses

            # Extract from area foundation courses (already a list)
            if "area_foundation_courses" in data:
                courses.extend(data["area_foundation_courses"])
            # Add CS Electives notice
            if "cs_electives" in data:
            
                courses.append(data["cs_electives"])

            return courses

    except Exception as e:
        return [f"Error loading courses: {e}"]

@app.route('/columbia')
def columbia_page():
    courses = get_columbia_courses()  # Get only course names
    return render_template('columbia.html', courses=courses)

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
        For the Queens College one its onlt three electives so please fill any other gap or spot just put Gen Ed of your choice instead. Also it should be like 5 courses per semester.
        Use Queens Colleges Computer Science BA gen ed requirements to recommend the gen eds. Also just put on the top of the box for only the Queens college page Hello! Hashir recommends this schedule: 
        """,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    schedule = chat_completion.choices[0].message.content

    return jsonify({"schedule": schedule})

    
@app.route('/plan_schedule', methods=['POST'])
def plan_schedule():
    data = request.get_json()
    year = data['year']
    semester = data['semester']
    completed_courses = data['completedCourses']
    columbia_courses = load_columbia_courses()

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""
        I am a {year} student in the {semester} semester at Queens College.
        I have already completed the following courses: {', '.join(completed_courses)}.
        Please generate a semester-by-semester course schedule for me considering prerequisites, graduation requirements, and electives.
        Here are the courses and their prerequisites: {json.dumps(columbia_courses, indent=2)}. Please just give the schedule no additional info.
        """,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    schedule = chat_completion.choices[0].message.content
    print(schedule)

    return jsonify({"schedule": schedule})


if __name__ == '__main__':
    app.run(debug=True)
    