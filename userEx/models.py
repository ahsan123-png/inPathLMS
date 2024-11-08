from django.db import models
from django.contrib.auth.models import User
from time import timezone
# Create your models here.
#========= Model for User Roles =============
class UserRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
#================ Model for Instructor Profile ===================
class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)  # Short biography
    degrees = models.TextField(null=True, blank=True)  # e.g., "PhD in Education"
    teaching_experience = models.IntegerField(default=0)  # Number of years
    specialization  = models.TextField(null=True, blank=True)  # e.g., "Mathematics, Physics"
    teaching_history = models.TextField(null=True, blank=True)  # e.g., "Taught at XYZ University"
    profile_picture = models.ImageField(upload_to='instructor_profiles/', null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

#=============== Category =========================
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
#=============== SubCategory =========================
class SubCategory(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

#========== Model for Courses =================
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'userrole__role': 'instructor'})
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    subcategory = models.ForeignKey('SubCategory', on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    discount_end_date = models.DateTimeField(null=True, blank=True)  # Optional discount expiry date
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_discounted_price(self):
        if self.discount_percentage and self.discount_end_date and self.discount_end_date > timezone.now():
            return self.price * (1 - (self.discount_percentage / 100))
        return self.price

#================ Model for Enrollments ================
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'userrole__role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)  # Percentage

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

#============== Model for Payments =================
class Payment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20)  # e.g., 'completed', 'pending'

    def __str__(self):
        return f"Payment of {self.amount} for {self.enrollment.course.title}"
#=========== Model for Quizzes =======================
class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    total_marks = models.IntegerField(default=0)
    time_limit = models.IntegerField(default=60)  # in minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
#=============== Model for Questions ====================
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20)  # e.g., 'multiple_choice', 'true_false', 'short_answer'
    correct_answer = models.TextField()

    def __str__(self):
        return self.question_text
# ============== Model for Student Responses ==================
class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'userrole__role': 'student'})
    selected_answer = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s response to {self.question}"
#======== Model for Assignments =================
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#========= Model for Assignment Submissions ===============
class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'userrole__role': 'student'})
    submission_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s submission for {self.assignment.title}"

#========= Model for Feedback ===============
class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Rating from 1 to 5
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.course.title}"
#========== notifications ===============
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('enrollment', 'Course Enrollment'),
        ('approval', 'Course Approval'),
        ('feedback', 'Feedback'),
        ('course_update', 'Course Update'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who receives the notification
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()  # The notification message
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.notification_type}"
# ============= Model for Course Updates ==================
class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)  # e.g., "Introduction"
    order = models.PositiveIntegerField()  # For ordering sections in the course

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Lecture(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField() 
    video_file = models.FileField(upload_to='lectures/videos/', null=True, blank=True) 

    def __str__(self):
        return f"{self.title} ({self.section.title})"
