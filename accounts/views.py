from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
from .models import User, BillItem, StudentFeedback, ChatMessage
from django.db import IntegrityError
from django.contrib.auth import logout as django_logout
from django.utils import translation
from django.utils.translation import gettext as _
from .chatbot_service import ChatbotService

# Ensure admin and manager exist
ADMIN_CREDENTIALS = {'username': 'admin', 'password': '12345', 'role': 'admin', 'name': 'Admin', 'email': ''}
MANAGER_CREDENTIALS = {'username': 'manager', 'password': '12345', 'role': 'manager', 'name': 'Manager', 'email': ''}

def ensure_admin_manager():
    for creds in [ADMIN_CREDENTIALS, MANAGER_CREDENTIALS]:
        User.objects.get_or_create(
            username=creds['username'],
            defaults={
                'password': creds['password'],
                'role': creds['role'],
                'name': creds['name'],
                'email': creds['email']
            }
        )

def switch_language(request):
    """Switch language and redirect back to homepage"""
    language = request.GET.get('lang', 'en')
    if language in ['en', 'ta', 'hi']:
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
    return redirect('homepage')

def homepage(request):
    """Serve the main homepage with integrated login and language support"""
    ensure_admin_manager()
    
    # Get current language
    current_language = translation.get_language()
    
    return render(request, 'accounts/homepage.html', {
        'current_language': current_language
    })

def new_homepage(request):
    """Serve the new homepage with integrated login and language support"""
    ensure_admin_manager()
    
    # Get current language
    current_language = translation.get_language()
    
    return render(request, 'accounts/new_homepage.html', {
        'current_language': current_language
    })

def login_page(request):
    ensure_admin_manager()
    current_language = translation.get_language()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username, password=password)
            if user.role == 'admin':
                return redirect('admin_page')
            elif user.role == 'manager':
                return redirect('manager_page')
            elif user.role == 'teacher':
                return redirect('teacher_page', teacher_id=user.id)
            elif user.role == 'student':
                return redirect('student_page', student_id=user.id)
        except User.DoesNotExist:
            pass
        error = _('Invalid credentials')
    else:
        error = None
    return render(request, 'accounts/login.html', {
        'error': error,
        'current_language': current_language
    })

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    ensure_admin_manager()
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    try:
        user = User.objects.get(username=username, password=password)
        return JsonResponse({
            'success': True,
            'role': user.role,
            'user_id': user.id,
            'name': user.name,
            'message': f'{user.role.capitalize()} login successful'
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)

@csrf_exempt
@require_http_methods(["POST"])
def add_teacher(request):
    ensure_admin_manager()
    data = json.loads(request.body)
    try:
        teacher = User.objects.create(
            username=data['username'],
            password=data['password'],
            name=data['name'],
            email=data.get('email', ''),
            area=data.get('area', ''),
            location=data.get('location', ''),
            role='teacher'
        )
        return JsonResponse({'success': True, 'message': 'Teacher added successfully', 'teacher_id': teacher.id})
    except IntegrityError:
        return JsonResponse({'success': False, 'message': 'Username already exists'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_http_methods(["GET"])
def get_teachers(request):
    ensure_admin_manager()
    teachers = User.objects.filter(role='teacher')
    teacher_list = []
    for teacher in teachers:
        teacher_list.append({
            'id': teacher.id,
            'username': teacher.username,
            'password': teacher.password,
            'name': teacher.name,
            'email': teacher.email,
            'area': teacher.area,
            'location': teacher.location
        })
    return JsonResponse({'success': True, 'teachers': teacher_list})

def manager_page(request):
    ensure_admin_manager()
    message = error = None
    teachers = User.objects.filter(role='teacher')
    bill_items = BillItem.objects.all().order_by('-submitted_at')
    
    if request.method == 'POST':
        # Check if this is a bill item submission
        if 'item_name' in request.POST and 'price' in request.POST:
            # Handle bill item submission
            item_name = request.POST.get('item_name')
            price = request.POST.get('price')
            
            if not all([item_name, price]):
                error = 'Item name and price are required.'
            else:
                try:
                    # Get the current manager user (assuming manager is logged in)
                    manager = User.objects.filter(role='manager').first()
                    if manager:
                        bill_item = BillItem.objects.create(
                            item_name=item_name,
                            price=price,
                            submitted_by=manager
                        )
                        message = f'Bill item "{bill_item.item_name}" added successfully!'
                        bill_items = BillItem.objects.all().order_by('-submitted_at')
                    else:
                        error = 'Manager not found.'
                except Exception as e:
                    error = f'Error saving bill item: {e}'
        else:
            # Handle teacher creation (existing code)
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            email = request.POST.get('email', '')
            area = request.POST.get('area', '')
            location = request.POST.get('location', '')
            
            if not all([username, password, name]):
                error = 'All fields are required.'
            else:
                try:
                    if User.objects.filter(username=username).exists():
                        error = 'Username already exists.'
                    else:
                        teacher = User.objects.create(
                            username=username, 
                            password=password, 
                            name=name, 
                            email=email, 
                            area=area,
                            location=location,
                            role='teacher'
                        )
                        message = f'Teacher {teacher.name} added successfully! Username: {teacher.username}, Password: {teacher.password}'
                        teachers = User.objects.filter(role='teacher')
                except Exception as e:
                    error = f'Error saving teacher: {e}'
    
    return render(request, 'accounts/manager.html', {
        'message': message, 
        'error': error, 
        'teachers': teachers,
        'bill_items': bill_items
    })

def delete_teacher(request, teacher_id):
    """Delete a teacher"""
    ensure_admin_manager()
    try:
        teacher = User.objects.get(id=teacher_id, role='teacher')
        teacher_name = teacher.name
        teacher.delete()
        return redirect('manager_page')
    except User.DoesNotExist:
        return redirect('manager_page')

def toggle_student_permission(request, teacher_id):
    """Toggle teacher's ability to add students"""
    ensure_admin_manager()
    try:
        teacher = User.objects.get(id=teacher_id, role='teacher')
        teacher.can_add_students = not teacher.can_add_students
        teacher.save()
        return redirect('manager_page')
    except User.DoesNotExist:
        return redirect('manager_page')

def teacher_page(request, teacher_id):
    ensure_admin_manager()
    message = error = None
    
    try:
        teacher = User.objects.get(id=teacher_id, role='teacher')
        students = User.objects.filter(role='student')
        
        if request.method == 'POST':
            # Check if this is a feedback submission
            if 'feedback_type' in request.POST:
                # Handle feedback submission
                student_id = request.POST.get('student_id')
                feedback_type = request.POST.get('feedback_type')
                description = request.POST.get('description')
                
                if not all([student_id, feedback_type, description]):
                    error = 'All feedback fields are required.'
                else:
                    try:
                        student = User.objects.get(id=student_id, role='student')
                        feedback = StudentFeedback.objects.create(
                            student=student,
                            teacher=teacher,
                            feedback_type=feedback_type,
                            rating=3,  # Default rating
                            title=f"{feedback_type.title()} Feedback",
                            description=description
                        )
                        message = f'Feedback for {student.name} added successfully!'
                    except User.DoesNotExist:
                        error = 'Student not found.'
                    except Exception as e:
                        error = f'Error saving feedback: {e}'
            else:
                # Handle student creation
                username = request.POST.get('username')
                password = request.POST.get('password')
                name = request.POST.get('name')
                email = request.POST.get('email', '')
                area = request.POST.get('area', '')
                location = request.POST.get('location', '')
                
                if not all([username, password, name]):
                    error = 'Username, password, and name are required.'
                else:
                    try:
                        if User.objects.filter(username=username).exists():
                            error = 'Username already exists.'
                        else:
                            student = User.objects.create(
                                username=username,
                                password=password,
                                name=name,
                                email=email,
                                area=area,
                                location=location,
                                role='student'
                            )
                            message = f'Student {student.name} added successfully! Username: {student.username}, Password: {student.password}'
                            students = User.objects.filter(role='student')
                    except Exception as e:
                        error = f'Error saving student: {e}'
        
        # Get feedback for each student
        student_feedback = {}
        for student in students:
            feedback_list = StudentFeedback.objects.filter(student=student, teacher=teacher).order_by('-created_at')
            student_feedback[student.id] = feedback_list
        
        return render(request, 'accounts/teacher.html', {
            'teacher': teacher,
            'students': students,
            'student_feedback': student_feedback,
            'message': message,
            'error': error
        })
    except User.DoesNotExist:
        return redirect('homepage')

def student_page(request, student_id):
    """Student dashboard showing their feedback and information"""
    ensure_admin_manager()
    
    try:
        student = User.objects.get(id=student_id, role='student')
        # Get all feedback for this student from all teachers
        feedback_list = StudentFeedback.objects.filter(student=student).order_by('-created_at')
        
        return render(request, 'accounts/student.html', {
            'student': student,
            'feedback_list': feedback_list
        })
    except User.DoesNotExist:
        return render(request, 'accounts/login.html', {'error': 'Student not found'})

def logout_view(request):
    django_logout(request)
    return redirect('/api/login-page/')

def admin_page(request):
    """Admin dashboard showing bill items and system overview"""
    ensure_admin_manager()
    bill_items = BillItem.objects.all().order_by('-submitted_at')
    teachers = User.objects.filter(role='teacher')
    students = User.objects.filter(role='student')
    
    # Calculate total amount of all bill items
    total_amount = sum(item.price for item in bill_items)
    
    return render(request, 'accounts/admin.html', {
        'bill_items': bill_items,
        'teachers': teachers,
        'students': students,
        'total_amount': total_amount
    })

# Chatbot Views
def chatbot_page(request, student_id):
    """Chatbot interface page for students"""
    ensure_admin_manager()
    
    try:
        student = User.objects.get(id=student_id, role='student')
        # Get recent chat history (last 20 messages)
        chat_history = ChatMessage.objects.filter(user=student).order_by('-timestamp')[:20]
        
        return render(request, 'accounts/chatbot.html', {
            'student': student,
            'chat_history': chat_history
        })
    except User.DoesNotExist:
        return redirect('homepage')

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, student_id):
    """Handle sending a message to the chatbot"""
    try:
        student = User.objects.get(id=student_id, role='student')
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'success': False, 'message': 'Message cannot be empty'})
        
        # Save user message
        user_chat_message = ChatMessage.objects.create(
            user=student,
            message_type='user',
            content=user_message
        )
        
        # Get chatbot service
        chatbot_service = ChatbotService()
        
        # Validate message
        if not chatbot_service.validate_message(user_message):
            bot_response = "I'm sorry, but I can only help with educational topics. Please ask me about your studies, homework, or academic questions."
        else:
            # Get conversation history for context
            conversation_history = ChatMessage.objects.filter(
                user=student
            ).order_by('timestamp')[:10]  # Last 10 messages for context
            
            # Get AI response
            bot_response = chatbot_service.get_response(user_message, conversation_history)
        
        # Save bot response
        bot_chat_message = ChatMessage.objects.create(
            user=student,
            message_type='bot',
            content=bot_response
        )
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_chat_message.id,
                'content': user_chat_message.content,
                'timestamp': user_chat_message.timestamp.isoformat()
            },
            'bot_response': {
                'id': bot_chat_message.id,
                'content': bot_chat_message.content,
                'timestamp': bot_chat_message.timestamp.isoformat()
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@require_http_methods(["GET"])
def get_chat_history(request, student_id):
    """Get chat history for a student"""
    try:
        student = User.objects.get(id=student_id, role='student')
        messages = ChatMessage.objects.filter(user=student).order_by('timestamp')
        
        chat_history = []
        for message in messages:
            chat_history.append({
                'id': message.id,
                'message_type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'chat_history': chat_history
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
