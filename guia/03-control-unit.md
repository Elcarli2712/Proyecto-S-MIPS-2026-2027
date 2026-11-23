# Control_Unit, Branch_Control y CPU

## Control_Unit: máquina de estados de Moore

- **Estado:** un registro `ESTADO` de 4 bits. Reloj = `CLK` directo y Clear = `RESET`, así que con RESET el estado es S0 (R6).
- **Decodificador del estado:** convierte `ESTADO` en 16 líneas `S0`…`S15`, de las que solo una vale 1.
- **Próximo estado:** un multiplexor de 16 entradas elegido por `ESTADO`. Cada entrada es una constante, salvo en DECODE, MEM_ADDR y SYSCALL, donde el destino depende de la instrucción.
- **Salidas:** dependen solo del estado (Moore). Algunas se combinan además con una señal del decodificador (`IsJal`, el valor de `$v0`).

### Estados y transiciones

| Estado | Nombre | Qué hace | Siguiente |
|---|---|---|---|
| S0 | FETCH | `IR ← M[PC]`, `PC ← PC + 4` (con la ALU) | S1 |
| S1 | DECODE | `A ← R[rs]`, `B ← R[rt]` (`$v0` y `$a0` si es syscall); `ALUOut ← PC + (SignExt(imm) << 2)` | según la clase |
| S2 | MEM_ADDR | `ALUOut ← A + SignExt(imm)` | Load → S3, Store → S5 |
| S3 | MEM_READ | `MDR ← byte o palabra de M[ALUOut]` (según `LoadType`) | S4 |
| S4 | LOAD_WB | `R[rt] ← MDR` | S0 |
| S5 | STORE | `M[ALUOut] ← B` (`MEM_WE = 1`; con sb, un solo byte) | S0 |
| S6 | EXEC_R | `ALUOut ← A op B` | S7 |
| S7 | R_WB | `R[rd] ← ALUOut` | S0 |
| S8 | EXEC_I | `ALUOut ← A op Ext(imm)` (lui: `{imm, 0}`) | S14 |
| S14 | I_WB | `R[rt] ← ALUOut` | S0 |
| S9 | BRANCH | `A − B`; si se cumple la condición, `PC ← ALUOut` | S0 |
| S10 | JUMP | `PC ← {PC[31:28], dir, 00}`; jal: `R[31] ← PC` (ya vale PC+4) | S0 |
| S11 | JR | `PC ← A` | S0 |
| S12 | SYSCALL | si `$v0 = 11`: `TTY_WE = 1` con `TTY_DATA = $a0[6:0]` | `$v0 = 10` → S13, si no S0 |
| S13 | HALT | `HALT = 1`, no escribe nada | S13 (hasta RESET) |

Desde DECODE: RType → S6, ImmALU → S8, Load/Store → S2, Branch → S9, Jump → S10, Jr → S11, SysCall → S12, Illegal → S13.

### Señales de control en cada estado

Las señales que no aparecen en una fila valen 0.

| Estado | Señales a 1 | ALUSrcA | ALUSrcB | ALU_Control | PCSource |
|---|---|---|---|---|---|
| S0 FETCH | IRwr, PCWrite | 0 (PC) | 00 (4) | 000 | 10 (ALU) |
| S1 DECODE | Awr, Bwr, ALUwr | 0 (PC) | 11 (SignExt≪2) | 000 | — |
| S2 MEM_ADDR | ALUwr | 1 (A) | 10 (Ext) | 000 | — |
| S3 MEM_READ | lorD, MDRwr | — | — | — | — |
| S4 LOAD_WB | RegDst, MemToReg, REG_WR | — | — | — | — |
| S5 STORE | lorD, MemWr | — | — | — | — |
| S6 EXEC_R | ALUwr | 1 (A) | 01 (B) | ALUOp | — |
| S7 R_WB | REG_WR | — | — | — | — |
| S8 EXEC_I | ALUwr | 1 (A) | 10 (Ext) | ALUOp | — |
| S14 I_WB | RegDst, REG_WR | — | — | — | — |
| S9 BRANCH | PCWriteCond | 1 (A) | 01 (B) | 001 (SUB) | 01 (ALUOut) |
| S10 JUMP | PCWrite; REG_WR si IsJal | — | — | — | 11 (salto) |
| S11 JR | PCWrite | — | — | — | 00 (A) |
| S12 SYSCALL | TTY si `$v0 = 11` | — | — | — | — |
| S13 HALT | HALT | — | — | — | — |

`RegDst`: 0 = rd, 1 = rt. Con `IsJal`, el registro destino es 31 y el dato es el PC.

### Ciclos por instrucción

| Clase | Ciclos |
|---|---|
| Tipo R, inmediato, sw/sb | 4 |
| lw/lb/lbu | 5 |
| beq/bne, j/jal, jr, syscall | 3 |

## Branch_Control

`PCEnable = PCWrite OR (PCWriteCond AND (Zero XOR IsBne))`

En beq se escribe el PC si `Zero = 1`; en bne, si `Zero = 0`.

## CPU

Dentro de `CPU` están `Instruction_Decoder`, `Control_Unit`, `Branch_Control` y `Datapath`, unidos por túneles con el nombre de cada señal. `CLK` y `RESET` van directos del pin a cada subcircuito, sin lógica en el camino del reloj (R3).

## Resultado de `run_tests.py`

```
OK    programs\arithmetic.asm  (6291 ciclos)
OK    programs\array_sum.asm  (882 ciclos)
OK    programs\branches.asm  (895 ciclos)
OK    programs\gcd.asm  (2743 ciclos)
OK    programs\hello.asm  (283 ciclos)
OK    programs\memory.asm  (4796 ciclos)
OK    programs\multiply.asm  (1904 ciclos)

7/7 correctos
```
