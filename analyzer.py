import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='Анализатор зависимостей')
    
    # Основные параметры
    parser.add_argument('--package', required=True, help='Имя пакета')
    
    # Репозиторий
    repo_group = parser.add_mutually_exclusive_group(required=True)
    repo_group.add_argument('--repo-url', help='URL репозитория')
    repo_group.add_argument('--repo-path', help='Путь к репозиторию')
    
    # Дополнительные настройки
    parser.add_argument('--mode', choices=['local', 'remote'], default='remote')
    parser.add_argument('--version', default='latest')
    parser.add_argument('--output', default='graph.png')
    parser.add_argument('--max-depth', type=int, default=5)
    parser.add_argument('--filter', default='')
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Проверяем ошибки
    if not args.package.strip():
        print("Ошибка: имя пакета пустое")
        sys.exit(1)
    
    if args.repo_path and not os.path.exists(args.repo_path):
        print(f"Ошибка: путь {args.repo_path} не существует")
        sys.exit(1)
    
    if args.max_depth <= 0:
        print("Ошибка: глубина должна быть > 0")
        sys.exit(1)
    
    # Показываем настройки
    print("Настройки:")
    print(f"  Пакет: {args.package}")
    print(f"  Репозиторий: {args.repo_url or args.repo_path}")
    print(f"  Режим: {args.mode}")
    print(f"  Версия: {args.version}")
    print(f"  Файл: {args.output}")
    print(f"  Глубина: {args.max_depth}")
    print(f"  Фильтр: {args.filter}")

if __name__ == "__main__":
    main()
