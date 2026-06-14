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

if __name__ == '__main__':
    app.run(debug=True, port=5000)