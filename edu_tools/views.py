from django.shortcuts import redirect, render
from django.contrib import messages

from edu.models import Classes, Subjects
from edu_tools.decorators import role_required
from users.models import User
from .forms import LessonsForm

from .tasks import add_schoolers_task, load_classes_subjects_task


@role_required(['A'])
def add_schoolers(request):
    if request.method == 'POST':
        if 'excel_file' not in request.FILES:
            messages.error(request, '❌ Файл не был загружен.')
            return redirect('school_structure')
        
        excel_file = request.FILES['excel_file']
        role = request.POST.get('Role')
        

        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(
                request,
                '❌ Неверный формат файла. Используйте .xlsx или .xls'
            )
            return redirect('school_structure')
        
        try:
            file_content = excel_file.read()
            
            task = add_schoolers_task.delay(
                file_content=file_content,
                role=role,
                file_name=excel_file.name
            )
            
            messages.info(
                request,
                f'📤 Файл "{excel_file.name}" отправлен на обработку. '
                f'Задача ID: {task.id[:8]}... '
                f'Результаты появятся через несколько минут.'
            )
            
            request.session['last_upload_task'] = task.id
            
        except Exception as e:
            messages.error(
                request,
                f'❌ Ошибка при запуске обработки: {str(e)}'
            )
        
        return redirect('school_structure')
    return redirect('school_structure')


@role_required(['A', 'T'])
def edu_program(request):
    if request.method == 'POST':
        form = LessonsForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            lesson = form.save()
            
            subject = form.cleaned_data['subject']
            subject.lesson_id.add(lesson)
            
            messages.success(
                request,
                f'✅ Урок "{lesson.topic}" успешно создан'
            )
            return redirect('redaction_teachers')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = LessonsForm(user=request.user)
    
    return render(request, 'tools/edu_program.html', {'form': form})


@role_required(['A'])
def class_change(request):
    students = User.objects.filter(role='S')
    classes = Classes.objects.all()
    
    if request.method == 'POST':
        selected_students = request.POST.getlist('selected_students')
        class_name = int(request.POST.get('class_filter'))
        
        for selection in selected_students:
            User.objects.filter(pk=int(selection)).update(
                classes_id=class_name
            )
        
        messages.success(
            request,
            f'✅ {len(selected_students)} учеников переведено в новый класс'
        )
    
    return render(request, 'tools/class_change.html', {
        'students': students,
        'classes': classes
    })


@role_required(['A'])
def load_classes_subjects(request):
    if request.method == "POST":
        if 'excel_file' not in request.FILES:
            messages.error(request, '❌ Файл не был загружен.')
            return redirect('school_structure')
        
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(
                request,
                '❌ Неверный формат файла. Используйте .xlsx или .xls'
            )
            return redirect('school_structure')
        
        try:
            file_content = excel_file.read()
            
            task = load_classes_subjects_task.delay(
                file_content=file_content,
                file_name=excel_file.name
            )
            
            messages.info(
                request,
                f'📤 Файл "{excel_file.name}" отправлен на обработку. '
                f'Задача ID: {task.id[:8]}... '
                f'Обновите страницу через минуту для просмотра результатов.'
            )
            
            request.session['last_structure_task'] = task.id
            
        except Exception as e:
            messages.error(
                request,
                f'❌ Ошибка при запуске обработки: {str(e)}'
            )
        
        return redirect('school_structure')
    
    return redirect('school_structure')


@role_required(['A'])
def school_structure(request):
    total_classes = Classes.objects.count()
    total_subjects = Subjects.objects.count()
    total_students = User.objects.filter(role='S').count()
    
    classes = Classes.objects.prefetch_related('sub_id').order_by(
        'number', 'letter'
    )
    
    classes_stats = []
    for class_obj in classes:
        subjects_list = [subj.name for subj in class_obj.sub_id.all()]
        students_count = User.objects.filter(
            classes_id=class_obj,
            role='S'
        ).count()
        
        classes_stats.append({
            'name': str(class_obj),
            'subjects_count': class_obj.sub_id.count(),
            'students_count': students_count,
            'subjects': subjects_list
        })

    context = {
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'total_students': total_students,
        'classes_stats': classes_stats,
    }
    
    return render(request, 'tools/school_structure.html', context)