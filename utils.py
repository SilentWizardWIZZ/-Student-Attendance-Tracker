import json
import datetime
import os
from typing import Dict, List, Optional, Union

def ensure_data_directory():
    """Ensure that the data directory exists."""
    if not os.path.exists('data'):
        os.makedirs('data')

def ensure_data_files():
    """Ensure that the data files exist with valid initial structure."""
    # Ensure students.json exists
    if not os.path.exists('data/students.json'):
        with open('data/students.json', 'w') as f:
            json.dump([], f)
    
    # Ensure attendance.json exists
    if not os.path.exists('data/attendance.json'):
        with open('data/attendance.json', 'w') as f:
            json.dump({}, f)

def load_students() -> List[Dict]:
    """Load students data from students.json file."""
    try:
        with open('data/students.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, return empty list
        return []

def save_students(students: List[Dict]) -> None:
    """Save students data to students.json file."""
    ensure_data_directory()
    with open('data/students.json', 'w') as f:
        json.dump(students, f, indent=4)

def load_attendance() -> Dict:
    """Load attendance data from attendance.json file."""
    try:
        with open('data/attendance.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, return empty dict
        return {}

def save_attendance(attendance: Dict) -> None:
    """Save attendance data to attendance.json file."""
    ensure_data_directory()
    with open('data/attendance.json', 'w') as f:
        json.dump(attendance, f, indent=4)

def get_next_id(students: List[Dict]) -> str:
    """Generate the next ID for a new student."""
    if not students:
        return "1"
    return str(max(int(student['id']) for student in students) + 1)

def get_student_by_id(student_id: str) -> Optional[Dict]:
    """Get a student by their ID."""
    students = load_students()
    for student in students:
        if student['id'] == student_id:
            return student
    return None

def get_date_range(year: int, month: int) -> List[str]:
    """Get a list of dates for a given month and year in YYYY-MM-DD format."""
    # Get the first day of the month
    first_day = datetime.datetime(year, month, 1)
    
    # Get the last day of the month
    if month == 12:
        last_day = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        last_day = datetime.datetime(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # Generate list of dates
    dates = []
    current_date = first_day
    while current_date <= last_day:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += datetime.timedelta(days=1)
    
    return dates

def calculate_attendance_stats(students: List[Dict], attendance_data: Dict, year: int, month: int) -> List[Dict]:
    """Calculate attendance statistics for each student for a given month."""
    # Get dates in the month
    dates_in_month = get_date_range(year, month)
    
    # Calculate statistics for each student
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
    
    return students