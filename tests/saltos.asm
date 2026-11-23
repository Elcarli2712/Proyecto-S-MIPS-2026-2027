# tests/saltos.asm - Control de flujo y procedimientos.
# Cubre (tabla de casos de la guia):
#   beq, bne : cada uno tomado y no tomado; un salto hacia atras    (lineas Q y R)
#   j        : al menos una vez                                      (linea J)
#   jal, jr  : procedimiento que llama a otro (no hoja) y uno
#              recursivo, guardando $ra en la pila; $sp vuelve a
#              su valor inicial                                      (linea P)
#   syscall  : servicios 11 (imprimir) y 10 (terminar)
# Tambien usa li, move, add, addi, sll, sw, lw y slt (dentro de la
# pseudoinstruccion blt).

        .text
main:
# --- Q: beq y bne. $s0 acumula 1, 2, 4, 8 segun que saltos NO se toman
        li      $a0, 'Q'
        jal     letra
        li      $s0, 0
        li      $t0, 5
        li      $t1, 5
        beq     $t0, $t1, q1            # tomado
        addi    $s0, $s0, 1             # no se ejecuta
q1:     move    $a0, $s0                # 00000000
        jal     phex
        li      $t1, 6
        beq     $t0, $t1, q2            # no tomado
        addi    $s0, $s0, 2
q2:     move    $a0, $s0                # 00000002
        jal     phex
        bne     $t0, $t1, q3            # tomado
        addi    $s0, $s0, 4             # no se ejecuta
q3:     move    $a0, $s0                # 00000002
        jal     phex
        li      $t1, 5
        bne     $t0, $t1, q4            # no tomado
        addi    $s0, $s0, 8
q4:     move    $a0, $s0                # 0000000a
        jal     phex
        jal     salto

# --- R: bucles con saltos hacia atras
        li      $a0, 'R'
        jal     letra
        li      $t0, 0                  # suma 1..5 con bne hacia atras
        li      $t1, 1
        li      $t2, 6
r1:     add     $t0, $t0, $t1
        addi    $t1, $t1, 1
        bne     $t1, $t2, r1
        move    $a0, $t0                # 0000000f
        jal     phex
        li      $t0, 1                  # duplicar hasta superar 1000 con blt
        li      $t3, 0
r2:     sll     $t0, $t0, 1
        addi    $t3, $t3, 1
        blt     $t0, 1000, r2           # slt + bne hacia atras
        move    $a0, $t0                # 00000400
        jal     phex
        move    $a0, $t3                # 0000000a
        jal     phex
        li      $t0, 3                  # beq hacia atras: cuenta atras hasta 0
        li      $t4, 0
r3:     addi    $t4, $t4, 7
        addi    $t0, $t0, -1
        beq     $t0, $zero, r3_fin
        beq     $zero, $zero, r3        # siempre tomado, hacia atras
r3_fin: move    $a0, $t4                # 00000015
        jal     phex
        jal     salto

# --- J: j salta por encima de una instruccion
        li      $a0, 'J'
        jal     letra
        li      $s1, 1
        j       j_fin
        li      $s1, 99                 # no se ejecuta
j_fin:  move    $a0, $s1                # 00000001
        jal     phex
        jal     salto

# --- P: procedimientos no hoja
        li      $a0, 'P'
        jal     letra
        li      $a0, 10
        jal     suma                    # suma(10) = 55 = 00000037
        jal     phex
        li      $a0, 6
        jal     doble_mas               # doble(6) + doble(7) = 26 = 0000001a
        jal     phex
        move    $a0, $sp                # la pila vuelve al valor inicial: 00003ffc
        jal     phex
        jal     salto

        li      $v0, 10
        syscall

# ---------------------------------------------------------------- procedimientos
# suma(n) = n + suma(n - 1), suma(0) = 0. Recursivo: guarda $ra y $a0 en la pila.
suma:
        addi    $sp, $sp, -8
        sw      $ra, 4($sp)
        sw      $a0, 0($sp)
        bne     $a0, $zero, suma_rec
        li      $a0, 0
        j       suma_fin
suma_rec:
        addi    $a0, $a0, -1
        jal     suma                    # $a0 = suma(n - 1)
        lw      $t0, 0($sp)
        add     $a0, $a0, $t0
suma_fin:
        lw      $ra, 4($sp)
        addi    $sp, $sp, 8
        jr      $ra

# doble_mas(x) = doble(x) + doble(x + 1). No hoja: llama dos veces a doble.
doble_mas:
        addi    $sp, $sp, -12
        sw      $ra, 8($sp)
        sw      $s0, 4($sp)
        sw      $a0, 0($sp)
        jal     doble
        move    $s0, $a0
        lw      $a0, 0($sp)
        addi    $a0, $a0, 1
        jal     doble
        add     $a0, $a0, $s0
        lw      $s0, 4($sp)
        lw      $ra, 8($sp)
        addi    $sp, $sp, 12
        jr      $ra

# doble(x) = 2x (hoja)
doble:
        sll     $a0, $a0, 1
        jr      $ra

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
