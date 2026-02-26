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
   OR simply run the orchestrator which will restore prebuilt DB if available:
   .\.venv\Scripts\python scripts\full_setup.py

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
   OR simply run the orchestrator which will restore prebuilt DB if available:
   python scripts/full_setup.py

4. Запустите приложение:

   python app.py

Примечания и советы
- Скрипты `setup_everything.py` и `scripts/auto_populate.py` сделаны так, чтобы их можно было запускать повторно — они дополняют БД, не стирая существующие данные.
- Скрипты изменяют `data.db`. Если база важна, сделайте резервную копию перед запуском.
- Если хотите автоматизировать запуск (например, CI), используйте `run_setup.sh` или `run_setup.bat` (в корне репозитория).

CI / GitHub integration
-----------------------
Мы добавили GitHub Actions workflow `.github/workflows/ci.yml`, который при пуше на ветки `main`/`master` выполнит полную сборку:

- установит зависимости из `requirements.txt`
- запустит `scripts/full_setup.py` или `setup_everything.py` для подготовки `data.db` и обучения движка
- вызовет `scripts/export_prebuilt.py` (если он есть) и поместит результаты в папку `prebuilt`
- загрузит содержимое `prebuilt` как артефакт workflow

Как использовать:

1. Закоммитьте и запушьте изменения в репозиторий:

```bash
git add .github/workflows/ci.yml
git add README_SETUP.md
git commit -m "Add CI workflow: build DB and export prebuilt artifacts"
git push origin main
```

2. Перейдите в Actions в GitHub — workflow запустится автоматически; после завершения вы сможете скачать `prebuilt` артефакт из страницы выполнения.

3. Если хотите, workflow можно расширить (например, автоматически коммитить `prebuilt/engine.joblib`), но это потребует настройки GitHub token и аккуратной настройки прав — могу помочь настроить это, если нужно.

Автоматическое обновление `prebuilt` в репозитории
-------------------------------------------------
Workflow теперь может автоматически закоммитить и запушить папку `prebuilt` обратно в ту же ветку. Для этого:

- В настройках репозитория (Settings → Actions → General) убедитесь, что `Allow GitHub Actions to create and approve pull requests` включено (обычно по умолчанию).
- По умолчанию используется встроенный `GITHUB_TOKEN`, у которого есть права записи — в workflow это установлено через `permissions: contents: write`.
- Чтобы избежать бесконечного цикла запусков, workflow добавляет коммит только если инициатором запуска был не `github-actions[bot]`. То есть первый пуш от вас вызовет сборку и коммит `prebuilt`; этот коммит также запустит workflow, но шаг коммита пропустится.

После того как вы запушите ветку `main`/`master`, workflow выполнит сборку и автоматически обновит `prebuilt` в репозитории (если артефакты изменились). Я не могу сам запушить в ваш репозиторий — пожалуйста, сделайте push, и напишите мне, когда он появится в GitHub, чтобы я проверил выполнение Actions и артефакты.
