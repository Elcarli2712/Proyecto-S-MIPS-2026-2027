# tests/alu.asm - Instrucciones aritmeticas, logicas y con inmediato.
# Cubre (tabla de casos de la guia):
#   add, sub     : operandos positivos y con un operando negativo           (linea A)
#   and, or      : operandos con unos en los 16 bits altos                  (linea L)
#   andi, ori    : inmediato con el bit 15 a 1 (extension con ceros)        (linea L)
#   slt, slti    : resultado 1 y 0; con negativo donde con y sin signo
#                  darian distinto (-7 < 25, 25 < -1)                       (linea C)
#   sll, srl     : shamt = 0 y shamt != 0; srl de un negativo (entran 0)   (linea D)
#   addi         : inmediato negativo                                       (linea I)
#   addiu, addu  : mediante li (constantes de 16 bits con signo) y move     (linea I)
#   lui          : inmediato con el bit 15 a 1                              (linea Z)
#   $zero        : escribir en $zero y comprobar que sigue valiendo 0       (linea Z)
#   syscall      : servicio 11 (imprimir) y 10 (terminar)
# Cada linea: una letra y cinco valores en hexadecimal.

        .text
main:
        li      $s0, 100                # addiu
        li      $s1, 25                 # addiu
        li      $s2, -7                 # addiu (negativo)

# --- A: add y sub
        li      $a0, 'A'
        jal     letra
        add     $a0, $s0, $s1           # 100 + 25 = 0000007d
        jal     phex
        add     $a0, $s0, $s2           # 100 + (-7) = 0000005d
        jal     phex
        sub     $a0, $s0, $s1           # 100 - 25 = 0000004b
        jal     phex
        sub     $a0, $s1, $s0           # 25 - 100 = ffffffb5
        jal     phex
        sub     $a0, $s0, $s2           # 100 - (-7) = 0000006b
        jal     phex
        jal     salto

# --- L: and, or, andi, ori
        li      $a0, 'L'
        jal     letra
        li      $s3, 0xF0F0FF00         # lui + ori
        li      $s4, 0xFF00F0F0
        and     $a0, $s3, $s4           # f000f000
        jal     phex
        or      $a0, $s3, $s4           # fff0fff0
        jal     phex
        andi    $a0, $s2, 0x8001        # fffffff9 & 00008001 = 00008001
        jal     phex
        ori     $a0, $zero, 0x8000      # 00008000
        jal     phex
        ori     $a0, $s1, 0x8001        # 00000019 | 00008001 = 00008019
        jal     phex
        jal     salto

# --- C: slt y slti (con signo)
        li      $a0, 'C'
        jal     letra
        slt     $a0, $s2, $s1           # -7 < 25 -> 1 (sin signo daria 0)
        jal     phex
        slt     $a0, $s1, $s2           # 25 < -7 -> 0
        jal     phex
        slti    $a0, $s2, 1             # -7 < 1 -> 1 (sin signo daria 0)
        jal     phex
        slti    $a0, $s1, -1            # 25 < -1 -> 0 (sin signo daria 1)
        jal     phex
        slti    $a0, $s1, 30            # 25 < 30 -> 1
        jal     phex
        jal     salto

# --- D: sll y srl
        li      $a0, 'D'
        jal     letra
        sll     $a0, $s1, 0             # 00000019
        jal     phex
        sll     $a0, $s1, 4             # 00000190
        jal     phex
        srl     $a0, $s1, 0             # 00000019
        jal     phex
        srl     $a0, $s2, 4             # fffffff9 >> 4 = 0fffffff
        jal     phex
        sll     $a0, $s2, 28            # 90000000
        jal     phex
        jal     salto

# --- I: addi negativo, li y move
        li      $a0, 'I'
        jal     letra
        addi    $a0, $s0, -150          # 100 - 150 = ffffffce
        jal     phex
        li      $a0, -32768             # ffff8000
        jal     phex
        li      $a0, 32767              # 00007fff
        jal     phex
        move    $t0, $s2                # addu: fffffff9
        move    $a0, $t0
        jal     phex
        addu    $a0, $s0, $s1           # 0000007d
        jal     phex
        jal     salto

# --- Z: lui y $zero
        li      $a0, 'Z'
        jal     letra
        lui     $a0, 0x8001             # 80010000
        jal     phex
        lui     $t0, 0xABCD
        ori     $a0, $t0, 0x1234        # abcd1234
        jal     phex
        addi    $zero, $s0, 5           # escribir en $zero no tiene efecto
        add     $zero, $s0, $s1
        lui     $zero, 0xFFFF
        move    $a0, $zero              # 00000000
        jal     phex
        add     $a0, $zero, $s1         # 0 + 25 = 00000019
        jal     phex
        sub     $a0, $zero, $s1         # 0 - 25 = ffffffe7
        jal     phex
        jal     salto

        li      $v0, 10
        syscall

# ---------------------------------------------------------------- rutinas
# phex: imprime $a0 como 8 cifras hexadecimales y un espacio (usa $t7-$t9)
phex:
        move    $t9, $a0
        li      $t8, 8
phex_cifra:
        srl     $a0, $t9, 28
        sll     $t9, $t9, 4
        slti    $t7, $a0, 10
        bne     $t7, $zero, phex_dec
        addi    $a0, $a0, 39            # 'a' - '0' - 10
phex_dec:
        addi    $a0, $a0, 48            # '0'
        li      $v0, 11
        syscall
        addi    $t8, $t8, -1
        bne     $t8, $zero, phex_cifra
        li      $a0, ' '
        li      $v0, 11
        syscall
        jr      $ra

# letra: imprime el caracter de $a0 y un espacio
letra:
        li      $v0, 11
        syscall
        li      $a0, ' '
        syscall
        jr      $ra

# salto: imprime un salto de linea
salto:
        li      $a0, 10
        li      $v0, 11
        syscall
        jr      $ra
