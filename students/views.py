from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from .forms import StudentForm, UploadPDFForm, StudentLoginForm, SemesterForm, StaffForm
from .models import Student, Result, AdminUser, Staff,  Attendance
from django.contrib import messages
import PyPDF2
import re
import pandas as pd
import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import datetime
from django.views.decorators.cache import never_cache, cache_control

logger = logging.getLogger(__name__)

@never_cache
def index(request):
    return render(request, 'index.html')

@never_cache
def login(request):
    logger.debug("Login view accessed")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        logger.debug(f"Attempting login for username: {username}")
        
        # Attempt authentication for admin
        user = authenticate(request, username=username, password=password)
        if user is not None:
            logger.debug("Admin authentication succeeded")
            auth_login(request, user)
            return redirect('dashboard')
        
        # Attempt authentication for staff
        try:
            staff = Staff.objects.get(staff_id=username, phone_number=password)
            logger.debug("Successful staff authentication")
            # Store the staff ID in the session
            request.session['staff_id'] = username
            return redirect('staff_dashboard')
        except Staff.DoesNotExist:
            pass
        
        # Attempt authentication for student
        try:
            student = Student.objects.get(rollno=username)
            if student.authenticate(password):
                logger.debug("Successful student authentication")
                # Store the roll number in the session
                request.session['rollno'] = username
                return redirect('student_dashboard')
        except Student.DoesNotExist:
            pass
        
        logger.debug("Authentication failed")
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    else:
        return render(request, 'login.html')

@never_cache
def dashboard(request):
    student_count = Student.objects.count()
    staff_count = Staff.objects.count()
    context = {
        'staff_count': staff_count,
        'students_count': student_count
    }
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            pdf_file = request.FILES.get('pdf_file')
            if pdf_file and pdf_file.name.endswith('.pdf'):
                process_uploaded_pdf(pdf_file, student)
                return redirect('dashboard')
            else:
                return render(request, 'dashboard.html', {'form': form, 'error': 'Please upload a PDF file.'})
    else:
        form = StudentForm()
    return render(request, 'dashboard.html', {'form': form})

@never_cache
def delete_student(request, roll_no):
    if request.method == 'POST':
        student = get_object_or_404(Student, rollno=roll_no)
        student.delete()
        messages.success(request, "Student deleted successfully.")
    return redirect('students')

@never_cache
def students(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            roll_no = form.cleaned_data['rollno']
            email = form.cleaned_data['email']
            if Student.objects.filter(rollno=roll_no).exists():
                # If the student with the same roll number already exists, add error to form's errors list
                form.add_error('rollno', 'A student with the same roll number already exists.')
            elif Student.objects.filter(email=email).exists():
                # If the student with the same email already exists, add error to form's errors list
                form.add_error('email', 'A student with the same email already exists.')
            else:
                form.save()  # Save the student details to the database
                # Render the student added success page
                return render(request, 'student_added_success.html')
    else:
        form = StudentForm()
    
    query = request.GET.get('query')
    student = None

    if query:
        try:
            student = Student.objects.get(rollno=query)
        except Student.DoesNotExist:
            # Handle the case where the student is not found
            return render(request, 'student_not_found.html', {'query': query})
        # Render the student details page if the student is found
        return render(request, 'students_details.html', {'student': student})

    students_list = Student.objects.all()  # Retrieve all students from the database

    return render(request, 'students.html', {'form': form, 'students_list': students_list})

@never_cache
def student_details(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    
    if request.method == 'POST':
        semester = request.POST.get('semester')
        
        # Query the results associated with the student's roll number and the selected semester
        results = Result.objects.filter(htno=student.rollno, semester=semester)
        
        return render(request, 'student_details.html', {'student': student, 'results': results, 'semester': semester})
    else:
        results = Result.objects.filter(htno=student.rollno)
        return render(request, 'student_details.html', {'student': student,'results': results})

@never_cache
def student_dashboard(request, semester=None):
    roll_no = request.session.get('rollno')
    selected_date = request.GET.get('attendance_date')
    
    # Fetch student details from the database
    try:
        student = Student.objects.get(rollno=roll_no)
    except Student.DoesNotExist:
        student = None
    
    if request.method == 'POST':
        semester = request.POST.get('semester')
        print("Roll Number from Session:", roll_no)  # Debug print statement
        
        if 'attendance_submit' in request.POST:  # Check if the attendance button was clicked
            # Render the student dashboard template with the attendance records for the selected date
            return render(request, 'student_dashboard.html', {'student': student, 'roll_no': roll_no, 'selected_date': selected_date})
        
        # Query the results associated with the logged-in student's roll number and the selected semester
        results = Result.objects.filter(htno=roll_no, semester=semester)
        print("Results Queryset:", results)  # Debug print statement
        
        # Render the student dashboard template with the results of the selected semester
        return render(request, 'student_dashboard.html', {'results': results, 'semester': semester, 'student': student,'selected_date': selected_date})
    else:
        # If the request method is not POST, render the template without any results
        return render(request, 'student_dashboard.html', {'student': student, 'roll_no': roll_no, 'selected_date': selected_date})

@never_cache
def display_results(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        semester = request.POST.get('semester')
        student = get_object_or_404(Student, pk=student_id)
        results = Result.objects.filter(htno=student.rollno, semester=semester)
        return render(request, 'display_results.html', {'student': student, 'results': results, 'semester': semester})
    else:
        return render(request, 'display_results.html')  # Render the display_results.html template

def process_uploaded_pdf(pdf_file_path, semester):
    # Your implementation for processing PDF files
    pass

@never_cache
def upload_pdf(request):
    if request.method == 'POST':
        form = UploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            semester = request.POST.get('semester')  # Get the selected semester
            # Save the uploaded PDF file to a temporary location
            with open('temp_pdf.pdf', 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)
            
            # Process the uploaded PDF file to extract data and save to the database
            pdf_file_path = 'temp_pdf.pdf'  # Provide the path to the uploaded PDF file
            process_uploaded_pdf(pdf_file_path, semester)  # Pass the semester to the processing function
            
            # Provide the Excel file path for download or further processing if needed
            return render(request, 'upload_success.html')
    else:
        form = UploadPDFForm()
    
    return render(request, 'students.html', {'form': form})

@never_cache
def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def calculate_grade_points(grade):
    grading_system = {
        'A+': 10, 'A': 9, 'B+': 8, 'B': 7,
        'C+': 6, 'C': 5, 'D': 4, 'F': 0
    }
    return grading_system.get(grade, 0)

def calculate_sgpa(results):
    total_grade_points = 0  # Initialize total grade points
    total_credit_hours = 0  # Initialize total credit hours
    for result in results:
        grade_points = calculate_grade_points(result.grade)  # Calculate grade points for the grade
        credit_hours = int(result.credits)  # Convert credits to integer
        total_grade_points += grade_points * credit_hours  # Add grade points multiplied by credit hours
        total_credit_hours += credit_hours  # Add credit hours
        
    if total_credit_hours > 0:
        sgpa = total_grade_points / total_credit_hours  # Calculate SGPA

        return round(sgpa, 2) # Round SGPA and CGPA to 2 decimal places
    return 0, 0

@never_cache
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save()  # Save the staff details to the database
            print("Staff added successfully:", staff)  # Print staff details for debugging
            # Redirect to a success page or any other page as needed
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging
    else:
        form = StaffForm()
    return render(request, 'add_staff.html', {'form': form})

@never_cache
def staff_dashboard(request):
    staff_id = request.session.get('staff_id')
    
    try:
        staff = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        staff = None
    
    if request.method == 'POST':
        rollno = request.POST.get('rollno')
        if rollno:
            try:
                student = Student.objects.get(rollno=rollno)
                return render(request, 'students_details.html', {'student': student, 'staff': staff})
            except Student.DoesNotExist:
                return render(request, 'student_not_found.html', {'rollno': rollno, 'staff': staff})
        else:
            return redirect('attendance_form')  # Redirect to the attendance form page
    else:
        return render(request, 'staff_dashboard.html', {'staff': staff})

@never_cache
def attendance_form(request):
    if request.method == 'POST':
        # Process the form data here
        
        # Redirect to the display_students page
        return redirect('display_students')  # Replace 'display_students' with the URL name of the page
        
    else:
        return render(request, 'attendance_form.html')

@never_cache
def display_students(request, branch, section, year, day, hour):
    if request.method == 'POST':
        branch = request.POST.get('branch')
        section = request.POST.get('section')
        year = request.POST.get('year')
        day = request.POST.get('day')
        hour = request.POST.get('hour')
        
        # Retrieve students based on the selected branch, section, and year
        students = Student.objects.filter(branch=branch, section=section, year=year)
        
        context = {
            'students': students,
            'branch': branch,
            'section': section,
            'year': year,
            'day': day,
            'hour': hour,
        }
        
        return render(request, 'display_students.html', context)
    else:
        return render(request, 'attendance_form.html')

@never_cache
def submit_attendance(request):
    if request.method == 'POST':
        branch = request.POST.get('branch')
        section = request.POST.get('section')
        year = request.POST.get('year')
        day = request.POST.get('day')
        hour = request.POST.get('hour')

        # Iterate through the submitted attendance data
        for rollno, attendance_status in request.POST.items():
            if rollno.startswith('attendance'):
                roll_number = rollno.split('_')[1]  # Extract the roll number from the input name
                present = attendance_status == 'present'

                # Create or update the Attendance object
                Attendance.objects.update_or_create(
                    date=day,
                    roll_number=roll_number,
                    hour=hour,
                    defaults={'present': present}
                )

        # Redirect back to the display_students page
        return redirect('display_students', branch=branch, section=section, year=year, day=day, hour=hour)

@never_cache
def view_attendance(request, selected_date):
    print("Selected Date:", selected_date)  # Debug print statement
    
    # Query attendance records for the selected date
    roll_no = request.session.get('rollno')
    attendance_records = Attendance.objects.filter(date=selected_date, roll_number=roll_no)
    print("Attendance Records Queryset:", attendance_records)  # Debug print statement

    # Render the attendance template with the attendance records
    return render(request, 'attendance.html', {'attendance_records': attendance_records, 'selected_date': selected_date})
