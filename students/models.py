from django.db import models
from django.utils import timezone
import uuid

class AdminUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password (use Django's password hashing)

    def __str__(self):
        return self.username

class Student(models.Model):
    rollno = models.CharField(max_length=50, unique=True,primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    branch = models.CharField(max_length=100)
    section = models.CharField(max_length=10)
    year = models.IntegerField()
    date_of_birth = models.DateField(default=timezone.now)
    regulation = models.CharField(max_length=10)



    def __str__(self):
        return self.name

    def authenticate(self, password):
        # Check if the provided password matches the date of birth in the format DDMMYYYY
        return password == self.date_of_birth.strftime('%d%m%Y')


class Result(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    htno = models.CharField(max_length=50,)
    subcode = models.CharField(max_length=20)
    subname = models.CharField(max_length=100)
    internals = models.CharField(max_length=10)
    grade = models.CharField(max_length=100)
    credits = models.FloatField()
    semester = models.CharField(max_length=10, default=None, null=True)
    def __str__(self):
       return self.htno
class Staff(models.Model):
    staff_id = models.CharField(primary_key=True, max_length=100)  # Primary key for the staff
    name = models.CharField(max_length=100)  # Name of the staff member
    email = models.EmailField()  # Email address of the staff member
    phone_number = models.CharField(max_length=15)  # Phone number of the staff member
    department = models.CharField(max_length=100, null=True)  # Department of the staff member
    designation = models.CharField(max_length=100,default='')  
    # Designation of the staff member

    def __str__(self):
        return self.name
class Attendance(models.Model):
    date = models.DateField(default=timezone.now)
    roll_number = models.CharField(max_length=50)  # Assuming roll_number is used to identify students
    hour = models.CharField(max_length=10)
    present = models.BooleanField(default=False)

    def __str__(self):
        status = 'Present' if self.present else 'Absent'
        return f"{self.date} - Roll Number: {self.roll_number} - Hour: {self.hour} ({status})"