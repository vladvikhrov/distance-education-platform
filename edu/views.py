from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
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
def students(request):
    if request.user.role == 'S':
        return render(request, "main_html/for_students.html")
    else:
        return HttpResponseForbidden()

def list_homework_view(request):
    if request.user.role != 'T':
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
    else:
        return HttpResponseForbidden()
# Teacher
def teachers(request):
    if request.user.role == 'T':
        return render(request, "main_html/for_teachers.html")
    else:
        return HttpResponseForbidden()

def redaction(request):
    if request.user.role != "S":
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
    else:
        return HttpResponseForbidden()

# Admin
def admin_panel(request):
    if request.user.role == 'A':
        return render(request, "main_html/for_admin.html")
    else:
        return HttpResponseForbidden()


    