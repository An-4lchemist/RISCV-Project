class InvalidRangeException(Exception):
    """Something's too big"""
    pass


MNE_CODES = {
    'jalr': 0,
    'lb': 0, 'lh': 1, 'lw': 2, 'lbu': 4, 'lhu': 5,
    'addi': 0, 'slti': 2, 'sltiu': 3, 'xori': 4, 'ori': 6, 'andi': 7,
    'slli': 1, 'srli': 5, 'srai': 5,
    'add': 0, 'sub': 0, 'sll': 1, 'slt': 2, 'sltu': 3, 'xor': 4, 'srl': 5, 'sra': 5, 'or': 6, 'and': 7
}

FUNC_CODES = {
    'R-Type': '0110011',
    'I-Type': '0010011',
    'Mem-I-Type': '0000011',
    'jalr': '1100111'
}


def convert(num, length):
    data = bin(num)[2:]
    if len(data) > length:
        raise InvalidRangeException
    if len(data) < length:
        data = '0' * (length - len(data)) + data
    return data


def convert_hex(data):
    res = ''
    while len(data):
        x = hex(int(data[:4], 2))
        data = data[4:]
        res += str(x)[2:]
    return res


def encoder(res):
    data = ''

    Mnemonic = res[0]
    Operands = res[1]
    Op_Type = Operands[0]
    Operands = Operands[1]

    if Mnemonic in ['add', 'sub', 'sll', 'slt', 'sltu', 'xor', 'srl', 'sra', 'or', 'and']:
        if Mnemonic in ['sub', 'sra']:
            data += '0100000'
        else:
            data += '0000000'

        if Op_Type != 1:
            raise Exception('Wrong Operands Format: Only Reg,Reg,Reg allowed for R-Type instructions')

        rd = Operands[0]
        rs1 = Operands[1]
        rs2 = Operands[2]

        data += convert(rs2, 5)
        data += convert(rs1, 5)
        data += convert(MNE_CODES[Mnemonic], 3)
        data += convert(rd, 5)
        data += FUNC_CODES['R-Type']

    elif Mnemonic in ['addi', 'slti', 'sltiu', 'xori', 'ori', 'andi']:
        if Op_Type != 2:
            raise Exception('Wrong Operands Format: Only Reg,Reg,Imm allowed for I-Type instructions')

        rd = Operands[0]
        rs1 = Operands[1]
        imm = Operands[2]

        data += convert(imm, 12)
        data += convert(rs1, 5)
        data += convert(MNE_CODES[Mnemonic], 3)
        data += convert(rd, 5)
        data += FUNC_CODES['I-Type']

    elif Mnemonic in ['slli', 'srli', 'srai']:
        if Mnemonic in ['srai']:
            data += '0100000'
        else:
            data += '0000000'

        if Op_Type != 2:
            raise Exception('Wrong Operands Format: Only Reg,Reg,Shift allowed for Shift I-Type instructions')

        rd = Operands[0]
        rs1 = Operands[1]
        shift = Operands[2]

        data += convert(shift, 5)
        data += convert(rs1, 5)
        data += convert(MNE_CODES[Mnemonic], 3)
        data += convert(rd, 5)
        data += FUNC_CODES['I-Type']

    elif Mnemonic in ['lb', 'lh', 'lw', 'lbu', 'lhu']:
        if Op_Type != 3:
            raise Exception('Wrong Operands Format: Only Reg,Imm(Reg) allowed for Mem I-Type instructions')

        rd = Operands[0]
        imm = Operands[1]
        rs1 = Operands[2]

        data += convert(imm, 12)
        data += convert(rs1, 5)
        data += convert(MNE_CODES[Mnemonic], 3)
        data += convert(rd, 5)
        data += FUNC_CODES['Mem-I-Type']

    elif Mnemonic in ['jalr']:
        if Op_Type != 3:
            raise Exception('Wrong Operands Format: Only Reg,Imm(Reg) allowed for jalr')

        rd = Operands[0]
        imm = Operands[1]
        rs1 = Operands[2]

        data += convert(imm, 12)
        data += convert(rs1, 5)
        data += convert(MNE_CODES[Mnemonic], 3)
        data += convert(rd, 5)
        data += FUNC_CODES['jalr']

    return data
