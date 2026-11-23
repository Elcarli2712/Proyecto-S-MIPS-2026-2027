# tests/memoria.asm - Acceso a memoria.
# Cubre (tabla de casos de la guia):
#   lw, sw  : desplazamiento positivo y negativo                       (lineas W y S)
#   lb, lbu : bytes con el bit 7 a 1 en dos posiciones distintas
#             de la palabra (d[1:0] = 2 y 3), y uno con bit 7 a 0      (lineas B y U)
#   sb      : en las cuatro posiciones de una palabra (d[1:0] = 0..3),
#             leyendo con lw despues de cada uno: los otros bytes
#             no cambian; tambien la palabra vecina                     (linea X)
#   syscall : servicios 11 y 10
# Tambien usa la (lui + ori), li (addiu / lui + ori), addi, jal, jr.

        .data
tabla:  .word   0x11223344, 0x55667788, 0x8899AABB
bytes:  .word   0x80FF7F01              # byte0=01 byte1=7f byte2=ff byte3=80
buf:    .word   0x00000000, 0xCAFEBABE, 0x00000000

        .text
main:
        la      $s0, tabla
        addi    $s1, $s0, 8             # $s1 apunta a tabla[2]

# --- W: lw con desplazamiento positivo y negativo
        li      $a0, 'W'
        jal     letra
        lw      $a0, 0($s0)             # 11223344
        jal     phex
        lw      $a0, 8($s0)             # 8899aabb
        jal     phex
        lw      $a0, -4($s1)            # 55667788
        jal     phex
        lw      $a0, -8($s1)            # 11223344
        jal     phex
        jal     salto

# --- S: sw con desplazamiento positivo y negativo
        li      $a0, 'S'
        jal     letra
        li      $t1, 0x12345678
        sw      $t1, 4($s0)             # tabla[1]
        lw      $a0, 4($s0)             # 12345678
        jal     phex
        li      $t1, -2
        sw      $t1, -8($s1)            # tabla[0]
        lw      $a0, 0($s0)             # fffffffe
        jal     phex
        lw      $a0, 0($s1)             # tabla[2] no cambia: 8899aabb
        jal     phex
        jal     salto

# --- B: lb (extension con signo)
        la      $s2, bytes
        li      $a0, 'B'
        jal     letra
        lb      $a0, 2($s2)             # ff -> ffffffff
        jal     phex
        lb      $a0, 3($s2)             # 80 -> ffffff80
        jal     phex
        lb      $a0, 1($s2)             # 7f -> 0000007f
        jal     phex
        lb      $a0, 0($s2)             # 01 -> 00000001
        jal     phex
        jal     salto

# --- U: lbu (extension con ceros)
        li      $a0, 'U'
        jal     letra
        lbu     $a0, 2($s2)             # 000000ff
        jal     phex
        lbu     $a0, 3($s2)             # 00000080
        jal     phex
        addi    $s3, $s2, 4
        lbu     $a0, -3($s3)            # byte1, desplazamiento negativo: 0000007f
        jal     phex
        jal     salto

# --- X: sb en las cuatro posiciones de buf[1] (inicialmente cafebabe)
        la      $s4, buf
        li      $a0, 'X'
        jal     letra
        li      $t1, 0x7711             # solo se guarda el byte bajo (11)
        sb      $t1, 4($s4)
        lw      $a0, 4($s4)             # cafeba11
        jal     phex
        li      $t1, 0xA2
        sb      $t1, 5($s4)
        lw      $a0, 4($s4)             # cafea211
        jal     phex
        li      $t1, 0x33
        sb      $t1, 6($s4)
        lw      $a0, 4($s4)             # ca33a211
        jal     phex
        li      $t1, -60                # ffffffc4: byte c4
        sb      $t1, 7($s4)
        lw      $a0, 4($s4)             # c433a211
        jal     phex
        lw      $t0, 0($s4)             # palabras vecinas sin cambios: 0 + 0
        lw      $t1, 8($s4)
        or      $a0, $t0, $t1           # 00000000
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
        addi    $a0, $a0, 39
phex_dec:
        addi    $a0, $a0, 48
        li      $v0, 11
        syscall
        addi    $t8, $t8, -1
        bne     $t8, $zero, phex_cifra
        li      $a0, ' '
        li      $v0, 11
        syscall
        jr      $ra

letra:
        li      $v0, 11
        syscall
        li      $a0, ' '
        syscall
        jr      $ra

salto:
        li      $a0, 10
        li      $v0, 11
        syscall
        jr      $ra
