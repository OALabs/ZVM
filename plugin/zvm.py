import struct


class LoopCounter:
    text = "LoopCounter"


class Data:
    text = "Data"


class DP:
    text = "DP"


class PC:
    text = "PC"


class OPKey:
    text = "OPKey"


def create_register_class(register_name):
    class Register:
        text = register_name

    return Register


registers = [create_register_class("reg" + str(i))() for i in range(0, 16)]


class DataSize:
    def __init__(self, value):
        self.value = value

    @classmethod
    def BYTE(cls):
        return cls(1)

    @classmethod
    def WORD(cls):
        return cls(2)

    @classmethod
    def DWORD(cls):
        return cls(4)

    def __str__(self):
        if self.value == 1:
            return "BYTE"
        elif self.value == 2:
            return "WORD"
        elif self.value == 4:
            return "DWORD"
        else:
            return f"VALUE({self.value})"


class Operand:
    def __init__(self):
        self.text = ""
        self.op_size = 0
        self.type = ""


class OperandData(Operand):
    def __init__(self, data_size: DataSize):
        super().__init__()
        self.op_size = 0
        self.data_size = data_size
        self.text = f"{self.data_size}(Data[DP])"
        self.type = "mem"

    def parse(self, code):
        pass


class OperandDP(Operand):
    def __init__(self, data_size: DataSize):
        super().__init__()
        self.op_size = 0
        self.data_size = data_size
        self.text = "dp"
        self.type = "reg"

    def parse(self, code):
        pass


class OperandPC(Operand):
    def __init__(self, data_size: DataSize):
        super().__init__()
        self.op_size = 0
        self.data_size = data_size
        self.text = "pc"
        self.type = "reg"

    def parse(self, code):
        pass


class OperandRegisterLow(Operand):
    def __init__(self, data_size: DataSize):
        super().__init__()
        self.op_size = 1
        self.reg_index = None
        self.reg = None
        self.data_size = data_size
        self.text = ""
        self.type = "reg"

    def parse(self, code):
        self.reg_index = code[0] & 0x0F
        self.reg = registers[self.reg_index]
        self.data_size = self.data_size
        self.text = f"{self.reg.text}"


class OperandRegisterHigh(Operand):
    def __init__(self, data_size: DataSize):
        super().__init__()
        self.op_size = 0
        self.reg_index = None
        self.reg = None
        self.data_size = data_size
        self.text = ""
        self.type = "reg"

    def parse(self, code):
        self.reg_index = (code[0] >> 4) & 0x0F
        self.reg = registers[self.reg_index]
        self.data_size = self.data_size
        self.text = f"{self.reg.text}"


class OperandImmediate(Operand):
    def __init__(self, data_size: DataSize):
        super().__init__()
        self.op_size = data_size.value
        self.data_size = data_size
        self.value = None
        self.text = ""
        self.type = "imm"

    def parse(self, code):
        int_size = self.data_size.value
        if int_size == 1:
            self.value = ord(code[0:int_size])
            self.text = f"{self.data_size}({hex(self.value)})"
        elif int_size == 2:
            self.value = struct.unpack("<H", code[0:int_size])[0]
            self.text = f"{self.data_size}({hex(self.value)})"
        elif int_size == 4:
            self.value = struct.unpack("<I", code[0:int_size])[0]
            self.text = f"{self.data_size}({hex(self.value)})"
        else:
            self.value = code[0:int_size]
            self.text = f"{self.data_size}({self.value.hex()})"


class OperandLoopCounter(Operand):
    def __init__(self, data_size: DataSize):
        super().__init__()
        self.data_size = data_size
        self.op_size = 0
        self.text = "loop_counter"
        self.type = "reg"

    def parse(self, code):
        pass


class OperandBuffer(Operand):
    def __init__(self, size: DataSize):
        super().__init__()
        self.op_size = size.value
        self.value = None
        self.text = ""
        self.type = "buffer"

    def parse(self, code):
        self.value = code[0 : self.op_size]
        self.text = f"Buffer[{self.value.hex()}]"


class Instruction:
    def __init__(self, code):
        self.size = 0
        self.text = ""
        self.key = 0
        self.operands = []

    def parse(self, code):
        for operand in self.operands:
            operand.parse(code[self.size :])
            self.size += operand.op_size
            self.text += " " + operand.text
        #print("size: " + str(self.size))
        #print("operand count: " + str(len(self.operands)))
        # Handle special case for nop of larger than one byte
        if self.size > 1 and len(self.operands) == 0:
            # We have real operands (bytes to skip) but no instruction operands
            # Use the first byte of the first operand as key
            #print(f"self.key ^= code[1]({hex(code[1])})")
            self.key ^= code[1]
        else:
            # Assumption, the first operand is never larger than 1 byte
            if len(self.operands) == 0:
                # Key is the opcode
                #print(f"self.key ^= code[0]({hex(code[0])})")
                self.key ^= code[0]
            elif len(self.operands) == 1:
                # Check if the operand is a real operand or a fake operand
                if self.operands[0].op_size != 0:
                    # Key is the first byte in the operand
                    #print(f"self.key ^= code[1]({hex(code[1])})")
                    self.key ^= code[1]
                else:
                    # Key is the opcode
                    #print(f"self.key ^= code[0]({hex(code[0])})")
                    self.key ^= code[0]
            elif len(self.operands) == 2:
                # If the both operands are real operands, the key is the first byte of the second operand
                if self.operands[0].op_size != 0 and self.operands[1].op_size != 0:
                    #print(f"self.key ^= code[2]({hex(code[2])})")
                    self.key ^= code[2]
                # If either of the operands is fake, the key is the first byte of the second operand (real operand 1)
                elif self.operands[0].op_size == 0 or self.operands[1].op_size == 0:
                    #print(f"self.key ^= code[1]({hex(code[1])})")
                    self.key ^= code[1]
                else:
                    raise Exception("Invalid operands")
            elif len(self.operands) == 4:
                # There is only one case with more than 2 operands, rc4
                # key_len, data_len, key_buff[key_len], (fake)data_buff[data_len]
                # The key is the first byte in the third operand
                #print(f"self.key ^= code[3]({hex(code[2])})")
                self.key ^= code[3]
            else:
                raise Exception("Invalid operands")


class nop_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "nop"
        self.key = 0xC7
        self.operands = []


class nop_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 2
        self.text = "nop"
        self.key = 0x45
        self.operands = []


class nop_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 4
        self.text = "nop"
        self.key = 0x25
        self.operands = []


class xor_data_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x51
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_xor_data_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x32
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_xor_data_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x7C
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class h_add_data_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0xB4
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_add_data_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x16
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_add_data_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 2
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class h_sub_data_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0xC9
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_sub_data_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0xF7
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_sub_data_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0x71
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class h_rol_b_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "rol"
        self.key = 0xC
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_rol_w_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "rol"
        self.key = 0xFA
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_rol_dw_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "rol"
        self.key = 0x57
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_ror_b_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "ror"
        self.key = 0x98
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_ror_w_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "ror"
        self.key = 0xD3
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_ror_dw_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "ror"
        self.key = 0xFB
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_not_b_data(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "not"
        self.key = 0xFA
        self.operands = [OperandData(DataSize.BYTE())]


class h_not_w_data(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "not"
        self.key = 0x28
        self.operands = [OperandData(DataSize.WORD())]


class h_not_dw_data(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "not"
        self.key = 4
        self.operands = [OperandData(DataSize.DWORD())]


class h_dw_data_shuffle(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "shuffle"
        self.key = 0x82
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_rc4(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "rc4"
        self.key = 0xC9
        self.operands = [
            OperandImmediate(DataSize.BYTE()),  # key_len
            OperandImmediate(DataSize.BYTE()),  # data_len
            OperandBuffer(DataSize(code[1])),  # key_buff[key_len]
            OperandData(DataSize(code[2])),
        ]  # data_buff[data_len]


class h_set_loop_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x4E
        self.operands = [
            OperandLoopCounter(DataSize.DWORD()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_set_loop_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x9D
        self.operands = [
            OperandLoopCounter(DataSize.DWORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_set_loop_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x61
        self.operands = [
            OperandLoopCounter(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class h_shift_data_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x8F
        self.operands = [OperandDP(DataSize.DWORD()), OperandImmediate(DataSize.WORD())]


class h_loop_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "loop"
        self.key = 0xF8
        # Immediate is subtracted from PC (displacement)
        self.operands = [OperandPC(DataSize.DWORD()), OperandImmediate(DataSize.BYTE())]


class h_loop_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "loop"
        self.key = 0x2C
        # Immediate is subtracted from PC (displacement)
        self.operands = [OperandPC(DataSize.DWORD()), OperandImmediate(DataSize.WORD())]


class h_mov_reg_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0xB3
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_mov_reg_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x9D
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_mov_reg_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0xAF
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class h_mov_reg_reg_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0xD5
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandRegisterHigh(DataSize.BYTE()),
        ]


class h_mov_reg_reg_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x9D
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandRegisterHigh(DataSize.WORD()),
        ]


class h_mov_reg_reg_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x4C
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandRegisterHigh(DataSize.DWORD()),
        ]


class h_add_reg_reg_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x1F
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandRegisterHigh(DataSize.BYTE()),
        ]


class h_add_reg_reg_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0xC9
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandRegisterHigh(DataSize.WORD()),
        ]


class h_add_reg_reg_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0xE0
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandRegisterHigh(DataSize.DWORD()),
        ]


class h_sub_reg_reg_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0x75
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandRegisterHigh(DataSize.BYTE()),
        ]


class h_sub_reg_reg_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0x8B
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandRegisterHigh(DataSize.WORD()),
        ]


class h_sub_reg_reg_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0xDD
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandRegisterHigh(DataSize.DWORD()),
        ]


class h_xor_reg2_to_reg1_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x77
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandRegisterHigh(DataSize.BYTE()),
        ]


class h_xor_reg2_to_reg1_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x79
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandRegisterHigh(DataSize.WORD()),
        ]


class h_xor_reg2_to_reg1_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x6A
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandRegisterHigh(DataSize.DWORD()),
        ]


class h_reg_add_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x49
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_reg_add_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0xF3
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_reg_add_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x1C
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class h_reg_sub_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0x54
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_reg_sub_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0x53
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_reg_sub_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0x23
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class h_reg_xor_imm_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x6E
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandImmediate(DataSize.BYTE()),
        ]


class h_reg_xor_imm_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x9A
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandImmediate(DataSize.WORD()),
        ]


class h_reg_xor_imm_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0xD1
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandImmediate(DataSize.DWORD()),
        ]


class mw_add_reg_to_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x46
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandRegisterLow(DataSize.BYTE()),
        ]


class mw_add_reg_to_data_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x32
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandRegisterLow(DataSize.WORD()),
        ]


class mw_add_reg_to_data_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "add"
        self.key = 0x3D
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandRegisterLow(DataSize.DWORD()),
        ]


class mw_subs_reg_from_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 4
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandRegisterLow(DataSize.BYTE()),
        ]


class mw_subs_reg_from_data_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0xDB
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandRegisterLow(DataSize.WORD()),
        ]


class mw_subs_reg_from_data_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "sub"
        self.key = 0xC6
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandRegisterLow(DataSize.DWORD()),
        ]


class mw_xor_data_with_reg_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x7D
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandRegisterLow(DataSize.BYTE()),
        ]


class mw_xor_data_with_reg_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x71
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandRegisterLow(DataSize.WORD()),
        ]


class mw_xor_data_with_reg_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "xor"
        self.key = 0x7A
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandRegisterLow(DataSize.DWORD()),
        ]


class h_mov_data_to_reg_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0xBC
        self.operands = [
            OperandRegisterLow(DataSize.BYTE()),
            OperandData(DataSize.BYTE()),
        ]


class h_mov_data_to_reg_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x3D
        self.operands = [
            OperandRegisterLow(DataSize.WORD()),
            OperandData(DataSize.WORD()),
        ]


class h_mov_data_to_reg_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x9F
        self.operands = [
            OperandRegisterLow(DataSize.DWORD()),
            OperandData(DataSize.DWORD()),
        ]


class mw_push_reg_to_data_b(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x22
        self.operands = [
            OperandData(DataSize.BYTE()),
            OperandRegisterLow(DataSize.BYTE()),
        ]


class mw_push_reg_to_data_w(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0xF8
        self.operands = [
            OperandData(DataSize.WORD()),
            OperandRegisterLow(DataSize.WORD()),
        ]


class mw_push_reg_to_data_dw(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "mov"
        self.key = 0x56
        self.operands = [
            OperandData(DataSize.DWORD()),
            OperandRegisterLow(DataSize.DWORD()),
        ]


class h_vm_exit(Instruction):
    def __init__(self, code):
        super().__init__(code)
        self.size = 1
        self.text = "exit"
        self.key = 0x00
        self.operands = []


# Create an array of the instruction functions
instructions = [
    nop_b,
    nop_w,
    nop_dw,
    xor_data_imm_b,
    h_xor_data_imm_w,
    h_xor_data_imm_dw,
    h_add_data_imm_b,
    h_add_data_imm_w,
    h_add_data_imm_dw,
    h_sub_data_imm_b,
    h_sub_data_imm_w,
    h_sub_data_imm_dw,
    h_rol_b_data_b,
    h_rol_w_data_b,
    h_rol_dw_data_b,
    h_ror_b_data_b,
    h_ror_w_data_b,
    h_ror_dw_data_b,
    h_not_b_data,
    h_not_w_data,
    h_not_dw_data,
    h_dw_data_shuffle,
    h_rc4,
    h_set_loop_imm_b,
    h_set_loop_imm_w,
    h_set_loop_imm_dw,
    h_shift_data_imm_w,
    h_loop_b,
    h_loop_w,
    h_mov_reg_imm_b,
    h_mov_reg_imm_w,
    h_mov_reg_imm_dw,
    h_mov_reg_reg_b,
    h_mov_reg_reg_w,
    h_mov_reg_reg_dw,
    h_add_reg_reg_b,
    h_add_reg_reg_w,
    h_add_reg_reg_dw,
    h_sub_reg_reg_b,
    h_sub_reg_reg_w,
    h_sub_reg_reg_dw,
    h_xor_reg2_to_reg1_b,
    h_xor_reg2_to_reg1_w,
    h_xor_reg2_to_reg1_dw,
    h_reg_add_imm_b,
    h_reg_add_imm_w,
    h_reg_add_imm_dw,
    h_reg_sub_imm_b,
    h_reg_sub_imm_w,
    h_reg_sub_imm_dw,
    h_reg_xor_imm_b,
    h_reg_xor_imm_w,
    h_reg_xor_imm_dw,
    mw_add_reg_to_data_b,
    mw_add_reg_to_data_w,
    mw_add_reg_to_data_dw,
    mw_subs_reg_from_data_b,
    mw_subs_reg_from_data_w,
    mw_subs_reg_from_data_dw,
    mw_xor_data_with_reg_b,
    mw_xor_data_with_reg_w,
    mw_xor_data_with_reg_dw,
    h_mov_data_to_reg_b,
    h_mov_data_to_reg_w,
    h_mov_data_to_reg_dw,
    mw_push_reg_to_data_b,
    mw_push_reg_to_data_w,
    mw_push_reg_to_data_dw,
    h_vm_exit,
]


def disassemble(code):
    key = 0x00
    ptr = 0
    disassembly = []
    while ptr < len(code):
        op = code[ptr]
        print(f"OP: {hex(op)}")
        op = (op ^ key) & 0x7F
        # Replace the ecrypted opcode with the decrypted one
        code = code[0:ptr] + bytes([op]) + code[ptr + 1 :]
        print(f"OP (decrypted): {hex(op)}")
        if op >= len(instructions):
            raise Exception(f"Invalid opcode {hex(op)}")
        inst = instructions[op](code[ptr:])
        print(f"INST: {type(inst).__name__}")
        inst.parse(code[ptr:])
        print(f"{hex(ptr)}: {op} -> {inst.text}")
        disassembly.append(inst)
        ptr += inst.size
        key = inst.key
        if inst.text == "exit":
            break
    return disassembly
