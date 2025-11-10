import argparse
import sys
import os
import requests
import json
import subprocess

class CargoAnalyzer:
    def __init__(self):
        self.visited_packages = set()
        
    def get_cargo_toml_from_github(self, repo_url, package, version):
        """Получить Cargo.toml из GitHub репозитория"""
        try:
            if 'github.com' in repo_url:
                raw_url = repo_url.replace('github.com', 'raw.githubusercontent.com')
                if raw_url.endswith('.git'):
                    raw_url = raw_url[:-4]
                
                branch = version if version != 'latest' else 'main'
                cargo_url = f"{raw_url}/{branch}/Cargo.toml"
            else:
                print(f"Ошибка: неподдерживаемый репозиторий {repo_url}")
                return None
            
            response = requests.get(cargo_url)
            return response.text if response.status_code == 200 else None
            
        except Exception as e:
            print(f"Ошибка при получении Cargo.toml: {e}")
            return None

    def parse_cargo_toml(self, content, current_package):
        """Парсим зависимости из Cargo.toml"""
        dependencies = []
        
        try:
            lines = content.split('\n')
            in_dependencies_section = False
            
            for line in lines:
                line = line.strip()
                
                if line == '[dependencies]':
                    in_dependencies_section = True
                    continue
                elif line.startswith('[') and in_dependencies_section:
                    break
                
                if in_dependencies_section and line and not line.startswith('#'):
                    line = line.split('#')[0].strip()
                    if line:
                        dep_name = line.split('=')[0].strip()
                        if dep_name and dep_name != current_package:
                            dependencies.append(dep_name)
                            
        except Exception as e:
            print(f"Ошибка парсинга Cargo.toml: {e}")
        
        return dependencies

    def get_dependency_tree(self, package, repo_url, version, max_depth, current_depth=0):
        """Рекурсивно получаем дерево зависимостей"""
        if current_depth > max_depth or package in self.visited_packages:
            return {}
            
        self.visited_packages.add(package)
        
        print(f"Анализируем {package} (глубина {current_depth})")
        cargo_content = self.get_cargo_toml_from_github(repo_url, package, version)
        
        if not cargo_content:
            return {package: {}}
        
        dependencies = self.parse_cargo_toml(cargo_content, package)
        tree = {package: {}}
        
        for dep in dependencies:
            # Для демонстрации используем те же URL для зависимостей
            dep_repo_url = f"https://github.com/rust-lang/{dep}"
            tree[package][dep] = self.get_dependency_tree(
                dep, dep_repo_url, version, max_depth, current_depth + 1
            )
        
        return tree

    def generate_plantuml(self, dependency_tree, output_file, package_filter):
        """Генерируем PlantUML код и сохраняем как PNG"""
        plantuml_code = ["@startuml"]
        plantuml_code.append("skinparam monochrome true")
        plantuml_code.append("skinparam shadowing false")
        plantuml_code.append("left to right direction")
        
        def add_relationships(tree, parent=None):
            for package, deps in tree.items():
                # Применяем фильтр если указан
                if package_filter and package_filter.lower() not in package.lower():
                    continue
                    
                if parent:
                    plantuml_code.append(f'"{parent}" --> "{package}"')
                
                if deps:
                    for dep_name, sub_deps in deps.items():
                        if package_filter and package_filter.lower() not in dep_name.lower():
                            continue
                        add_relationships({dep_name: sub_deps}, package)
        
        add_relationships(dependency_tree)
        plantuml_code.append("@enduml")
        
        # Сохраняем PlantUML код
        plantuml_text = '\n'.join(plantuml_code)
        with open('graph.puml', 'w', encoding='utf-8') as f:
            f.write(plantuml_text)
        
        # Конвертируем в PNG используя PlantUML онлайн сервер
        try:
            import urllib.parse
            encoded = urllib.parse.quote(plantuml_text)
            url = f"http://www.plantuml.com/plantuml/png/~1{encoded}"
            
            response = requests.get(url)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"Граф сохранен как: {output_file}")
            else:
                print("Ошибка генерации PNG")
        except Exception as e:
            print(f"Ошибка при создании PNG: {e}")
            print("PlantUML код сохранен в graph.puml")

def main():
    parser = argparse.ArgumentParser(description='Визуализатор зависимостей Rust')
    
    parser.add_argument('--package', required=True, help='Имя пакета')
    parser.add_argument('--repo-url', required=True, help='URL репозитория')
    parser.add_argument('--version', default='latest', help='Версия пакета')
    parser.add_argument('--output', default='dependency_graph.png', help='Файл для графа')
    parser.add_argument('--max-depth', type=int, default=3, help='Глубина анализа')
    parser.add_argument('--filter', default='', help='Фильтр пакетов')
    
    args = parser.parse_args()
    
    analyzer = CargoAnalyzer()
    
    print(f"Анализируем пакет: {args.package}")
    print(f"Версия: {args.version}")
    print(f"Глубина: {args.max_depth}")
    
    # Получаем дерево зависимостей
    dependency_tree = analyzer.get_dependency_tree(
        args.package, args.repo_url, args.version, args.max_depth
    )
    
    # Генерируем визуализацию
    analyzer.generate_plantuml(dependency_tree, args.output, args.filter)
    
    print("\nПримеры для тестирования:")
    print("1. python cargo_analyzer.py --package serde --repo-url https://github.com/serde-rs/serde --max-depth 2")
    print("2. python cargo_analyzer.py --package tokio --repo-url https://github.com/tokio-rs/tokio --max-depth 2")
    print("3. python cargo_analyzer.py --package reqwest --repo-url https://github.com/seanmonstar/reqwest --max-depth 2")

if __name__ == "__main__":
    main()
