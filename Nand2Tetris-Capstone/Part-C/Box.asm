
// Nand2Tetris Capstone - Part C
// K = 77
// Box: 32 pixels wide, 20 rows tall

(LOOP)
    // Check keyboard
    @KBD
    D=M

    @BLACK
    D;JGT

    // No key pressed: white
    @R12
    M=0
    @PREP
    0;JMP

(BLACK)
    // Key pressed: black
    @R12
    M=-1

(PREP)
    // Starting screen address = 18848
    @18848
    D=A
    @R13
    M=D

    // 20 rows
    @20
    D=A
    @R14
    M=D

(ROW)
    // 2 words = 32 pixels
    @2
    D=A
    @R15
    M=D

(WORD)
    // Draw current word
    @R12
    D=M
    @R13
    A=M
    M=D

    // Move to next word
    @R13
    M=M+1

    // Decrease word counter
    @R15
    MD=M-1
    @WORD
    D;JGT

    // Skip remaining 30 words
    @30
    D=A
    @R13
    M=D+M

    // Decrease row counter
    @R14
    MD=M-1
    @ROW
    D;JGT

    // Check keyboard again
    @LOOP
    0;JMP
