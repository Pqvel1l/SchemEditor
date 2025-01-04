import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import re

LEVEL_MAPPING = {
    1: "wooden",
    2: "cobblestone",
    3: "iron",
    4: "gold",
    5: "diamond",
    6: "netherite",
    7: "adamantite",
    8: "fault"
}

DISPLAY_SETTINGS = {
    "thirdperson_righthand": {
        "rotation": [24, 0, 0],
        "translation": [0, 0.75, -0.5],
        "scale": [0.6, 0.6, 0.6]
    },
    "thirdperson_lefthand": {
        "rotation": [24, 0, 0],
        "translation": [0, 0.75, -0.5],
        "scale": [0.6, 0.6, 0.6]
    },
    "firstperson_righthand": {
        "rotation": [0, 109, 5],
        "translation": [2.75, 6.5, 0],
        "scale": [0.83, 0.83, 0.83]
    },
    "firstperson_lefthand": {
        "rotation": [0, 109, 5],
        "translation": [2.75, 6.5, 0],
        "scale": [0.83, 0.83, 0.83]
    },
    "ground": {
        "translation": [0, 3.5, 0],
        "scale": [0.65, 0.65, 0.65]
    },
    "gui": {
        "rotation": [25, 151, 0],
        "translation": [0.25, 2.25, 0],
        "scale": [0.72, 0.72, 0.72]
    },
    "head": {
        "translation": [0, 14.4, 0]
    },
    "fixed": {
        "rotation": [-90, 0, 0],
        "translation": [0, -1, -15.5],
        "scale": [1.92, 1.92, 1.92]
    }
}

RENDER_TYPE = "minecraft:cutout"

def get_level_from_registry_line(line):
    match = re.search(r"TIERA(\d+)_BLOCK", line)
    if match:
        return int(match.group(1))
    raise ValueError(f"Не удалось извлечь уровень из строки: {line}")

def update_textures_with_level(template_data, level_number):
    level_name = LEVEL_MAPPING.get(level_number)
    if not level_name:
        raise ValueError(f"Неверный уровень: {level_number}")

    # Игнорируем текущие цифры в `textures` и заменяем содержимое
    template_data["textures"] = {
        "0": f"cobblemon_generators:block/generator_arable_land_{level_name}",
        "particle": f"cobblemon_generators:block/generator_arable_land_{level_name}"
    }

def add_display_and_render_type(template_data):
    template_data["display"] = DISPLAY_SETTINGS
    template_data["render_type"] = RENDER_TYPE

def generate_files_from_template(template_file, texture_files, output_folder, levels):
    with open(template_file, 'r', encoding='utf-8') as f:
        try:
            template_data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Невозможно прочитать файл шаблона")
            return

    for level in levels:
        try:
            updated_data = template_data.copy()
            update_textures_with_level(updated_data, level)
            add_display_and_render_type(updated_data)

            save_file(updated_data, output_folder, f"tier_arable_{level}.json")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

def save_file(data, output_folder, file_name):
    os.makedirs(output_folder, exist_ok=True)
    with open(os.path.join(output_folder, file_name), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def read_registry_file(file_path):
    registry_lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                registry_lines.append(line)
    return registry_lines

def select_files():
    return filedialog.askopenfilenames(title="Выберите файлы текстур", filetypes=[("Все файлы", "*.*")])

def select_folder():
    return filedialog.askdirectory(title="Выберите папку для сохранения")

def create_main_window():
    def handle_task():
        registry_file = filedialog.askopenfilename(title="Выберите файл с регистрацией блоков", filetypes=[("Текстовые файлы", "*.txt")])
        if not registry_file:
            return

        try:
            registry_lines = read_registry_file(registry_file)
            levels = [get_level_from_registry_line(line) for line in registry_lines]
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return

        template_file = filedialog.askopenfilename(title="Выберите файл шаблона", filetypes=[("JSON файлы", "*.json")])
        if not template_file:
            return

        texture_files = select_files()
        if not texture_files:
            return

        output_folder = select_folder()
        if not output_folder:
            return

        generate_files_from_template(template_file, texture_files, output_folder, levels)
        messagebox.showinfo("Успех", "Операция выполнена успешно!")

    root = tk.Tk()
    root.title("Minecraft JSON Tool")
    root.geometry("600x400")

    btn = tk.Button(root, text="Сгенерировать файлы models/block", command=handle_task)
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
