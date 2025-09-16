from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from edu_tools.decorators import role_required
from .models import Lessons
from edu.forms import LessonForm
from django.contrib import messages
# в дальнейшем использовать LoginRequiredMixin

# urls for main_html dir
def home(request):
    return render(request, "main_html/add_base.html")

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lessons, pk=lesson_id)
    if lesson.document:
        initial_document = {'document': lesson.document}
    else: 
        initial_document = None
    form = None
    if request.user.role != 'S':
        if request.method == "POST":
            form = LessonForm(request.POST, request.FILES, instance=lesson)
            if form.is_valid():
                form.save()
                
                if 'document' in request.FILES:
                    lesson.document = request.FILES['document']
                    lesson.save()
                messages.success(request, 'Изменения сохранены')
        else:
            form = LessonForm(instance=lesson, initial=initial_document)
    return render(request, 'detail_lesson.html', {'lesson': lesson, 'form': form})
    
# Student
@role_required(['S'])
def students(request):
    return render(request, "main_html/for_students.html")

@role_required(['S', 'A'])
def list_homework_view(request):
    subjects = request.user.classes_id.sub_id.all()
    sub_name = request.GET.get('sub_name') or None
    if sub_name != None:
        lessons = subjects.get(name=sub_name).lesson_id.all()
    context = {
        'lessons': None if sub_name==None else lessons,
        'subjects': subjects,
        'active_sub': sub_name,
        }
    return render(request, "student/list_homework.html", context=context)

# Teacher
@role_required(['T'])
def teachers(request):
    return render(request, "main_html/for_teachers.html")

@role_required(['T', 'A'])
def redaction(request):
    subjects = request.user.subjects_id.all()
    sub_name = request.GET.get('sub_name') or None
    if sub_name != None:
        lessons = subjects.get(name=sub_name).lesson_id.all()
        pass

    context = {
        'lessons': None if sub_name==None else lessons,
        'subjects': subjects,
        'active_sub': sub_name,
        }
    return render(request, "teacher/redaction.html", context=context)

# Admin
@role_required(['A'])
def admin_panel(request):
    return render(request, "main_html/for_admin.html")