# Automatizaciones A1–A3 — Chickenmart

**Autor:** Juan David · **Estado:** borrador para revisión del equipo
**Convención:** **[HECHO]** = sale del PDF *Diagnóstico AS IS* (págs. 5–8) o de Maria Camila Jimenez · **[PROPUESTA]** = diseño nuestro · **[SUPUESTO]** = valor de ejemplo que debe validar el negocio · **[PENDIENTE]** = dato que no tenemos.

> **Frase guía:** convertir el peso recibido en un registro fiable y una disponibilidad de venta actualizada.

**Proceso común del equipo:** recepción → pesaje neto confirmado → inventario central → disponibilidad vendible → reserva → salida real y conciliación.

A1–A3 son **reglas** (si pasa X, haz Y). No predicen: la predicción (IA1–IA3) es de Carolina; los agentes (G1–G3) son de Nataly; el gemelo lo modela Orozco. Todos leen y escriben el **mismo registro central de movimientos**.

---

## Punto de partida (AS IS) [HECHO]

- Chickenmart vende derivados del pollo en el Alto de Las Palmas (Envigado) por **punto físico, web y WhatsApp**.
- El catálogo tiene SKU, peso, presentación, precio, proveedor y vencimiento.
- El inventario se lleva en **archivos y comprobaciones físicas**; los canales **no están completamente sincronizados**.
- Al recibir mercancía, el inventario se actualiza **después**.
- Maria Camila Jimenez pide como prioridad **medir con báscula inteligente** los pesos recibidos para el inventario y la disponibilidad web.

**No sabemos [PENDIENTE]:** qué báscula existe, cómo se pesa hoy, qué plataforma usa la web, qué sistema de caja hay, cómo se registran las ventas de WhatsApp ni cómo es la conectividad.

---

## A1. Recepción y pesaje conectado

| Campo | Contenido |
|---|---|
| **Problema actual** | El peso recibido se anota y luego se digita en archivos; el inventario se actualiza tarde y puede tener errores de transcripción. [HECHO: actualización posterior] |
| **Disparador** | Llega mercancía de un proveedor y el auxiliar abre una "captura de recepción". |
| **Entradas** | SKU (seleccionado o escaneado), proveedor, lote, vencimiento, peso bruto estable (báscula), tara, responsable. |
| **Pasos** | 1) Seleccionar/escanear SKU → 2) ingresar proveedor, lote y vencimiento → 3) colocar producto; la interfaz espera **peso estable** → 4) descontar **tara** (canastilla/empaque) → 5) la persona **revisa y confirma** identidad y aceptación de la mercancía → 6) se registra **una sola entrada** con ID único. |
| **Salida** | Movimiento `RECEPCION` con: neto, unidad, momento, responsable, ID de captura, lote; el saldo físico y vendible suben de inmediato. |
| **Responsable** | Auxiliar de recepción (captura); administradora (correcciones). [PENDIENTE: confirmar quién recibe hoy] |
| **Tecnología requerida** | Báscula con salida de datos (USB/RS-232/Bluetooth/red — **por verificar con proveedor**), interfaz de captura (tablet/PC o app web), inventario central. |
| **Excepciones / fallos** | Peso inestable → repetir o registro manual justificado · Tara mayor que el bruto → bloquea y pide revisión · Reenvío por reintento/cola offline → se ignora el duplicado (ID de captura) · Error detectado después → **ajuste autorizado** que referencia el original (no se borra) · Báscula sin comunicación → digitación manual marcada como "manual" · Producto rechazado → no entra al inventario. |
| **Beneficio** | Evita volver a digitar la lectura; relaciona directamente lo recibido con las existencias; trazabilidad por lote y vencimiento. |
| **Indicadores** | Tiempo medio de recepción (min/recepción) · Errores de digitación o ajustes por recepción (%) · % recepciones capturadas desde báscula vs. manuales. Metas: **pendientes de medición** (línea base AS IS). |
| **Costo a investigar** (→ Carolina) | Báscula con salida de datos o adaptador, tablet/PC, licencia o desarrollo de la interfaz, impresora de etiquetas (opcional), instalación/calibración. |

**Controles clave**
- No se guarda cada lectura repetida: solo **un** valor cuando hay N lecturas estables (demo: 3 lecturas dentro de ±0,01 kg).
- **La báscula aporta el peso; la persona verifica** qué producto es y si se acepta. La báscula no identifica el producto.
- **kg vs. paquetes/unidades:** el inventario guarda kg; si un SKU se vende por paquete, se registra kg y cantidad de paquetes con su peso nominal [PENDIENTE: tipos de presentación].
- **Fraccionamiento** (ej. pollo entero → presas): movimiento `TRANSFORMACION` = salida del SKU origen + entradas de SKUs derivados + merma, con pesos reales. [PENDIENTE: confirmar si se fracciona en tienda]

**Caso Chickenmart (ficticio):** llega pechuga del "Proveedor A", lote L-2026-1007, vence 10-oct. Lecturas: 12,40 (inestable) … 21,62 ×3 (estable). Tara canastilla 1,62 kg → **neto 20,00 kg**. Se crea un único movimiento; el reintento de la cola offline se rechaza.

---

## A2. Sincronización y reservas entre canales

| Campo | Contenido |
|---|---|
| **Problema actual** | Cada canal mira información distinta; se puede vender lo que ya no hay o dejar de vender lo que sí hay. [HECHO: canales no sincronizados] |
| **Disparador** | Un pedido confirmado en web, caja o WhatsApp; un despacho; una cancelación. |
| **Entradas** | Pedido (ID, canal, SKU, kg solicitados), peso real al alistar, decisión del cliente si cambia el peso. |
| **Pasos** | 1) Canal consulta **vendible** en el inventario central → 2) al confirmar, **reserva** (compromete kg) en una transacción que valida y escribe a la vez → 3) al alistar/despachar (regla a acordar con Santiago) se pesa el **real** → 4) se registra la **salida** que descuenta físico y consume la reserva en un solo movimiento → 5) si se cancela, **liberación** de la reserva. |
| **Salida** | Disponibilidad vendible actualizada para todos los canales; historial de movimientos por pedido. |
| **Responsable** | Cada canal registra sus pedidos (web automático, cajero, asesor de WhatsApp); alistador registra peso real. |
| **Tecnología requerida** | Inventario central con API o conector; integración con web [PENDIENTE: plataforma]; caja [PENDIENTE: sistema]; formulario o gestor de pedidos para WhatsApp. |
| **Excepciones / fallos** | Pide más de lo vendible → ofrecer ajustar o escalar · Peso final fuera de tolerancia → validar con el cliente antes de cobrar · Ventas simultáneas → solo una reserva gana · Desconexión → ver tabla abajo · Datos antiguos → el canal muestra "actualizado hace X min" y la reserva siempre revalida en el central. |
| **Beneficio** | Un solo saldo para todos los canales; menos pedidos afectados por agotados; ventas de WhatsApp dejan rastro. |
| **Indicadores** | Demora de actualización (min entre movimiento y reflejo en web) · Pedidos afectados por agotados (%) · % ventas de WhatsApp registradas. Metas: pendientes. |
| **Costo a investigar** | Conector/plugin de la plataforma web, integración con caja, herramienta de pedidos WhatsApp (formulario o WhatsApp Business), hosting de la base central. |

**Fórmula (ejemplo ficticio del enunciado):**
`vendible = físico − reservado − bloqueado` → 20 kg − 4 kg − 1 kg = **15 kg vendibles**.

**Sin doble descuento:** la reserva no toca el físico. La salida hace **físico −real** y **reservado −reservado original** en el mismo movimiento.

**Precio con peso variable [PROPUESTA, validar con Santiago y Maria Camila]:** precio por kg; el cliente aprueba un valor estimado; se cobra el peso real. Si la diferencia supera una tolerancia **[SUPUESTO ±5 %]**, el pedido queda *pendiente de cliente* hasta que acepte el nuevo valor o se ajuste.

**Canales sin conexión y datos antiguos**

| Situación | Comportamiento propuesto |
|---|---|
| Báscula/captura sin red | Guarda capturas en cola local con ID único; al reconectar se envían y el central ignora duplicados. |
| Caja sin red | Vende con límite conservador o registro manual; concilia al reconectar; las diferencias quedan como alerta. |
| Web sin acceso al central | Oculta "agregar al carrito" o muestra "por confirmar"; no promete stock. |
| WhatsApp | El asesor registra el pedido en el gestor (no solo en el chat); sin registro no hay reserva. |

> Tener Wi-Fi en la báscula **no** demuestra que pueda conectarse al sistema elegido: hay que verificar protocolo y formato de datos.

**Caso:** web reserva 2,5 kg y WhatsApp 1,5 kg; 1 kg bloqueado → 15 kg vendibles. La caja pide 16 kg → rechazado, se ofrecen 15. Web y WhatsApp piden 10 kg al mismo tiempo → solo uno queda reservado.

---

## A3. Alertas por reglas de inventario

| Campo | Contenido |
|---|---|
| **Problema actual** | Los faltantes y vencimientos se detectan con revisión física. [HECHO: comprobaciones físicas] |
| **Disparador** | Cada movimiento y una revisión diaria programada. |
| **Entradas** | Saldo vendible por SKU, mínimo configurable, fecha de vencimiento por lote, días de aviso configurables. |
| **Pasos** | 1) Evaluar reglas → 2) si se cumple y no hay una alerta abierta igual, crear alerta → 3) notificar al destinatario → 4) responsable atiende y marca estado. |
| **Salida** | Alerta con: regla, SKU/lote, mensaje, **destinatario, prioridad, responsable, estado**, fecha de creación y de atención. |
| **Responsable** | Administradora (destinataria) [SUPUESTO]; responsable de inventario (atiende). |
| **Tecnología requerida** | Tarea programada sobre el inventario central + canal de aviso (correo, WhatsApp interno o panel). |
| **Excepciones / fallos** | Alertas repetidas → no se duplican mientras sigan abiertas · Umbral mal configurado → solo la administradora lo cambia · Aviso no entregado → queda visible en el panel. |
| **Beneficio** | Detectar a tiempo faltantes y lotes próximos a vencer sin depender de la revisión manual. |
| **Indicadores** | Alertas atendidas (%) · Tiempo de respuesta (h) · Mermas por vencimiento (kg) [con Orozco]. Metas: pendientes. |
| **Costo a investigar** | Servicio de notificaciones (correo / WhatsApp Business API), programador de tareas. |

**Ejemplo [SUPUESTO]:** avisar a la administradora cuando queden **menos de X kg** (demo usa 8 kg) o cuando un lote esté a **Y días** de vencer (demo usa 2 días). X e Y los define el negocio.

**Límites:** el **bloqueo automático** de un lote solo con una regla validada por el negocio; **compras y promociones** siempre requieren autorización humana. Predecir qué se venderá antes de vencer es IA (Carolina), no A3.

---

## Riesgos y limitaciones

| Riesgo | Mitigación |
|---|---|
| La báscula actual no tiene salida de datos | Verificar modelo; adaptador o báscula nueva (costo con Carolina); modo manual mientras tanto. |
| Tara incorrecta | Taras registradas por tipo de canastilla; revisión en la confirmación; ajuste trazable. |
| Ventas no registradas (WhatsApp, mostrador) | Regla: sin registro no hay salida; conciliación con conteo físico periódico. |
| Conectividad inestable en la zona | Cola offline con ID único; caja con límite conservador. |
| Resistencia al cambio / carga operativa | Interfaz de pocos pasos; capacitación; piloto con 1–2 SKU. |
| Confundir inventario con tablero | El inventario transaccional manda; Power BI solo lee copias. |

## Fuentes

- PDF *Diagnóstico AS IS de Chickenmart para el proyecto de transformación digital* (13 págs.), págs. 5–8.
- Necesidad de pesaje conectado: Maria Camila Jimenez.
- Alcance: imágenes de la tarea y reparto del equipo.
- Demo: `demo/` de este repositorio (datos ficticios).
