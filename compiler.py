
# coding=utf-8

import os
import re

import pin
import assembly as ASM

dirname = os.path.dirname(__file__)

inputfile = os.path.join(dirname, 'program.asm') # 读入汇编文件
outputfile = os.path.join(dirname, 'program.bin')

annotation = re.compile(r"(.*?);.*") # 正则匹配

codes = []
marks={}


OP2 = { # 二操作数指令列表
    'MOV': ASM.MOV,
    'ADD': ASM.ADD,
    'SUB': ASM.SUB,
    'OR': ASM.OR,
    'XOR': ASM.XOR,
    'CMP': ASM.CMP,
}

OP1 = { # 一操作数指令列表
    'INC': ASM.INC,
    'DEC': ASM.DEC,
    'NOT': ASM.NOT,
    'JMP': ASM.JMP,
    'JO': ASM.JO,
    'JNO': ASM.JNO,
    'JZ': ASM.JZ,
    'JNZ': ASM.JNZ,
    'JP': ASM.JP,
    'JNP': ASM.JNP,
    'PUSH': ASM.PUSH,
    'POP': ASM.POP,
    'CALL' : ASM.CALL,
    'INT' : ASM.INT
}

OP0 = { # 零操作数指令列表
    'NOP': ASM.NOP,
    'RET': ASM.RET,
    'IRET': ASM.IRET,
    'STI': ASM.STI,
    'CLI': ASM.CLI,
    'HLT': ASM.HLT,
}

OP2SET = set(OP2.values()) 
OP1SET = set(OP1.values())
OP0SET = set(OP0.values())

REGISTERS = { # 可操作寄存器
    "A": pin.A,
    "B": pin.B,
    "C": pin.C,
    "D": pin.D,
    "SS": pin.SS,
    "SP": pin.SP,
}


class Code(object): # Code对象

    TYPE_CODE = 1
    TYPE_LABEL = 2

    def __init__(self, number, source:str):
        self.numer = number # 行号
        self.source = source.upper() # 源代码
        self.op = None
        self.dst = None
        self.src = None
        self.type = 1
        self.index = 0
        self.prepare_source() # 调用预处理源代码

    def get_op(self): # 获取指令
        if self.op in OP2:
            return OP2[self.op]
        if self.op in OP1:
            return OP1[self.op]
        if self.op in OP0:
            return OP0[self.op]
        raise SyntaxError(self)

    def get_am(self, addr): # 获取目的 操作数和源操作数
        global marks
        if not addr: # 如果啥都没有，返回0
            return None,None
        if addr in marks:
            return pin.AM_INS,marks[addr].index*3
        if addr in REGISTERS: # 如果是寄存器，列表中存在返回寄存器编码
            return pin.AM_REG, REGISTERS[addr]
        if re.match(r'^[0-9]+$', addr): # 如果是数字，返回立即数
            return pin.AM_INS, int(addr)
        if re.match(r'^0X[0-9A-F]+$', addr): # 如果是十六进制数，返回十六进制立即数
            return pin.AM_INS, int(addr, 16)
        match=re.match(r'^\[([0-9]+)\]$', addr) # 如果是十进制地址位，返回十进制地址
        if match:
            return pin.AM_DIR, int(match.group(1))
        match=re.match(r'^\[(0X[0-9A-F]+)\]$', addr) # 如果是十六进制地址位，返回十进制地址
        if match:
            return pin.AM_DIR, int(match.group(1),16)
        match=re.match(r'^\[(.+)\]$', addr)
        if match and match.group(1) in REGISTERS:
            return pin.AM_RAM,REGISTERS[match.group(1)]

        raise SyntaxError(self)

    def prepare_source(self): # 预处理源代码

        if self.source.endswith(':'): # 处理标记
            self.type = 2
            self.name = self.source.strip(':') 
            return
        tup = self.source.split(',') # 用逗号分割代码
        if len(tup) > 2: # 如果分割出来长度大于2 说明语法错误
            raise SyntaxError(self)
        if len(tup) == 2: # 如果分割出来等于二
            self.src = tup[1].strip() # 把逗号后面的分配给源操作数

        tup = re.split(r" +", tup[0]) # 用正则空格来分割
        if len(tup) > 2: # 如果分割出来长度大于2 说明语法错误
            raise SyntaxError(self)
        if len(tup) == 2: # 如果等于二
            self.dst = tup[1].strip() # 将后面的分配给目的操作数

        self.op = tup[0].strip() # 前面的分配给指令

    def compile_code(self):
        op = self.get_op() # 获取指令

        amd, dst = self.get_am(self.dst) # 获取目的操作数编码
        ams, src = self.get_am(self.src) # 获取源操作数编码

        if src is not None and  (amd, ams) not in ASM.INSTRUCTIONS[2][op]:
            raise SyntaxError(self)
        if src is None and dst is not None and amd not in ASM.INSTRUCTIONS[1][op]:
            raise SyntaxError(self)
        if src is None and dst is None and op not in ASM.INSTRUCTIONS[0]:
            raise SyntaxError(self)

        amd = amd or 0
        dst = dst or 0
        ams = ams or 0
        src = src or 0

        if op in OP2SET: # 获取指令编码
            ir = op | (amd << 2) | ams
        elif op in OP1SET:
            ir = op | amd
        else:
            ir = op

        return [ir, dst, src]

    def __repr__(self): # 打印的时候显示
        return f'[{self.numer}] - {self.source}' # 显示行号+源代码


class SyntaxError(Exception): # 语法错误

    def __init__(self, code: Code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code


def compile_program():
    global codes
    global marks
    with open(inputfile, encoding='utf8') as file: # 读入汇编文件
        lines = file.readlines() # 记录行号

    for index, line in enumerate(lines):
        source = line.strip() # 将两端的空格去掉
        if ';' in source: # 将;后面的去掉
            match = annotation.match(source)
            source = match.group(1)
        if not source: # 如果没有代码跳过
            continue
        code = Code(index + 1, source) # 生成Code类对源代码进行处理
        codes.append(code)

    code = Code(index+2,'HLT')
    codes.append(code)

    result = []
        
    current=None
    for var in range(len(codes)-1,-1,-1):
        code=codes[var]
        if code.type==Code.TYPE_CODE:
            current = code
            result.insert(0,code)
            continue
        if code.type==Code.TYPE_LABEL:
            marks[code.name]=current
            continue
        raise SyntaxError(code)

    for index,var in enumerate(result):
        var.index = index

    with open(outputfile, 'wb') as file:
        for code in result:
            values = code.compile_code() # 获得 编码
            for value in values:
                result = value.to_bytes(1, byteorder='little')
                file.write(result)


def main():
    compile_program()
    # try:
    #     compile_program()
    # except SyntaxError as e:
    #     print(f'Syntax error at {e.code}')
    #     return

    print('compile program.asm finished!!!')


if __name__ == '__main__':
    main()





