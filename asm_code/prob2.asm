section .data
x:
    1                   ; первое число фибоначчи
y:
    2                   ; второе число фибоначчи
z:
    0                   ; третье число фибоначчи
sum:
    2                   ; сумма четных чисел
max_value:
    4000000             ; значение, после которого нужно завершить программу

section .code

next_number:            ; функция, для нахождения нового числа фибоначчи
    load x
    add y
    store z
    load y
    store x
    load z
    store y
    ret

_start:
    call next_number
    load z

    cmp max_value       ; проверка, больше ли новое число максимального разрешенного значения
    jge end

    mod #2              ; проверка числа на четность
    jnz _start

    load sum            ; если число прошло проверку на четность, добавляем его к сумме
    add z
    store sum

    jmp _start

    end:
        halt
