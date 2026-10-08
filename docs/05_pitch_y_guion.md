# Pitch ejecutivo — estructura, mis 2 diapositivas y guion

## Secuencia del pitch (ajustar al tiempo real)

| # | Diapositiva | Dueño del contenido |
|---|---|---|
| 1 | Portada + frase de valor | Juan David (diseño) |
| 2 | Problema / AS IS | Santiago / Nataly |
| 3 | TO BE: proceso común (recepción → … → conciliación) | Santiago |
| 4 | **Báscula y flujo conectado (A1 + IoT)** | **Juan David** |
| 5 | **Sincronización, alertas y controles (A2 + A3)** | **Juan David** |
| 6 | Arquitectura (diagrama) + demo/implementación | Juan David + Orozco |
| 7 | Tablero Power BI / Data Hub | Orozco |
| 8 | IA (IA1–IA3) | Carolina |
| 9 | Agentes (G1–G3) | Nataly |
| 10 | Gemelo digital | Orozco |
| 11 | Inversión y cronograma | Carolina (cifras) |
| 12 | Riesgos y ROI | Todos / Santiago |
| 13 | Resultados esperados, visión y decisión solicitada | Santiago + Juan David |

Si hay más contenido que tiempo, no se eliminan criterios de la rúbrica: se fusionan diapositivas.

## Diapositiva 4 — Báscula y flujo conectado

**Título:** Del peso recibido al inventario, sin volver a digitar

- Hoy [HECHO]: inventario en archivos, actualizado después de recibir.
- Propuesta: SKU → proveedor/lote/vencimiento → **peso estable** → **tara** → confirmación humana → **1 registro único**.
- Cada registro: neto, unidad, momento, responsable, ID.
- La báscula pesa; la persona identifica y acepta la mercancía.
- Controles: sin duplicados, tara revisada, correcciones autorizadas y trazables.
- KPI: tiempo de recepción · errores de digitación (meta: tras medir línea base).

*Visual:* flujo de 6 pasos con iconos + ejemplo ficticio "21,62 − 1,62 = 20,00 kg".

## Diapositiva 5 — Un solo saldo para web, caja y WhatsApp

**Título:** Lo que se ve en la web es lo que hay

- Fórmula: **vendible = físico − reservado − bloqueado** (ej. ficticio 20 − 4 − 1 = 15 kg).
- Reserva al confirmar; salida con peso real; cancelación libera. Sin doble descuento.
- Ventas simultáneas: solo una reserva gana (demostrado en la demo).
- Peso variable: se cobra el real; fuera de tolerancia, el cliente confirma.
- Alertas por regla: mínimo de X kg y vencimiento a Y días → administradora (X, Y por definir).
- KPI: demora de actualización · pedidos afectados por agotados · alertas atendidas y tiempo de respuesta.

*Visual:* barra apilada físico/reservado/bloqueado/vendible + 3 iconos de canal conectados al centro.

## Guion (≈ 2 minutos)

> **(Diap. 4)** Hoy en Chickenmart el inventario vive en archivos y se actualiza después de recibir la mercancía; por eso la web, la caja y WhatsApp no siempre ven lo mismo. Maria Camila nos pidió algo muy concreto: medir con báscula lo que llega.
>
> Nuestra propuesta es simple: el auxiliar elige el producto, anota proveedor, lote y vencimiento, pone la canastilla y el sistema espera a que el peso esté estable. Descuenta la tara, la persona confirma que la mercancía es correcta y se crea **un único registro** con peso neto, hora, responsable e identificador. La báscula pesa; la persona decide. Si alguien se equivoca, la administradora corrige, pero el original no se borra.
>
> **(Diap. 5)** Ese registro alimenta un inventario central que consultan los tres canales. Lo vendible es lo físico menos lo reservado y lo bloqueado: con 20 kilos, 4 reservados y 1 en revisión, se pueden vender 15. Si dos clientes piden lo mismo al mismo tiempo, solo uno lo obtiene; lo probamos en nuestra demo con datos ficticios. Al despachar se cobra el peso real y, si cambia mucho, el cliente confirma.
>
> Además, reglas sencillas avisan a la administradora cuando un producto baja de un mínimo o un lote está por vencer.
>
> En resumen: **convertir el peso recibido en un registro fiable y una disponibilidad de venta actualizada.** Lo mediremos con tiempo de recepción, errores de digitación, demora de actualización y pedidos afectados por agotados.

## Checklist de diseño del pitch

- [ ] Una misma historia y cifras verificadas con Santiago y Nataly.
- [ ] Cada cifra con fuente o etiqueta **ficticio / supuesto**.
- [ ] Incluye implementación (demo) y tablero.
- [ ] Incluye inversión, tiempo (cronograma), riesgos y ROI (aunque las cifras las prepare otro).
- [ ] Cierre con decisión solicitada a Chickenmart.
- [ ] Ensayo el día anterior con cronómetro.
