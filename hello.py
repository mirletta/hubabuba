import shlex
import sys
import os

def execute_command(line, script_path=None):
    """Выполнить одну команду"""
    line = line.strip()
    if not line or line.startswith('#'):
        return True

    if script_path:
        print(f"vfs@{line}")

    try:
        args = shlex.split(line)
    except ValueError as e:
        print(f"Ошибка парсинга: {e}")
        return True
    
    if len(args) == 0:
        return True
    
    if args[0] == "exit":
        return False
    elif args[0] == "ls":
        print(args)
    elif args[0] == "cd":
        print(args)
    else:
        print(f"{args[0]}: command not found")
    
    return True

def run_script(script_path):
    """Выполнить стартовый скрипт"""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not execute_command(line, script_path):
                    break
    except FileNotFoundError:
        print(f"Ошибка: файл скрипта '{script_path}' не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка выполнения скрипта: {e}")
        sys.exit(1)

def main():
    vfs_path = None
    script_path = None
    
    # Обработка параметров командной строки
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--vfs' and i + 1 < len(sys.argv):
            vfs_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--script' and i + 1 < len(sys.argv):
            script_path = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Отладочный вывод параметров
    print("=== Параметры эмулятора ===")
    print(f"VFS путь: {vfs_path if vfs_path else 'не задан'}")
    print(f"Стартовый скрипт: {script_path if script_path else 'не задан'}")
    print("===========================")
    
    # Если есть стартовый скрипт, выполнить его
    if script_path:
        run_script(script_path)
    
    # REPL режим
    while True:
        try:
            cmd = input("vfs@")
            if not execute_command(cmd, script_path):
                break
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            break

if __name__ == "__main__":
    main()
