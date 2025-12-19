#!/usr/bin/env python3

import subprocess
import sys
import os
import time
from pathlib import Path
import argparse


def run_tests(test_type, pattern=None):
    print(f"\n{'=' * 60}")
    print('=' * 60)

    tests_dir = Path(__file__).parent / 'tests'

    if test_type == 'unit':
        test_path = tests_dir / 'unit'
    elif test_type == 'integration':
        test_path = tests_dir / 'integration'
    elif test_type == 'system':
        test_path = tests_dir / 'system'
    elif test_type == 'all':
        test_path = tests_dir
    else:
        print(f"Неизвестный тип тестов: {test_type}")
        return False

    if not test_path.exists():
        print(f"Директория {test_path} не существует!")
        print("Создайте структуру: tests/{unit,integration,system}/")
        return False

    cmd = [
        sys.executable, '-m', 'pytest',
        str(test_path),
        '-v',  # Подробный вывод
        '--tb=short',  # Короткий traceback
    ]

    # Добавляем паттерн если указан
    if pattern:
        cmd.append('-k')
        cmd.append(pattern)

    # Запускаем тесты
    start_time = time.time()

    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        elapsed_time = time.time() - start_time

        # Выводим результат
        print(result.stdout)
        if result.stderr and "warning" not in result.stderr.lower():
            print("STDERR:", result.stderr)

        print(f"\nВремя выполнения: {elapsed_time:.2f} секунд")
        print(f"Код возврата: {result.returncode}")

        return result.returncode == 0

    except FileNotFoundError:
        print("Ошибка: pytest не найден. Установите его: pip install pytest")
        return False
    except Exception as e:
        print(f"Ошибка при запуске тестов: {e}")
        return False


def run_simple_tests():
    print(f"\n{'=' * 60}")
    print("Запуск упрощенных тестов")
    print('=' * 60)

    # Запускаем только unit и integration тесты (без system)
    test_types = ['unit', 'integration']

    results = []
    for test_type in test_types:
        print(f"\n>>> Запуск {test_type} тестов:")
        success = run_tests(test_type)
        results.append((test_type, success))
        time.sleep(1)  # Небольшая пауза между запусками

    return results


def main():

    print(" Запуск тестов Flask приложения")
    print(f"Текущая директория: {os.getcwd()}")
    print(f"Python: {sys.executable}")

    try:
        import pytest
        print(f"✓ pytest {pytest.__version__} установлен")
    except ImportError:
        print("✗ pytest не установлен. Установите: pip install pytest")
        return 1

    # Проверяем структуру папок
    tests_dir = Path('tests')
    if not tests_dir.exists():
        print("\nСоздаю структуру тестов...")
        for subdir in ['unit', 'integration', 'system']:
            (tests_dir / subdir).mkdir(parents=True, exist_ok=True)
            (tests_dir / subdir / '__init__.py').touch()
        print("Структура создана:")
        for path in tests_dir.rglob('*'):
            if path.is_dir():
                print(f"  📁 {path.relative_to(tests_dir.parent)}")

    # Создаем примеры тестов если они не существуют
    create_example_tests()

    # Парсим аргументы
    parser = argparse.ArgumentParser(description='Запуск тестов Flask приложения')
    parser.add_argument('--type', choices=['unit', 'integration', 'system', 'all', 'simple'],
                        default='simple', help='Тип тестов для запуска')
    parser.add_argument('--pattern', help='Шаблон для поиска тестовых файлов')
    parser.add_argument('--list', action='store_true', help='Показать доступные тесты')

    args = parser.parse_args()

    if args.list:
        show_available_tests()
        return 0

    # Запускаем указанный тип тестов
    if args.type == 'all':
        success = run_all_tests()
    elif args.type == 'simple':
        results = run_simple_tests()
        success = all(s for _, s in results)
    else:
        success = run_tests(args.type, args.pattern)

    return 0 if success else 1


def create_example_tests():
    test_files = {

    }

    for file_path, content in test_files.items():
        full_path = Path('tests') / file_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Создан пример теста: {full_path}")


def show_available_tests():
    print("\nДоступные тесты:")
    tests_dir = Path('tests')

    if not tests_dir.exists():
        print("Директория tests не найдена!")
        return

    for test_type in ['unit', 'integration', 'system']:
        type_dir = tests_dir / test_type
        if type_dir.exists():
            test_files = list(type_dir.glob('test_*.py'))
            if test_files:
                print(f"\n{test_type.upper()} тесты:")
                for test_file in test_files:
                    print(f"  📄 {test_file.name}")
                    # Показываем тестовые функции
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Ищем функции с test_
                            import re
                            test_funcs = re.findall(r'def (test_\w+)', content)
                            test_classes = re.findall(r'class (Test\w+)', content)
                            for func in test_funcs:
                                print(f"      → {func}()")
                            for cls in test_classes:
                                print(f"      → {cls} (класс)")
                    except:
                        pass
            else:
                print(f"\n{test_type.upper()} тесты: нет файлов тестов")


def run_all_tests():
    print(f"\n{'=' * 60}")
    print("Запуск всех тестов")
    print('=' * 60)

    test_types = ['unit', 'integration', 'system']
    report = []

    for test_type in test_types:
        print(f"\n>>> Запуск {test_type} тестов:")
        success = run_tests(test_type)

        report.append({
            'type': test_type,
            'success': success,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })

        time.sleep(1)  # Пауза между запусками

    # Выводим итоговый отчет
    print(f"\n{'=' * 60}")
    print("ИТОГОВЫЙ ОТЧЕТ")
    print('=' * 60)

    total_tests = len(report)
    passed_tests = sum(1 for r in report if r['success'])

    for r in report:
        status = 'ПРОЙДЕНО' if r['success'] else '✗ ПРОВАЛЕНО'
        print(f"{r['type'].upper():15} {status:15} {r['timestamp']}")

    print(f"\nВсего типов тестов: {total_tests}")
    print(f"Успешно пройдено: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print("\nНЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        return False


if __name__ == '__main__':
    sys.exit(main())
