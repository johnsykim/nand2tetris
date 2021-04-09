// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Initialize
@R0
D=M
@n
M=D   // n=R0
@R1
D=M
@mult
M=D   // mult=R1
@prod
M=0   // prod=0

// Execute
(LOOP)
  @mult
  D=M
  @STOP
  D;JEQ   // if mult=0 exit LOOP
  @n
  D=M
  @prod
  M=M+D   // prod=prod+n
  @mult
  M=M-1   // mult=mult-1
  @LOOP
  0;JMP
(STOP)
  @prod
  D=M
  @R2
  M=D     // R2=prod
  @STOP
  0;JMP
