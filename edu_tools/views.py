from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Count, Q

import pandas as pd

from edu.models import Classes, Lessons, Subjects
from edu_tools.decorators import role_required
from users.models import User
from edu.models import Classes, Lessons, Subjects
from .forms import LessonsForm


# код для добавление учеников или учителей
@role_required(['A'])
def add_schoolers(request):
    if request.method == 'POST':
        try:
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
        except:
            messages.error(request, 'Файл не был заугружен.')
            messages.warning(request, 'Проверьте формат или наличие подгрузки.')
            return redirect('add_schoolers')
        
        role = request.POST.get('Role')
        
        
        for index, row in df.iterrows():
            username = row.get('Логин')
            name = row.get('Имя')
            surname = row.get('Фамилия')
            password = row.get('Пароль')
            patronymic = row.get('Отчество')

            if not isinstance(patronymic, str):
                patronymic = ''

            if None in [username, name, surname, password, patronymic]:
                messages.error(request, 'Файл имеет не верный формат.')
                return redirect('add_schoolers')
            
            if username and password and name and surname:  
                User.objects.create_user(login=username, password=password, first_name=name, last_name=surname, patronymic=patronymic, role=role)
        
        return redirect('school_structure')
    messages.success(request, '✅ Загрузка завершина, все ок.')
    return redirect('school_structure')  

# Добавление уроков
@role_required(['A', 'T'])
def edu_program(request):
    if request.method == 'POST':
        form = LessonsForm(request.POST, request.FILES, user = request.user)
        if form.is_valid():

            lesson = Lessons.objects.create(
                topic = request.POST.get('topic'),
                additionals = request.POST.get('additionals'),
                home_work = request.POST.get('home_work'),
                data = request.POST.get('data'),
                email = request.POST.get('email'),
                document = request.FILES['document'],
            )
            
            subject = Subjects.objects.get(id=request.POST.get('class_field'))
            subject.lesson_id.add(lesson)
            subject.save()
            messages.success(request, 'Запись успешно создана')
        
        return redirect('redaction_teachers')
    else:
        form = LessonsForm(user = request.user)
    return render(request, 'tools/edu_program.html', {'form': form})

# измениение классов по классам
@role_required(['A'])
def class_change(request):
    students = User.objects.filter(role='S')
    classes = Classes.objects.all()
    if request.method == 'POST':
        selected_students = request.POST.getlist('selected_students')
        class_name= int(request.POST.get('class_filter'))
        print(class_name)
        for selection in selected_students: 
                User.objects.filter(pk=int(selection)).update(classes_id=class_name)
    return render(request, 'tools/class_change.html', {'students': students, 'classes': classes})

# автодобавлени классов и предмету
@role_required(['A'])
def load_classes_subjects(request):
    if  request.method == "POST":
        try: 
            xls = pd.ExcelFile(request.FILES['excel_file'])
        except Exception as e: 
            messages.error(request, 'Ошибка при чтении файла.')
            messages.warning(request, f'Ошибка: {e}')
            return redirect('school_stucture')
        
        success_classes = 0
        success_subjects = 0

        for sheet_name in xls.sheet_names:
            # Название листа = класс (например "9В", "11А")
            class_name = sheet_name.strip()

            if len(class_name) < 2:
                messages.warning(request, f'Некоректное название класса {class_name}')
        
            number = class_name[:-1]
            letter = class_name[-1]

            if not letter.isupper():
                messages.warning(request, f'Класс {class_name}: буква должна быть заглавной!')
                continue

            class_obj, created = Classes.objects.get_or_create(
                number=number, 
                letter=letter,
            )
        
            if created:
                success_classes += 1

            df = pd.read_excel(xls, sheet_name=sheet_name)

            for column in df.columns:
                subject_name = str(column).strip()

                if subject_name and subject_name != 'nan':

                    full_subject_name = f"{subject_name} {class_name}"
                    subject_obj, created = Subjects.objects.get_or_create(
                        name = full_subject_name
                    )
                    if created:
                        success_subjects += 1
                    
                    if subject_obj not in class_obj.sub_id.all():
                        class_obj.sub_id.add(subject_obj)

        if success_classes > 0 or success_subjects > 0:
            messages.success(request, f'Успешно загружено: {success_classes} классов, {success_subjects} новых предметов')
        else:
            messages.info(request, 'Новые данные не добавлены. Возможно, они уже существуют.')
        
        return redirect('school_structure')
    
    messages.success(request, '✅ Загрузка завершина, все ок.')
    return redirect('school_structure')

def school_structure(request):
    total_classes = Classes.objects.count()
    total_subjects = Subjects.objects.count()
    total_students = User.objects.filter(role='S').count()
    classes = Classes.objects.prefetch_related('sub_id').order_by('number', 'letter')
    
    classes_stats = []
    for class_obj in classes:
        subjects_list = [subj.name for subj in class_obj.sub_id.all()]
        students_count = User.objects.filter(classes_id=class_obj, role='S').count()
        
        classes_stats.append({
            'name': str(class_obj),                    # "9А"
            'subjects_count': class_obj.sub_id.count(), # Количество предметов
            'students_count': students_count,           # Количество учеников
            'subjects': subjects_list                   # ['Математика 9А', 'Русский 9А', ...]
        })

    context = {
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'total_students': total_students,
        'classes_stats': classes_stats,
    }
    
    return render(request, 'tools/school_structure.html', context)