import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import zipfile
import re

def sort_files_by_extension(dir_path: str) -> None:
    """
    Сортирует файлы в указанной директории по расширению файла.
    Файлы без расширения помещаются в папку 'no_extension'.
    """
    directory = Path(dir_path)

    if not directory.exists():
        print(f"❌ Ошибка: путь не существует — {dir_path}")
        return

    if not directory.is_dir():
        print(f"❌ Ошибка: путь не является директорией — {dir_path}")
        return

    items = list(directory.iterdir())
    if not items:
        print("⚠️ Папка пуста, сортировка не требуется.")
        return

    for item in items:
        if item.is_file():
            ext = item.suffix.lower()
            # Убираем точку, если есть; если нет расширения — ставим заглушку
            ext_name = ext[1:] if ext else "no_extension"

            target_folder = directory / ext_name
            target_folder.mkdir(exist_ok=True)

            destination = target_folder / item.name
            orig_destination = destination
            counter = 1

            # Защита от перезаписи: если файл уже есть, добавляем суффикс _1, _2 и т.д.
            while destination.exists():
                stem = orig_destination.stem
                suffix = orig_destination.suffix
                destination = orig_destination.parent / f"{stem}_{counter}{suffix}"
                counter += 1

            try:
                shutil.move(str(item), str(destination))
                print(f"✅ Перемещён: {item.name} → {destination.name}")
            except Exception as e:
                print(f"❌ Ошибка при перемещении {item.name}: {e}")


def rename_files(dir_path: str, old_pattern: str, new_pattern: str) -> None:
    """
    Массово переименовывает файлы в директории, заменяя old_pattern на new_pattern.
    Работает рекурсивно по подпапкам.
    """
    directory = Path(dir_path)

    if not directory.exists() or not directory.is_dir():
        print(f"❌ Ошибка: некорректный путь — {dir_path}")
        return

    for root, _, files in os.walk(directory):
        for filename in files:
            if old_pattern in filename:
                old_path = Path(root) / filename
                new_filename = filename.replace(old_pattern, new_pattern)
                new_path = Path(root) / new_filename

                # Защита от перезаписи
                if new_path.exists():
                    stem = new_path.stem
                    suffix = new_path.suffix
                    counter = 1
                    while new_path.exists():
                        new_path = new_path.parent / f"{stem}_{counter}{suffix}"
                        counter += 1

                try:
                    old_path.rename(new_path)
                    print(f"✅ Переименован: {old_path.name} → {new_path.name}")
                except Exception as e:
                    print(f"❌ Ошибка при переименовании {old_path.name}: {e}")


def archive_old_files(dir_path: str, day_threshold: int = 30, archive_format: str = "zip") -> None:
    """
    Архивирует файлы, которые не изменялись дольше day_threshold дней.
    Архивы создаются в той же директории с именем archive_YYYY-MM-DD.zip.
    """
    directory = Path(dir_path)

    if not directory.exists() or not directory.is_dir():
        print(f"❌ Ошибка: некорректный путь — {dir_path}")
        return

    cutoff_date = datetime.now() - timedelta(days=day_threshold)
    files_to_archive = []

    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = Path(root) / filename
            # Пропускаем уже созданные архивы, чтобы не зациклиться
            if file_path.suffix.lower() in [".zip", ".tar", ".gz"]:
                continue

            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    files_to_archive.append(file_path)
            except Exception as e:
                print(f"⚠️ Не удалось получить дату изменения для {file_path}: {e}")

    if not files_to_archive:
        print("⚠️ Нет файлов старше указанного порога для архивации.")
        return

    archive_name = f"archive_{datetime.now().strftime('%Y-%m-%d')}.{archive_format}"
    archive_path = directory / archive_name

    try:
        if archive_format == "zip":
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files_to_archive:
                    # Сохраняем относительный путь внутри архива
                    arcname = file_path.relative_to(directory)
                    zipf.write(file_path, arcname)
                    print(f"📦 Добавлен в архив: {arcname}")
        else:
            print(f"⚠️ Формат архива '{archive_format}' не поддерживается в этой версии.")
            return

        print(f"✅ Архив успешно создан: {archive_path}")
    except Exception as e:
        print(f"❌ Ошибка при создании архива: {e}")


# --- Пример использования ---
if __name__ == "__main__":
    target_dir = "files"  # Укажите путь к вашей папке

    # 1. Сортировка по расширениям
    sort_files_by_extension(target_dir)

    # 2. Массовое переименование (например, IMG_ → Vacation_Photo_)
    rename_files(target_dir, old_pattern="IMG_", new_pattern="Vacation_Photo_")

    # 3. Архивация файлов старше 30 дней
    archive_old_files(target_dir, day_threshold=30, archive_format="zip")

# import os
# from pathlib import Path
# import shutil

# def sort_files_by_extension(dir_path):
#     """
#     Сортирует файлы в указанной директории по расширению файла
    
#     Args: dir_path (str) - путь до директории для сортировки
#     """
#     directory = Path(dir_path)

#     if not directory:
#         print("Ошибка пути к папке")
#         return

#     if not directory.is_dir():
#         print(f"Путь {dir_path} должен быть до папки")
#         return

#     items = directory.iterdir()

#     if len(list(items)) == 0:  # оборачиваем в list(), чтобы посчитать длину
#         print("Папка пустая")
#         return

#     # Цикл должен быть ВНУТРИ функции, с отступом
#     for item in items:
#         if item.is_file():
#             # получаем расширение файла
#             ext = item.suffix.lower()[1:]
#             if not ext:
#                 ext = "no_extension"
            
#             # Создаем папку для этого расширения
#             target_folder = directory / ext    
#             target_folder.mkdir(exist_ok=True) 
            
#             # Формируем путь назначения
#             destination = target_folder / item.name 
#             orig_destination = destination
#             counter = 1

#             # Проверяем, не существует ли уже такой файл (избегаем перезаписи)
#             while destination.exists():
#                 stem = orig_destination.stem
#                 suffix = orig_destination.suffix
#                 destination = orig_destination.parent / f"{stem}_{counter}{suffix}"
#                 counter += 1

#             # Перемещаем файл
#             shutil.move(str(item), str(destination))

# # Вызов функции
# sort_files_by_extension("files")




