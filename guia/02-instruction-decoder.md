# Instruction_Decoder

Circuito combinacional, sin estado. Recibe `Opcode` (IR[31:26]) y `Funct` (IR[5:0]) y dice qué instrucción es.

## Cómo está construido

1. Un **Decoder** de 6 bits sobre `Opcode`: activa una línea por opcode. Solo se usan las de S-MIPS (túneles `opR`, `opADDI`, `opLW`…).
2. Otro **Decoder** de 6 bits sobre `Funct` (túneles `fADD`, `fSLL`…).
3. Las instrucciones tipo R son `opR AND fXXX` (túneles `isADD`, `isSUB`…). Así `funct` solo cuenta cuando `op = 0` (R11).
4. Puertas **OR** agrupan las instrucciones en clases y forman los bits de `ALUOp`.
5. `Illegal = NOT (alguna clase)`: cualquier par (op, funct) que no esté en la tabla es ilegal (R10).

## Salidas

| Salida | Ancho | Vale 1 para |
|---|---|---|
| `RType` | 1 | add, addu, sub, and, or, slt, sll, srl |
| `ImmALU` | 1 | addi, addiu, slti, andi, ori, lui |
| `Load` | 1 | lw, lb, lbu |
| `Store` | 1 | sw, sb |
| `Branch` | 1 | beq, bne |
| `Jump` | 1 | j, jal |
| `Jr` | 1 | jr |
| `SysCall` | 1 | syscall |
| `Illegal` | 1 | ninguna de las anteriores |
| `ALUOp` | 3 | operación de la ALU en el ciclo de ejecución (tabla abajo) |
| `LoadType` | 2 | `00` lb (con signo), `01` lbu (con ceros), `10` lw |
| `IsSb` | 1 | sb (escritura de un byte) |
| `IsAndi`, `IsOri` | 1 | andi / ori (inmediato extendido con ceros) |
| `IsLui` | 1 | lui (el resultado es `{imm, 0x0000}`) |
| `IsJal` | 1 | jal (escribe PC+4 en `$31`) |
| `IsBne` | 1 | bne (salta si **no** son iguales) |

## Codificación de `ALUOp`

| ALUOp | Operación | Instrucciones |
|---|---|---|
| `000` | ADD | add, addu, addi, addiu, lui, cargas y almacenamientos |
| `001` | SUB | sub, beq, bne |
| `010` | AND | and, andi |
| `011` | OR | or, ori |
| `100` | SLT | slt, slti |
| `101` | SLL | sll |
| `110` | SRL | srl |

Fórmulas usadas:

- `ALUOp[0] = sub | beq | bne | or | ori | sll`
- `ALUOp[1] = and | andi | or | ori | srl`
- `ALUOp[2] = slt | slti | sll | srl`

## Comprobación

Se probaron las 25 instrucciones (23 de S-MIPS más addu y addiu) y 4 palabras ilegales (op `0x3F`, op `0x01`, funct `0x01` y funct `0x18`). Las 29 dieron las salidas esperadas.
