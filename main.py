import trimesh
import pyvista as pv
import numpy as np
import flet as ft


def load_and_fix_obj(file_path):
    try:
        # Загрузка модели с использованием trimesh
        mesh = trimesh.load(file_path, force="mesh")
        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError("Файл не является корректной 3D-моделью.")

        print(f"Модель успешно загружена: {file_path}")
        print(f"Количество вершин: {len(mesh.vertices)}")
        print(f"Количество граней: {len(mesh.faces)}")

        if len(mesh.faces) == 0:
            print("Грани отсутствуют. Обрабатываю как облако точек.")
            return pv.PolyData(mesh.vertices)

        # Конвертируем формат граней в формат PyVista
        faces = np.hstack([[3] + face.tolist() for face in mesh.faces])
        print("Первые несколько граней:", mesh.faces[:5])

        # Возвращаем PyVista объект
        return pv.PolyData(mesh.vertices, faces)
    except Exception as e:
        print(f"Ошибка при загрузке: {e}")
        return None


def open_obj_file_pyvista(file_path, theme, display_mode):
    try:
        mesh = load_and_fix_obj(file_path)
        if not mesh:
            print("Не удалось загрузить модель.")
            return

        plotter = pv.Plotter()
        background_color = "black" if theme == "dark" else "white"
        wireframe_color = "white" if theme == "dark" else "black"
        plotter.set_background(background_color)

        if display_mode == "color":
            plotter.add_mesh(mesh, color="gray", show_edges=False)
        elif display_mode == "wireframe":
            plotter.add_mesh(mesh, style="wireframe", color=wireframe_color)

        plotter.show()
    except Exception as e:
        print(f"Произошла ошибка при визуализации: {e}")


def main(page: ft.Page):
    page.title = "Загрузчик OBJ файлов"
    page.window.width = 500
    page.window.height = 400

    selected_file = ft.Text(value="Выбранный файл: нет")
    theme = ft.Dropdown(
        options=[ft.dropdown.Option("light"), ft.dropdown.Option("dark")],
        value="light",
        label="Тема",
    )
    display_mode = ft.Dropdown(
        options=[
            ft.dropdown.Option("color"),
            ft.dropdown.Option("wireframe"),
        ],
        value="color",
        label="Режим отображения",
    )

    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file.value = f"Выбранный файл: {e.files[0].name}"
            selected_file.data = e.files[0].path
        else:
            selected_file.value = "Выбор файла отменён"
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def select_file(_):
        file_picker.pick_files(allow_multiple=False)

    def open_file(_):
        if not hasattr(selected_file, "data") or not selected_file.data:
            selected_file.value = "Сначала выберите файл!"
            page.update()
            return
        open_obj_file_pyvista(selected_file.data, theme.value, display_mode.value)

    page.add(
        ft.Column(
            controls=[
                selected_file,
                ft.ElevatedButton("Выбрать файл", on_click=select_file),
                theme,
                display_mode,
                ft.ElevatedButton("Открыть файл", on_click=open_file),
            ],
            spacing=20,
        )
    )


ft.app(target=main)
