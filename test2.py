import xml.etree.ElementTree as ET
from tkinter import filedialog, ttk, simpledialog, messagebox
import tkinter as tk

class XmlProcessor:
    def __init__(self):
        self.data_list = []
        self.column_names = []

    def read_xml_file(self, xml_file_path):
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        self.data_list = []
        self.column_names = []

        ns = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}

        # Чтение заголовков столбцов
        header_row = root.find('.//ss:Row', ns)
        if header_row:
            for cell in header_row.findall('./ss:Cell', ns):
                data_tag = cell.find('./ss:Data', ns)
                if data_tag is not None:
                    header = data_tag.text
                    self.column_names.append(header)

        # Чтение данных
        for row in root.findall('.//ss:Row', ns):
            data = {}

            for idx, cell in enumerate(row.findall('./ss:Cell', ns)):
                data_tag = cell.find('./ss:Data', ns)
                if data_tag is not None:
                    data_type = data_tag.attrib.get('ss:Type', 'String')
                    data_value = data_tag.text

                    if data_type == 'String':
                        data[self.column_names[idx]] = data_value
                    elif data_type == 'Number':
                        data[self.column_names[idx]] = float(data_value)
                    elif data_type == 'DateTime':
                        data[self.column_names[idx]] = data_value

            self.data_list.append(data)

    def get_column_names(self):
        if self.data_list:
            return list(self.data_list[0].keys())
        else:
            return []

    def get_data(self):
        return self.data_list.copy()

class App:
    def __init__(self, root):
        self.root = root
        self.xml_processor = XmlProcessor()

        # Этап 1: Загрузка файла XML
        self.load_file_button = tk.Button(root, text="Load XML File", command=self.browse_xml_file)
        self.load_file_button.pack(pady=10)

    def browse_xml_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            # Загрузка файла XML
            self.xml_processor.read_xml_file(file_path)

            # Переход к этапу 2: Выбор столбцов
            self.select_columns()

    def select_columns(self):
        # Этап 2: Выбор столбцов
        column_names = self.xml_processor.get_column_names()

        if not column_names:
            messagebox.showerror("Error", "No data found in the XML file.")
            return

        column_selection_window = tk.Toplevel(self.root)
        column_selection_window.title("Select Columns")

        selected_columns = tk.StringVar(value=column_names)

        # Виджет для выбора столбцов
        column_listbox = tk.Listbox(column_selection_window, selectmode=tk.MULTIPLE, listvariable=selected_columns)
        column_listbox.pack(pady=10)

        # Кнопка для продолжения к следующему этапу
        next_button = tk.Button(column_selection_window, text="Next", command=lambda: self.display_table(selected_columns))
        next_button.pack(pady=10)

    def display_table(self, selected_columns):
        # Этап 3: Отображение полученной таблицы
        if not selected_columns.get():
            messagebox.showerror("Error", "Please select at least one column.")
            return

        selected_column_names = [column.replace("'", "").strip() for column in selected_column_names]
        selected_column_indices = [self.xml_processor.get_column_names().index(column) for column in selected_column_names]

        # Закрываем окно выбора столбцов
        self.root.focus_set()
        self.root.grab_set()
        self.root.grab_release()

        # Создание окна для отображения таблицы
        display_table_window = tk.Toplevel(self.root)
        display_table_window.title("Display Table")

        # Заголовки столбцов
        headers = self.xml_processor.get_column_names()

        # Создание виджета Treeview для отображения таблицы
        table_treeview = tk.ttk.Treeview(display_table_window, columns=headers, show="headings")
        for header in headers:
            table_treeview.heading(header, text=header)
        table_treeview.pack(pady=10)

        # Заполнение таблицы данными
        for row_data in self.xml_processor.get_data():
            table_treeview.insert("", "end", values=[row_data[headers[column]] for column in selected_column_indices])

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
