# Paso 0 — Lo básico de Logisim Evolution 5.0.0

Lee esto una vez antes de construir la ALU. Lo usarás en todos los pasos.

## 0.1 Configurar las rutas (una sola vez)

Abre PowerShell y ejecuta estas dos líneas (después cierra y vuelve a abrir la terminal):

```powershell
setx LOGISIM_JAR "C:\Program Files\logisim-evolution\app\logisim-evolution-5.0.0-all.jar"
setx MARS_JAR "C:\Proyecto AC Carlos\Mars\Mars45.jar"
```

## 0.2 Abrir el proyecto

1. Abre **Logisim Evolution** desde el menú Inicio.
2. Menú **File → Open…** (Archivo → Abrir) y elige
   `C:\Proyecto AC Carlos\Proyecto-S-MIPS-2026-2027\circuit\smips.circ`.
3. Si te pregunta algo sobre la versión del archivo, acepta.

## 0.3 Las partes de la ventana

```
┌───────────────────────────────────────────────────────────────────┐
│ Menús:  File  Edit  Project  Simulate  FPGA  Window  Help         │
│ Barra:  [✋ mano] [↖ flecha] [A texto] [□ pin entrada] [○ pin salida] [NOT][AND][OR] │
├──────────────────────┬────────────────────────────────────────────┤
│ Pestañas:            │                                            │
│ [Design] [Simulate]  │                                            │
│                      │                                            │
│ ▸ smips              │           LIENZO (canvas)                  │
│    Board             │       aquí dibujas el circuito             │
│    CPU               │                                            │
│    Memory            │                                            │
│    Datapath          │                                            │
│    ALU               │                                            │
│    Instruction_Dec…  │                                            │
│ ▸ Wiring             │                                            │
│ ▸ Gates              │                                            │
│ ▸ Plexers            │                                            │
│ ▸ Arithmetic         │                                            │
│ ▸ Memory             │                                            │
├──────────────────────┤                                            │
│ TABLA DE PROPIEDADES │                                            │
│ (atributos del       │                                            │
│  componente elegido) │                                            │
└──────────────────────┴────────────────────────────────────────────┘
```

- **Panel izquierdo, pestaña Design**: arriba están tus circuitos (Board, CPU, ALU…) y debajo las **bibliotecas** de componentes (Wiring, Gates, Plexers, Arithmetic, Memory…). Haz clic en el triángulo ▸ para abrir una biblioteca.
- **Tabla de propiedades** (abajo a la izquierda): muestra los atributos (ancho de bits, nombre, orientación…) del componente o herramienta seleccionado. **Aquí se configura todo.**
- **Lienzo**: la zona grande donde colocas y cableas.

> Si tu Logisim está en español, los nombres equivalen así: Wiring = Cableado, Gates = Puertas, Plexers = Multiplexores, Arithmetic = Aritmética, Data Bits = Bits de datos, Label = Etiqueta, Facing = Orientación.

## 0.4 Abrir un circuito para editarlo

En la pestaña **Design**, haz **doble clic** sobre el nombre del circuito (por ejemplo `ALU`). El lienzo pasa a mostrar ese circuito y el título de la ventana lo indica.

⚠️ **No toques `Board` ni `Memory`** (requisito R2). Tampoco hagas clic derecho → *Set as Main Circuit* en otro circuito.

## 0.5 Las dos herramientas principales

| Herramienta | Icono | Para qué |
|---|---|---|
| **Edit / Flecha** | ↖ | Seleccionar, mover, cablear y borrar. **Es la que usarás casi siempre al construir.** |
| **Poke / Mano** | ✋ | Cambiar valores de entradas durante la simulación (para probar). |

Atajos útiles: `Ctrl+Z` deshacer · `Supr` borrar lo seleccionado · `Ctrl+C`/`Ctrl+V` copiar/pegar · `Ctrl+S` guardar · rueda del ratón + `Ctrl` = zoom.

## 0.6 Colocar un componente

1. En el panel izquierdo, abre la biblioteca (por ejemplo ▸ **Arithmetic**) y haz **un clic** sobre el componente (por ejemplo **Adder**).
2. **Antes de colocarlo**, mira la tabla de propiedades: puedes cambiar ya el atributo **Data Bits** (por ejemplo a 32).
3. Mueve el ratón al lienzo: verás la silueta del componente. Haz **clic** donde quieras dejarlo.
4. Para colocar otro igual, vuelve a hacer clic en el lienzo. Para dejar de colocar, pulsa la **flecha ↖** de la barra.
5. Para cambiar un atributo después: con la flecha ↖, haz clic sobre el componente y edita la tabla de propiedades.

## 0.7 Cablear

1. Con la flecha ↖, coloca el ratón sobre un **punto de conexión** (los extremos de patas de componentes; se ve un pequeño círculo verde al pasar por encima).
2. **Arrastra** (mantén pulsado el botón) hasta el otro punto de conexión y suelta.
3. Un cable puede doblar: arrastra en L, Logisim hace la esquina solo. También puedes empezar un cable desde la mitad de otro cable (crea un punto de unión).

**Colores de los cables — muy importante para detectar errores:**

| Color | Significado |
|---|---|
| Verde oscuro | cable de 1 bit con valor 0 |
| Verde claro | cable de 1 bit con valor 1 |
| Negro | cable de varios bits (bus) funcionando |
| **Azul** | sin valor: no está conectado a nada que lo alimente |
| **Naranja** | **error de ancho**: estás uniendo cosas de distinto número de bits |
| **Rojo** | conflicto: dos salidas escriben en el mismo cable |

Si pasas el ratón por encima de una pata de un componente, aparece un recuadro con su nombre (por ejemplo "Carry In"). Úsalo siempre que dudes qué pata es.

## 0.8 Pines (entradas y salidas del circuito)

- **Pin de entrada**: botón □ de la barra (o *Wiring → Pin* con *Output? = No*).
- **Pin de salida**: botón ○ de la barra (o *Wiring → Pin* con *Output? = Yes*).
- Atributos que siempre debes poner: **Data Bits** (ancho) y **Label** (nombre).

Los pines de un subcircuito se convierten en sus patas cuando lo uses dentro de otro circuito.

## 0.9 Túneles: conectar sin cables largos

Un **túnel** (*Wiring → Tunnel*) es una "etiqueta de cable": todos los túneles con el **mismo Label** están conectados entre sí aunque no haya cable visible. Así el circuito queda limpio.

- Atributos: **Label** (nombre de la señal) y **Data Bits** (debe coincidir con el cable).
- Truco: coloca un túnel pegado a cada pin y a cada entrada/salida de componente, y no tendrás que cruzar cables por todo el lienzo.

## 0.10 Otros componentes de *Wiring* que usaremos

- **Constant**: un valor fijo. Atributos **Data Bits** y **Value** (se escribe en hex, por ejemplo `0x1`).
- **Bit Extender**: cambia el ancho de un bus. Atributos **Bit Width In**, **Bit Width Out**, **Extension Type** (*Zero* rellena con ceros, *Sign* copia el bit más alto). Si la salida es más estrecha que la entrada, se queda con los bits bajos.
- **Splitter**: separa un bus en partes o las junta.

## 0.11 Probar un circuito

1. Abre el circuito (doble clic en la pestaña Design).
2. Elige la **mano ✋**.
3. Haz clic sobre un pin de entrada para cambiar su valor:
   - Pin de 1 bit: cada clic alterna 0 ↔ 1.
   - Pin de varios bits: haz clic sobre el pin; en Logisim Evolution aparece un pequeño editor donde puedes escribir el valor (elige hexadecimal). Si no aparece, haz clic sobre cada dígito binario para cambiarlo uno a uno.
4. Mira los pines de salida: muestran el resultado al instante.

Si nada cambia, comprueba que **Simulate → Auto-Propagate** (Propagación automática) esté activado.

## 0.12 Guardar y hacer commit

- `Ctrl+S` a menudo.
- Cuando una pieza funcione, en PowerShell:

```powershell
cd "C:\Proyecto AC Carlos\Proyecto-S-MIPS-2026-2027"; git add -A; git commit -m "ALU terminada"
```
