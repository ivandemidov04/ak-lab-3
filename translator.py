import json
import sys

from machine.isa import Opcode

commands_with_labels = [Opcode.JMP, Opcode.JGE, Opcode.JZ, Opcode.JNZ, Opcode.CALL]

def divide_and_delete_comments(code):
    instr, data = [], []
    section = ""
    for i in range(0, len(code)):
        line = code[i]
        if ";" in line:
            index = line.index(';')
            line = line[0:index]
        line = line.strip()

        if len(line) == 0:
            continue

        if line[0:7] == "section":
            words = line.split()
            section = words[1]

        if section == ".data":
            data.append(line)
        else:
            instr.append(line)

    return instr, data


def work_with_labels(instr, data):
    res_instr, res_data = [], []
    label_instr, label_data = {}, {}

    cnt = 0
    for i in range(1, len(instr)):
        line = instr[i]
        if ":" in line:
            index = line.index(':')
            label = line[0:index]
            label_instr[label] = cnt
        else:
            res_instr.append(line)
            cnt += 1

    tmp_data = []
    for i in range(1, len(data)):
        line = data[i]
        if ":" in line:
            tmp_data.append(line)
            continue

        if line.isnumeric():
            tmp_data.append(line)
        else:
            for j in range(1, len(line)-1):
                letter = line[j]
                tmp_data.append('\'' + letter + '\'')
            tmp_data.append('\0')
    data = tmp_data

    cnt = 0
    for i in range(len(data)):
        line = data[i]
        if ":" in line:
            index = line.index(':')
            label = line[0:index]
            label_data[label] = cnt
        else:
            res_data.append(line)
            cnt += 1

    return res_instr, res_data, label_instr, label_data


def write_instr(target, instr, data, label_instr, label_data):
    buf = [json.dumps({"_start": label_instr["_start"]})]
    with open(target, "w") as f:
        for i in range(len(instr)):
            line = instr[i]
            words = line.split()
            if len(words) == 1:
                buf.append(json.dumps({"index": i, "opcode": words[0]}))
            else:
                res = words[1]
                if words[0] == Opcode.IN or words[0] == Opcode.OUT:
                    res = int(res)
                elif res[0] == '#':
                    res = res
                    # res = int(res[1:])
                elif res[0] == '*':
                    if res[len(res) - 1] == '+':
                        ind = label_data[res[1:len(res) - 1]]
                        res = '*' + data[ind] + '+'
                    else:
                        ind = label_data[res[1:]]
                        res = '*' + data[ind]
                else:
                    if words[0] in commands_with_labels:
                        res = int(label_instr.get(res))
                    else:
                        res = label_data.get(res)
                buf.append(json.dumps({"index": i, "opcode": words[0], "arg": res}))
        f.write("[" + ",\n ".join(buf) + "]\n")

def write_data(target, data):
    buf = []
    with open(target, "a") as f:
        for i in range(len(data)):
            buf.append(json.dumps({"index": i, "data": data[i]}))
        for i in range(len(data), 53):
            buf.append(json.dumps({"index": i, "data": "0"}))
        f.write("[" + ",\n ".join(buf) + "]")

def main(code, target):
    with open(code, "r") as f:
        code = f.readlines()

    instr, data = divide_and_delete_comments(code)

    instr, data, label_instr, label_data = work_with_labels(instr, data)

    write_instr(target, instr, data, label_instr, label_data)
    write_data(target, data)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
