import sys
import pandas as pd
import numpy as np
from pprint import pprint

class Parser:
    # Initialize
    def __init__(self, asm):
        self.asm = asm

    # Clean input commands
    def clean(self):
        with open("{}".format(self.asm), "r") as f:
            lines = f.readlines()
            lines_clean = []
            for line in lines:
                # Treat newline, comments, and whitespace
                line = line.rstrip('\n').split("//",1)[0].strip()
                lines_clean.append(line)
            lines_clean = [line for line in lines_clean if line != ""]
        return lines_clean

    # Determine command type
    def determine(self):
        lines_clean = self.clean()
        A_COMMAND = [False for i in range(len(lines_clean))]
        C_COMMAND = [False for i in range(len(lines_clean))]
        L_COMMAND = [False for i in range(len(lines_clean))]

        for index, value in enumerate(lines_clean):
            # A_COMMAND
            if value.startswith("@"):
                A_COMMAND[index] = True
            # C_COMMAND
            elif "=" in value or ";" in value:
                C_COMMAND[index] = True
            # L_COMMAND
            if value.startswith("("):
                L_COMMAND[index] = True

        dict = {'instr':lines_clean,
                'A_COMM':A_COMMAND, 'C_COMM':C_COMMAND, 'L_COMM':L_COMMAND}
        return pd.DataFrame(dict)

    # Retrieve mnemonics
    def retrieve(self):
        df = self.determine()

        # Retrieve mnemonics Xxx of @Xxx
        df.loc[(df['A_COMM'] == True), 'symbol'] = df['instr'].str.strip('@')
        df.loc[(df['L_COMM'] == True), 'symbol'] = df['instr'].str.strip('()')

        # Retrieve mnemonics of dest, comp, jump
        df['bool_dest'] = df['instr'].str.contains('=')
        df['bool_jump'] = df['instr'].str.contains(';')
        df.loc[(df['C_COMM']) & (df['bool_dest']), 'dest'] = df['instr'].str.split('[=]').str[0]
        df.loc[(df['C_COMM']) & (df['bool_dest']), 'comp'] = df['instr'].str.split('[=]').str[1]
        df.loc[(df['C_COMM']) & (df['bool_jump']), 'comp'] = df['instr'].str.split('[;]').str[0]
        df.loc[(df['C_COMM']) & (df['bool_jump']), 'jump'] = df['instr'].str.split('[;]').str[1]
        df = df.drop(['bool_dest', 'bool_jump'], axis=1).replace(np.nan, '')
        df = df.replace(np.nan, '')

        return df

class Code:
    # Initialize
    def __init__(self, asm):
        self.asm = asm

    # Convert mnemonics to binary
    def convert(self):
        # Prepare mnemonics lists
        parsed = Parser(self.asm).retrieve()
        symb_lst = parsed['symbol'].tolist()
        dest_lst = parsed['dest'].tolist()
        comp_lst = parsed['comp'].tolist()
        jump_lst = parsed['jump'].tolist()

        # Prepare field tables for C-instruction
        dest_key = ['','M','D','MD','A','AM','AD','AMD']
        dest_val = ['000','001','010','011','100','101','110','111']
        dest_dict = dict(zip(dest_key, dest_val))

        comp_key = ['0','1','-1','D','A','!D','!A','-D','-A','D+1','A+1','D-1','A-1','D+A','D-A','A-D','D&A','D|A',
                    'M','!M','-M','M+1','M-1','D+M','D-M','M-D','D&M','D|M']
        comp_val = ['0101010','0111111','0111010','0001100','0110000','0001101','0110001','0001111','0110011','0011111','0110111','0001110','0110010','0000010','0010011','0000111','0000000','0010101',
                   '1110000','1110001','1110011','1110111','1110010','1000010','1010011','1000111','1000000','1010101']
        comp_dict = dict(zip(comp_key, comp_val))

        jump_key = ['','JGT','JEQ','JGE','JLT','JNE','JLE','JMP']
        jump_val = ['000','001','010','011','100','101','110','111']
        jump_dict = dict(zip(jump_key, jump_val))

        # Convert A-instruction to binary
        binary_A = []
        for s in symb_lst:
            if s == "":
                binary_A.append(s)
            else:
                binary = bin(int(s))[2:].zfill(16)
                binary_A.append(binary)
        parsed['binary_A'] = binary_A

        # Convert C-instruction to binary
        dest_bin = []
        for d in dest_lst:
            binary = dest_dict.get(d)
            dest_bin.append(binary)

        comp_bin = []
        for d in comp_lst:
            binary = comp_dict.get(d)
            comp_bin.append(binary)

        jump_bin = []
        for d in jump_lst:
            binary = jump_dict.get(d)
            jump_bin.append(binary)

        parsed['binary_dest'] = dest_bin
        parsed['binary_comp'] = comp_bin
        parsed['binary_jump'] = jump_bin
        parsed['binary_C'] = '111' + parsed['binary_comp'] + parsed['binary_dest'] + parsed['binary_jump']

        parsed = parsed.replace(np.nan, '')
        parsed['binary'] = parsed['binary_A'] + parsed['binary_C']

        #cols = ['instr','symbol','dest','comp','jump','binary']
        cols = ['binary']
        return parsed[cols]

    # Write the converted 16-bit instruction to output file
    def output(self):
        hack = self.asm.replace(".asm", '.hack')
        converted = self.convert()
        converted.to_csv("{}".format(hack), index=False, header=None)
        return "{} was assembled to {}".format(self.asm, hack)

if __name__=="__main__":
    asm = Code(sys.argv[1])
    print(asm.output())
