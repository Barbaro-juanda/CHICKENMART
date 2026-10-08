CREATE TABLE IF NOT EXISTS productos (
    sku            TEXT PRIMARY KEY,
    nombre         TEXT NOT NULL,
    unidad_venta   TEXT NOT NULL CHECK (unidad_venta IN ('kg', 'paquete')),
    precio_kg      REAL NOT NULL,          -- COP/kg, ficticio
    minimo_kg      REAL,                   -- umbral de alerta, SUPUESTO
    dias_aviso_venc INTEGER                -- aviso de vencimiento, SUPUESTO
);
CREATE TABLE IF NOT EXISTS lotes (
    lote_id      TEXT PRIMARY KEY,
    sku          TEXT NOT NULL REFERENCES productos(sku),
    proveedor    TEXT NOT NULL,
    vencimiento  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS movimientos (
    mov_id          TEXT PRIMARY KEY,
    tipo            TEXT NOT NULL,         -- RECEPCION, RESERVA, LIBERACION, SALIDA, BLOQUEO, AJUSTE, MERMA
    sku             TEXT NOT NULL REFERENCES productos(sku),
    lote_id         TEXT REFERENCES lotes(lote_id),
    delta_fisico    REAL NOT NULL DEFAULT 0,
    delta_reservado REAL NOT NULL DEFAULT 0,
    delta_bloqueado REAL NOT NULL DEFAULT 0,
    unidad          TEXT NOT NULL DEFAULT 'kg',
    canal           TEXT,                  -- bascula_recepcion, web, caja, whatsapp, admin
    pedido_id       TEXT,
    responsable     TEXT NOT NULL,
    momento         TEXT NOT NULL,
    clave_unica     TEXT UNIQUE,           -- evita duplicados (reintentos, cola offline)
    ref_mov_id      TEXT REFERENCES movimientos(mov_id),  -- correcciones trazables
    detalle         TEXT
);
CREATE TABLE IF NOT EXISTS pedidos (
    pedido_id     TEXT PRIMARY KEY,
    canal         TEXT NOT NULL,
    sku           TEXT NOT NULL,
    kg_reservado  REAL NOT NULL,
    estado        TEXT NOT NULL          -- RESERVADO, PENDIENTE_CLIENTE, DESPACHADO, CANCELADO
);
CREATE TABLE IF NOT EXISTS alertas (
    alerta_id     TEXT PRIMARY KEY,
    regla         TEXT NOT NULL,           -- MINIMO, VENCIMIENTO
    sku           TEXT NOT NULL,
    lote_id       TEXT,
    mensaje       TEXT NOT NULL,
    destinatario  TEXT NOT NULL,
    prioridad     TEXT NOT NULL,
    responsable   TEXT NOT NULL,
    estado        TEXT NOT NULL,           -- ABIERTA, ATENDIDA
    creada        TEXT NOT NULL,
    atendida      TEXT
);
