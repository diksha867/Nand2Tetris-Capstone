
// Computes maximum of R0 and R1
// Stores result in R2

@R0
D=M

@R1
D=D-M

@OUTPUT_FIRST
D;JGT

@R1
D=M

@OUTPUT
0;JMP

(OUTPUT_FIRST)
@R0
D=M

(OUTPUT)
@R2
M=D

(INFINITE_LOOP)
@INFINITE_LOOP
0;JMP
