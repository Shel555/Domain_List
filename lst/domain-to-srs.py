#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для конвертации файла с доменами в формат sing-box ruleset (.srs)
Открывает диалоговое окно для выбора файла, создает JSON и компилирует в .srs
Результат сохраняется в той же папке, что и исходный файл
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import subprocess
from pathlib import Path

def select_file_and_process():
    """
    Функция для выбора файла через диалоговое окно и обработки доменов
    """
    # Создаем корневое окно tkinter (скрываем его)
    root = tk.Tk()
    root.withdraw()
    
    # Открываем диалог выбора файла
    file_path = filedialog.askopenfilename(
        title="Выберите файл с доменами",
        filetypes=[
            ("Файлы списков", "*.lst"),
            ("Текстовые файлы", "*.txt"),
            ("Все файлы", "*.*")
        ]
    )
    
    if not file_path:
        print("Файл не выбран")
        return
    
    # Получаем информацию о файле
    input_file = Path(file_path)
    input_directory = input_file.parent
    base_name = input_file.stem
    
    print(f"Обрабатываем файл: {file_path}")
    
    # Читаем домены из файла
    domains = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                domain = line.strip()
                if domain and not domain.startswith('#'):  # Пропускаем пустые строки и комментарии
                    domains.append(domain)
    except Exception as e:
        error_msg = f"Ошибка при чтении файла: {e}"
        print(error_msg)
        messagebox.showerror("Ошибка", error_msg)
        return
    
    if not domains:
        error_msg = "В файле не найдено ни одного домена"
        print(error_msg)
        messagebox.showwarning("Предупреждение", error_msg)
        return
    
    print(f"Найдено доменов: {len(domains)}")
    
    # Создаем структуру JSON для sing-box ruleset
    data = {
        "version": 3,
        "rules": [
            {
                "domain_suffix": domains
            }
        ]
    }
    
    # Пути для выходных файлов в той же папке, что и исходный файл
    json_file_path = input_directory / f"{base_name}.json"
    srs_file_path = input_directory / f"{base_name}.srs"
    
    try:
        # Сохраняем JSON файл
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"JSON файл создан: {json_file_path}")
        
        # Компилируем в .srs формат
        result = subprocess.run(
            ["sing-box", "rule-set", "compile", str(json_file_path), "-o", str(srs_file_path)], 
            check=True,
            capture_output=True,
            text=True
        )
        
        success_msg = f"Успешно создан SRS файл: {srs_file_path}"
        print(success_msg)
        messagebox.showinfo("Успех", success_msg)
        
        # Опционально удаляем промежуточный JSON файл
        # json_file_path.unlink()
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Ошибка компиляции sing-box:\n{e.stderr}"
        print(f"Ошибка компиляции: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        messagebox.showerror("Ошибка компиляции", error_msg)
    except FileNotFoundError:
        error_msg = "sing-box не найден в PATH. Убедитесь, что sing-box установлен и доступен."
        print(error_msg)
        messagebox.showerror("Ошибка", error_msg)
    except Exception as e:
        error_msg = f"Ошибка при обработке файлов: {e}"
        print(error_msg)
        messagebox.showerror("Ошибка", error_msg)

def main():
    """
    Основная функция программы
    """
    print("Конвертер доменов в sing-box ruleset (.srs)")
    print("=" * 45)
    
    try:
        select_file_and_process()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        messagebox.showerror("Критическая ошибка", str(e))

if __name__ == "__main__":
    main()