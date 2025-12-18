; Тест 1: Загрузка и запись (LOAD и WRITE)
LOAD 1, 777
WRITE 1, 10

; Тест 2: Копирование (READ и WRITE)
LOAD 2, 10
READ 3, 2, 0
WRITE 3, 20

; Тест 3: АЛУ (BITREV)
LOAD 4, 1
LOAD 5, 30
WRITE 5, 0
BITREV 4, 0
