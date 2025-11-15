from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import markdown
from config import settings
from edu_tools.decorators import role_required
from .models import Lessons
from edu.forms import LessonForm
# в дальнейшем использовать LoginRequiredMixin

# urls for main_html dir
def home(request):
    readme_path = settings.BASE_DIR / 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    html_content = markdown.markdown(
        md_text, 
        extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'sane_lists',
            'codehilite',
        ]
    )
    
    return render(request, 'main_html/add_base.html', {'readme_html': html_content})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lessons, pk=lesson_id)
    subjects = lesson.subjects.all()
    if lesson.document:
        initial_document = {'document': lesson.document}
    else: 
        initial_document = None
    form = None
    if request.user.role != 'S':
        if request.method == "POST":
            form = LessonForm(request.POST, request.FILES, instance=lesson)
            if form.is_valid():
                if form.cleaned_data.get('remove_file'):
                    lesson.document.delete(save=False)
                    lesson.document = None
                form.save()
                
                if 'document' in request.FILES:
                    lesson.document = request.FILES['document']
                    lesson.save()
                messages.success(request, 'Изменения сохранены')
                return redirect('detail_lesson', lesson_id=lesson.id)
            else:
                messages.error(request, 'Ошибка при сохранении. Проверьте данные.')
        else:
            form = LessonForm(instance=lesson, initial=initial_document)
    return render(request, 'detail_lesson.html', {'lesson': lesson, 'form': form, 'subjects': subjects})
    
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