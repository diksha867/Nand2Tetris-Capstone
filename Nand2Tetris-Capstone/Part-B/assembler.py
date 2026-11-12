
import sys
import re
from pathlib import Path

# Predefined Hack symbols
SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

for i in range(16):
    SYMBOLS[f"R{i}"] = i

# Destination codes
DEST = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

# Computation codes
COMP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
}

# Jump codes
JUMP = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


def clean_lines(filename):
    """Remove comments and blank lines."""
    instructions = []

    with open(filename, "r") as file:
        for line_number, line in enumerate(file, 1):
            line = line.split("//")[0].strip()

            if line:
                instructions.append((line_number, line))

    return instructions


def first_pass(instructions):
    """Find labels and their ROM addresses."""

    rom_address = 0
    labels_seen = set()

    for line_number, line in instructions:

        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]

            if not re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", label):
                raise ValueError(
                    f"Line {line_number}: invalid label"
                )

            if label in labels_seen:
                print(
                    f"Warning: Line {line_number}: "
                    f"Label '{label}' is defined twice."
                )
                continue

            labels_seen.add(label)
            SYMBOLS[label] = rom_address

        else:
            if "(" in line or ")" in line:
                raise ValueError(
                    f"Line {line_number}: invalid label syntax"
                )

            rom_address += 1

    return instructions


def second_pass(instructions):
    """Convert instructions into 16-bit binary."""

    machine_code = []
    next_variable = 16

    for line_number, line in instructions:

        try:

            # Skip label declarations
            if line.startswith("(") and line.endswith(")"):
                continue

            # A-instruction
            if line.startswith("@"):

                symbol = line[1:].strip()

                if not symbol:
                    raise ValueError("empty A-instruction")

                if symbol.isdigit():
                    address = int(symbol)

                else:
                    if not re.fullmatch(
                        r"[A-Za-z_.$:][A-Za-z0-9_.$:]*",
                        symbol
                    ):
                        raise ValueError("invalid symbol")

                    if symbol not in SYMBOLS:
                        SYMBOLS[symbol] = next_variable
                        next_variable += 1

                    address = SYMBOLS[symbol]

                if not 0 <= address <= 32767:
                    raise ValueError("address out of range")

                binary = format(address, "016b")

            # C-instruction
            else:

                instruction = line.replace(" ", "")

                if instruction.count("=") > 1:
                    raise ValueError("invalid destination")

                if instruction.count(";") > 1:
                    raise ValueError("invalid jump")

                if "=" in instruction:
                    dest, instruction = instruction.split("=")
                else:
                    dest = ""

                if ";" in instruction:
                    comp, jump = instruction.split(";")
                else:
                    comp = instruction
                    jump = ""

                if not comp or dest not in DEST:
                    raise ValueError("invalid destination or computation")

                if comp not in COMP:
                    raise ValueError("invalid computation")

                if jump not in JUMP:
                    raise ValueError("invalid jump")

                binary = (
                    "111"
                    + COMP[comp]
                    + DEST[dest]
                    + JUMP[jump]
                )

            machine_code.append(binary)

        except ValueError as error:
            raise ValueError(
                f"Line {line_number}: {error}"
            ) from error

    return machine_code


def assemble(input_file):

    instructions = clean_lines(input_file)

    first_pass(instructions)

    machine_code = second_pass(instructions)

    output_file = Path(input_file).with_suffix(".hack")

    with open(output_file, "w") as file:
        file.write("\n".join(machine_code) + "\n")

    print("Assembly successful!")
    print("Output file:", output_file)
    print("Total instructions:", len(machine_code))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python assembler.py filename.asm")
    else:
        try:
            assemble(sys.argv[1])
        except (ValueError, OSError) as error:
            print("Assembler Error:", error)
