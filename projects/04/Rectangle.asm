// Rectangle.asm

// Initialize

  // addr = SCREEN
  @SCREEN
  D=A
  @addr
  M=D

  // n = RAM[0]
  @R0
  D=M
  @n
  M=D

  // i=0
  @i
  M=0

// Execute
(LOOP)

  // if i>n goto END
  @i
  D=M
  @n
  D=D-M
  @END
  D;JGT

  // RAM[addr] = -1
  @addr
  A=M
  M=-1

  // i = i + 1
  @i
  M=M+1

  // addr = addr + 32
  @32
  D=A
  @addr
  M=D+M

  // goto LOOP
  @LOOP
  0;JMP

(END)
  @END
  0;JMP
