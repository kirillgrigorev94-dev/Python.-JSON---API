from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
JSON_FILE_PATH = 'data.json' # Путь к файлу данных

def load_data():
    """Загружает данные из JSON-файла. Если файл не существует возвращает пустой список."""
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    """Сохраняет данные в JSON-файл с форматированием."""
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
@app.route('/items', methods=['GET'])
def get_all_items():
    """Возвращает все элементы из JSON-файла."""
    data = load_data()
    return jsonify(data), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Возвращает элемент с указанным ID или ошибку 404, если не найден."""
    data = load_data()
    item = next((item for item in data if item['id'] == item_id),None)
    if item:
        return jsonify(item), 200
    return jsonify({'error': 'Элемент не найден'}), 404

@app.route('/items', methods=['POST'])
def create_item():
    """Создаёт новый элемент. Проверяет обязательные поля и присваивает новый ID."""
    if not request.is_json:
        return jsonify({'error': 'Ожидался JSON'}), 400
    
    new_data = request.get_json()
    required_fields = ['name', 'description', 'price']
    for field in required_fields:
        if field not in new_data:
            return jsonify({'error': f'Отстутствует поле {field}'}), 400
    
    data = load_data()
    new_id = max((item['id'] for item in data), default=0) + 1
    new_item = {
        'id': new_id,
        'name': new_data['name'],
        'description': new_data['description'],
        'price': new_data['price']
    }
    data.append(new_item)
    save_data(data)
    return jsonify(new_item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Обновляет элемент с указанным ID. Возвращает ошибку 404, если элемент не найден."""
    if not request.is_json:
        return jsonify({'error': 'Ожидался JSON'}), 400
    
    updated_data = request.get_json()
    data = load_data()
    
    for item in data:
        if item['id'] == item_id:
            item['name'] = updated_data.get('name', item['name'])
            item['description'] = updated_data.get('description', item['description'])
            item['price'] = updated_data.get('price', item['price'])
            save_data(data)
            return jsonify(item), 200
    return jsonify({'error': 'Элемент не найден'}), 404

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Удаляет элемент с указанным ID. Возвращает ошибку 404, если элемент не найден."""
    data = load_data()
    initial_length = len(data)
    data = [item for item in data if item['id'] != item_id]
    
    if len(data) == initial_length:
        return jsonify({'error': 'Элемент не найден'}), 404
    
    save_data(data)
    return '', 204

@app.route('/items/filter', methods=['GET'])
def filter_items():
    # Получаем параметры из URL
    min_price_str = request.args.get('min_price')
    max_price_str = request.args.get('max_price')
    search_term = request.args.get('search')
    
    # Преобразуем строки в числа и проверяем их корректность
    min_price = None
    max_price = None
    
    if min_price_str:
        try:
            min_price = float(min_price_str)
            if min_price < 0:
                return jsonify({'error': 'min_price должно быть неотрицательным числом.'}), 400
        except ValueError:
            return jsonify({'error': 'min_price должен быть числом'}), 400
        
    if max_price_str:
        try:
            max_price = float(max_price_str)
            if max_price < 0:
                return jsonify({'error': 'max_price должно быть неотрицательным числом.'}), 400
        except ValueError:
            return jsonify({'error': 'max_price должен быть числом'}), 400
        
    # Загружаем все данные
    all_items = load_data()
    
    # Создаём пустой список для отфильтрованных элементов
    filtered_items = []
    
    # Проходим по всем элементам и проверяем каждый на соответствие условиям
    for item in all_items:
        price = item.get('price', 0)
        name_lower = item.get('name', '').lower()
        desc_lower = item.get('description', '').lower()
        
        # Проверяем условие по минимальной цене
        if min_price is not None and price < min_price:
            continue
        
        # Проверяем условие по максимальной цене
        if max_price is not None and price < max_price:
            continue
        
        if search_term:
            search_lower = search_term.lower()
            if search_lower not in name_lower and search_lower not in desc_lower:
                continue
            
        # Если все условия прошли, добавляем элемент в результат
        filtered_items.append(item)
        
    # Возвращаем отфильтрованный список с кодом 200 ОК
    return jsonify(filtered_items), 200



if __name__ == '__main__':
    app.run(debug=True, port=5000)