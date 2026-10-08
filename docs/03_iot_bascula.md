# IoT: báscula conectada — especificación funcional

**[PROPUESTA]** No sabemos qué báscula tiene Chickenmart hoy **[PENDIENTE]**. Esta es la especificación de lo que necesitamos; Carolina la usa para buscar equipos compatibles y precios. **Comprobar protocolos con los proveedores antes de afirmar compatibilidad.**

| Aspecto | Requisito / descripción |
|---|---|
| **Sensor de peso** | Celda de carga en plataforma. Capacidad y resolución según lo que se recibe [PENDIENTE: peso máx. por canastilla]. Ejemplo a validar: capacidad ≥ 30 kg, resolución ≤ 5–10 g. Uso comercial: preferible equipo con verificación metrológica vigente en Colombia (confirmar requisito con proveedor). |
| **Selección de producto** | **La báscula no identifica el producto.** El SKU se elige en la interfaz o se escanea (código de barras/QR del proveedor o etiqueta interna). La persona confirma. |
| **Tara** | Tara por tipo de recipiente (canastilla, bandeja) guardada en la interfaz, o tara en la báscula. Se registra bruto, tara y neto. Tara mayor que el bruto o inusual → revisión. |
| **Estabilidad** | Usar la bandera de "peso estable" que envía la báscula y/o regla en software: N lecturas seguidas dentro de una tolerancia (demo: 3 lecturas, ±0,01 kg). Solo se guarda un valor por captura. |
| **Salida de datos** | Opciones a verificar: USB (HID/serial), RS-232, Bluetooth, Ethernet/Wi-Fi con API. Formato: trama de texto con peso, unidad y estado. **Tener Wi-Fi no garantiza integración**: se necesita protocolo documentado o SDK. |
| **Compatibilidad** | Con el dispositivo de captura (tablet/PC, sistema operativo) y con el inventario central. Pedir al proveedor: manual de protocolo, ejemplo de trama, drivers, soporte. |
| **Frecuencia** | La báscula puede emitir varias lecturas por segundo; la interfaz solo las usa para detectar estabilidad. Se registra **un evento por recepción**, no un flujo continuo. |
| **Fallos** | Sin comunicación → registro manual marcado · Lectura inestable → repetir · Descalibración → verificación periódica con pesa patrón y registro · Sin red → cola local · Sobrecarga → aviso en pantalla. |
| **Extensión futura (no existente)** | Sensor de **temperatura** en nevera/cuarto frío para cadena de frío. Es una extensión propuesta; **no hay sensores instalados** que sepamos. |

## Requisitos para Carolina (Cloud / costos)

1. Báscula de recepción con salida de datos documentada (o adaptador para la actual).
2. Dispositivo de captura (tablet o PC) + lector de códigos (opcional).
3. Interfaz de captura (desarrollo propio o módulo de un software de inventario).
4. Inventario central con API, hosting y respaldo; usuarios y roles.
5. Conector con la plataforma web [PENDIENTE] y con la caja [PENDIENTE].
6. Gestor de pedidos para WhatsApp (formulario o WhatsApp Business).
7. Notificaciones de alertas (correo / WhatsApp).
8. Conectividad en tienda (y plan de contingencia).
9. Instalación, calibración, capacitación y soporte.
