# Web explicativa: La última copia

Página que explica de forma visual la condición de carrera del proyecto
Biblioteca Digital, igual que el video hecho con Manim.

Prototipo en Figma: https://www.figma.com/design/AcBXwVHdxjpTF3R4CCVgVC

## Cómo abrirla

Doble clic en `index.html`. No necesita instalar nada.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `index.html` | La estructura: portada, personajes, simulador, resultado. |
| `styles.css` | Colores, tamaños y las animaciones (transiciones de CSS). |
| `app.js` | El simulador. La lista `PASOS` describe cada paso de los dos modos. |
| `codigo.js` | Copia del método `prestar()` de `src/biblioteca_basica.py` y `src/biblioteca_compleja.py`, con sus números de línea. Si cambias ese código en `src/`, actualiza también este archivo. |

## Cómo funciona el simulador

Cada paso de `PASOS` describe el **estado completo** de la escena: dónde está
cada actor, qué dice su etiqueta, dónde está el libro, quién tiene la llave y
qué líneas agrega al diálogo. La función `render()` lee ese estado y mueve
las piezas; las transiciones de CSS animan el movimiento entre pasos.

Para agregar o cambiar un paso, solo hay que editar la lista `PASOS`.

## Los tres paneles del simulador

El simulador muestra tres paneles en una fila: **Escena**, **Diálogo** y
**Código**. Cada uno se minimiza con el botón "—" y se vuelve a abrir haciendo
clic en su tira. Los paneles abiertos se reparten el espacio.

El panel **Código** tiene pestañas **Básica / Compleja**. Muestra el
`prestar()` real (sin las líneas de `self.log`, para que quepa) con sus
números de línea originales. Cada paso de `PASOS` tiene un campo `code` con la
línea donde está cada hilo (`b` = básica, `x` = compleja), sus variables
locales y el historial.
