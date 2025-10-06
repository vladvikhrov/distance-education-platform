# distance Education Platform

Сайт для дистанционного обучения в учебном заведении. Присутсвует контроль домашних заданий, бд учеников. Учителя могу создавать занятия как в электронном дневники домашние задания, но более стабильно и гибко. Ученики могут смотреть дз и выполнять их. Также есть связь с преподоватлеями в удобном интерфейсе. Админисраторы имееют широкие возможности для редактирования платформы. 

Подробные планы разработки описаны в [Issues](./md/issues.md)

## Installation Instructions

1. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Apply migrations and create superuser**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

Access the app at `http://127.0.0.1:8000`.

4. Meke .env file.
   Make your SECRET_KEY for django

# Instruction
## I. Excel files settings. Classes, Subs, Users

Важной частью проекта - автоматизация. Поэтому реализована часть для загрузки сначала пользователей, а потом и классов и предметов, чтобы их не создавать вручную в django admin. 

Подробную инструкцию я оставил в [ИНСТРУКЦИЯ](./md/excel_instructions.md)