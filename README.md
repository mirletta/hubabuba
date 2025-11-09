
```bash
python hello.py [--vfs <путь>] [--script <путь_к_скрипту>]
```

### Параметры

- `--vfs` — путь к виртуальной файловой системе
- `--script` — путь к стартовому скрипту

## Команды

- `ls [args]` — список файлов
- `cd [path]` — смена директории  
- `exit` — выход

## Примеры

Интерактивный режим:
```bash
python hello.py
```

С параметрами:
```bash
python hello.py --vfs /mnt/virtual --script test_script.txt
```

## Тестирование

Запустите тестовые скрипты:
- `run_test1.bat` — без параметров
- `run_test2.bat` — с VFS
- `run_test3.bat` — со скриптом
- `run_test4.bat` — все параметры
