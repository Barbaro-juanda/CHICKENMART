# Demo: recepción y efectos en saldo/reservas

> **Todos los datos son FICTICIOS.** Prototipo académico; no está conectado a ninguna báscula, web, caja o WhatsApp reales.

## Ejecutar

```bash
python3 demo/demo_recepcion.py
```

Requiere solo Python 3.10+ (biblioteca estándar, SQLite).

## Entradas (ficticias)

- Producto `PECH-001` (pechuga), 18.000 COP/kg, mínimo **[SUPUESTO]** 8 kg, aviso de vencimiento **[SUPUESTO]** 2 días.
- Lecturas de báscula: 12,40 (inestable), 20,95 (inestable), 21,70, 21,58, 21,62 ×4 (estables). Tara 1,62 kg.
- Pedidos: web 2,5 kg; WhatsApp 1,5 kg; bloqueo 1 kg; caja 16 kg; web y WhatsApp 10 kg simultáneos.

## Salida esperada (el script verifica cada una)

| Paso | Físico | Reservado | Bloqueado | Vendible |
|---|---|---|---|---|
| 1. Recepción (neto 20,00) | 20 | 0 | 0 | 20 |
| 2. Duplicado / tara inválida / sin confirmar → rechazados | 20 | 0 | 0 | 20 |
| 3. Reservas 2,5 + 1,5 y bloqueo 1 | 20 | 4 | 1 | **15** |
| 4. Caja pide 16 → rechazado | 20 | 4 | 1 | 15 |
| 5. Dos reservas simultáneas de 10 → solo 1 | 20 | 14 | 1 | 5 |
| 6. Despacho 2,5 → real 2,58 | 17,42 | 11,5 | 1 | 4,92 |
| 7. Despacho 10 → real 11,2 (cliente confirma) | 6,22 | 1,5 | 1 | 3,72 |
| 8. Cancelación 1,5 | 6,22 | 0 | 1 | 5,22 |
| 9. Merma del kg bloqueado | 5,22 | 0 | 0 | 5,22 |
| 10. Corrección autorizada (neto 19,80) | 5,02 | 0 | 0 | 5,02 |
| 11. Alertas: mínimo y vencimiento (sin duplicar) | — | — | — | — |

## Evidencia

- `evidencia/salida_demo.txt` — registro completo de la ejecución.
- `evidencia/movimientos.csv`, `pedidos.csv`, `alertas.csv`, `lotes.csv`, `productos.csv` — para Orozco (Data Hub / Power BI).
- `evidencia/esquema.sql` — esquema de datos.

Los IDs y horas cambian en cada ejecución; en el paso 5 el canal ganador puede variar (siempre gana exactamente uno).

## Limitaciones

- Lecturas de báscula simuladas; no hay protocolo real implementado.
- SQLite local en lugar de un servidor con API; sin autenticación real (roles como texto).
- Umbrales, tolerancias, precios y taras son supuestos.
- El inventario se lleva por SKU; el detalle por lote (FIFO) y el fraccionamiento quedan como extensión.
