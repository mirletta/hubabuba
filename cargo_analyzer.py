import argparse
import sys
import os
import requests
import json

def get_cargo_toml_from_github(repo_url, package, version):
    """Получить Cargo.toml из GitHub репозитория"""
    try:
        # Преобразуем URL в raw-формат
        if 'github.com' in repo_url:
            # Меняем обычный URL на raw.githubusercontent.com
            raw_url = repo_url.replace('github.com', 'raw.githubusercontent.com')
            if raw_url.endswith('.git'):
                raw_url = raw_url[:-4]
            
            # Для версии используем ветку или тег
            branch = version if version != 'latest' else 'main'
            cargo_url = f"{raw_url}/{branch}/Cargo.toml"
        else:
            print(f"Ошибка: неподдерживаемый репозиторий {repo_url}")
            return None
        
        print(f"Загружаем Cargo.toml из: {cargo_url}")
        response = requests.get(cargo_url)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка загрузки: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении Cargo.toml: {e}")
        return None

def parse_cargo_toml(content):
    """Парсим зависимости из Cargo.toml"""
    dependencies = []
    
    try:
        lines = content.split('\n')
        in_dependencies_section = False
        
        for line in lines:
            line = line.strip()
            
            # Находим секцию зависимостей
            if line == '[dependencies]':
                in_dependencies_section = True
                continue
            elif line.startswith('[') and in_dependencies_section:
                # Конец секции зависимостей
                break
            
            # Парсим зависимости в секции
            if in_dependencies_section and line and not line.startswith('#'):
                # Убираем комментарии
                line = line.split('#')[0].strip()
                if line:
                    # Берем имя пакета до первого пробела или =
                    dep_name = line.split('=')[0].strip()
                    if dep_name:
                        dependencies.append(dep_name)
                        
    except Exception as e:
        print(f"Ошибка парсинга Cargo.toml: {e}")
    
    return dependencies

def main():
    parser = argparse.ArgumentParser(description='Анализатор зависимостей Rust')
    
    # Основные параметры
    parser.add_argument('--package', required=True, help='Имя пакета')
    parser.add_argument('--repo-url', required=True, help='URL репозитория')
    parser.add_argument('--version', default='latest', help='Версия пакета')
    parser.add_argument('--output', default='graph.png', help='Файл для графа')
    
    args = parser.parse_args()
    
    # Проверяем ошибки
    if not args.package.strip():
        print("Ошибка: имя пакета пустое")
        sys.exit(1)
    
    print(f"Анализируем пакет: {args.package}")
    print(f"Версия: {args.version}")
    print(f"Репозиторий: {args.repo_url}")
    
    # Получаем Cargo.toml
    cargo_content = get_cargo_toml_from_github(args.repo_url, args.package, args.version)
    
    if not cargo_content:
        print("Не удалось получить Cargo.toml")
        sys.exit(1)
    
    # Парсим зависимости
    dependencies = parse_cargo_toml(cargo_content)
    
    # Выводим зависимости
    print("\nПрямые зависимости:")
    if dependencies:
        for dep in dependencies:
            print(f"  - {dep}")
    else:
        print("  Зависимости не найдены")

if __name__ == "__main__":
    main()
