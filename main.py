import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json

class JSONParserApp:
    def load_json_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите JSON-файл",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                items = json.load(f)

            # Очищаем Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Добавляем элементы из файла в Treeview
            for item in items:
                self.tree.insert('', tk.END, values=(
                    item['id'], item['name'], item['description'], item['price']
                ))
            messagebox.showinfo("Успех", f"Загружено {len(items)} записей из файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            
    def __init__(self, root):
        self.root = root
        self.root.title("Сервис парсинга JSON")
        self.root.geometry("1024x720")
        
        # Убедитесь, что API работает на этом адресе
        self.api_url = "http://localhost:5000"
        
        # Инициализация интерфейса
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм с отступами
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Сервис парсинга JSON", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Фрейм для кнопок управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=10, sticky=(tk.E, tk.W))
        ttk.Button(button_frame, text="Загрузить JSON", command=self.load_json_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить список", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        
        # LabelFrame для списка элементов
        list_frame = ttk.LabelFrame(main_frame, text="Список элементов", padding="10")
        list_frame.grid(row=2, column=0, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W), columnspan=2)
        
        # Treeview для отображения данных
        columns = ('ID', 'Name', 'Description', 'Price')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        # Scrollbar для Treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # LabelFrame для формы ввода
        form_frame = ttk.LabelFrame(main_frame, text="Форма элемента", padding="10")
        form_frame.grid(row=3, column=0, pady=10, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Переменные для полей ввода
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.price_var = tk.DoubleVar()
        
        # Поля ввода
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.id_entry = ttk.Entry(form_frame, textvariable=self.id_var, state='readonly')
        self.id_entry.grid(row=0, column=1, sticky=(tk.E, tk.W), pady=5, padx=(5, 0))
        
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=1, column=1, sticky=(tk.E, tk.W), pady=5, padx=(5, 0))
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.desc_var).grid(row=2, column=1, sticky=(tk.E, tk.W), pady=5, padx=(5, 0))
        ttk.Label(form_frame, text="Price:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(form_frame, textvariable=self.price_var).grid(row=3, column=1, sticky=(tk.E, tk.W), pady=5, padx=(5, 0))
        
        # Фрейм для кнопок формы
        form_button_frame = ttk.Frame(form_frame)
        form_button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.E, tk.W))
        
        self.add_button = ttk.Button(form_button_frame, text="Добавить", command=self.create_item)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = ttk.Button(form_button_frame, text="Обновить", command=self.update_item, state='disabled')
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(form_button_frame, text="Удалить", command=self.delete_item, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(form_button_frame, text="Очистить", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Настройка весов для растягивания элементов при изменении размера окна
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1) # для растяжения list_frame
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1) # для растяжения полей ввода
        
        # Привязка события выбора строки в Treeview
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Загрузка начальных данных
        self.refresh_list()
        
    def refresh_list(self):
        """Обновляет список элементов из API."""
        try:
            response = requests.get(f"{self.api_url}/items")
            if response.status_code == 200:
                items = response.json()
                # Очищаем Treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                # Добавляем элементы из API в Treeview
                for item in items:
                    self.tree.insert('', tk.END, values=(
                        item['id'], item['name'], item['description'], item['price']
            ))
            else:
                messagebox.showerror("Ошибка API", f"Не удалось загрузить данные: код {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")
    
    def clear_form(self):
        """Очищает форму ввода и отключает кнопки Update и Delete."""
        self.id_var.set("")
        self.name_var.set("")
        self.desc_var.set("")
        self.price_var.set("0.0")
        self.update_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        
    def on_tree_select(self, event):
        """Обрабатывает выбор строки в Treeview - заполняет форму данными выбранного элемента."""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0])["values"]
            self.id_var.set(item_values[0])
            self.name_var.set(item_values[1])
            self.desc_var.set(item_values[2])
            self.price_var.set(item_values[3])
            # Включаем кнопки Update и Delete
            self.update_button.config(state='normal')
            self.delete_button.config(state='normal')
            
    def create_item(self):
        """Создаёт новый элемент через API."""
        if not self.validate_inputs():
            return
        
        try:
            new_item = {
                'name': self.name_var.get(),
                'description': self.desc_var.get(),
                'price': float(self.price_var.get())
            }
            response = requests.post(f"{self.api_url}/items", json=new_item)
            if response.status_code == 201:
                messagebox.showinfo("Успех", "Элемент успешно создан!")
                self.clear_form()
                self.refresh_list()
            else:
                error_text = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка создания", f"Не удалось создать элемент:\n{error_text}")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Цена должна быть числом!")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")
            
    def update_item(self):
        """Обновляет выбранный элемент через API."""
        if not self.validate_inputs():
            return
        
        try:
            item_id = int(self.id_var.get())
            update_item = {
                'name': self.name_var.get(),
                'description': self.desc_var.get(),
                'price': float(self.price_var.get())
            }
            response = requests.put(f"{self.api_url}/items/{item_id}", json=update_item)
            if response.status_code == 200:
                messagebox.showinfo("Успех", "Элемент успешно обновлён!")
                self.clear_form()
                self.refresh_list()
            elif response.status_code == 404:
                messagebox.showwarning("Ошибка", "Элемент не найден!")
            else:
                error_text = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка обновления", f"Не удалось обновить элемент:\n{error_text}")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID и цена должны быть числами!")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")
            
    def delete_item(self):
        """Удаляет выбранный элемент через API с подтверждением."""
        item_id = self.id_var.get()
        if not item_id:
            messagebox.showwarning("Предупреждение", "Выберите элемент для удаления!")
            return

        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить элемент с ID {item_id}?")
        if not confirm:
            return

        try:
            response = requests.delete(f"{self.api_url}/items/{item_id}")
            if response.status_code == 204:
                messagebox.showinfo("Успех", "Элемент успешно удалён!")
                self.clear_form()
                self.refresh_list()
            elif response.status_code == 404:
                messagebox.showwarning("Ошибка", "Элемент не найден!")
            else:
                error_text = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить элемент:\n{error_text}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось подключиться к API:\n{str(e)}")
            
    def validate_inputs(self):
        """Проверяет корректность введённых данных."""
        # Проверка обязательных полей
        if not self.name_var.get().strip():
            messagebox.showerror("Ошибка ввода", "Поле 'Name' не может быть пустым!")
            return False
        if not self.desc_var.get().strip():
            messagebox.showerror("Ошибка ввода", "Поле 'Description' не может быть пустым!")
            return False
        
        # Проверка корректности цены
        try:
            price = float(self.price_var.get())
            if price < 0:
                messagebox.showerror("Ошибка ввода", "Цена не может быть отрицательной!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Цена должна быть числом!")
            return False
        return True
    
def main():
    root = tk.Tk()
    app = JSONParserApp(root)
    root.mainloop()
        
if __name__ == "__main__":
    main()