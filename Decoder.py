FUNC_CODES = {
    '0110011': 'R-Type',
    '0010011': 'I-Type',
    '0000011': 'Mem-I-Type',
    '1100111': 'jalr'
}

MNE_CODES = {
    'R-Type': {
        0: 'add',
        1: 'sll',
        2: 'slt',
        3: 'sltu',
        4: 'xor',
        5: 'srl',
        6: 'or',
        7: 'and'
    },
    'I-Type': {
        0: 'addi',
        2: 'slti',
        3: 'sltiu',
        4: 'xori',
        6: 'ori',
        7: 'andi',
        1: 'slli',
        5: 'srli'
    },
    'Mem-I-Type': {
        0: 'lb',
        1: 'lh',
        2: 'lw',
        4: 'lbu',
        5: 'lhu',
    }
}

MNE_CODES_EXCEPTIONS = {
    'R-Type': {
        0: 'sub',
        5: 'sra',
    },
    'I-Type': {
        5: 'srai'
    }
}


def decoder(data):
    func_code = data[-7:]
    instr_type = FUNC_CODES[func_code]
    instruction = ''
    mne = ''
    if instr_type in MNE_CODES:
        mne_code = int(data[-15:-12], 2)
        if int(data[1]):
            mne = MNE_CODES_EXCEPTIONS[instr_type][mne_code]
        else:
            mne = MNE_CODES[instr_type][mne_code]
        instruction += mne
    else:
        instruction += instr_type

    instruction += ' '

    operands = ''
    if instr_type == 'R-Type':
        rd = int(data[-12:-7], 2)
        rs1 = int(data[-20:-15], 2)
        rs2 = int(data[-25:-20], 2)
        operands += f'x{rd}, x{rs1}, x{rs2}'

    elif instr_type == 'Mem-I-Type' or instr_type == 'jalr':
        rd = int(data[-12:-7], 2)
        rs1 = int(data[-20:-15], 2)
        imm = int(data[:-20], 2)
        operands += f'x{rd}, {imm}(x{rs1})'

    elif instr_type == 'I-Type':
        rd = int(data[-12:-7], 2)
        rs1 = int(data[-20:-15], 2)
        if mne in ['slli', 'srli', 'srai']:
            imm = int(data[-25:-20], 2)
        else:
            imm = int(data[:-20], 2)
        operands += f'x{rd}, x{rs1}, {imm}'

    instruction += operands

    return instruction
