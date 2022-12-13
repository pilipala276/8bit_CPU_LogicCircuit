# coding=utf-8
import pin

##定义指令
MOV = (0 << pin.ADDR2_SHIFT) | pin.ADDR2  # MOV指令定义位1000 xxxx
ADD = (1 << pin.ADDR2_SHIFT) | pin.ADDR2  # ADD指令定义为 1001 xxxx
SUB = (2 << pin.ADDR2_SHIFT) | pin.ADDR2  # SUB指令定义为 1010 xxxx
AND = (3 << pin.ADDR2_SHIFT) | pin.ADDR2  # AND指令定义为 1011 xxxx
OR = (4 << pin.ADDR2_SHIFT) | pin.ADDR2  # OR指令定义为 1100 xxxx
XOR = (5 << pin.ADDR2_SHIFT) | pin.ADDR2  # XOR指令定义为 1101 xxxx
CMP = (6 << pin.ADDR2_SHIFT) | pin.ADDR2  # SUB指令定义为 1110 xxxx

INC = (0 << pin.ADDR1_SHIFT) | pin.ADDR1  # INC指令定义为 010000 xx
DEC = (1 << pin.ADDR1_SHIFT) | pin.ADDR1  # DEC指令定义为 010001 xx

NOT = (2 << pin.ADDR1_SHIFT) | pin.ADDR1  # NOT指令定义为 010010 xx

JMP = (3 << pin.ADDR1_SHIFT) | pin.ADDR1  # JMP指令定义为 010011 xx
JO = (4 << pin.ADDR1_SHIFT) | pin.ADDR1  # JO指令定义为 010100 xx
JNO = (5 << pin.ADDR1_SHIFT) | pin.ADDR1  # JNO指令定义为 010101 xx
JZ = (6 << pin.ADDR1_SHIFT) | pin.ADDR1  # JZ指令定义为 010110 xx
JNZ = (7 << pin.ADDR1_SHIFT) | pin.ADDR1  # JNZ指令定义为 010111 xx
JP = (8 << pin.ADDR1_SHIFT) | pin.ADDR1  # JP指令定义为 011000 xx
JNP = (9 << pin.ADDR1_SHIFT) | pin.ADDR1  # JNP指令定义为 011001 xx

PUSH = (10 << pin.ADDR1_SHIFT) | pin.ADDR1  # PSUH指令定义为 011010 xx
POP = (11 << pin.ADDR1_SHIFT) | pin.ADDR1  # POP指令定义为 011011 xx

CALL = (12 << pin.ADDR1_SHIFT) | pin.ADDR1  # CALL指令定义为 011100 xx
INT = (13 << pin.ADDR1_SHIFT) | pin.ADDR1  # INT指令定义为 011101 xx

NOP = 0     # NOP指令定义为 0000 0000
RET = 1     # RET指令定义为 0000 0001
IRET = 2    # RET指令定义为 0000 0010
STI = 3     # STI指令定义为 0000 0011
CLI = 4     # CLI指令定义为 0000 0100


HLT = 0x3f  # HLT指令定义为 0011 1111


INSTRUCTIONS = {
    2: { # 二操作数指令列表
        MOV: { # MOV指令寻址方式列表
            (pin.AM_REG, pin.AM_INS): [  # (寄存器寻址，立即数) 例如 MOV C,5
                pin.DST_W | pin.SRC_OUT, # 微指令：DST寄存器写，SRC读，SRC->DST，这里DST_W是控制寄存器写
            ],
            (pin.AM_REG, pin.AM_REG): [  # (寄存器寻址，寄存器寻址) 例如 MOV D,C
                pin.DST_W | pin.SRC_R, # 微指令：DST寄存器写，SRC寄存器读，SRC->DST，这里DST_W是控制寄存器写,SRC_R是控制寄存器读
            ],
            (pin.AM_REG, pin.AM_DIR): [  # (寄存器寻址，直接寻址) 例如 MOV A,[5]
                pin.SRC_OUT | pin.MAR_IN,# 微指令：SRC寄存器中的数据取到MAR寄存器，使内存取到SRC中的数据对应的地址的数据
                pin.DST_W | pin.RAM_OUT, # 微指令：DST寄存器写，RAM寄存器读，RAM->DST，这里DST_W是控制寄存器写
            ],
            (pin.AM_REG, pin.AM_RAM): [  # (寄存器寻址，寄存器间接寻址) 例如MOV B,[D]
                pin.SRC_R | pin.MAR_IN,  # 微指令：SRC控制的寄存器中的数据取到MAR寄存器，使内存取到SRC控制的寄存器中的数据对应的地址的数据
                pin.DST_W | pin.RAM_OUT, # 微指令：DST寄存器写，RAM寄存器读，RAM->DST，这里DST_W是控制寄存器写
            ],
            (pin.AM_DIR, pin.AM_INS): [  # (直接寻址，立即数)，例如MOV [0x2f],5
                pin.DST_OUT | pin.MAR_IN,  # 微指令：DST中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_OUT, # 微指令：SRC中的数据存到RAM中
            ],
            (pin.AM_DIR, pin.AM_REG): [  # (直接寻址，寄存器寻址)，例如MOV [0x2f],A
                pin.DST_OUT | pin.MAR_IN,  # 微指令：DST中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_R, # 微指令：SRC控制的寄存器中的数据存到RAM中
            ],
            (pin.AM_DIR, pin.AM_DIR): [  # (直接寻址，直接寻址)，例如MOV [0x2e],[0x10]
                pin.SRC_OUT | pin.MAR_IN,# 微指令：SRC寄存器中的数据取到MAR寄存器，
                pin.RAM_OUT | pin.SRC_IN, # 微指令：RAM的数据存到SRC寄存器中
                pin.DST_OUT | pin.MAR_IN,  # 微指令：DST中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_OUT, # 微指令：SRC寄存器中的数据存到RAM中
            ],
            (pin.AM_DIR, pin.AM_RAM): [  # (直接寻址，寄存器间接寻址，例如MOV [0x2e],[c]
                pin.SRC_R | pin.MAR_IN,# 微指令：SRC控制的寄存器中的数据取到MAR寄存器，
                pin.RAM_OUT | pin.SRC_IN, # 微指令：RAM的数据存到SRC寄存器中
                pin.DST_OUT | pin.MAR_IN,  # 微指令：DST中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_OUT, # 微指令：SRC寄存器中的数据存到RAM中
            ],
            (pin.AM_RAM, pin.AM_INS): [  # (寄存器间接寻址，立即数)，例如MOV [C],5
                pin.DST_R | pin.MAR_IN,  # 微指令：DST控制的寄存器中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_OUT, # 微指令：SRC中的数据存到RAM中
            ],
            (pin.AM_RAM, pin.AM_REG): [  # (寄存器间接寻址，寄存器寻址)，例如MOV [C],A
                pin.DST_R | pin.MAR_IN,  # 微指令：DST控制的寄存器中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_R, # 微指令：SRC控制的寄存器中的数据存到RAM中
            ],
            (pin.AM_RAM, pin.AM_DIR): [  # (寄存器间接寻址，直接寻址)，例如MOV [C],[0x2e]
                pin.SRC_OUT | pin.MAR_IN,# 微指令：SRC中的数据取到MAR寄存器，
                pin.RAM_OUT | pin.SRC_IN, # 微指令：RAM的数据存到SRC寄存器中
                pin.DST_R | pin.MAR_IN,  # 微指令：DST控制的寄存器中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_OUT, # 微指令：SRC寄存器中的数据存到RAM中
            ],
            (pin.AM_RAM, pin.AM_RAM): [  # (寄存器间接寻址，寄存器间接寻址)，例如MOV [C],[D]
                pin.SRC_R | pin.MAR_IN,# 微指令：SRC中的数据取到MAR寄存器，
                pin.RAM_OUT | pin.SRC_IN, # 微指令：RAM的数据存到SRC寄存器中
                pin.DST_R | pin.MAR_IN,  # 微指令：DST中的数据（地址数据）存到MAR寄存器中
                pin.RAM_IN | pin.SRC_OUT, # 微指令：SRC寄存器中的数据存到RAM中
            ]
        },
        ADD: { # ADD指令寻址方式列表
            (pin.AM_REG, pin.AM_INS): [ 
                pin.DST_R | pin.A_IN, 
                pin.SRC_OUT | pin.B_IN, 
                pin.OP_ADD | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
            (pin.AM_REG, pin.AM_REG): [  
                pin.DST_R | pin.A_IN,
                pin.SRC_R | pin.B_IN, 
                pin.OP_ADD | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
        },
        SUB: { # SUB指令寻址方式列表
            (pin.AM_REG, pin.AM_INS): [ 
                pin.DST_R | pin.A_IN, 
                pin.SRC_OUT | pin.B_IN, 
                pin.OP_SUB | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
            (pin.AM_REG, pin.AM_REG): [  
                pin.DST_R | pin.A_IN,
                pin.SRC_R | pin.B_IN, 
                pin.OP_SUB | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
        },
        OR: { # OR指令寻址方式列表
            (pin.AM_REG, pin.AM_INS): [ 
                pin.DST_R | pin.A_IN, 
                pin.SRC_OUT | pin.B_IN, 
                pin.OP_OR | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
            (pin.AM_REG, pin.AM_REG): [  
                pin.DST_R | pin.A_IN,
                pin.SRC_R | pin.B_IN, 
                pin.OP_OR | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
        },
        XOR: { # XOR指令寻址方式列表
            (pin.AM_REG, pin.AM_INS): [ 
                pin.DST_R | pin.A_IN, 
                pin.SRC_OUT | pin.B_IN, 
                pin.OP_XOR | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
            (pin.AM_REG, pin.AM_REG): [  
                pin.DST_R | pin.A_IN,
                pin.SRC_R | pin.B_IN, 
                pin.OP_XOR | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
        },
        CMP: { # CMP指令寻址方式列表
            (pin.AM_REG, pin.AM_INS): [ 
                pin.DST_R | pin.A_IN, 
                pin.SRC_OUT | pin.B_IN, 
                pin.OP_SUB | pin.ALU_PSW
            ],
            (pin.AM_REG, pin.AM_REG): [  
                pin.DST_R | pin.A_IN,
                pin.SRC_R | pin.B_IN, 
                pin.OP_SUB |  pin.ALU_PSW
            ],
        },

    },
    1: {# 一操作数指令列表
        INC: { # INC指令寻址方式列表
            pin.AM_REG: [ 
                pin.DST_R | pin.A_IN,  
                pin.OP_INC | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
        },
        DEC: { # DEC指令寻址方式列表
            pin.AM_REG: [ 
                pin.DST_R | pin.A_IN,  
                pin.OP_DEC | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
        },
        NOT: { # NOT指令寻址方式列表
            pin.AM_REG: [ 
                pin.DST_R | pin.A_IN,  
                pin.OP_NOT | pin.ALU_OUT | pin.DST_W | pin.ALU_PSW
            ],
        },
        JMP: { # JMP指令寻址方式列表
            pin.AM_INS: [ 
                pin.DST_OUT | pin.PC_IN,
            ],
        },
        JO: { # JO指令寻址方式列表
            pin.AM_INS: [ 
                pin.DST_OUT | pin.PC_IN,
            ],
        },
        JNO: { # JNO指令寻址方式列表
            pin.AM_INS: [ 
                pin.DST_OUT | pin.PC_IN,
            ],
        },
        JZ: { # JZ指令寻址方式列表
            pin.AM_INS: [ 
                pin.DST_OUT | pin.PC_IN,
            ],
        },
        JNZ: { # JNZ指令寻址方式列表
            pin.AM_INS: [ 
                pin.DST_OUT | pin.PC_IN,
            ],
        },
        JP: { # JP指令寻址方式列表
            pin.AM_INS: [ 
                pin.DST_OUT | pin.PC_IN,
            ],
        },
        JNP: { # JNP指令寻址方式列表
            pin.AM_INS: [ 
                pin.DST_OUT | pin.PC_IN,
            ],
        },
        PUSH:{# PUSH指令寻址方式列表
            pin.AM_REG: [ 
                pin.SP_OUT | pin.A_IN,
                pin.OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT  | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.DST_R | pin.RAM_IN,
                pin.CS_OUT | pin.MSR_IN,
            ],
            pin.AM_INS: [ 
                pin.SP_OUT | pin.A_IN,
                pin.OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.DST_OUT | pin.RAM_IN,
                pin.CS_OUT | pin.MSR_IN,
            ],
        },
        POP:{# POP指令寻址方式列表
            pin.AM_REG: [ 
                pin.SS_OUT | pin.MSR_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.DST_W | pin.RAM_OUT,
                pin.SP_OUT | pin.A_IN,
                pin.OP_INC | pin.ALU_OUT | pin.SP_IN,
                pin.CS_OUT | pin.MSR_IN,
            ],
        },
        CALL:{# CALL指令寻址方式列表
            pin.AM_REG: [ 
                pin.SP_OUT | pin.A_IN,
                pin.OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT  | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.PC_OUT | pin.RAM_IN,
                pin.DST_R | pin.PC_IN,
                pin.CS_OUT | pin.MSR_IN,
            ],
            pin.AM_INS: [ 
                pin.SP_OUT | pin.A_IN,
                pin.OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.PC_OUT | pin.RAM_IN,
                pin.DST_OUT | pin.PC_IN,
                pin.CS_OUT | pin.MSR_IN,
            ],
        },
        INT:{# INT指令寻址方式列表
            pin.AM_REG: [ 
                pin.SP_OUT | pin.A_IN,
                pin.OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT  | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.PC_OUT | pin.RAM_IN,
                pin.DST_R | pin.PC_IN,
                pin.CS_OUT | pin.MSR_IN | pin.ALU_PSW | pin.ALU_CLI,
            ],
            pin.AM_INS: [ 
                pin.SP_OUT | pin.A_IN,
                pin.OP_DEC | pin.ALU_OUT | pin.SP_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.SS_OUT | pin.MSR_IN,
                pin.PC_OUT | pin.RAM_IN,
                pin.DST_OUT | pin.PC_IN,
                pin.CS_OUT | pin.MSR_IN | pin.ALU_PSW | pin.ALU_CLI,
            ],
        },
        


    },
    0: {  # 零操作数指令列表
        NOP: [
            pin.CYC, # 让指令周期清零，跳过这次指令
        ],
        RET:[# RET指令寻址方式列表
                pin.SS_OUT | pin.MSR_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.PC_IN | pin.RAM_OUT,
                pin.SP_OUT | pin.A_IN,
                pin.OP_INC | pin.ALU_OUT | pin.SP_IN,
                pin.CS_OUT | pin.MSR_IN,
            
        ],
        IRET:[# ORET指令寻址方式列表
                pin.SS_OUT | pin.MSR_IN,
                pin.SP_OUT | pin.MAR_IN,
                pin.PC_IN | pin.RAM_OUT,
                pin.SP_OUT | pin.A_IN,
                pin.OP_INC | pin.ALU_OUT | pin.SP_IN,
                pin.CS_OUT | pin.MSR_IN | pin.ALU_PSW | pin.ALU_STI,
            
        ],
        STI:[# STI指令寻址方式列表
                pin.ALU_PSW | pin.ALU_STI,
        ],
        CLI:[# CLI指令寻址方式列表
                pin.ALU_PSW | pin.ALU_CLI,
        ],
        HLT: [
            pin.HLT, # 指令停止
        ]
    }
}






FETCH = [
    pin.PC_OUT | pin.MAR_IN,
    pin.RAM_OUT | pin.IR_IN | pin.PC_INC,
    pin.PC_OUT | pin.MAR_IN,
    pin.RAM_OUT | pin.DST_IN | pin.PC_INC,
    pin.PC_OUT | pin.MAR_IN,
    pin.RAM_OUT | pin.SRC_IN | pin.PC_INC,
]
