import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk

def open_edit_window_with_tabs(files_to_edit):
    edit_window = tk.Toplevel(root)
    edit_window.title("Редактирование текстур и parent")
    edit_window.geometry("900x800")

    top_frame = tk.Frame(edit_window)
    top_frame.pack(side="top", fill="x")

    notebook = ttk.Notebook(edit_window)
    notebook.pack(expand=True, fill="both")

    chunk_size = 110
    text_widgets = []
    parent_entries = []

    for i in range(0, len(files_to_edit), chunk_size):
        frame = tk.Frame(notebook)
        notebook.add(frame, text=f"Группа {i // chunk_size + 1}")

        canvas = tk.Canvas(frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollable_frame.bind(
            "<Configure>",
            lambda e, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        for file, file_path, parent, textures in files_to_edit[i:i + chunk_size]:
            tk.Label(scrollable_frame, text=f"{file}", font=("Arial", 12, "bold")).pack(pady=(10, 0))

            parent_label = tk.Label(scrollable_frame, text='parent:', font=("Arial", 10, "italic"))
            parent_label.pack(pady=5)
            parent_entry = tk.Entry(scrollable_frame, width=100)
            parent_entry.insert(0, parent)
            parent_entry.pack(pady=5)
            parent_entries.append((file_path, parent_entry))

            text_widget = tk.Text(scrollable_frame, height=10, width=100, wrap="none", undo=True)
            text_widget.pack(padx=10, pady=5)
            texture_text = json.dumps(textures, indent=4)
            text_widget.insert(tk.END, texture_text)
            bind_shortcuts(text_widget)
            text_widgets.append((file_path, text_widget))

    def apply_changes():
        for (file_path, parent_entry), (_, text_widget) in zip(parent_entries, text_widgets):
            try:
                new_textures = json.loads(text_widget.get("1.0", tk.END))
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", f"Некорректный JSON формат в файле: {file_path}")
                return
            new_parent = parent_entry.get()
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
            data["textures"] = new_textures
            if new_parent:
                data["parent"] = new_parent
            elif "parent" in data:
                del data["parent"]
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        messagebox.showinfo("Успех", "Текстуры и parent успешно обновлены.")
        edit_window.destroy()

    def find_and_replace():
        find_text = simpledialog.askstring("Найти", "Введите текст для поиска:", parent=edit_window)
        replace_text = simpledialog.askstring("Заменить", "Введите текст для замены:", parent=edit_window)
        if find_text and replace_text:
            for _, text_widget in text_widgets:
                content = text_widget.get("1.0", tk.END)
                new_content = content.replace(find_text, replace_text)
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, new_content)

    tk.Button(top_frame, text="Сохранить всё", command=apply_changes).pack(side="left", padx=5, pady=5)
    tk.Button(top_frame, text="Найти и заменить", command=find_and_replace).pack(side="left", padx=5, pady=5)

def edit_textures_in_files():
    models_dir = "C:/Users/mebao/OneDrive/Desktop/mod_implement/models/block"
    selected_files = filedialog.askopenfilenames(
        title="Выберите файлы для редактирования",
        initialdir=models_dir,
        filetypes=[("JSON файлы", "*.json")]
    )
    if not selected_files:
        return
    files_to_edit = []
    for file_path in selected_files:
        with open(file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                continue
            textures = data.get("textures", {})
            parent = data.get("parent", "")
            files_to_edit.append((os.path.basename(file_path), file_path, parent, textures))
    if not files_to_edit:
        messagebox.showinfo("Информация", "Файлы с текстурами не найдены.")
        return
    open_edit_window_with_tabs(files_to_edit)


def add_render_type_to_files():
    models_dir = "resources/assets/souldercontent/models/block"
    selected_files = filedialog.askopenfilenames(
        title="Выберите файлы для изменения render_type и display",
        initialdir=models_dir,
        filetypes=[("JSON файлы", "*.json")]
    )
    if not selected_files:
        return

    new_display_data = {
        "display": {
            "thirdperson_righthand": {
                "rotation": [24, 0, 0],
                "translation": [0, 3, -0.5],
                "scale": [0.3, 0.3, 0.3]
            },
            "thirdperson_lefthand": {
                "rotation": [24, 0, 0],
                "translation": [0, 3, -0.5],
                "scale": [0.3, 0.3, 0.3]
            },
            "firstperson_righthand": {
                "rotation": [0, 109, 5],
                "translation": [3.25, 3.5, 0],
                "scale": [0.5, 0.5, 0.5]
            },
            "firstperson_lefthand": {
                "rotation": [0, 109, 5],
                "translation": [3.75, 3.5, 0],
                "scale": [0.5, 0.5, 0.5]
            },
            "ground": {
                "translation": [0, 3.5, 0],
                "scale": [0.5, 0.5, 0.5]
            },
            "gui": {
                "rotation": [25, 151, 0],
                "translation": [0.25, 0.5, 0],
                "scale": [0.72, 0.72, 0.72]
            },
            "head": {
                "translation": [0, 11.15, 0],
                "scale": [0.5, 0.5, 0.5]
            },
            "fixed": {
                "rotation": [-90, 0, 0],
                "translation": [0, -1, -15.5],
                "scale": [1.92, 1.92, 1.92]
            }
        }
    }
    new_render_type = "minecraft:cutout"

    for file_path in selected_files:
        with open(file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                continue

            # Перезаписываем "render_type"
            data["render_type"] = new_render_type

            # Перезаписываем "display"
            data["display"] = new_display_data["display"]

            # Сохраняем изменения в файл
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

    messagebox.showinfo("Успех", "render_type и display перезаписаны в выбранных файлах.")


def bind_shortcuts(widget):
    widget.bind("<Control-c>", lambda e: widget.event_generate("<<Copy>>"))
    widget.bind("<Control-v>", lambda e: widget.event_generate("<<Paste>>"))
    widget.bind("<Control-a>", lambda e: widget.tag_add("sel", "1.0", "end"))

# Окно генератора blockstates
def open_blockstates_generator():
    def create_files_with_template(selected_files, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file in selected_files:
            block_name = os.path.splitext(os.path.basename(file))[0]
            output_file = os.path.join(output_folder, f"{block_name}.json")

            file_data = json.loads(json.dumps(blockstates_template).replace("BLOCKNAME", block_name))

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=4)

    def select_files():
        files = filedialog.askopenfilenames(title="Выберите файлы")
        if files:
            file_list.delete(0, tk.END)
            for file in files:
                file_list.insert(tk.END, file)

    def select_output_folder():
        folder = filedialog.askdirectory(title="Выберите папку для сохранения файлов")
        if folder:
            output_folder_entry.delete(0, tk.END)
            output_folder_entry.insert(0, folder)

    def generate_files():
        selected_files = file_list.get(0, tk.END)
        output_folder = output_folder_entry.get()

        if not selected_files:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один файл!")
            return
        if not output_folder:
            messagebox.showwarning("Ошибка", "Выберите папку для сохранения файлов!")
            return

        try:
            create_files_with_template(selected_files, output_folder)
            messagebox.showinfo("Успех", "Файлы успешно созданы!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    blockstate_window = tk.Toplevel(root)
    blockstate_window.title("Генератор blockstates файлов")

    file_frame = tk.Frame(blockstate_window)
    file_frame.pack(pady=10)

    file_label = tk.Label(file_frame, text="Выбранные файлы:")
    file_label.pack(side=tk.LEFT)

    file_list = tk.Listbox(file_frame, selectmode=tk.MULTIPLE, width=50)
    file_list.pack(side=tk.LEFT)

    select_files_button = tk.Button(file_frame, text="Выбрать файлы", command=select_files)
    select_files_button.pack(side=tk.LEFT, padx=10)

    output_folder_frame = tk.Frame(blockstate_window)
    output_folder_frame.pack(pady=10)

    output_folder_label = tk.Label(output_folder_frame, text="Папка для сохранения:")
    output_folder_label.pack(side=tk.LEFT)

    output_folder_entry = tk.Entry(output_folder_frame, width=40)
    output_folder_entry.pack(side=tk.LEFT)

    select_folder_button = tk.Button(output_folder_frame, text="Выбрать папку", command=select_output_folder)
    select_folder_button.pack(side=tk.LEFT, padx=10)

    generate_button = tk.Button(blockstate_window, text="Создать файлы", command=generate_files)
    generate_button.pack(pady=20)

blockstates_template = {
    "variants": {
        "facing=east": {
            "model": "souldercontent:block/BLOCKNAME",
            "y": 90
        },
        "facing=north": {
            "model": "souldercontent:block/BLOCKNAME"
        },
        "facing=south": {
            "model": "souldercontent:block/BLOCKNAME",
            "y": 180
        },
        "facing=west": {
            "model": "souldercontent:block/BLOCKNAME",
            "y": 270
        }
    }
}

# Окно генератора loot-table
def open_loot_table_generator():
    def create_files_with_template(selected_files, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file in selected_files:
            block_name = os.path.splitext(os.path.basename(file))[0]
            output_file = os.path.join(output_folder, f"{block_name}.json")

            file_data = json.loads(json.dumps(loot_table_template).replace("BLOCKNAME", block_name))

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=4)

    def select_files():
        files = filedialog.askopenfilenames(title="Выберите файлы")
        if files:
            file_list.delete(0, tk.END)
            for file in files:
                file_list.insert(tk.END, file)

    def select_output_folder():
        folder = filedialog.askdirectory(title="Выберите папку для сохранения файлов")
        if folder:
            output_folder_entry.delete(0, tk.END)
            output_folder_entry.insert(0, folder)

    def generate_files():
        selected_files = file_list.get(0, tk.END)
        output_folder = output_folder_entry.get()

        if not selected_files:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один файл!")
            return
        if not output_folder:
            messagebox.showwarning("Ошибка", "Выберите папку для сохранения файлов!")
            return

        try:
            create_files_with_template(selected_files, output_folder)
            messagebox.showinfo("Успех", "Файлы успешно созданы!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    loot_table_window = tk.Toplevel(root)
    loot_table_window.title("Генератор loot-table файлов")

    file_frame = tk.Frame(loot_table_window)
    file_frame.pack(pady=10)

    file_label = tk.Label(file_frame, text="Выбранные файлы:")
    file_label.pack(side=tk.LEFT)

    file_list = tk.Listbox(file_frame, selectmode=tk.MULTIPLE, width=50)
    file_list.pack(side=tk.LEFT)

    select_files_button = tk.Button(file_frame, text="Выбрать файлы", command=select_files)
    select_files_button.pack(side=tk.LEFT, padx=10)

    output_folder_frame = tk.Frame(loot_table_window)
    output_folder_frame.pack(pady=10)

    output_folder_label = tk.Label(output_folder_frame, text="Папка для сохранения:")
    output_folder_label.pack(side=tk.LEFT)

    output_folder_entry = tk.Entry(output_folder_frame, width=40)
    output_folder_entry.pack(side=tk.LEFT)

    select_folder_button = tk.Button(output_folder_frame, text="Выбрать папку", command=select_output_folder)
    select_folder_button.pack(side=tk.LEFT, padx=10)

    generate_button = tk.Button(loot_table_window, text="Создать файлы", command=generate_files)
    generate_button.pack(pady=20)

loot_table_template = {
    "type": "minecraft:block",
    "pools": [
        {
            "rolls": 1,
            "entries": [
                {"type": "minecraft:item", "name": "souldercontent:BLOCKNAME"}
            ],
            "conditions": [
                {"condition": "minecraft:survives_explosion"}
            ]
        }
    ]
}

# Окно генератора block-item
def open_block_item_generator():
    def create_files_with_template(selected_files, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for file in selected_files:
            block_name = os.path.splitext(os.path.basename(file))[0]
            output_file = os.path.join(output_folder, f"{block_name}.json")

            file_data = json.loads(json.dumps(block_item_template).replace("BLOCKNAME", block_name))

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=4)

    def select_files():
        files = filedialog.askopenfilenames(title="Выберите файлы")
        if files:
            file_list.delete(0, tk.END)
            for file in files:
                file_list.insert(tk.END, file)

    def select_output_folder():
        folder = filedialog.askdirectory(title="Выберите папку для сохранения файлов")
        if folder:
            output_folder_entry.delete(0, tk.END)
            output_folder_entry.insert(0, folder)

    def generate_files():
        selected_files = file_list.get(0, tk.END)
        output_folder = output_folder_entry.get()

        if not selected_files:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один файл!")
            return
        if not output_folder:
            messagebox.showwarning("Ошибка", "Выберите папку для сохранения файлов!")
            return

        try:
            create_files_with_template(selected_files, output_folder)
            messagebox.showinfo("Успех", "Файлы успешно созданы!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    block_item_window = tk.Toplevel(root)
    block_item_window.title("Генератор block-item файлов")

    file_frame = tk.Frame(block_item_window)
    file_frame.pack(pady=10)

    file_label = tk.Label(file_frame, text="Выбранные файлы:")
    file_label.pack(side=tk.LEFT)

    file_list = tk.Listbox(file_frame, selectmode=tk.MULTIPLE, width=50)
    file_list.pack(side=tk.LEFT)

    select_files_button = tk.Button(file_frame, text="Выбрать файлы", command=select_files)
    select_files_button.pack(side=tk.LEFT, padx=10)

    output_folder_frame = tk.Frame(block_item_window)
    output_folder_frame.pack(pady=10)

    output_folder_label = tk.Label(output_folder_frame, text="Папка для сохранения:")
    output_folder_label.pack(side=tk.LEFT)

    output_folder_entry = tk.Entry(output_folder_frame, width=40)
    output_folder_entry.pack(side=tk.LEFT)

    select_folder_button = tk.Button(output_folder_frame, text="Выбрать папку", command=select_output_folder)
    select_folder_button.pack(side=tk.LEFT, padx=10)

    generate_button = tk.Button(block_item_window, text="Создать файлы", command=generate_files)
    generate_button.pack(pady=20)

block_item_template = {
    "parent": "souldercontent:block/BLOCKNAME"
}
root = tk.Tk()
root.title("Редактор блоков Minecraft")
root.geometry("500x500")

tab_control = ttk.Notebook(root)
tab_control.pack(expand=True)

edit_tab = ttk.Frame(tab_control)
tab_control.add(edit_tab, text="Редактировать текстуры")
tk.Button(edit_tab, text="Редактировать текстуры", command=edit_textures_in_files).pack(pady=10)
tk.Button(edit_tab, text="Добавить render_type", command=add_render_type_to_files).pack(pady=10)

blockstates_tab = ttk.Frame(tab_control)
tab_control.add(blockstates_tab, text="Blockstates Generator")
ttk.Button(blockstates_tab, text="Open Blockstates Generator", command=open_blockstates_generator).pack(pady=20)

loot_table_tab = ttk.Frame(tab_control)
tab_control.add(loot_table_tab, text="Loot Table Generator")
ttk.Button(loot_table_tab, text="Open Loot Table Generator", command=open_loot_table_generator).pack(pady=20)

block_item_tab = ttk.Frame(tab_control)
tab_control.add(block_item_tab, text="models/item-block Generator")
ttk.Button(block_item_tab, text="Open Block Item Generator", command=open_block_item_generator).pack(pady=20)

root.mainloop()
