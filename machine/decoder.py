from machine.isa import Opcode
from machine.machine_signals import Signal, Operands
import re

class Decoder:

    def __init__(self, control_unit, opcode, arg):
        self.cu = control_unit
        self.opcode = opcode
        self.arg = arg

    def process_addressing(self):
        dp = self.cu.data_path
        if isinstance(self.arg, int):
            dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, self.arg)
            self.cu.tick()
        elif self.arg[-1] == '+':
            self.arg = self.arg[1:-1]
            dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, self.arg)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(Opcode.INC, [Operands.MEM])
            dp.signal_latch_regs(Signal.BUF_LATCH)
            dp.memory_manager(Signal.WRITE)
            self.cu.tick()

            dp.alu_working(Opcode.DEC, [Operands.BUF])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()
        elif self.arg[0] == '*':
            self.arg = self.arg[1:]
            dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, self.arg)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(Opcode.ADD, [Operands.MEM])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

    def decode_memory_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.LOAD:
            if isinstance(self.arg, str) and self.arg[0] == '#':
                self.arg = self.arg[1:]
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
                self.cu.tick()
            else:
                self.process_addressing()
                dp.memory_manager(Signal.READ)
                dp.alu_working(Opcode.ADD, [Operands.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
                self.cu.tick()
        else:
            self.process_addressing()
            dp.alu_working(Opcode.ADD, [Operands.ACC])####
            dp.memory_manager(Signal.WRITE)
            self.cu.tick()

    def decode_arithmetic_commands(self):
        dp = self.cu.data_path
        if self.opcode not in [Opcode.INC, Opcode.DEC]:
            if isinstance(self.arg, str) and self.arg[0] == '#':
                self.arg = self.arg[1:]
                if isinstance(self.arg, int):
                    dp.alu_working(Opcode.ADD, [Operands.ACC])
                    dp.signal_latch_regs(Signal.BUF_LATCH)
                    self.cu.tick()

                    dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
                    dp.alu_working(self.opcode, [Operands.BUF, Operands.ACC])
                    if self.opcode != Opcode.CMP:
                        dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
                    else:
                        dp.alu_working(Opcode.ADD, [Operands.BUF])
                        dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
                    self.cu.tick()
                else:
                    dp.alu_working(Opcode.ADD, [Operands.ACC])
                    dp.signal_latch_regs(Signal.BUF_LATCH)
                    self.cu.tick()

                    dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
                    dp.alu_working(self.opcode, [Operands.BUF, Operands.ACC])
                    if self.opcode != Opcode.CMP:
                        dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
                    else:
                        dp.alu_working(Opcode.ADD, [Operands.BUF])
                        dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
                    self.cu.tick()
            else:
                self.process_addressing()
                dp.memory_manager(Signal.READ)
                dp.alu_working(self.opcode, [Operands.ACC, Operands.MEM])
                if self.opcode != Opcode.CMP:
                    dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
                self.cu.tick()
        else:
            dp.alu_working(self.opcode, [Operands.ACC])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            self.cu.tick()

    def decode_flow_commands(self):
        dp = self.cu.data_path
        jumps = {
            Opcode.JMP: True,
            Opcode.JGE: not dp.flags["n"],
            Opcode.JZ: dp.flags["z"],
            Opcode.JNZ: not dp.flags["z"]
        }
        if jumps[self.opcode]:
            signal = Signal.JMP_ARG
        else:
            signal = Signal.NEXT_IP
        self.cu.tick()
        return signal

    def decode_subprogram_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.CALL:
            dp.alu_working(Opcode.ADD, [Operands.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.alu_working(Opcode.ADD, [Operands.ACC])
            dp.signal_latch_regs(Signal.BUF_LATCH)
            self.cu.tick()

            dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.cu.ip)
            self.cu.tick()

            dp.alu_working(Opcode.ADD, [Operands.ACC])
            dp.memory_manager(Signal.WRITE)
            self.cu.tick()

            dp.alu_working(Opcode.DEC, [Operands.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)
            self.cu.tick()

            dp.alu_working(Opcode.ADD, [Operands.BUF])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            self.cu.tick()

            self.cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
            self.cu.tick()
        else:
            dp.alu_working(Opcode.INC, [Operands.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            dp.signal_latch_regs(Signal.STACK_LATCH)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(Opcode.ADD, [Operands.MEM])
            self.cu.signal_latch_ip(Signal.DATA_IP)
            self.cu.tick()

    def decode_stack_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.PUSH:
            dp.alu_working(Opcode.ADD, [Operands.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.alu_working(Opcode.ADD, [Operands.ACC])
            dp.memory_manager(Signal.WRITE)
            self.cu.tick()

            dp.alu_working(Opcode.DEC, [Operands.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)
            self.cu.tick()
        else:
            dp.alu_working(Opcode.INC, [Operands.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            dp.signal_latch_regs(Signal.STACK_LATCH)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(Opcode.ADD, [Operands.MEM])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            self.cu.tick()

    def decode_io_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.IN:
            dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.cu.input_tokens[0])
            del self.cu.input_tokens[0]
            self.cu.tick()
        else:
            dp.alu_working(Opcode.ADD, [Operands.ACC])
            if dp.alu_out != "":
                print(dp.alu_out, end="")
            else:
                print(dp.alu_out)
            self.cu.tick()
        self.cu.tick()
