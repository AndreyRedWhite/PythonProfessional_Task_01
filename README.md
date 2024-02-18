
# 1-ое задание из курса PythonProfessional от Otus

### Анализатор логов

Это первое задание из курса PythonProfessional в Otus.

## Описание

Анализатор логов - это скрипт на Python, предназначенный для анализа лог-файлов Nginx и генерации отчетов на основе данных, извлеченных из логов.

## Возможности

- Парсит лог-файлы Nginx для извлечения актуальных данных.
- Рассчитывает различную статистику, такую как количество запросов, общее время, среднее время, максимальное время и медианное время для каждого URL.
- Генерирует HTML-отчеты на основе проанализированных лог-данных.
- Поддерживает настройку с помощью файла JSON.
- Обрабатывает ошибки вежливо и записывает их для удобной отладки.

## Установка

Клонируйте репозиторий:

```bash 
git clone https://github.com/AndreyRedWhite/PythonProfessional_Task_01.git
```
## Требования
Python >=3.9

## Использование
- Измените файл config.json, чтобы при необходимости настроить поведение скрипта.
- Запустите скрипт log_analyzer.py:
 ```python log_analyzer.py```
- Проверьте сгенерированные отчеты в каталоге reports.

## Конфигурация
Вы можете настроить скрипт, используя файл config.json. Доступные параметры конфигурации включают:

- REPORT_SIZE: Количество URL-адресов для включения в отчет.
- reports: Каталог, в котором будут сохранены отчеты.
- log: Каталог с лог-файлами Nginx.
- logging: Путь к файлу журнала для регистрации выполнения скрипта.
