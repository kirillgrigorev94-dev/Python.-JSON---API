# Сервис парсинга JSON с GUI и API


Приложение на Python для работы с данными из JSON‑файла через графический интерфейс (Tkinter) и RESTful API (Flask). Поддерживает операции CRUD.

## Функционал

* **GUI‑интерфейс** на `tkinter`:
  * отображение данных в виде таблицы (`Treeview`);
  * форма для добавления/редактирования элементов;
  * кнопки для CRUD‑операций;
  * загрузка произвольного JSON‑файла;
  * обработка ошибок и валидация данных.
* **RESTful API** на Flask:
  * эндпоинты `/items` (GET, POST) и `/items/<id>` (GET, PUT, DELETE);
  * сохранение данных в `data.json`;
  * возврат корректных HTTP‑кодов.

## Структура проекта

json_parser_app/
│
├── main.py # GUI‑приложение (Tkinter)
├── api_service.py # Flask API
├── data.json # Файл с данными
└── README.md # Документация

## Запуск

```bash
pip install flask

    Запуск API-сервера

python api_service.py

    Запуск GUI‑приложения

python main.py

