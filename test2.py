import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox, ttk, simpledialog
import tkinter as tk
import xlwt

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

        # Reading column headers
        header_row = root.find('.//ss:Row', ns)
        if header_row:
            self.column_names = [cell.find('./ss:Data', ns).text for cell in header_row.findall('./ss:Cell', ns)]

        # Reading data
        for row in root.findall('.//ss:Row', ns):
            data = {}
            for idx, cell in enumerate(row.findall('./ss:Cell', ns)):
                data_tag = cell.find('./ss:Data', ns)
                if data_tag is not None:
                    data_type = data_tag.attrib.get('ss:Type', 'String')
                    data_value = data_tag.text

                    if data_type == 'Number':
                        data_value = float(data_value)

                    data[self.column_names[idx]] = data_value

            self.data_list.append(data)

    def get_column_names(self):
        return self.column_names

    def get_data(self):
        return self.data_list

    def save_as_xls(self, file_path, selected_column_names, filters=None, data=None):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("Data")

        # Write column headers
        for col, header in enumerate(selected_column_names):
            sheet.write(0, col, header)

        # Write data
        for row, row_data in enumerate(data or self.data_list[1:], start=1):
            # Apply filters if provided
            if filters and not all(self.is_row_matching_filters(row_data, col, filter_value) for col, filter_value in filters.items()):
                continue

            values = [row_data.get(column_name, "") for column_name in selected_column_names]
            for col, value in enumerate(values):
                sheet.write(row, col, value)

        # Save the file
        workbook.save(file_path)
        messagebox.showinfo("Save", "Data saved successfully to {}".format(file_path))

    def is_row_matching_filters(self, row_data, column_name, filter_value):
        if column_name in row_data:
            cell_value = row_data[column_name]
            if isinstance(cell_value, (int, float)):
                # Numeric column
                return self.apply_numeric_filter(cell_value, filter_value)
            elif isinstance(cell_value, str):
                # Text column
                return self.apply_text_filter(cell_value, filter_value)
        return False

    def apply_numeric_filter(self, cell_value, filter_value):
        if filter_value.startswith(">"):
            return cell_value > float(filter_value[1:])
        elif filter_value.startswith("<"):
            return cell_value < float(filter_value[1:])
        elif filter_value.startswith("="):
            return cell_value == float(filter_value[1:])
        else:
            return False

    def apply_text_filter(self, cell_value, filter_value):
        filter_options = filter_value.split(',')
        return cell_value in filter_options

class App:
    def __init__(self, root):
        self.root = root
        self.xml_processor = XmlProcessor()
        self.filter_window = None  # New instance variable to hold the filter window
        self.filters = {}
        self.treeview = None
        self.save_button = None
        self.column_filter_window = None

        self.load_file_button = tk.Button(root, text="Load XML File", command=self.browse_xml_file)
        self.load_file_button.pack(pady=10)

    def browse_xml_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_path:
            self.xml_processor.read_xml_file(file_path)
            self.show_column_selection_window()

    def show_column_selection_window(self):
        column_names = self.xml_processor.get_column_names()
        # This line assigns the new window to an attribute for later reference
        self.column_filter_window = column_filter_window

        if not column_names:
            messagebox.showerror("Error", "No data found in the XML file.")
            return

        # Create a new Toplevel window for column selection and filters
        column_filter_window = tk.Toplevel(self.root)
        column_filter_window.title("Select Columns and Set Filters")

        # Create a Frame to contain the Listbox, Scrollbar, and filter entries
        frame = tk.Frame(column_filter_window)
        frame.pack(padx=10, pady=10)

        # Create Listbox and Scrollbar
        column_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=0)
        scrollbar = tk.Scrollbar(frame, command=column_listbox.yview)
        column_listbox.config(yscrollcommand=scrollbar.set)

        # Insert column names into Listbox
        for column in column_names:
            column_listbox.insert(tk.END, column)

        # Set the height of the Listbox to the maximum height of the column names
        max_height = min(len(column_names), 10)
        column_listbox.config(height=max_height)

        # Pack Listbox and Scrollbar
        column_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create Apply Filters button
        apply_button = tk.Button(column_filter_window, text="Apply Filters", command=self.show_table)
        apply_button.pack(pady=10)

        # Create filter entries dynamically based on selected columns
        for column_name in column_names:
            label = tk.Label(column_filter_window, text=f"Filter for {column_name}:")
            label.pack()
            entry_var = tk.StringVar()
            filter_entry = tk.Entry(column_filter_window, textvariable=entry_var)
            filter_entry.pack()
            self.filters[column_name] = entry_var

    def show_table(self):
        if self.column_filter_window is not None:  # Check if column_filter_window is not None
            selected_indices = self.column_filter_window.winfo_children()[0].winfo_children()[0].curselection()

        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one column.")
            return

        all_column_names = self.xml_processor.get_column_names()
        selected_column_names = [all_column_names[index] for index in selected_indices]

        # Create Treeview widget
        table_window = tk.Toplevel(self.root)
        table_window.title("Table View")

        self.treeview = ttk.Treeview(table_window, columns=selected_column_names, show="headings")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=self.treeview.yview)
        scrollbar.pack(side="right", fill="y")

        self.treeview.configure(yscrollcommand=scrollbar.set)
        self.treeview.pack(expand=tk.YES, fill=tk.BOTH)

        filtered_data = [row for row in self.xml_processor.get_data() if self.is_row_matching_filters(row, self.filters)]

        # Populate the Treeview with data
        for row_data in filtered_data:
            values = [row_data.get(column, "") for column in selected_column_names]
            self.treeview.insert("", "end", values=values)

        # Add Save button to Table View
        self.save_button = tk.Button(table_window, text="Save", command=lambda: self.save_as_xls(selected_column_names))
        self.save_button.pack(pady=10)

    def is_row_matching_filters(self, row_data, filters):
            for col, filter_var in filters.items():
                filter_value = filter_var.get()  # Use .get() here to retrieve the string value
                if not self.xml_processor.is_row_matching_filters(row_data, col, filter_value):
                    return False
            return True

    def save_as_xls(self, selected_column_names):
        file_path = filedialog.asksaveasfilename(defaultextension=".xls", filetypes=[("XLS files", "*.xls")])

        if file_path:
            try:
                # Get the filtered data
                filtered_data = [row for row in self.xml_processor.get_data() if self.is_row_matching_filters(row, self.filters)]

                # Save the data to the Excel file
                self.xml_processor.save_as_xls(file_path, selected_column_names, data=filtered_data)
                messagebox.showinfo("Save", f"Data saved successfully to {file_path}")
            except (IOError, PermissionError) as e:
                messagebox.showerror("Error", f"An error occurred while saving: {str(e)}")

class FilterWindow:
    def __init__(self, root, column_names, on_apply_filters):
        self.root = root
        self.column_names = column_names
        self.filters = {}

        self.filter_window = tk.Toplevel(self.root)
        self.filter_window.title("Set Filters")

        for column_name in self.column_names:
            label = tk.Label(self.filter_window, text=f"Filter for {column_name}:")
            label.pack()
            entry_var = tk.StringVar()
            filter_entry = tk.Entry(self.filter_window, textvariable=entry_var)
            filter_entry.pack()
            self.filters[column_name] = entry_var

        # Modify the apply button command to check if it's already being saved
        apply_button = tk.Button(self.filter_window, text="Apply Filters", command=lambda: on_apply_filters(self.filters))
        apply_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
