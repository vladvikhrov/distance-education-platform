from celery import shared_task
import pandas as pd
from io import BytesIO

from edu.models import Classes, Subjects
from users.models import User


@shared_task(bind=True)
def add_schoolers_task(self, file_content, role, file_name='upload.xlsx'):    

    result = {
        'success_count': 0,
        'error_count': 0,
        'errors': []
    }
    
    try:
        df = pd.read_excel(BytesIO(file_content))
        
        total_rows = len(df)
        
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': total_rows,
                'status': f'Начинаю обработку {total_rows} записей...'
            }
        )
        
    except Exception as e:
        result['errors'].append(f'Ошибка чтения файла: {str(e)}')
        return result
    

    for index, row in df.iterrows():
        try:
            username = row.get('Логин')
            name = row.get('Имя')
            surname = row.get('Фамилия')
            password = row.get('Пароль')
            patronymic = row.get('Отчество', '')
            
            if not isinstance(patronymic, str):
                patronymic = ''
            
            if None in [username, name, surname, password]:
                result['errors'].append(
                    f'Строка {index + 2}: отсутствуют обязательные поля'
                )
                result['error_count'] += 1
                continue
            
            # Если роль ученик
            class_obj = None
            if role == "S":  
                class_name = row.get('Класс')
                
                if not pd.isna(class_name):
                    class_name = str(class_name).strip()
                    
                    if len(class_name) >= 2:
                        number = class_name[:-1]  
                        letter = class_name[-1]   
                        
                        try:
                            class_obj = Classes.objects.get(
                                number=number,
                                letter=letter
                            )
                        except Classes.DoesNotExist:
                            result['errors'].append(
                                f'Строка {index + 2}: класс "{class_name}" не найден. '
                                f'Пользователь создан без класса.'
                            )
            
            user = User.objects.create_user(
                login=username,
                password=password,
                first_name=name,
                last_name=surname,
                patronymic=patronymic,
                role=role,
            )
            
            if class_obj:
                user.classes_id = class_obj
                user.save()
            
            result['success_count'] += 1
            
            # Может изменить?
            if (index + 1) % 10 == 0:
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': index + 1,
                        'total': total_rows,
                        'status': f'Обработано {index + 1} из {total_rows}'
                    }
                )
        
        except Exception as e:
            result['errors'].append(
                f'Строка {index + 2}: {str(e)}'
            )
            result['error_count'] += 1
    
    return result


@shared_task(bind=True)
def load_classes_subjects_task(self, file_content, file_name='upload.xlsx'):

    result = {
        'success_classes': 0,
        'success_subjects': 0,
        'errors': []
    }
    
    try:
        xls = pd.ExcelFile(BytesIO(file_content))
        
        total_sheets = len(xls.sheet_names)
        
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': total_sheets,
                'status': 'Начинаю обработку классов...'
            }
        )
        
    except Exception as e:
        result['errors'].append(f'Ошибка чтения файла: {str(e)}')
        return result
    
    for sheet_index, sheet_name in enumerate(xls.sheet_names):
        try:
            class_name = sheet_name.strip()
            
            if len(class_name) < 2:
                result['errors'].append(
                    f'Некорректное название класса: {class_name}'
                )
                continue
            
            number = class_name[:-1]
            letter = class_name[-1]
            
            if not letter.isupper():
                result['errors'].append(
                    f'Класс {class_name}: буква должна быть заглавной!'
                )
                continue
            
            class_obj, created = Classes.objects.get_or_create(
                number=number,
                letter=letter,
            )
            
            if created:
                result['success_classes'] += 1
            
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            for column in df.columns:
                subject_name = str(column).strip()
                
                if subject_name and subject_name != 'nan':
                    full_subject_name = f"{subject_name} {class_name}"
                    
                    subject_obj, created = Subjects.objects.get_or_create(
                        name=full_subject_name
                    )
                    
                    if created:
                        result['success_subjects'] += 1
                    
                    if subject_obj not in class_obj.sub_id.all():
                        class_obj.sub_id.add(subject_obj)
            
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': sheet_index + 1,
                    'total': total_sheets,
                    'status': f'Обработан класс {class_name}'
                }
            )
        
        except Exception as e:
            result['errors'].append(
                f'Ошибка обработки листа {sheet_name}: {str(e)}'
            )
    
    return result