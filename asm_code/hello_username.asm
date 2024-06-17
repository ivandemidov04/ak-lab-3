section .data

ptr:
    0

welcome_ptr:                ; начало строки welcome ; 1ая ячейка памяти по факту
    2

welcome:
    "What's your name?"     ; длина строки с 0-терминатором = 18 ; 0-терминатор в 19ой ячейке

hello_ptr:                  ; 20ая ячейка по факту
    22

name_ptr:                   ; 21ая ячейка по факту
    29

hello:
    "Hello, "               ; длина строки с 0-терминатором = 8 ; 0-терминатор в 29ой ячейке

section .code

input:
    in 1
    store *ptr+             ; сохраняем в память очередной символ, устанавливаем указатель на следующий символ
    cmp #'\x00'
    jnz input               ; если последний введенный символ - не 0-терминатор, то продолжаем читать данные
    ret

print:
    load *ptr+              ; загружаем в аккумулятор очередной символ, устанавливаем указатель на следующий символ
    out 2
    cmp #'\x00'             ; проверяем, является ли только что напечатанный символ 0-терминатором
    jnz print               ; если нет, то печатаем следующий символ
    ret

_start:
    load welcome_ptr
    store ptr
    call print

    load name_ptr
    store ptr
    call input

    load hello_ptr
    store ptr
    call print

    halt
