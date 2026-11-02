from django.shortcuts import render, redirect
from .forms import StudentForm
from .models import Student
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import permission_required
import csv
from django.http import HttpResponse


@login_required
def home(request):
    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()
    total_courses = Student.objects.values('course').distinct().count()

    context = {
    'total_students': total_students,
    'active_students': active_students,
    'total_courses': total_courses,
}
    

    return render(request, "home.html", context)

@login_required
@permission_required('students.add_student')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form})

@login_required
@permission_required('students.view_student')
def view_students(request):
    query = request.GET.get('search')
    status = request.GET.get('status')

    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(course__icontains=query)
        )

    if status == 'active':
        students = students.filter(is_active=True)

    elif status == 'inactive':
        students = students.filter(is_active=False)

    paginator = Paginator(students, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_students.html', {
        'students': page_obj,
        'page_obj': page_obj,
        'query': query,
        'status': status
    })
@login_required
@permission_required('students.change_student')
def edit_student(request, id):
    student = Student.objects.get(id=id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            return redirect('view_students')

    else:
        form = StudentForm(instance=student)

    return render(request, 'edit_student.html', {
        'form': form,
        'student': student
    })
@login_required
@permission_required('students.delete_student')
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.delete()
        return redirect('view_students')

    return render(request, 'delete_student.html', {'student': student})
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {
        'form': form
    })
@login_required
def profile(request):
    return render(request, 'profile.html')
@login_required
@permission_required('students.view_student')
def export_students(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)

    writer.writerow(['Name', 'Email', 'Phone', 'Course', 'Status'])

    students = Student.objects.all()

    for student in students:
        status = 'Active' if student.is_active else 'Inactive'

        writer.writerow([
            student.name,
            student.email,
            student.phone,
            student.course,
            status
        ])

    return response