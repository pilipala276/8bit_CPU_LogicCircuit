;数据传送指令

; MOV C,0x2e

; MOV D,0x2c

; MOV A,[5]

; MOV B,[D]

; MOV [0x2f],5

; MOV [C],5

; MOV [C],A

; MOV [0x2e],A

; MOV [0x2d],[0x10]

; MOV [0x2c],[C]

; MOV [C],[0x11]

; MOV [D],[C]


;算术、逻辑运算指令

; MOV D,1

; MOV C,2

; ADD D,2

; ADD D,C

; SUB D,1

; SUB D,C

; MOV D,0xCE

; MOV C,0x28

; OR D,0x10

; OR D,C

; MOV D,0x02

; MOV C,0x24

; XOR D,0x11

; XOR D,C

; MOV D,2

; INC D

; DEC D

; NOT D

; MOV D,5

; MOV C,250

; CMP D,C

;转移指令
; MOV D,1

; INCREASE:

;     INC D
;     CMP D,7
;     JO INCREASE

; DECREASE:

;     DEC D
;     CMP D,0
;     JZ INCREASE
;     JMP DECREASE

;堆栈操作指令

; MOV ss,1

; MOV sp,0x10

; MOV D,10

; push D 
; push 1

; pop C
; pop B

; add C,B

; MOV D,C

;函数操作指令
; MOV ss,1

; MOV sp,0x20

; JMP START

; SHOW:
;     MOV D,255
;     RET

; START:
;     MOV C,0

; INCREASE:
;     INC C
;     MOV D,C
;     CALL SHOW
;     JMP INCREASE

;中断操作指令
mov ss,1

mov sp,0x20

jmp START

SHOW:
    mov D,255
    iret

START:
    mov C,0

INCREASE:
    inc C
    mov D,C
    jp DISABLE

ENABLE:
    sti
    jmp INTERRUPT

DISABLE:
    cli

INTERRUPT:
    int SHOW
    jmp INCREASE

    HLT;停止

