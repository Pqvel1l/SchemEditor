import yaml
import tkinter as tk
from tkinter import messagebox, filedialog


# Функция для загрузки данных из файла с иконками (формат YAML)
def load_icons(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# Функция для генерации нового документа на основе шаблона
def generate_glyphs_template(icon_data, output_file_path, start_number, slot_ranges):
    # Шаблон для создания записи с сохранением всех переносов строк
    template = """\
  glyph_{number}:
    material: oraxen-{icon}
    slot: {slot}
    priority: 1
    hide_enchantments: true
    view_requirement:
      requirements:
        has_rank:
          type: 'has permission'
          permission: 'glyph.{number}'
    display_name: '&eЗначок &f{character}&e'
    lore:
    - ''
    - '&aВы уже приобрели данный значок!'
    - '&8Слот: {slot}'
    - '&aНажмите чтобы установить!'
    click_commands:
    - '[console] lp user %player_name% meta removesuffix 1'
    - '[console] lp user %player_name% permission set suffix.1.&f{character}'
    - '[message]&x&F&2&D&9&1&DCobblemon  &1>>&a Вы успешно установили значок.'
  no_glyph_{number}:
    material: barrier
    slot: {slot}
    priority: 2
    display_name: '&eЗначок &f{character}&e'
    lore:
    - ''
    - '&cУ вас нет прав на использование данного значка!'
    click_commands:
    - '[message]&x&F&2&D&9&1&DCobblemon  &1>>&a Для того, чтобы установить данный значок, купите его в нашем дискорде!'
    """

    # Список для хранения конечных записей
    glyphs = []

    # Индекс слота
    slot_idx = 0

    # Перебираем диапазоны слотов
    slots = []
    for start, end in slot_ranges:
        slots.extend(range(start, end + 1))

    # Перебираем данные о иконках и создаём запись для каждого символа
    for idx, (key, icon_info) in enumerate(icon_data.items(), start=start_number):
        # Извлекаем имя иконки, которое является полным ключом (например, screamtail_icon)
        icon = key  # Это извлечет полное имя иконки, включая _icon

        # Извлекаем символ и текстуру
        character = icon_info['char']

        # Если слоты еще не кончились, то берем текущий слот
        if slot_idx < len(slots):
            slot = slots[slot_idx]
            slot_idx += 1
        else:
            # Если слоты закончились, выходим из цикла (можно расширить, если нужно)
            break

        # Формируем запись для glyph_{number} в правильном формате
        glyph_entry = template.format(number=idx, icon=icon, character=character, slot=slot)

        # Добавляем записи в список
        glyphs.append(glyph_entry)

    # Открываем файл для записи
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # Записываем все строки в файл, включая все переносы строк
        output_file.write("\n".join(glyphs))


# Функция для запуска через интерфейс tkinter
def on_generate_button_click():
    # Получаем значения из полей ввода
    start_number_str = entry_start_number.get()

    # Проверяем, что введено правильное число
    try:
        start_number = int(start_number_str)
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число для начала пагинации.")
        return

    # Открываем диалог для выбора файла с иконками (YAML)
    icon_file_path = filedialog.askopenfilename(title="Выберите файл с иконками", filetypes=[("YAML files", "*.yml")])
    if not icon_file_path:
        return  # Если файл не выбран, выходим

    # Загружаем данные из выбранного файла (чтение YAML)
    try:
        icon_data = load_icons(icon_file_path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {str(e)}")
        return

    # Открываем диалог для сохранения выходного файла
    output_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not output_file_path:
        return  # Если файл не выбран, выходим

    # Диапазоны слотов (для примера: 14-16, 18-25, 26-34, 37-43)
    slot_ranges = [(10, 16), (19, 25), (28, 34), (37, 43)]

    # Генерируем новый текстовый файл с шаблонами
    generate_glyphs_template(icon_data, output_file_path, start_number, slot_ranges)

    # Уведомляем пользователя о завершении
    messagebox.showinfo("Готово", f"Файл успешно сгенерирован и сохранён как {output_file_path}")


# Настройка интерфейса tkinter
root = tk.Tk()
root.title("Генератор Glyphs Шаблонов")

# Надпись и поле ввода для начального числа пагинации
label_start_number = tk.Label(root, text="Начальное число пагинации:")
label_start_number.pack(padx=10, pady=5)

entry_start_number = tk.Entry(root)
entry_start_number.pack(padx=10, pady=5)

# Кнопка для генерации файла
generate_button = tk.Button(root, text="Генерировать Шаблон", command=on_generate_button_click)
generate_button.pack(padx=10, pady=20)

# Запуск главного цикла интерфейса
root.mainloop()
