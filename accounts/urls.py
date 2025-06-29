from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('new/', views.new_homepage, name='new_homepage'),
    path('switch-language/', views.switch_language, name='switch_language'),
    path('login/', views.login, name='login'),
    path('login-page/', views.login_page, name='login_page'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('teachers/', views.get_teachers, name='get_teachers'),
    path('manager/', views.manager_page, name='manager_page'),
    path('admin/', views.admin_page, name='admin_page'),
    path('teacher/<int:teacher_id>/', views.teacher_page, name='teacher_page'),
    path('student/<int:student_id>/', views.student_page, name='student_page'),
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('toggle-student-permission/<int:teacher_id>/', views.toggle_student_permission, name='toggle_student_permission'),
    path('logout/', views.logout_view, name='logout'),
    # Chatbot URLs
    path('chatbot/<int:student_id>/', views.chatbot_page, name='chatbot_page'),
    path('chatbot/<int:student_id>/send/', views.send_message, name='send_message'),
    path('chatbot/<int:student_id>/history/', views.get_chat_history, name='get_chat_history'),
]