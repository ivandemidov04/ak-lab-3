import sys

from machine.decoder import Decoder
from machine.isa import Opcode
from machine.machine_signals import Operands, Signal


class DataPath:

    def __init__(self, data, ports):
        self.data_memory = data
        self.ports = ports
        self.acc = 0
        self.buf_reg = 0
        self.stack_pointer = 51
        self.address_reg = 0
        self.memory_out = 0
        self.flags = {"z": False, "n": False}
        self.alu_out = 0

    def signal_latch_acc(self, sel, load=0):
        if sel == Signal.DIRECT_ACC_LOAD:
            self.acc = load
        else:
            self.acc = self.alu_out

    def signal_latch_address(self, sel, load=0):
        if sel == Signal.DIRECT_ADDRESS_LOAD:
            self.address_reg = int(load)
        else:
            self.address_reg = int(self.alu_out)

    def memory_manager(self, operation):
        if operation == Signal.READ:
            self.memory_out = self.data_memory[self.address_reg]
        elif operation == Signal.WRITE:
            self.data_memory[self.address_reg] = self.alu_out

    def signal_latch_regs(self, *regs):
        if Signal.BUF_LATCH in regs:
            self.buf_reg = self.alu_out
        if Signal.STACK_LATCH in regs:
            self.stack_pointer = self.alu_out

    def execute_alu_operation2(self, operation, value=0):
        if operation == Opcode.ADD:
            return self.alu_out + value
        if operation == Opcode.SUB:
            return self.alu_out - value
        if operation == Opcode.MUL:
            return self.alu_out * value
        if operation == Opcode.DIV:
            return self.alu_out // value
        return None

    def execute_alu_operation(self, operation, value=0):
        if operation in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV]:
            return self.execute_alu_operation2(operation, value)
        if operation == Opcode.MOD:
            return self.alu_out % int(value)
        if operation == Opcode.INC:
            return self.alu_out + 1
        if operation == Opcode.DEC:
            return self.alu_out - 1
        if operation == Opcode.CMP:
            self.flags = {"z": self.alu_out == value or self.alu_out == "",
                          "n": self.alu_out < value
                          if isinstance(self.alu_out, int) and isinstance(value, int) else False}
            return self.alu_out
        return None

    def get_bus_value(self, bus):
        if bus == Operands.ACC:
            return self.acc
        if bus == Operands.BUF:
            return self.buf_reg
        if bus == Operands.STACK:
            return self.stack_pointer
        if bus == Operands.MEM:
            return self.memory_out
        return None

    def alu_working(self, operation, valves):
        self.alu_out = self.get_bus_value(valves[0])
        if operation in [Opcode.INC, Opcode.DEC]:
            self.alu_out = self.execute_alu_operation(operation)
        elif len(valves) > 1:
            self.alu_out = self.execute_alu_operation(operation, self.get_bus_value(valves[1]))
        if operation != Opcode.CMP and isinstance(self.alu_out, int):
            self.flags = {"z": self.alu_out == 0, "n": self.alu_out < 0}


class ControlUnit:

    def __init__(self, first_instr, instructions, data_path, input_tokens):
        self.ip = first_instr
        self.input_tokens = input_tokens
        self.instructions = instructions
        self.instr = self.instructions[0]
        self.data_path = data_path
        self._tick = 0
        self.instr_counter = 0

    def get_ticks(self):
        return self._tick

    def tick(self):
        self._tick += 1
        self.data_path.alu_out = 0
        self.data_path.memory_out = 0

        if self._tick > 10000:
            exit(0)

    def decode_command(self, decode):
        if decode.opcode in [Opcode.LOAD, Opcode.STORE]:
            decode.decode_memory_commands()
        elif (decode.opcode in
              [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD, Opcode.INC, Opcode.DEC, Opcode.CMP]):
            decode.decode_arithmetic_commands()
        elif decode.opcode in [Opcode.CALL, Opcode.RET]:
            decode.decode_subprogram_commands()
        elif decode.opcode in [Opcode.PUSH, Opcode.POP]:
            decode.decode_stack_commands()
        elif decode.opcode in [Opcode.IN, Opcode.OUT]:
            decode.decode_io_commands()

    def execute(self):
        while self.instructions[self.ip][0] != Opcode.HALT:
            self.instr = self.instructions[self.ip]
            self.instr_counter += 1
            if self.instr[0] not in [Opcode.HALT, Opcode.INC, Opcode.DEC, Opcode.PUSH, Opcode.POP, Opcode.RET]:
                decode = Decoder(self, self.instr[0], self.instr[1])
            else:
                decode = Decoder(self, self.instr[0], 0)
            signal = Signal.NEXT_IP

            if decode.opcode in [Opcode.JMP, Opcode.JGE, Opcode.JZ, Opcode.JNZ]:
                signal = decode.decode_flow_commands()
            else:
                self.decode_command(decode)

            if self.instr[0] != Opcode.CALL:
                self.signal_latch_ip(signal, decode.arg)

            print("TICK: " + str(self._tick) + " | INSTR: " + str(self.instr_counter) + " " + str(self.instr)
                        + " | ACC: " + str(self.data_path.acc) + " | BUF_REG: " + str(self.data_path.buf_reg)
                        + " | SP: " + str(self.data_path.stack_pointer) + " | ADDR: " + str(self.data_path.address_reg)
                        + " | IP: " + str(self.ip) + " | FLAGS: " + str(self.data_path.flags), file=sys.stderr)

        return self._tick, self.instr_counter

    def signal_latch_ip(self, signal=Signal.NEXT_IP, arg=0):
        if signal == Signal.NEXT_IP:
            self.ip += 1
        elif signal == Signal.JMP_ARG:
            self.ip = arg
        elif signal == Signal.DATA_IP:
            self.ip = self.data_path.alu_out
