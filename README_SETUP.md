Пошаговая инструкция — быстро развернуть проект и получить тот же сайт, что у автора

Windows (рекомендуемый сценарий)

1. Клонируйте репозиторий:

   git clone https://github.com/DmitryPrivalov/Project_4kurs.git
   cd Project_4kurs

2. Создайте виртуальное окружение и установите зависимости:

   python -m venv .venv
   .\.venv\Scripts\python -m pip install --upgrade pip
   .\.venv\Scripts\pip install -r requirements.txt

3. Подготовьте базу и заполните данными (скрипт idempotent):

   .\.venv\Scripts\python setup_everything.py
   .\.venv\Scripts\python scripts\auto_populate.py

4. Запустите приложение локально:

   .\.venv\Scripts\python app.py

Unix / macOS

1. Клонируйте репозиторий и перейдите в папку проекта

   git clone https://github.com/DmitryPrivalov/Project_4kurs.git
   cd Project_4kurs

2. Создайте виртуальное окружение и установите зависимости:

   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt

3. Подготовьте базу и заполните данными:

   python setup_everything.py
   python scripts/auto_populate.py

4. Запустите приложение:

   python app.py

Примечания и советы
- Скрипты `setup_everything.py` и `scripts/auto_populate.py` сделаны так, чтобы их можно было запускать повторно — они дополняют БД, не стирая существующие данные.
- Скрипты изменяют `data.db`. Если база важна, сделайте резервную копию перед запуском.
- Если хотите автоматизировать запуск (например, CI), используйте `run_setup.sh` или `run_setup.bat` (в корне репозитория).
