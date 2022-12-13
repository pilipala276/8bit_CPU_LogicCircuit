# coding=utf-8
from ast import Pass
import pin
import assembly as ASM
import os

filename = "D:\8位二进制cpu的设计与实现\micro.bin"

micro = [pin.HLT for _ in range(0x10000)] # 在ROM里写满HLT指令

CJMPS={ASM.JO,ASM.JNO,ASM.JZ,ASM.JNZ,ASM.JP,ASM.JNP}

def compile_addr2(addr, ir, psw, index): # 处理二操作数的指令
    global micro

    op = ir & 0xf0 # 取出操作指令
    amd = (ir >> 2) & 3 # 取出目标操作数的寻址方式
    ams = ir & 3 # 取出源操作数的寻址方式

    INST = ASM.INSTRUCTIONS[2] # 取出二操作数的所有指令的列表
    if op not in INST:         # 遍历二操作数的所有指令看存不存在，如果不存在
        micro[addr] = pin.CYC # 跳过该指令
        return
    am = (amd, ams) # 目的操作数和源操作数合起来
    if am not in INST[op]: # 遍历该指令下的所有寻址方式，如果不存在
        micro[addr] = pin.CYC # 跳过该指令
        return

    EXEC = INST[op][am] # 假设指令和寻址方式都找到了，则拷贝出对应的微指令
    if index < len(EXEC): # 把指令补到后面
        micro[addr] = EXEC[index]
    else:
        micro[addr] = pin.CYC

def get_condition_jump(exec,op,psw):
    overflow= psw & 1
    zero= psw & 2
    parity= psw & 4

    if op ==ASM.JO and overflow:
        return exec
    if op ==ASM.JNO and not overflow:
        return exec
    if op ==ASM.JZ and zero:
        return exec
    if op ==ASM.JNZ and not zero:
        return exec
    if op ==ASM.JP and parity:
        return exec
    if op ==ASM.JNP and not parity:
        return exec
    return [pin.CYC]


def get_interrupt(exec,op,psw):
    interrupt = psw & 8
    if interrupt:
        return exec
    return [pin.CYC]



def compile_addr1(addr, ir, psw, index): # 处理一操作数的指令
    global micro
    global CJMPS

    op = ir & 0xfc # 取出操作指令
    ams = ir & 0x03 # 取出源操作数的寻址方式
    INST = ASM.INSTRUCTIONS[1] # 取出一操作数的所有指令的列表
    if op not in INST:         # 遍历一操作数的所有指令看存不存在，如果不存在
        micro[addr] = pin.CYC # 跳过该指令
        return
    am = ams # 目的操作数和源操作数合起来
    
    if am not in INST[op]: # 遍历该指令下的所有寻址方式，如果不存在
        micro[addr] = pin.CYC # 跳过该指令
        return     
    EXEC = INST[op][am] # 假设指令和寻址方式都找到了，则拷贝出对应的微指令
    if op in CJMPS:
        EXEC =get_condition_jump(EXEC,op,psw)
    if op == ASM.INT:
        EXEC =get_interrupt(EXEC,op,psw)

    if index < len(EXEC): # 把指令补到后面
        micro[addr] = EXEC[index]
    else:
        micro[addr] = pin.CYC


def compile_addr0(addr, ir, psw, index): # 处理零操作数的指令
    global micro

    op = ir # 取出操作指令

    INST = ASM.INSTRUCTIONS[0] # 取出零操作数的所有指令的列表
    if op not in INST: # 遍历二操作数的所有指令看存不存在，如果不存在
        micro[addr] = pin.CYC # 跳过该指令
        return

    EXEC = INST[op] # 假设指令找到了，则拷贝出对应的微指令
    if index < len(EXEC): # 把指令补到后面
        micro[addr] = EXEC[index]
    else:
        micro[addr] = pin.CYC

for addr in range(0x10000):
    ir = addr >> 8            # 从地址中取出IR即指令信息
    psw = (addr >> 4) & 0xf   # 从地址中取出PSW即状态字信息
    cyc = addr & 0xf          # 从地址中取出系统时钟周期信息

    if cyc < len(ASM.FETCH):  # 如果将指令一个个填充进去
        micro[addr] = ASM.FETCH[cyc]
        continue

    addr2 = ir & (1 << 7)    # 取出表示二操作数指令的位
    addr1 = ir & (1 << 6)    # 取出表示一操作数指令的位

    index = cyc - len(ASM.FETCH) # ASM.FETCH已经有6个指令

    if addr2: # 对操作数不同的指令分情况处理
        compile_addr2(addr, ir, psw, index)
    elif addr1:
        compile_addr1(addr, ir, psw, index)
    else:
        compile_addr0(addr, ir, psw, index)

with open(filename, 'wb') as file: # 转换成二进制
    for var in micro:
        value = var.to_bytes(4, byteorder='little')
        file.write(value)

print('Compile micro instruction finish!!!')