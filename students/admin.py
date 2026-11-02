from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'course', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'email')