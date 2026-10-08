# Dependencias con el equipo y preguntas para el negocio

## Lo que debo acordar o entregar

| Con | Qué | Qué le entrego / pido |
|---|---|---|
| **Santiago** | Unidades (kg vs. paquete), regla de reserva, momento de salida (alistar o despachar), devoluciones, política de precio variable | Le propongo: reserva al confirmar; salida con peso real al alistar; tolerancia ±5 % [SUPUESTO]; devolución = movimiento `DEVOLUCION` que suma físico si el producto es apto, si no `MERMA`. Además integra la presentación. |
| **Carolina** | Compatibilidad y precio | Entrego `docs/03_iot_bascula.md` (requisitos para costos). Pido: cotizaciones, inversión y tiempo para el pitch. |
| **Nataly** | Acciones que los agentes pueden ejecutar | Propuesta: agentes **pueden** consultar saldo, crear borrador de pedido, recordar alertas abiertas; **requieren aprobación**: ajustes, bloqueos, compras, promociones; **nunca**: borrar movimientos. Le envío mis preguntas para agrupar. |
| **Orozco** | Eventos para Data Hub, Power BI y gemelo; integración | Entrego `demo/evidencia/esquema.sql` + `movimientos.csv` + lista de eventos (`docs/02_arquitectura.md`). Pido: definiciones finales de indicadores. |

## Preguntas para Maria Camila Jimenez (enviar a Nataly para agrupar)

1. ¿Qué báscula usan hoy (marca/modelo)? ¿Tiene puerto USB, serial, Bluetooth o red?
2. ¿Cómo pesan hoy la mercancía recibida y dónde lo anotan?
3. ¿Usan canastillas/bandejas? ¿Cuánto pesan (tara)? ¿Son siempre las mismas?
4. ¿Qué presentaciones manejan (kg a granel, paquetes de peso fijo, unidades)?
5. ¿Quién recibe la mercancía y en qué horario?
6. ¿Fraccionan productos en tienda (ej. pollo entero → presas)? ¿Cómo registran la merma?
7. ¿Qué sistema de caja (POS) usan?
8. ¿En qué plataforma está la web (Shopify, WooCommerce, Wix, desarrollo propio, otra)?
9. ¿Cómo se registran hoy las ventas de WhatsApp?
10. ¿Cómo es la conexión a internet en la tienda? ¿Se cae con frecuencia? ¿Qué hacen sin internet?
11. ¿Quién debería recibir alertas de bajo inventario y vencimiento? ¿Con cuántos días de anticipación?
12. Cuando el peso real de un pedido difiere de lo pedido, ¿cómo cobran hoy?

## Solicitud a cada compañero para el pitch (plantilla)

> Hola, para el pitch necesito de tu bloque, máximo en 2 diapositivas de contenido:
> 1. **Afirmación de negocio** (una frase: qué gana Chickenmart).
> 2. **Evidencia** (dato del diagnóstico, cálculo o demo — con fuente; marca lo ficticio).
> 3. **Decisión** que le pedimos a la empresa.
> 4. Cifras de inversión/tiempo/riesgo si aplican y tu frase de exposición.
> Fecha: borrador a mitad del plazo; final idealmente 2 días antes del ensayo.
