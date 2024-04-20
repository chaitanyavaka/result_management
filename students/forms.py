# forms.py
from django import forms
from .models import Student, Staff

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'branch', 'rollno', 'section', 'year','date_of_birth','regulation']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'})
        }
class StudentLoginForm(forms.Form):
    username = forms.CharField(label='Registered Number', max_length=50)
    password = forms.DateField(label='Date of Birth', widget=forms.DateInput(attrs={'type': 'date'}))

class UploadPDFForm(forms.Form):
    pdf_file = forms.FileField(label='Select a PDF file')
class SemesterForm(forms.Form):
    SEMESTER_CHOICES = [
        ('1-1', '1-1'),
        ('1-2', '1-2'),
        ('2-1', '2-1'),
        ('2-2', '2-2'),
        ('3-1', '3-1'),
        ('3-2', '3-2'),
        ('4-1', '4-1'),
        ('4-2', '4-2'),
    ]

    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, label='Select Semester')
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_id','name', 'email', 'phone_number','department','designation']  # Define the fields you want to include in the form
        labels = {
            'staff_id': 'Staff ID',
            'name': 'Name',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'department': 'Department',
            'designation': 'Designation',
        }
