from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [  
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('students/', views.students, name='students'),
    path('logout/', views.custom_logout, name='logout'),
    path('delete_student/<str:roll_no>/', views.delete_student, name='delete_student'),
    path('students/<int:student_id>/', views.student_details, name='student_details'),
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('display_results/', views.display_results, name='display_results'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('attendance_form/', views.attendance_form, name='attendance_form'),
    path('display_students/<str:branch>/<str:section>/<int:year>/<str:day>/<int:hour>/', views.display_students, name='display_students'),
    path('submit_attendance/', views.submit_attendance, name='submit_attendance'),
    path('view_attendance/<str:selected_date>/', views.view_attendance, name='view_attendance'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
