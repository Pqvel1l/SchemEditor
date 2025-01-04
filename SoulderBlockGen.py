import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Базовый словарь с переводами для демонстрации
TRANSLATION_DICT = {
    "pokedoll_zorua": "Кукла Зоруа",
    "normal_chest": "Обычный сундук",
    # Добавляйте сюда новые переводы по мере необходимости
}

# Функция для перевода на русский с использованием словаря
def translate_to_russian(text):
    return TRANSLATION_DICT.get(text, " ".join(word.capitalize() for word in text.split("_")))

# Функция для генерации файла с константами блоков
def generate_block_constants():
    selected_files = filedialog.askopenfilenames(
        title="Выберите файлы для генерации блоков",
        filetypes=[("Все файлы", "*.*")]
    )
    if not selected_files:
        messagebox.showinfo("Информация", "Файлы не выбраны.")
        return

    output_folder = filedialog.askdirectory(title="Выберите папку для сохранения файла")
    if not output_folder:
        messagebox.showinfo("Информация", "Папка для сохранения не выбрана.")
        return

    output_file_path = os.path.join(output_folder, "GeneratedBlocks.java")

    try:
        with open(output_file_path, "w") as output_file:
            output_file.write("public class GeneratedBlocks {\n\n")
            for file in selected_files:
                filename = os.path.splitext(os.path.basename(file))[0]
                constant_name = filename.upper()
                lowercase_name = filename.lower()
                output_file.write(f"    public final Block {constant_name} = fullCube(\"{lowercase_name}\");\n")
            output_file.write("\n}")

        messagebox.showinfo("Успех", f"Файл с блоками успешно создан: {output_file_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при создании файла: {e}")

# Функция для генерации строк с Identifier
def generate_identifiers():
    selected_files = filedialog.askopenfilenames(
        title="Выберите файлы для генерации идентификаторов",
        filetypes=[("Все файлы", "*.*")]
    )
    if not selected_files:
        messagebox.showinfo("Информация", "Файлы не выбраны.")
        return

    output_folder = filedialog.askdirectory(title="Выберите папку для сохранения файла")
    if not output_folder:
        messagebox.showinfo("Информация", "Папка для сохранения не выбрана.")
        return

    output_file_path = os.path.join(output_folder, "GeneratedIdentifiers.java")

    try:
        with open(output_file_path, "w") as output_file:
            output_file.write("public class GeneratedIdentifiers {\n\n")
            for file in selected_files:
                filename = os.path.splitext(os.path.basename(file))[0]
                lowercase_name = filename.lower()
                output_file.write(f"    new Identifier(SoulderContent.ID, \"{lowercase_name}\"),\n")
            output_file.write("\n}")

        messagebox.showinfo("Успех", f"Файл с идентификаторами успешно создан: {output_file_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при создании файла: {e}")

# Функция для генерации строк Item
def generate_item_constants():
    selected_files = filedialog.askopenfilenames(
        title="Выберите файлы для генерации предметов",
        filetypes=[("Все файлы", "*.*")]
    )
    if not selected_files:
        messagebox.showinfo("Информация", "Файлы не выбраны.")
        return

    output_folder = filedialog.askdirectory(title="Выберите папку для сохранения файла")
    if not output_folder:
        messagebox.showinfo("Информация", "Папка для сохранения не выбрана.")
        return

    output_file_path = os.path.join(output_folder, "GeneratedItems.java")

    try:
        with open(output_file_path, "w") as output_file:
            output_file.write("public class GeneratedItems {\n\n")
            for file in selected_files:
                filename = os.path.splitext(os.path.basename(file))[0]
                constant_name = filename.upper()
                lowercase_name = filename.lower()
                output_file.write(
                    f"    public final Item {constant_name} = blockItem(\"{lowercase_name}\", SoulderBlocks.getInstance().{constant_name});\n")
            output_file.write("\n}")

        messagebox.showinfo("Успех", f"Файл с предметами успешно создан: {output_file_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при создании файла: {e}")

# Функция для генерации переведённой локализации
def generate_translated_localization():
    selected_files = filedialog.askopenfilenames(
        title="Выберите файлы для генерации перевода",
        filetypes=[("JSON files", "*.json")]
    )
    if not selected_files:
        messagebox.showinfo("Информация", "Файлы не выбраны.")
        return

    output_folder = filedialog.askdirectory(title="Выберите папку для сохранения переведённого файла")
    if not output_folder:
        messagebox.showinfo("Информация", "Папка для сохранения не выбрана.")
        return

    output_file_path = os.path.join(output_folder, "TranslatedLocalization.json")

    try:
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write("{\n")
            for file in selected_files:
                filename = os.path.splitext(os.path.basename(file))[0]
                localized_key = f"block.souldercontent.{filename.lower()}"
                translated_value = translate_to_russian(filename)
                output_file.write(f'    "{localized_key}": "{translated_value}",\n')
            output_file.write("}")

        messagebox.showinfo("Успех", f"Файл с переведённой локализацией успешно создан: {output_file_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при создании файла: {e}")

# Создание окна приложения
root = tk.Tk()
root.title("Генератор различных штуковин")
root.geometry("400x400")

# Кнопка для генерации файла с константами блоков
generate_button_constants = tk.Button(root, text="Генерировать SoulderBlocks", command=generate_block_constants)
generate_button_constants.pack(pady=10)

# Кнопка для генерации идентификаторов
generate_button_identifiers = tk.Button(root, text="Генерировать ForgeItems", command=generate_identifiers)
generate_button_identifiers.pack(pady=10)

# Кнопка для генерации предметов
generate_button_items = tk.Button(root, text="Генерировать SoulderItems", command=generate_item_constants)
generate_button_items.pack(pady=10)

# Кнопка для генерации переведённой локализации
generate_button_translated_localization = tk.Button(root, text="[WIP] Генерировать переведённые строки локализации ", command=generate_translated_localization)
generate_button_translated_localization.pack(pady=10)

# Запуск основного цикла программы
root.mainloop()
