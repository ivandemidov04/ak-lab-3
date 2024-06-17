import os
import sys

from machine.cpu import DataPath, ControlUnit

def start(first_instr, code, data, input_tokens):
    dp = DataPath(data, [1, 2])
    cu = ControlUnit(first_instr, code, dp, input_tokens)
    # print(first_instr)
    # print(code)
    # print(data)
    # print(input_tokens)
    # return ""
    result_string = cu.execute()
    return result_string

def get_tokens(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        input_string = f.readline()

    input_tokens = []

    for char in input_string:
        input_tokens.append(char)
    input_tokens.append("")
    return input_tokens

def main(code_file, input_file):
    input_tokens = get_tokens(input_file)
    code_for_json, data_for_json = [], []

    with open(code_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i in range(len(lines)-53):
            code_for_json.append(lines[i])
        for i in range(len(lines)-53, len(lines)-1):
            data_for_json.append(lines[i])

    ind = code_for_json[0].index(':')
    first_instr = int(code_for_json[0][ind+2:len(code_for_json[0])-3])
    del code_for_json[0]

    code = []
    for i in range(len(code_for_json)):
        line = code_for_json[i]
        ind = line.find('opcode')
        line = line[ind+10:len(line)-3]
        ind = line.find('\"')
        tmp = []
        tmp.append(line[:ind])
        line = line[ind+1:]
        if len(line) > 0:
            ind = line.find('arg')
            line = line[ind+6:len(line)]
            if len(line) >= 3 and line[0] == "\"":
                line = line[1:len(line)-1]
            if line.isnumeric():
                line = int(line)
            tmp.append(line)
        code.append(tmp)

    data = []
    for i in range(len(data_for_json)):
        line = data_for_json[i]
        ind = line.find('data')
        line = line[ind+8:len(line)-4]
        if line.isnumeric():
            line = int(line)
        elif not(line == '\\u0000'):
            line = line[1:len(line)-1]
        data.append(line)

    result_string = start(first_instr, code, data, input_tokens)
    print(result_string)

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: cpu.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    with open("processor.txt", 'w') as f:
        f.write('')

    main(code_file, input_file)
