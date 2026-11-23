# Programas de prueba propios (`tests/`)

Cada programa imprime una letra por grupo de pruebas y, a continuación, los valores calculados en hexadecimal. Usa solo instrucciones de S-MIPS, las pseudoinstrucciones vistas en clase (`li`, `la`, `move`, `blt`) y los servicios 11 y 10.

## Tabla de cobertura

| Instrucciones | Caso obligatorio | Programa (línea de salida) |
|---|---|---|
| add, sub | Operandos positivos y con un operando negativo | `alu.asm` (A) |
| and, or | Operandos con unos en los 16 bits altos | `alu.asm` (L) |
| slt, slti | Resultado 1 y 0; `-7 < 25` y `25 < -1` dan distinto con y sin signo | `alu.asm` (C) |
| sll, srl | shamt = 0 y ≠ 0; srl de un negativo (entran ceros) | `alu.asm` (D) |
| addi | Inmediato negativo (−150) | `alu.asm` (I) |
| addiu, addu | `li` con −32768, 32767, −7, 25, 100 y `move` (más un `addu` explícito) | `alu.asm` (I) |
| andi, ori | Inmediato con el bit 15 a 1 (`0x8001`, `0x8000`) | `alu.asm` (L) |
| lui | Inmediato con el bit 15 a 1 (`0x8001`, `0xABCD`) | `alu.asm` (Z) |
| lw, sw | Desplazamiento positivo y negativo | `memoria.asm` (W, S) |
| lb, lbu | Bytes con el bit 7 a 1 en `d[1:0] = 2` y `3` (y uno con bit 7 a 0) | `memoria.asm` (B, U) |
| sb | Las 4 posiciones de una palabra, con `lw` después de cada una; las palabras vecinas no cambian | `memoria.asm` (X) |
| beq, bne | Cada uno tomado y no tomado; saltos hacia atrás con bne, beq y blt | `saltos.asm` (Q, R) |
| j | Salta por encima de una instrucción | `saltos.asm` (J) |
| jal, jr | `suma` recursiva y `doble_mas`, que llama dos veces a `doble`; los dos guardan `$ra` en la pila y `$sp` vuelve a `0x3FFC` | `saltos.asm` (P) |
| syscall | Servicio 11 en todas las líneas y 10 al final de cada programa | todos |
| `$zero` | `addi`, `add` y `lui` escriben en `$zero`; después vale 0 | `alu.asm` (Z) |

## Salida esperada (MARS) y obtenida (CPU)

```
alu.asm
A 0000007d 0000005d 0000004b ffffffb5 0000006b
L f000f000 fff0fff0 00008001 00008000 00008019
C 00000001 00000000 00000001 00000000 00000001
D 00000019 00000190 00000019 0fffffff 90000000
I ffffffce ffff8000 00007fff fffffff9 0000007d
Z 80010000 abcd1234 00000000 00000019 ffffffe7

memoria.asm
W 11223344 8899aabb 55667788 11223344
S 12345678 fffffffe 8899aabb
B ffffffff ffffff80 0000007f 00000001
U 000000ff 00000080 0000007f
X cafeba11 cafea211 ca33a211 c433a211 00000000

saltos.asm
Q 00000000 00000002 00000002 0000000a
R 0000000f 00000400 0000000a 00000015
J 00000001
P 00000037 0000001a 00003ffc
```

El resultado completo de `run_tests.py` está en [`salida-tests.txt`](../salida-tests.txt): 10/10 correctos.
