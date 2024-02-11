from binaryninja.log import log_info, log_warn
from binaryninja.architecture import Architecture
from binaryninja.function import RegisterInfo, InstructionInfo, InstructionTextToken
from binaryninja.enums import InstructionTextTokenType, BranchType

from .zvm import instructions


class ZVM(Architecture):
    name = 'ZVM'
    address_size = 4        # 32-bit addresses
    default_int_size = 1    # 1-byte integers
    instr_alignment = 1     # no instruction alignment
    max_instr_length = 256  # maximum length of an instruction (operands + 2 opcodes + variable 255 opcode)

    # Regsiters
    stack_pointer = 'sp'
    regs = {'sp': RegisterInfo('sp', 4),
            # Setup registers from 0 to 15
            'reg0': RegisterInfo('reg0', 4),
            'reg1': RegisterInfo('reg1', 4),
            'reg2': RegisterInfo('reg2', 4),
            'reg3': RegisterInfo('reg3', 4),
            'reg4': RegisterInfo('reg4', 4),
            'reg5': RegisterInfo('reg5', 4),
            'reg6': RegisterInfo('reg6', 4),
            'reg7': RegisterInfo('reg7', 4),
            'reg8': RegisterInfo('reg8', 4),
            'reg9': RegisterInfo('reg9', 4),
            'reg10': RegisterInfo('reg10', 4),
            'reg11': RegisterInfo('reg11', 4),
            'reg12': RegisterInfo('reg12', 4),
            'reg13': RegisterInfo('reg13', 4),
            'reg14': RegisterInfo('reg14', 4),
            'reg15': RegisterInfo('reg15', 4),
            # Setup special registers
            'pc': RegisterInfo('pc', 4),
            # Data pointer for data buffer
            'dp': RegisterInfo('dp', 4),
            'loop_counter': RegisterInfo('loop_counter', 4),
            }
    
    # Xor keys
    xor_keys = {0:0}

    def get_instruction_info(self, data, addr):
        result = InstructionInfo()
        result.length = 1

        # Check if there is an xor key for our instruction
        if addr not in ZVM.xor_keys:
            log_warn(f"Address {addr} not in xor_keys")
            return None
        
        # Decrypt the instruction
        opcode = (data[0] ^ ZVM.xor_keys[addr]) & 0x7f
        tmp_data = bytes([opcode]) + data[1:]
        instr = instructions[opcode](tmp_data)
        # Parse the operands
        instr.parse(tmp_data)
       
        # Set the next xor key
        ZVM.xor_keys[addr + instr.size] = instr.key

        # Set the instruction length
        result.length = instr.size

        # Check if the instruction is a branch
        if instr.text[:4] == 'loop':
            result.add_branch(BranchType.TrueBranch, addr + instr.size - instr.operands[1].value)
            result.add_branch(BranchType.FalseBranch, addr + instr.size )
        elif instr.text[:3] == 'exit':
            result.add_branch(BranchType.FunctionReturn)

        return result


    def get_instruction_text(self, data, addr):
        # Check if there is an xor key for our instruction
        if addr not in ZVM.xor_keys:
            log_warn(f"Address {addr} not in xor_keys")
            return None, 0
        
        # Decrypt the instruction
        opcode = (data[0] ^ ZVM.xor_keys[addr]) & 0x7f
        tmp_data = bytes([opcode]) + data[1:]
        instr = instructions[opcode](tmp_data)

        # Get the mnemonic
        mnemonic = instr.text

        # Parse the operands
        instr.parse(tmp_data)

        # Set the next xor key
        ZVM.xor_keys[addr + instr.size] = instr.key

        # Parse the tokens from the instruction
        tokens = []
        tokens.append(InstructionTextToken(InstructionTextTokenType.InstructionToken, mnemonic))
        tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, " "))
        for i, op in enumerate(instr.operands):
            if i != 0:
                tokens.append(InstructionTextToken(InstructionTextTokenType.OperandSeparatorToken, ", "))
            # Add operand based on type
            if op.type == 'reg':
                # Check size of register
                if op.data_size.value == 1:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"{op.text}.b"))
                elif op.data_size.value == 2:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"{op.text}.w"))
                else:
                    tokens.append(InstructionTextToken(InstructionTextTokenType.RegisterToken, f"{op.text}"))
            elif op.type == 'imm':
                tokens.append(InstructionTextToken(InstructionTextTokenType.IntegerToken, f"{hex(op.value)}", value=op.value))
            else:
                tokens.append(InstructionTextToken(InstructionTextTokenType.TextToken, f"{op.text}"))

        return tokens, instr.size
    
    def get_instruction_low_level_il(self, data, addr, il):
        return None

ZVM.register()



    

 