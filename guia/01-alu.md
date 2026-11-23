# Paso 1 — La ALU

**Objetivo:** un circuito combinacional que recibe dos números de 32 bits (`A`, `B`) y un código de 3 bits (`ALUOp`), y devuelve `Result` y `Zero`.

## Codificación (apúntala; la usarás en el decodificador)

| ALUOp | Operación | Instrucciones que la usan |
|---|---|---|
| `000` | A + B | add, addu, addi, addiu, lw, sw, lb, lbu, sb, lui, PC+4, destino de salto |
| `001` | A − B | sub, beq, bne |
| `010` | A AND B | and, andi |
| `011` | A OR B | or, ori |
| `100` | 1 si A < B (con signo), si no 0 | slt, slti |
| `101` | B desplazado a la izquierda A[4:0] posiciones | sll |
| `110` | B desplazado a la derecha A[4:0] posiciones (entran ceros) | srl |
| `111` | 0 | (no se usa) |

## Esquema de lo que vas a construir

```
 A ──┬──────────────► [Adder] a                                  
     │      B ─►[XOR]─► [Adder] b ──► SUMA ───────► entrada 0 ┐
     │   esResta ─┘     carry in ◄─ esResta         entrada 1 ┤
     ├─► [AND] ◄─ B  ───────────► AND_RES ────────► entrada 2 │
     ├─► [OR]  ◄─ B  ───────────► OR_RES  ────────► entrada 3 │  MUX 8:1
     ├─► [Comparator <] ─► ext ─► SLT_RES ────────► entrada 4 ├──► Result ──► [= 0 ?] ──► Zero
     └─► [5 bits bajos] ─► SH                                 │
          B ─► [Shifter izq] ◄─ SH ─► SLL_RES ────► entrada 5 │
          B ─► [Shifter der] ◄─ SH ─► SRL_RES ────► entrada 6 │
                                     constante 0 ─► entrada 7 ┘
                                             ALUOp ─► selector
```

Trabajaremos con **túneles** (ver 0.9): cada señal tendrá un nombre y no hará falta tirar cables largos.

---

## 1.1 Abrir la ALU

Pestaña **Design** → **doble clic** en `ALU`. El lienzo está vacío.

## 1.2 Pines de entrada

Coloca tres pines de entrada en la parte izquierda del lienzo, uno debajo de otro, separados unas 6 cuadrículas.

Para cada uno: botón **□** de la barra → clic en el lienzo → con la flecha ↖, clic sobre el pin → en la tabla de propiedades pon:

| Label | Data Bits |
|---|---|
| `A` | 32 |
| `B` | 32 |
| `ALUOp` | 3 |

## 1.3 Pines de salida

En la parte derecha, coloca dos pines de salida (botón **○**):

| Label | Data Bits |
|---|---|
| `Result` | 32 |
| `Zero` | 1 |

## 1.4 Túneles en los pines

1. Abre ▸ **Wiring** y haz clic en **Tunnel**.
2. En la tabla de propiedades, pon **Data Bits = 32** y **Label = `A`**.
3. Coloca el túnel a la derecha del pin `A`, con un poco de separación, y cablea la punta del pin con la punta del túnel.
4. Repite para `B` (32 bits) y `ALUOp` (3 bits).
5. Para las salidas, pon el túnel a la **izquierda** del pin: `Result` (32) y `Zero` (1). Si el túnel queda mirando al lado contrario, cambia su atributo **Facing** (east/west).

> Comprueba: con la flecha, pasa el ratón por el cable entre pin y túnel. Si está **naranja**, el túnel no tiene el mismo número de bits que el pin.

## 1.5 Señal `esResta` (vale 1 solo cuando ALUOp = 001)

1. ▸ **Arithmetic** → **Comparator**. Propiedades: **Data Bits = 3**, **Numeric Type = Unsigned**. Colócalo.
2. Pasa el ratón por sus patas: a la izquierda tiene dos entradas (**A** arriba y **B** abajo) y a la derecha tres salidas (**>**, **=**, **<**).
3. Conecta a la entrada superior un túnel `ALUOp` (3 bits).
4. ▸ **Wiring** → **Constant**: **Data Bits = 3**, **Value = 0x1**. Conéctala a la entrada inferior del comparador.
5. A la salida **=** (la del medio) conecta un túnel de **1 bit** llamado `esResta`.

## 1.6 Suma y resta con un solo sumador

Truco: A − B = A + (NOT B) + 1. Si `esResta = 1`, invertimos B y ponemos el acarreo de entrada a 1.

1. **Extensor de `esResta` a 32 bits:**
   - ▸ **Wiring** → **Bit Extender**. Propiedades: **Bit Width In = 1**, **Bit Width Out = 32**, **Extension Type = Sign**.
   - Entrada (izquierda): túnel `esResta` (1 bit). Así, si esResta = 1, la salida es `FFFFFFFF`; si es 0, `00000000`.
2. **XOR para invertir B:**
   - ▸ **Gates** → **XOR Gate**. Propiedades: **Data Bits = 32**, **Number Of Inputs = 2**.
   - Entrada 1: túnel `B` (32 bits). Entrada 2: la salida del Bit Extender.
3. **Sumador:**
   - ▸ **Arithmetic** → **Adder**. Propiedades: **Data Bits = 32**.
   - Patas (compruébalo pasando el ratón): **a** izquierda-arriba, **b** izquierda-abajo, **Carry In** arriba, **salida** derecha, **Carry Out** abajo.
   - **a** ← túnel `A`.
   - **b** ← salida del XOR.
   - **Carry In** (arriba) ← túnel `esResta` (1 bit).
   - **Carry Out**: déjalo sin conectar.
   - **Salida** → túnel `SUMA` (32 bits).

## 1.7 AND y OR

1. ▸ **Gates** → **AND Gate**: **Data Bits = 32**, **Number Of Inputs = 2**. Entradas: túneles `A` y `B`. Salida: túnel `AND_RES` (32).
2. ▸ **Gates** → **OR Gate**: igual. Entradas `A` y `B`. Salida: túnel `OR_RES` (32).

## 1.8 SLT (menor que, con signo)

1. ▸ **Arithmetic** → **Comparator**: **Data Bits = 32**, **Numeric Type = 2's Complement** (¡importante: con signo!).
2. Entrada superior ← `A`. Entrada inferior ← `B`.
3. Salida **<** (la de abajo) → un **Bit Extender** con **Bit Width In = 1**, **Bit Width Out = 32**, **Extension Type = Zero**.
4. Salida del extensor → túnel `SLT_RES` (32).

## 1.9 Desplazamientos

1. **Sacar la cantidad (5 bits bajos de A):**
   - **Bit Extender** con **Bit Width In = 32**, **Bit Width Out = 5** (el tipo da igual). Al ser más estrecho, se queda con los bits 4..0.
   - Entrada ← túnel `A`. Salida → túnel `SH` (**5 bits**).
2. **Desplazamiento a la izquierda:**
   - ▸ **Arithmetic** → **Shifter**: **Data Bits = 32**, **Shift Type = Logical Left**.
   - Pasa el ratón por las dos entradas de la izquierda: una es el **dato** y otra la **distancia** (Distance, 5 bits).
   - Dato ← `B`. Distancia ← `SH`. Salida → túnel `SLL_RES` (32).
3. **Desplazamiento a la derecha:**
   - Otro **Shifter**: **Data Bits = 32**, **Shift Type = Logical Right**.
   - Dato ← `B`. Distancia ← `SH`. Salida → túnel `SRL_RES` (32).

## 1.10 Multiplexor del resultado

1. ▸ **Plexers** → **Multiplexer**: **Select Bits = 3**, **Data Bits = 32**, **Include Enable? = No**.
2. Al colocarlo verás 8 entradas a la izquierda (la **0** arriba, la **7** abajo), la salida a la derecha y el **selector** abajo (la pata pequeña inferior). Pasa el ratón para confirmar el número de cada entrada.
3. Conecta un túnel (32 bits) a cada entrada:

| Entrada | Túnel |
|---|---|
| 0 | `SUMA` |
| 1 | `SUMA` (otra vez: la resta sale del mismo sumador) |
| 2 | `AND_RES` |
| 3 | `OR_RES` |
| 4 | `SLT_RES` |
| 5 | `SLL_RES` |
| 6 | `SRL_RES` |
| 7 | **Constant** 32 bits, Value `0x0` |

4. Selector (abajo) ← túnel `ALUOp` (3 bits).
5. Salida → túnel `Result` (32).

> Truco: para colocar varias entradas iguales, coloca un túnel, selecciónalo, `Ctrl+C`, `Ctrl+V` y arrástralo a su sitio; luego cambia el Label.

## 1.11 Zero

1. ▸ **Arithmetic** → **Comparator**: **Data Bits = 32**, **Numeric Type = Unsigned**.
2. Entrada superior ← túnel `Result`. Entrada inferior ← **Constant** de 32 bits con valor `0x0`.
3. Salida **=** (la del medio) → túnel `Zero` (1 bit).

## 1.12 Texto explicativo (cuenta para la nota de claridad)

Herramienta **A** de la barra → clic en una zona libre → escribe, por ejemplo:

`ALUOp: 000 ADD | 001 SUB | 010 AND | 011 OR | 100 SLT | 101 SLL (B<<A[4:0]) | 110 SRL (B>>A[4:0])`

## 1.13 Revisión antes de probar

- [ ] No hay ningún cable **naranja** (error de ancho) ni **rojo**.
- [ ] Ningún túnel está escrito con otro nombre (por ejemplo `Sum` en un sitio y `SUMA` en otro). Los nombres distinguen mayúsculas.
- [ ] Ningún túnel tiene **dos salidas** alimentándolo (por ejemplo, dos componentes escribiendo en `SUMA`).

## 1.14 Pruebas

Elige la **mano ✋** y pon estos valores en los pines de entrada. Comprueba las salidas:

| # | A | B | ALUOp | Result esperado | Zero |
|---|---|---|---|---|---|
| 1 | `00000005` | `00000003` | 000 | `00000008` | 0 |
| 2 | `00000005` | `00000005` | 001 | `00000000` | **1** |
| 3 | `00000003` | `00000005` | 001 | `FFFFFFFE` | 0 |
| 4 | `FFFF00FF` | `0F0F0F0F` | 010 | `0F0F000F` | 0 |
| 5 | `FFFF0000` | `0000FFFF` | 011 | `FFFFFFFF` | 0 |
| 6 | `FFFFFFFF` | `00000001` | 100 | `00000001` | 0 |
| 7 | `00000001` | `FFFFFFFF` | 100 | `00000000` | 1 |
| 8 | `00000004` | `00000001` | 101 | `00000010` | 0 |
| 9 | `00000004` | `80000000` | 110 | `08000000` | 0 |

**Si algo falla:**

- Prueba 2 o 3 mal → revisa `esResta`: el comparador debe comparar `ALUOp` con la constante `0x1` (3 bits) y usar la salida **=**; el Bit Extender debe ser **Sign**; el Carry In debe recibir `esResta`.
- Prueba 6 da 0 → el comparador de SLT está en *Unsigned*; cámbialo a **2's Complement**.
- Pruebas 8 o 9 mal → revisa que el **dato** del Shifter sea `B` y la **distancia** sea `SH` (puede que las tengas al revés).
- Una salida en azul o `xxxx` → algún túnel no tiene pareja (nombre mal escrito) o falta un cable.

Cuando todo cuadre: `Ctrl+S`, haz el commit (ver 0.12) y dime **"ALU lista"**. Revisaré el archivo y seguimos con el **Register_File**.
