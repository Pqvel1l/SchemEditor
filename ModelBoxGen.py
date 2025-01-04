import os
import json
from tkinter import Tk, filedialog


# Функция для генерации Java-класса
def generate_java_class(model_name, elements, output_dir):
    class_name = model_name.capitalize()
    file_path = os.path.join(output_dir, f"{class_name}.java")

    # Генерация VoxelShape
    voxel_shapes = []
    for element in elements:
        from_coords = element["from"]  # Начальные координаты
        to_coords = element["to"]  # Конечные координаты
        voxel_shapes.append(
            f"VoxelShapes.cuboid({from_coords[0] / 16}, {from_coords[1] / 16}, {from_coords[2] / 16}, {to_coords[0] / 16}, {to_coords[1] / 16}, {to_coords[2] / 16})"
        )

    voxel_shapes_union = "VoxelShapes.union(\n            " + ",\n            ".join(voxel_shapes) + "\n        )"

    # Шаблон класса
    class_template = f"""
    package generated;

    import net.minecraft.block.Block;
    import net.minecraft.block.BlockState;
    import net.minecraft.block.ShapeContext;
    import net.minecraft.util.shape.VoxelShape;
    import net.minecraft.util.shape.VoxelShapes;
    import net.minecraft.world.BlockView;
    import net.minecraft.util.math.BlockPos;

    public class {class_name} extends Block {{

        private static final VoxelShape SHAPE = {voxel_shapes_union};

        public {class_name}(Settings settings) {{
            super(settings);
        }}

        @Override
        public VoxelShape getOutlineShape(BlockState state, BlockView world, BlockPos pos, ShapeContext context) {{
            return SHAPE;
        }}
    }}
    """

    # Сохранение файла
    with open(file_path, "w") as file:
        file.write(class_template)


# Основная функция
if __name__ == "__main__":
    # Выбор файлов моделей
    Tk().withdraw()  # Скрыть главное окно Tkinter
    file_paths = filedialog.askopenfilenames(title="Выберите JSON-модели", filetypes=[("JSON Files", "*.json")])

    if not file_paths:
        print("Файлы не выбраны. Завершение программы.")
        exit()

    # Выбор папки для сохранения
    output_dir = filedialog.askdirectory(title="Выберите папку для сохранения Java-классов")
    if not output_dir:
        print("Папка не выбрана. Завершение программы.")
        exit()

    # Обработка каждого файла
    for file_path in file_paths:
        with open(file_path, "r") as file:
            model_data = json.load(file)

        # Проверка на наличие элементов
        if "elements" not in model_data:
            print(f"Модель {os.path.basename(file_path)} не содержит элементов. Пропуск.")
            continue

        # Генерация класса
        model_name = os.path.splitext(os.path.basename(file_path))[0]
        generate_java_class(model_name, model_data["elements"], output_dir)

    print(f"Генерация завершена. Файлы сохранены в папке: {output_dir}")
