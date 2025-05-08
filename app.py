import os
import json
import logging
import csv
import io
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Ensure data files exist with empty structures
if not os.path.exists('data/students.json'):
    with open('data/students.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('data/attendance.json'):
    with open('data/attendance.json', 'w') as f:
        json.dump({}, f)

# Utility functions
def load_students():
    try:
        with open('data/students.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_students(students):
    with open('data/students.json', 'w') as f:
        json.dump(students, f, indent=4)

def load_attendance():
    try:
        with open('data/attendance.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_attendance(attendance):
    with open('data/attendance.json', 'w') as f:
        json.dump(attendance, f, indent=4)

def get_next_id(students):
    if not students:
        return 1
    return max(int(student['id']) for student in students) + 1

def get_student_by_id(student_id):
    students = load_students()
    for student in students:
        if student['id'] == student_id:
            return student
    return None

# Routes
@app.route('/')
def index():
    students = load_students()
    attendance = load_attendance()
    
    # Get today's date in YYYY-MM-DD format
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Calculate some stats for dashboard
    total_students = len(students)
    present_today = 0
    
    if today in attendance:
        for student_id, status in attendance[today].items():
            if status == 'present':
                present_today += 1
    
    absent_today = total_students - present_today
    
    # Get attendance for the last 30 days for chart
    dates = []
    present_counts = []
    absent_counts = []
    
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        dates.append(date_str)
        
        present = 0
        if date_str in attendance:
            for student_id, status in attendance[date_str].items():
                if status == 'present':
                    present += 1
        
        present_counts.append(present)
        absent_counts.append(total_students - present if total_students > 0 else 0)
        
        current_date += datetime.timedelta(days=1)
    
    return render_template('index.html', 
                          total_students=total_students,
                          present_today=present_today,
                          absent_today=absent_today,
                          dates=dates,
                          present_counts=present_counts,
                          absent_counts=absent_counts)

@app.route('/students', methods=['GET'])
def students():
    students = load_students()
    return render_template('students.html', students=students)

@app.route('/students/add', methods=['POST'])
def add_student():
    students = load_students()
    
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    gender = request.form.get('gender', '').strip()
    grade = request.form.get('grade', '').strip()
    
    # Validate form data
    if not first_name or not last_name or not gender or not grade:
        flash('All fields are required', 'danger')
        return redirect(url_for('students'))
    
    # Create new student record
    new_student = {
        'id': str(get_next_id(students)),
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'grade': grade
    }
    
    students.append(new_student)
    save_students(students)
    
    flash('Student added successfully', 'success')
    return redirect(url_for('students'))

@app.route('/students/edit/<string:student_id>', methods=['POST'])
def edit_student(student_id):
    students = load_students()
    
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    gender = request.form.get('gender', '').strip()
    grade = request.form.get('grade', '').strip()
    
    # Validate form data
    if not first_name or not last_name or not gender or not grade:
        flash('All fields are required', 'danger')
        return redirect(url_for('students'))
    
    # Update student record
    for student in students:
        if student['id'] == student_id:
            student['first_name'] = first_name
            student['last_name'] = last_name
            student['gender'] = gender
            student['grade'] = grade
            break
    
    save_students(students)
    
    flash('Student updated successfully', 'success')
    return redirect(url_for('students'))

@app.route('/students/delete/<string:student_id>', methods=['POST'])
def delete_student(student_id):
    students = load_students()
    
    # Filter out the student to delete
    students = [student for student in students if student['id'] != student_id]
    save_students(students)
    
    # Also remove this student from all attendance records
    attendance = load_attendance()
    for date in attendance:
        if student_id in attendance[date]:
            del attendance[date][student_id]
    save_attendance(attendance)
    
    flash('Student deleted successfully', 'success')
    return redirect(url_for('students'))

@app.route('/attendance', methods=['GET'])
def attendance():
    students = load_students()
    attendance_data = load_attendance()
    
    # Get the date from query parameter, default to today
    selected_date = request.args.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
    
    # Get attendance for the selected date
    day_attendance = attendance_data.get(selected_date, {})
    
    # Prepare attendance data for each student
    for student in students:
        student_id = student['id']
        student['attendance_status'] = day_attendance.get(student_id, 'absent')
    
    return render_template('attendance.html', 
                          students=students,
                          selected_date=selected_date)

@app.route('/attendance/mark', methods=['POST'])
def mark_attendance():
    attendance_data = load_attendance()
    
    date = request.form.get('date')
    student_id = request.form.get('student_id')
    status = request.form.get('status')
    
    if not date or not student_id or not status:
        flash('Invalid attendance data', 'danger')
        return redirect(url_for('attendance', date=date))
    
    # Initialize the date in attendance if it doesn't exist
    if date not in attendance_data:
        attendance_data[date] = {}
    
    # Mark attendance
    attendance_data[date][student_id] = status
    save_attendance(attendance_data)
    
    flash('Attendance marked successfully', 'success')
    return redirect(url_for('attendance', date=date))

@app.route('/reports', methods=['GET'])
def reports():
    students = load_students()
    attendance_data = load_attendance()
    
    # Get current month and year
    now = datetime.datetime.now()
    selected_month = int(request.args.get('month', now.month))
    selected_year = int(request.args.get('year', now.year))
    
    # Get all dates in the selected month
    first_day = datetime.datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        last_day = datetime.datetime(selected_year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        last_day = datetime.datetime(selected_year, selected_month + 1, 1) - datetime.timedelta(days=1)
    
    dates_in_month = []
    current_date = first_day
    while current_date <= last_day:
        dates_in_month.append(current_date.strftime('%Y-%m-%d'))
        current_date += datetime.timedelta(days=1)
    
    # Calculate attendance statistics for each student
    for student in students:
        student_id = student['id']
        student['present_count'] = 0
        student['absent_count'] = 0
        
        for date in dates_in_month:
            if date in attendance_data and student_id in attendance_data[date]:
                if attendance_data[date][student_id] == 'present':
                    student['present_count'] += 1
                else:
                    student['absent_count'] += 1
            else:
                # If no record, count as absent
                student['absent_count'] += 1
        
        # Calculate attendance percentage
        total_days = len(dates_in_month)
        if total_days > 0:
            student['attendance_percentage'] = (student['present_count'] / total_days) * 100
        else:
            student['attendance_percentage'] = 0
    
    return render_template('reports.html', 
                          students=students,
                          selected_month=selected_month,
                          selected_year=selected_year,
                          months=range(1, 13),
                          years=range(now.year - 5, now.year + 1))

@app.route('/export/csv', methods=['GET'])
def export_csv():
    students = load_students()
    attendance_data = load_attendance()
    
    # Get month and year from query parameters
    now = datetime.datetime.now()
    selected_month = int(request.args.get('month', now.month))
    selected_year = int(request.args.get('year', now.year))
    
    # Get all dates in the selected month
    first_day = datetime.datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        last_day = datetime.datetime(selected_year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        last_day = datetime.datetime(selected_year, selected_month + 1, 1) - datetime.timedelta(days=1)
    
    dates_in_month = []
    current_date = first_day
    while current_date <= last_day:
        dates_in_month.append(current_date.strftime('%Y-%m-%d'))
        current_date += datetime.timedelta(days=1)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    header = ['Student ID', 'First Name', 'Last Name', 'Grade']
    for date in dates_in_month:
        header.append(date)
    header.extend(['Present Count', 'Absent Count', 'Attendance Percentage'])
    writer.writerow(header)
    
    # Write data for each student
    for student in students:
        student_id = student['id']
        row = [student_id, student['first_name'], student['last_name'], student['grade']]
        
        present_count = 0
        absent_count = 0
        
        for date in dates_in_month:
            if date in attendance_data and student_id in attendance_data[date]:
                status = attendance_data[date][student_id]
                row.append(status)
                if status == 'present':
                    present_count += 1
                else:
                    absent_count += 1
            else:
                row.append('absent')
                absent_count += 1
        
        # Calculate attendance percentage
        total_days = len(dates_in_month)
        if total_days > 0:
            attendance_percentage = (present_count / total_days) * 100
        else:
            attendance_percentage = 0
        
        row.extend([present_count, absent_count, f"{attendance_percentage:.2f}%"])
        writer.writerow(row)
    
    # Prepare the response
    output.seek(0)
    month_name = datetime.datetime(selected_year, selected_month, 1).strftime('%B')
    filename = f"attendance_{month_name}_{selected_year}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)