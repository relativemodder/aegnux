# Тестирование проекта

## Подготовка к тестированию

1. **Окружение:**
   ```bash
   # Создание виртуального окружения
   python -m venv .venv
   source .venv/bin/activate
   
   # Установка зависимостей
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Конфигурация:**
   ```bash
   # Копирование конфигурации
   cp config.example.ini config.ini
   
   # Настройка путей к After Effects
   # Редактируйте config.ini согласно вашей системе
   ```

## Запуск тестов

1. **Модульные тесты:**
   ```bash
   # Запуск всех тестов
   pytest
   
   # Запуск конкретного модуля
   pytest tests/test_plugins_events.py
   
   # Запуск с покрытием
   pytest --cov=src tests/
   ```

2. **Интеграционные тесты:**
   ```bash
   # Тесты интеграции с Wine
   pytest tests/integration/
   
   # Тесты плагинов
   pytest tests/plugins/
   ```

3. **UI тесты:**
   ```bash
   # Тесты интерфейса
   pytest tests/ui/
   ```

## Проверка производительности

1. **Базовые тесты:**
   ```bash
   # Запуск бенчмарков
   pytest tests/benchmarks/
   ```

2. **Профилирование:**
   ```bash
   python -m cProfile -o profile.stats src/main.py
   ```

## Подготовка к релизу

1. **Проверка стиля кода:**
   ```bash
   # Проверка PEP 8
   flake8 src/ tests/
   
   # Проверка типов
   mypy src/
   ```

2. **Сборка документации:**
   ```bash
   # Генерация документации
   sphinx-build -b html docs/source/ docs/build/
   ```

3. **Сборка пакета:**
   ```bash
   # Создание дистрибутива
   python setup.py sdist bdist_wheel
   ```

## Деплой

1. **Подготовка:**
   ```bash
   # Проверка зависимостей
   pip check
   
   # Очистка кэша и временных файлов
   python setup.py clean --all
   ```

2. **Создание релиза:**
   ```bash
   # Создание тегов
   git tag -a v0.1.0-alpha -m "Alpha release 0.1.0"
   git push origin v0.1.0-alpha
   ```

3. **Публикация:**
   ```bash
   # Загрузка на PyPI (если требуется)
   python -m twine upload dist/*
   ```

## Чеклист проверки

- [ ] Все тесты проходят успешно
- [ ] Покрытие кода тестами > 80%
- [ ] Документация актуальна
- [ ] README обновлен
- [ ] Зависимости проверены
- [ ] Версия обновлена
- [ ] Changelog создан/обновлен
- [ ] Legal notice актуально

## Известные проблемы

1. Производительность:
   - [ ] Проверить утечки памяти
   - [ ] Оптимизировать работу с большими проектами
   - [ ] Улучшить время загрузки

2. Совместимость:
   - [ ] Тестирование с различными версиями AE
   - [ ] Проверка работы популярных плагинов
   - [ ] Тестирование на разных дистрибутивах

3. Интерфейс:
   - [ ] Проверка локализации
   - [ ] Тестирование отзывчивости UI
   - [ ] Проверка работы горячих клавиш

## Автоматизация тестирования

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest --cov=src tests/
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Мониторинг после деплоя

1. **Логирование:**
   ```python
   # Настройка логирования
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('aegnux.log'),
           logging.StreamHandler()
       ]
   )
   ```

2. **Отслеживание ошибок:**
   ```python
   # Настройка обработчика исключений
   def error_handler(exctype, value, traceback):
       logging.error(
           f"Uncaught exception",
           exc_info=(exctype, value, traceback)
       )
   
   sys.excepthook = error_handler
   ```

3. **Телеметрия:**
   - Отслеживание использования функций
   - Мониторинг производительности
   - Сбор статистики использования

## Обновление системы

1. **Проверка обновлений:**
   ```python
   def check_updates():
       """Проверка наличия обновлений"""
       try:
           response = requests.get(UPDATE_URL)
           latest_version = response.json()["version"]
           return latest_version > current_version
       except Exception as e:
           logging.error(f"Ошибка проверки обновлений: {e}")
           return False
   ```

2. **Автоматическое обновление:**
   ```python
   def update_system():
       """Обновление системы"""
       try:
           # Резервное копирование
           backup_config()
           
           # Загрузка обновлений
           download_updates()
           
           # Применение обновлений
           apply_updates()
           
           # Проверка после обновления
           verify_update()
           
       except Exception as e:
           logging.error(f"Ошибка обновления: {e}")
           rollback_update()
   ```

## Поддержка пользователей

1. **Документация:**
   - Руководство пользователя
   - FAQ
   - Известные проблемы и решения

2. **Каналы поддержки:**
   - GitHub Issues
   - Электронная почта
   - Форум поддержки