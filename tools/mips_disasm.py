#!/usr/bin/env python3
"""Minimal little-endian MIPS III disassembler for EE ELF snippets."""
from __future__ import annotations

import struct
from pathlib import Path

REGS = [
    "$0", "$at", "$v0", "$v1", "$a0", "$a1", "$a2", "$a3",
    "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7",
    "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
    "$t8", "$t9", "$k0", "$k1", "$gp", "$sp", "$fp", "$ra",
]
FUNCT = {
    0: "sll", 2: "srl", 3: "sra", 4: "sllv", 6: "srlv", 7: "srav",
    8: "jr", 9: "jalr", 0x0C: "syscall", 0x0D: "break",
    0x10: "mfhi", 0x12: "mflo", 0x18: "mult", 0x19: "multu",
    0x1A: "div", 0x1B: "divu", 0x20: "add", 0x21: "addu",
    0x22: "sub", 0x23: "subu", 0x24: "and", 0x25: "or",
    0x26: "xor", 0x27: "nor", 0x2A: "slt", 0x2B: "sltu",
    0x2D: "daddu", 0x2F: "dsubu",
}
OP = {
    2: "j", 3: "jal", 4: "beq", 5: "bne", 6: "blez", 7: "bgtz",
    8: "addi", 9: "addiu", 0x0A: "slti", 0x0B: "sltiu",
    0x0C: "andi", 0x0D: "ori", 0x0E: "xori", 0x0F: "lui",
    0x14: "beql", 0x15: "bnel", 0x16: "blezl", 0x17: "bgtzl",
    0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu",
    0x28: "sb", 0x29: "sh", 0x2B: "sw",
    0x1A: "ldl", 0x1B: "ldr", 0x27: "lwu", 0x37: "ld", 0x3F: "sd",
    0x31: "lwc1", 0x39: "swc1",
}

LOAD_V = 0x210000
LOAD_FILE = 0x1000


def va_to_off(va: int) -> int:
    return va - LOAD_V + LOAD_FILE


def s16(x: int) -> int:
    x &= 0xFFFF
    return x - 0x10000 if x >= 0x8000 else x


def disasm_word(pc: int, w: int) -> str:
    op = w >> 26
    rs = (w >> 21) & 31
    rt = (w >> 16) & 31
    rd = (w >> 11) & 31
    sa = (w >> 6) & 31
    fn = w & 63
    imm = w & 0xFFFF
    simm = s16(imm)
    target = ((pc + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
    if op == 0:
        name = FUNCT.get(fn, f"spec.{fn:02x}")
        if fn in (0, 2, 3):
            return f"{name} {REGS[rd]}, {REGS[rt]}, {sa}"
        if fn in (8,):
            return f"{name} {REGS[rs]}"
        if fn in (9,):
            return f"{name} {REGS[rd]}, {REGS[rs]}"
        if fn in (0x10, 0x12):
            return f"{name} {REGS[rd]}"
        if fn in (0x18, 0x19, 0x1A, 0x1B):
            return f"{name} {REGS[rs]}, {REGS[rt]}"
        return f"{name} {REGS[rd]}, {REGS[rs]}, {REGS[rt]}"
    if op in (2, 3):
        return f"{OP[op]} 0x{target:08x}"
    name = OP.get(op, f"op.{op:02x}")
    if op == 0x0F:
        return f"{name} {REGS[rt]}, 0x{imm:x}"
    if op in (4, 5, 0x14, 0x15):
        dest = pc + 4 + simm * 4
        return f"{name} {REGS[rs]}, {REGS[rt]}, 0x{dest:08x}"
    if op in (6, 7, 0x16, 0x17):
        dest = pc + 4 + simm * 4
        return f"{name} {REGS[rs]}, 0x{dest:08x}"
    if op in (8, 9, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E):
        if op in (0x0C, 0x0D, 0x0E):
            return f"{name} {REGS[rt]}, {REGS[rs]}, 0x{imm:x}"
        return f"{name} {REGS[rt]}, {REGS[rs]}, {simm}"
    if op in (0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B, 0x31, 0x39, 0x37, 0x3F):
        return f"{name} {REGS[rt]}, {simm}({REGS[rs]})"
    return f"{name} 0x{w:08x}"


def disasm_range(elf: bytes, va: int, n: int = 80) -> list[str]:
    lines = []
    off = va_to_off(va)
    for i in range(n):
        pc = va + i * 4
        w = struct.unpack_from("<I", elf, off + i * 4)[0]
        lines.append(f"{pc:08x}  {w:08x}  {disasm_word(pc, w)}")
    return lines


def find_func_start(elf: bytes, va: int, max_back: int = 0x800) -> int:
    """Walk backwards to a typical prologue addiu $sp."""
    off = va_to_off(va)
    for i in range(0, max_back, 4):
        pc = va - i
        if pc < LOAD_V:
            break
        w = struct.unpack_from("<I", elf, va_to_off(pc))[0]
        # addiu $sp, $sp, -imm
        if (w >> 16) == 0x27BD:
            # previous instr often not jr
            return pc
    return va


if __name__ == "__main__":
    import sys
    elf = Path("/home/ubuntu/translation/extracted/SLPM_658.39").read_bytes()
    va = int(sys.argv[1], 16)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    print("\n".join(disasm_range(elf, va, n)))
