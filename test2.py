import tkinter as tk
from tkinter import ttk
import os

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.load_currencies()

        self.amount_entries = {}
        
        self.gradations_counter = 0

        # Первое поле ввода для суммы
        ttk.Label(root, text="Введите сумму:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(root, width=40)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Второе поле ввода для диапазона
        ttk.Label(root, text="Диапазон:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.range_entry = ttk.Entry(root, width=40)
        self.range_entry.grid(row=0, column=3, padx=5, pady=5)

        # Создание списка для выбора валют
        self.selected_currencies = []
        self.selected_currencies_var = tk.StringVar()
        self.currency_listbox = tk.Listbox(root, listvariable=self.selected_currencies_var, selectmode="multiple", width=50, height=10)
        self.currency_listbox.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Заполнение списка доступными валютами
        for currency_code in self.currencies.keys():
            self.currency_listbox.insert(tk.END, currency_code)

        # Обработчик события нажатия кнопки "Конвертировать"
        ttk.Button(root, text="Конвертировать", command=self.convert).grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(root, text="Настройки", command=self.show_settings).grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        
        # Поле для добавления дополнительных градаций
        self.add_gradation_button = ttk.Button(root, text="Добавить градацию", command=self.add_gradation)
        self.add_gradation_button.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        # Счетчик для отслеживания количества добавленных градаций
        self.gradations_counter = 1

    def add_gradation(self):
        if self.gradations_counter < 5:  # Максимальное количество градаций
            self.gradations_counter += 1
            gradation_label = ttk.Label(self.root, text=f"Градация {self.gradations_counter}:")
            gradation_label.grid(row=self.gradations_counter + 2, column=0, padx=5, pady=5, sticky="e")
            
            amount_entry = ttk.Entry(self.root, width=40)
            amount_entry.grid(row=self.gradations_counter + 2, column=1, padx=5, pady=5)
            self.amount_entries[self.gradations_counter] = amount_entry  # сохраняем ссылку
            
            range_entry = ttk.Entry(self.root, width=40)
            range_entry.grid(row=self.gradations_counter + 2, column=3, padx=5, pady=5)
            delete_button = ttk.Button(self.root, text="Удалить градацию", command=lambda gradation=self.gradations_counter: self.delete_gradation(gradation))
            delete_button.grid(row=self.gradations_counter + 2, column=4, padx=5, pady=5)

    def delete_gradation(self, gradation):
        # Удаляем соответствующие элементы интерфейса для градации
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) == gradation + 2:
                widget.grid_forget()
        self.gradations_counter -= 1
    
    def load_currencies(self):
        self.currencies = {}
        currencies_file_path = os.path.join(os.path.dirname(__file__), "Currencies.txt")
        if not os.path.exists(currencies_file_path):
            print("Файл Currencies.txt не найден. Создание нового файла.")
            with open(currencies_file_path, "w"):
                pass
        with open(currencies_file_path, "r") as file:
            for line in file:
                currency_code, rate = line.strip().split(':')
                self.currencies[currency_code] = {'name': currency_code, 'rate': float(rate)}

        if 'EUR' not in self.currencies:
            self.currencies['EUR'] = {'name': 'EUR', 'rate': 1.0}

    def update_selected_currencies_text(self):
        selected_currencies_text = ", ".join(self.selected_currencies)
        self.selected_currencies_var.set(selected_currencies_text)

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        
        ttk.Label(settings_window, text="Изменить курсы валют к Евро:").grid(row=0, column=0, padx=5, pady=5)
        
        self.currency_entries = {}
        row_counter = 1
        for currency_code, currency_info in self.currencies.items():
            if currency_code != 'EUR':
                ttk.Label(settings_window, text=currency_info['name']).grid(row=row_counter, column=0, padx=5, pady=5)
                entry = ttk.Entry(settings_window)
                entry.insert(0, str(currency_info['rate']))
                entry.grid(row=row_counter, column=1, padx=5, pady=5)
                self.currency_entries[currency_code] = entry
                row_counter += 1
        
        ttk.Button(settings_window, text="Добавить валюту", command=self.add_currency).grid(row=row_counter, column=0, padx=5, pady=5)
        ttk.Button(settings_window, text="Удалить валюту", command=self.remove_currency).grid(row=row_counter, column=1, padx=5, pady=5)
        row_counter += 1
        ttk.Button(settings_window, text="Сохранить", command=lambda: self.save_settings_and_close(settings_window)).grid(row=row_counter, column=0, columnspan=2, padx=5, pady=5)
    
    def add_currency(self):
        add_currency_window = tk.Toplevel(self.root)
        add_currency_window.title("Добавить валюту")
        
        ttk.Label(add_currency_window, text="Код валюты:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(add_currency_window, text="Курс к Евро:").grid(row=1, column=0, padx=5, pady=5)
        
        self.new_currency_code_entry = ttk.Entry(add_currency_window)
        self.new_currency_code_entry.grid(row=0, column=1, padx=5, pady=5)
        self.new_currency_rate_entry = ttk.Entry(add_currency_window)
        self.new_currency_rate_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(add_currency_window, text="Добавить", command=lambda: self.save_new_currency_and_close(add_currency_window)).grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    
    def save_new_currency_and_close(self, add_currency_window):
        new_currency_code = self.new_currency_code_entry.get().strip()
        new_currency_rate = float(self.new_currency_rate_entry.get().strip())
        if new_currency_code and new_currency_rate:
            self.currencies[new_currency_code] = {'name': new_currency_code, 'rate': new_currency_rate}
            add_currency_window.destroy()
            self.save_currencies_to_file()

    def remove_currency(self):
        remove_currency_window = tk.Toplevel(self.root)
        remove_currency_window.title("Удалить валюту")
        
        ttk.Label(remove_currency_window, text="Код валюты:").grid(row=0, column=0, padx=5, pady=5)
        self.currency_code_to_remove_entry = ttk.Entry(remove_currency_window)
        self.currency_code_to_remove_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(remove_currency_window, text="Удалить", command=lambda: self.remove_selected_currency_and_close(remove_currency_window)).grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    
    def remove_selected_currency_and_close(self, remove_currency_window):
        currency_code_to_remove = self.currency_code_to_remove_entry.get().strip()
        if currency_code_to_remove in self.currencies and currency_code_to_remove != 'EUR':
            del self.currencies[currency_code_to_remove]
            remove_currency_window.destroy()
            self.save_currencies_to_file()

    def save_settings_and_close(self, settings_window):
        self.save_settings()
        settings_window.destroy()

    def save_settings(self):
        for currency_code, entry in self.currency_entries.items():
            self.currencies[currency_code]['rate'] = float(entry.get())
        self.save_currencies_to_file()
    
    def save_currencies_to_file(self):
        currencies_file_path = os.path.join(os.path.dirname(__file__), "Currencies.txt")
        with open(currencies_file_path, "w") as file:
            for currency_code, currency_info in self.currencies.items():
                file.write(f"{currency_code}:{currency_info['rate']}\n")

    def convert(self):
        selected_currency_indices = self.currency_listbox.curselection()
        selected_currencies = [self.currency_listbox.get(index) for index in selected_currency_indices]

        try:
            amount = float(self.amount_entry.get())

            gradation_count = self.gradations_counter
            for i in range(1, gradation_count + 1):
                gradation_number = i
                result_text_amount = ""
                result_text_range = ""
                
                for currency_code in selected_currencies:
                    currency_info = self.currencies[currency_code]
                    converted_amount = amount * currency_info['rate'] / self.currencies['EUR']['rate']
                    result_text_amount += f"{currency_code}: {int(converted_amount)}, "

                amount_entry = self.amount_entries.get(gradation_number)
                if amount_entry:
                    amount_entry_value = amount_entry.get()
                    if amount_entry_value:  # Проверяем, есть ли значение ввода для данной градации
                        if gradation_number == gradation_count:  # последняя градация
                            converted_min = float(amount_entry_value) * currency_info['rate'] / self.currencies['EUR']['rate']
                            result_text_range += f"min {currency_code}: {int(converted_min)}, "
                        else:
                            converted_range_min = float(amount_entry_value) * currency_info['rate'] / self.currencies['EUR']['rate']
                            converted_range_max = (float(amount_entry_value) * 2) * currency_info['rate'] / self.currencies['EUR']['rate']
                            result_text_range += f"{currency_code}: {int(converted_range_min)}...{int(converted_range_max)}, "

                result_text_amount = result_text_amount[:-2]
                if result_text_range:  # Проверяем, не пуст ли результат для градации
                    result_text_range = result_text_range[:-2]
                    print(f"amount {result_text_amount}")
                    print(f"range {result_text_range}")
                else:
                    print(f"amount {result_text_amount}")

        except ValueError:
            print("Ошибка: введите корректную сумму и значения для каждой градации.")

root = tk.Tk()
app = CurrencyConverterApp(root)
root.mainloop()
