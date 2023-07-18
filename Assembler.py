import ply.lex as lex
import ply.yacc as yacc
from Encoder import encoder, InvalidRangeException
from Decoder import decoder

# ======================================================================================================================
# Rules:

# start         -> MNE Operands | EMPTY
# EMPTY         -> // do nothing
# Operands      -> Case_1 | Case_2 | Case_3
# Case_1        -> REG COMMA REG COMMA REG
# Case_2        -> REG COMMA REG COMMA IMM
# Case_3        -> REG COMMA IMM LB REG RB

# ======================================================================================================================
# Decode:
# result[] = (MNE, Operands[])
# Operands[] = (Op_Type, Reg_Imm[])

# Op_Type = 1
# Reg_Imm[] = (reg, reg, reg)

# Op_Type = 2
# Reg_Imm[] = (reg, reg, imm)

# Op_Type = 3
# Reg_Imm[] = (reg, imm, reg)

# ======================================================================================================================
# Tokens:

# COMMA         -> ,
# LB            -> (
# RB            -> )
# Comment       -> # {Anything}
# REG           -> x{num} | t{num} | s{num} | a{num} | zero | ra | sp | gp | tp | fp
# IMM           -> {Any decimal num}
# MNE           -> jalr |
#                  lb | lh | lw | lbu | lhu |
#                  addi | slti | sltiu | xori | ori | andi | slli | srli | srai |
#                  add | sub | sll | slt | sltu | xor | srl | sra | or | and


# ======================================================================================================================

tokens = ['COMMA', 'LB', 'RB',
          'REG', 'IMM', 'MNE']

t_COMMA = r','
t_LB = r'\('
t_RB = r'\)'
t_ignore = ' \t'

SPEC_REGS = {
    'zero': 0,
    'ra': 1,
    'sp': 2,
    'gp': 3,
    'tp': 4,
    'fp': 8
}


def t_comment(t):
    r"""\#.*"""
    pass


def t_MNE(t):
    r"""[x][o][r][i] | [x][o][r] | [s][u][b] | [s][r][l][i] | [s][r][l] | [s][r][a][i] | [s][r][a] | [s][l][t][u] |
    [s][l][t][i][u] | [s][l][t][i] | [s][l][t] | [s][l][l][i] | [s][l][l] | [o][r][i] | [o][r] | [l][w] | [l][h][u] |
    [l][h] | [l][b][u] | [l][b] | [j][a][l][r] | [a][n][d][i] | [a][n][d] | [a][d][d][i] | [a][d][d]"""
    return t


def t_REG(t):
    r"""([x]\d+) | ([t]\d+) | ([s]\d+) | ([a]\d+) |
    [z][e][r][o] | [r][a] | [s][p] | [g][p] | [t][p] | [f][p]"""
    if t.value in SPEC_REGS.keys():
        t.value = SPEC_REGS[t.value]
    else:
        token_type = t.value[0]
        token_val = int(t.value[1:])
        if token_type == 'x':
            if 0 <= token_val <= 31:
                t.value = token_val
            else:
                my_error(t, "register should be in x0 - x31")
        elif token_type == 't':
            if 0 <= token_val <= 2:
                t.value = token_val + 5
            elif 3 <= token_val <= 6:
                t.value = token_val + 25
            else:
                my_error(t, "register should be in t0 - t6")
        elif token_type == 's':
            if 0 <= token_val <= 1:
                t.value = token_val + 8
            elif 2 <= token_val <= 11:
                t.value = token_val + 16
            else:
                my_error(t, "register should be in s0 - s11")
        elif token_type == 'a':
            if 0 <= token_val <= 7:
                t.value = token_val + 10
            else:
                my_error(t, "register should be in a0 - a7")
    return t


def t_IMM(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


def my_error(t, msg):
    print(msg)
    t_error(t)


def t_error(t):
    raise Exception("Illegal character '%s'" % t.value[0])


def p_start_0(p):
    """
    start : EMPTY
    EMPTY :
    """
    p[0] = None


def p_start_1(p):
    """start : MNE Operands"""
    p[0] = (p[1], p[2])


def p_Operands(p):
    """
    Operands : Case_1
    Operands : Case_2
    Operands : Case_3
    """
    p[0] = p[1]


def p_Case_1(p):
    """Case_1 : REG COMMA REG COMMA REG"""
    p[0] = (1, (p[1], p[3], p[5]))


def p_Case_2(p):
    """Case_2 : REG COMMA REG COMMA IMM"""
    p[0] = (2, (p[1], p[3], p[5]))


def p_Case_3(p):
    """Case_3 : REG COMMA IMM LB REG RB"""
    p[0] = (3, (p[1], p[3], p[5]))


def p_error(p):
    raise Exception("Syntax Error In Input '%s' " % p)


lexer = lex.lex()
parser = yacc.yacc()

if __name__ == '__main__':

    ASSEMBLY_FNAME = 'data.s'
    ENCODED_FNAME = 'out1.txt'
    DECODED_FNAME = 'out2.txt'

    # Encode
    with open(ASSEMBLY_FNAME) as f:
        lines = f.read().splitlines()

    fd = open(ENCODED_FNAME, 'w')
    line_no = 0
    for line in lines:
        line_no += 1
        result = parser.parse(line.lower())
        if result is not None:
            # print(result)
            try:
                fd.write(encoder(result))
            except InvalidRangeException:
                print(f'Error in line {line_no}: {line}')
                print(f'Something\'s too big!')
                exit()

        fd.write('\n')
    fd.close()

    # Decode
    with open(ENCODED_FNAME) as f:
        lines = f.read().splitlines()

    fd = open(DECODED_FNAME, 'w')
    for line in lines:
        if line != '':
            fd.write(decoder(line))
        fd.write('\n')
    fd.close()
