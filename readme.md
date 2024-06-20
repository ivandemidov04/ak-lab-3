# Лабораторная работа №3 по АК

- Демидов Иван Алексеевич P3207
- Вариант: `asm | acc | harv | hw | instr | struct | trap -> stream | port | cstr | prob2 | spi`
- Упрощенный вариант: `asm | acc | harv | hw | instr | struct | stream | port | cstr | prob2`

## Язык программирования - Assembly
```
program ::= { line }

line ::= section_declaration "\n"
       | label [ comment ] "\n"
       | instr [ comment ] "\n"
       | [ comment ] "\n"
       
section_declaration ::= "section" section_type

section_type ::= ".data"
               | ".code"

label ::= label_name ":"

instr ::= op0
        | op1 integer
        | op1 char
        | op1 address
        | op1 value_name
        | op2 arg
        | op3 label_name

op0 ::= "halt"
      | "inc"
      | "dec"
      | "push"
      | "pop"
      | "ret"

op1 ::= "load"
      | "store"
      | "add"
      | "sub"
      | "mul"
      | "div"
      | "mod"
      | "cmp"
      
op2 ::= "in"
      | "out"

op3 ::= "jmp"
      | "jz"
      | "jnz"
      | "jge"
      | "call"

integer ::= [ "-" ] { <any of "0-9"> }-

char ::= '<"a-z A-z">'

address ::= <any of *> { <any of "0-9"> }

arg ::= <any of "0-9">

value_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

comment ::= ";" <any symbols except "\n">
```

## Система команд

**Операции:**

`halt` - остановить процессор

_Операции с памятью:_
- `load` - загружает в аккумулятор указанное в аргументе число или значение из указанной ячейки памяти
- `store` - сохраняет в память значение из аккумулятора по указанной ячейке памяти

_Арифметические операции (результат записывается в аккумулятор):_
- `add` - произвести сложение аккумулятора с указанным числом или значением из указанной ячейки памяти
- `sub` - произвести вычитание указанного числа или значения из указанной ячейки памяти из аккумулятора
- `mul` - произвести умножение аккумулятора на указанное число или значение из указанной ячейки памяти
- `div` - произвести деление аккумулятора на указанное число или значение из указанной ячейки памяти
- `mod` - вычисление остатка от деления аккумулятора на указанное число или значение из указанной ячейки памяти
- `cmp` - установить флаги по вычитанию указанного числа или значения из указанной ячейки памяти из аккумулятора
- `inc` - инкремент аккумулятора
- `dec` - декремент аккумулятора

_Инструкции перехода_:
- `jmp` - безусловный переход на метку
- `jz` - переход на метку, если флаг 'Z' равен 1. Переход, если равно
- `jnz` - переход на метку, если флаг 'Z' равен 0. Переход, если не равно
- `jge` - переход на метку, если флаг 'N' равен 0. Переход, если больше или равно

_Инструкции подпрограмм_:
- `call` - переход на подпрограмму. Добавление в стек адреса возврата из подпрограммы
- `ret` - возврат из подпрограммы. Восстановление IP из стека

_Операции со стеком:_
- `push` - записать в стек значение аккумулятора
- `pop` - записать в аккумулятор значение из вершины стека

_Операции ввода-вывода:_
- `in` - записать данные из аккумулятора в порт устройства
- `out` - записать данные из порта устройства в аккумулятор

**Машинные инструкции:**

- Машинный код сериализуется в список JSON.
- Один элемент списка - одна инструкция или одна ячейка памяти данных.
- Индекс списка - адрес инструкции или ячейки памяти данных (зависит от "opcode").
- В начале списка инструкций хранится строка с индексом входа в программу (ключ "_start").
```
 [{
    "_start": 20
 },
 {
    "index": 0, 
    "opcode": "store", 
    "arg": "*2"
 },
 ...]
 [{
   "index": 0,
   "data": "1"
 },
 ...]
```
- index - адрес инструкции
- opcode - строка с кодом операции;
- arg - аргумент (может отсутствовать);

Все инструкции описаны в файле [isa.py](https://github.com/ivandemidov04/ak-lab-3/blob/main/machine/isa.py) в классе `Opcode`.

## Организация памяти

Модель памяти процессора:
1. Память команд и данных разделены (Гарвардская архитектура).
2. Программист может обращаться только к памяти данных, однако инструкции перехода и call в некотором смысле позволяют взаимодействовать с памятью инструкций.
3. Память команд. Машинное слово - не определено. Реализуется списком словарей, описывающих инструкции (одно слово - одна ячейка).
4. Память данных. Машинное слово - 4 байта, знаковое. Реализуется списком чисел.
5. Система команд выстроена вокруг аккумулятора (ACC), поэтому программисту доступен только этот регистр.
6. Для реализации подпрограмм присутствует указатель стека (SP), который указывает на конец памяти данных.

**Адресация:**

Операции с памятью и арифметические операции поддерживают 4 типа адресации. 
1. <ins>Прямая загрузка</ins>: **instr #10**. Значением выступает просто константа, указанная в 
аргументе инструкции. Можно указать символ в одинарных кавычках (актуально для load). Его код будет
использоваться в качестве значения. Инструкция "store" не поддерживает прямую загрузку.
   - **load #10** - загружает в аккумулятор число 10.
   - **load #'H'** - загружает в аккумулятор код символа 'H' - 72.
   - **add #10** - производит сложение аккумулятора с числом 10.
2. <ins>Абсолютная адресация</ins>: **instr 10**. Значением выступает содержимое из ячейки памяти, 
указанной после символа \*.
   - **load 10** - загружает в аккумулятор значение из 10-ой ячейки памяти. 
   - **add 10** - производит сложение аккумулятора со значением из 10-ой ячейки.
3. <ins>Косвенная адресация</ins>: **instr \*10**. Значением выступает содержимое ячейки памяти, 
указатель которой лежит в другой ячейке, указанная после звездочки.
   - **load \*10** - загружает в аккумулятор значение из ячейки памяти, указатель которой 
    находится в ячейке 10. 
   - **add \*10** - производит сложение аккумулятора со значением из ячейки памяти, указатель которой 
    находится в ячейке 10. 
4. <ins>Косвенная автоинкрементая адресация</ins>: **instr \*10+**. Работает также, как и косвенная 
адресация, но после получения содержимого ячейки инкрементирует указатель, лежащий в указанной в аргументе 
ячейке. Используется для реализации автоматического указателя.
   - **load \*10+** - загружает в аккумулятор значение из ячейки памяти, указатель которой 
   находится в ячейке 10, инкрементируя указатель в 10-ой ячейке. 
   - **add \*10+** - производит сложение аккумулятора со значением из ячейки памяти, указатель которой 
   находится в ячейке 10, инкрементируя указатель в 10-ой ячейке.

## Набор инструкций

| Инструкция | Кол-во тактов | Мнемоника            |
|------------|:-------------:|----------------------|
| halt       |       0       | Остановка процессора |

**Операции с памятью**

| Инструкция |       Адресация       | Кол-во тактов | Мнемоника                                                   |
|------------|:---------------------:|:-------------:|-------------------------------------------------------------|
| load       |    Прямая загрузка    |       1       | ARG -> ACC                                                  |
| load       |      Абсолютная       |       2       | ARG -> ADDR; MEM -> ACC                                     | 
| load       |       Косвенная       |       3       | ARG -> ADDR; MEM -> ADDR; MEM -> ACC                        |
| load       |  Косвенная автоинкр.  |       4       | ARG -> ADDR; MEM + 1 -> BR, MEM; BR - 1 -> ADDR; MEM -> ACC |
| store      |      Абсолютная       |       2       | ARG -> ADDR; ACC -> MEM                                     | 
| store      |       Косвенная       |       3       | ARG -> ADDR; MEM -> ADDR; ACC -> MEM                        |
| store      |  Косвенная автоинкр.  |       4       | ARG -> ADDR; MEM + 1 -> BR, MEM; BR - 1 -> ADDR; ACC -> MEM |

**Арифметические операции**

| Инструкция |    Адресация    | Кол-во тактов | Мнемоника                     |
|------------|:---------------:|:-------------:|-------------------------------|
| add        | Прямая загрузка |       1       | ACC + ARG -> ACC              |
| sub        | Прямая загрузка |       1       | ACC - ARG -> ACC              |
| mul        | Прямая загрузка |       1       | ACC * ARG -> ACC              |
| div        | Прямая загрузка |       1       | ACC / ARG -> ACC              |
| mod        | Прямая загрузка |       1       | ACC % ARG -> ACC              |
| cmp        | Прямая загрузка |       1       | Установить флаги по ACC - ARG |
| inc        |        -        |       1       | ACC + 1 -> ACC                |
| dec        |        -        |       1       | ACC - 1 -> ACC                |

| Инструкция |      Адресация      | Кол-во тактов | Мнемоника                                                         |
|------------|:-------------------:|:-------------:|-------------------------------------------------------------------|
| add        |       Прямая        |       1       | ACC + ARG -> ACC                                                  |
| add        |     Абсолютная      |       2       | ARG -> ADDR; ACC + MEM -> ACC                                     |
| add        |      Косвенная      |       3       | ARG -> ADDR; MEM -> ADDR; ACC + MEM -> ACC                        |
| add        | Косвенная автоинкр. |       4       | ARG -> ADDR; MEM + 1 -> BR, MEM; BR - 1 -> ADDR; ACC + MEM -> ACC |

Аналогично с другими арифметическими операциями, кроме inc и dec

**Инструкции перехода**

| Инструкция | Кол-во тактов | Мнемоника          |
|------------|:-------------:|--------------------|
| jmp        |       1       | ARG -> IP          |
| je         |       1       | if Z==1: ARG -> IP |
| jne        |       1       | if Z==0: ARG -> IP |
| jge        |       1       | if N==0: ARG -> IP |

**Операции со стеком:**

| Инструкция | Кол-во тактов | Мнемоника                            |
|------------|:-------------:|--------------------------------------|
| push       |       3       | SP -> ADDR; ACC -> MEM; SP - 1 -> SP |
| pop        |       2       | SP + 1 -> SP, ADDR; MEM -> ACC       |

**Операции ввода-вывода:**

- P(A) - порт с адресом A, где A - аргумент инструкции

| Инструкция | Кол-во тактов | Мнемоника   |
|------------|:-------------:|-------------|
| in         |       1       | P(A) -> ACC |
| out        |       1       | ACC -> P(A) |


## Транслятор

Интерфейс командной строки: translator.py <input_file> <instruction_file>

Реализовано в модуле: [translator.py](https://github.com/ivandemidov04/ak-lab-3/blob/main/translator.py)

Алгоритм трансляции:
1. Удаление комментариев и пустых строк.
2. Разделение памяти инструкций и памяти данных. Если в памяти данных присутствуют строки, то они разбиваются посимвольно. В одной ячейке лежит один символ. После последнего символа строки записывается 0-терминатор.
3. Замещение меток реальными адресами инструкций или данных.
4. Сохранение данных в формате JSON. Сначала идет память команд с ключами index, opcode, arg. Самое первое значение - точка входа в программу (_start). После памяти команд идет память данных с ключами index, data (адрес ячейки памяти и значение, которое в ней хранится, соответственно).

## Модель процессора

Интерфейс командной строки: machine.py <machine_code_file> <input_file>

### ControlUnit

![control_unit](https://github.com/ivandemidov04/ak-lab-3/blob/main/control_unit.png)

Реализован в классе ```ControlUnit``` в модуле [cpu.py](https://github.com/ivandemidov04/ak-lab-3/blob/main/machine/cpu.py).

Hardwired (реализовано полностью на Python).
- Цикл симуляции осуществляется в метод ```execute```.
- В методе ```execute``` вызываются методы класса ```Decoder```, формирующие управляющие сигналы и данные в DataPath и выполняющие инструкции процессора. Класс ```Decoder``` реализован в модуле
[decoder.py](https://github.com/ivandemidov04/ak-lab-3/blob/main/machine/decoder.py).
- Отсчет времени работы ведется в тактах. После каждой инструкции в поток ошибок добавляется информация о состоянии процессора. Состояние процессора показывает:
    - время в тактах
    - текущую инструкцию
    - значения регистров
    - флаги

### DataPath

![datapath](https://github.com/ivandemidov04/ak-lab-3/blob/main/datapath.png)

Реализован в классе ```DataPath``` в модуле [cpu.py](https://github.com/ivandemidov04/ak-lab-3/blob/main/machine/cpu.py).

- Управляющие сигналы и данные на шинах поступают с декодера

**Сигналы**

Все сигналы хранятся в модуле [machine_signals.py](https://github.com/ivandemidov04/ak-lab-3/blob/main/machine/machine_signals.py)
- ```signal_latch_acc/buf/stack/address```. Защелкивают значения с шин в регистры.
- ```sel_acc/address``` - сигналы на соответствующие мультиплексоры. Выбирают либо пропустить значения с шин из декодера или из ```alu_out```.
- ```operation``` - выбор математической операции для АЛУ. Операция происходит в методе ```alu_working```, а выбор операции в ```execute_alu_operation```.
- ```valves``` - вентили на шинах данных из регистров и из памяти. Для совершения математической операции или просто для пропуска данных через АЛУ нужно открыть соответствующие вентили. Получение данных с шин реализуется в методе ```get_bus_value```. Названия вентелей хранятся в том же модули, что и сигналы в классе ```Operands```.
- ```read/write``` - сигналы для чтения и записи данных в память соответственно. Данные читаются/записыватся из ячейки, указанной в адресном регистре. Реализуется в методе ```memory_manager```.

**Шины**
- Есть две входных шин данных, которые приходят с декодера:
  - ```load_acc```. Используется для прямой загрузки в аккумулятор.
  - ```load_address```. Загружает значение ячейки памяти, указанной в аргументе инструкции.
- И две выходных шин:
  - ```alu_out```. В ControlUnit называется ```data```
  - ```flags```. По значению флагов происходят условные переходы. Поступают на декодер.

**Флаги**

- устанавливаются по значению аккумулятора или после инструкции ```cmp```.
- Флаг ```Z``` (zero) - устанавливается в 1, если в аккумуляторе 0 или результат cmp равен 0.
- Флаг ```N``` (negative) - устанавливается в 1, если в аккумуляторе отрицательное число или результат cmp \- отрицательный.

## Тестирование

Тестирование выполняется при помощи golden test-ов в формате yaml. Файлы .yml лежат в папке [golden](https://github.com/ivandemidov04/ak-lab-3/blob/main/golden). Тесты содержат входные данные и проверку на
- код программы
- машинный код
- вывод процессора
- журнал работы процессора

**Алгоритмы и их тесты**

- ```hello.asm``` - [hello_asm.yml](https://github.com/ivandemidov04/ak-lab-3/blob/main/golden/hello_asm.yml)
- ```cat.asm``` - [cat_asm.yml](https://github.com/ivandemidov04/ak-lab-3/blob/main/golden/cat_asm.yml)
- ```hello_username.asm``` - [hello_user_name_asm.yml](https://github.com/ivandemidov04/ak-lab-3/blob/main/golden/hello_username_asm.yml)
- ```prob2.asm``` - [prob2_asm.yml](https://github.com/ivandemidov04/ak-lab-3/blob/main/golden/prob2_asm.yml)

## Аналитика алгоритмов

```
| ФИО | <алг> | <LoC> | <code инстр.> | <инстр.> | <такт.> | <вариант> |
| Демидов И.А. | hello | 26 | 10 | 60 | 139 | (asm | acc | harv | hw | instr | struct | stream | port | cstr | prob2) |
| Демидов И.А. | cat | 34 | 18 | 40 | 98 | (asm | acc | harv | hw | instr | struct | stream | port | cstr | prob2) |
| Демидов И.А. | hello_username | 50 | 21 | 152 | 354 | (asm | acc | instr | hw | instr | struct | stream | port | cstr | prob2) |
```
