from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    area = models.CharField(max_length=100, blank=True, null=True, help_text="Assigned area for teachers")
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Location of the user")
    created_at = models.DateTimeField(auto_now_add=True)
    can_add_students = models.BooleanField(default=True, help_text="Whether teacher can add new students")

    def __str__(self):
        return f"{self.username} ({self.role})"

class BillItem(models.Model):
    item_name = models.CharField(max_length=200, help_text="Name of the item")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the item")
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_bills')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item_name} - ₹{self.price} (Submitted by {self.submitted_by.name})"

class StudentFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('academic', 'Academic Performance'),
        ('behavior', 'Behavior'),
        ('attendance', 'Attendance'),
        ('participation', 'Class Participation'),
        ('homework', 'Homework'),
        ('general', 'General'),
    ]
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_feedback')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, help_text="Brief title for the feedback")
    description = models.TextField(help_text="Detailed feedback description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback for {self.student.name} by {self.teacher.name} - {self.get_feedback_type_display()}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.user.name} - {self.get_message_type_display()} - {self.timestamp}"
