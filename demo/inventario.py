"""Prototipo académico de inventario central para Chickenmart.

TODOS LOS DATOS SON FICTICIOS. Este módulo no se conecta a ninguna báscula,
web, caja ni WhatsApp reales: simula el registro central que esos canales
consultarían. Solo usa la biblioteca estándar de Python (sqlite3).

Idea central: el inventario es un LIBRO DE MOVIMIENTOS (ledger). Cada
movimiento declara su efecto sobre tres saldos:

    delta_fisico     -> kg que existen en la tienda
    delta_reservado  -> kg comprometidos con pedidos aún no despachados
    delta_bloqueado  -> kg retenidos (calidad, revisión, vencimiento)

    vendible = fisico - reservado - bloqueado

Así una venta que consume una reserva hace fisico -= real y
reservado -= reservado_original en UN solo movimiento: no se descuenta dos veces.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import date, datetime

ESQUEMA = """
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
"""

ROLES_CORRECCION = {"administradora"}  # quién puede corregir una recepción (SUPUESTO)
TOLERANCIA_PESO_FINAL = 0.05           # ±5 % sin reconfirmar con cliente (SUPUESTO)


class ErrorInventario(Exception):
    pass


def ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def conectar(ruta: str = ":memory:") -> sqlite3.Connection:
    con = sqlite3.connect(ruta, isolation_level=None, timeout=10, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(ESQUEMA)
    return con


# ---------------------------------------------------------------- saldos

@dataclass
class Saldo:
    fisico: float
    reservado: float
    bloqueado: float

    @property
    def vendible(self) -> float:
        return round(self.fisico - self.reservado - self.bloqueado, 3)

    def __str__(self) -> str:
        return (f"físico={self.fisico:.2f} kg | reservado={self.reservado:.2f} kg | "
                f"bloqueado={self.bloqueado:.2f} kg | VENDIBLE={self.vendible:.2f} kg")


def saldo(con: sqlite3.Connection, sku: str) -> Saldo:
    f, r, b = con.execute(
        "SELECT COALESCE(SUM(delta_fisico),0), COALESCE(SUM(delta_reservado),0), "
        "COALESCE(SUM(delta_bloqueado),0) FROM movimientos WHERE sku = ?", (sku,)
    ).fetchone()
    return Saldo(round(f, 3), round(r, 3), round(b, 3))


def _insertar_mov(con, *, tipo, sku, responsable, canal, lote_id=None, df=0.0, dr=0.0,
                  db=0.0, pedido_id=None, clave_unica=None, ref=None, detalle=None) -> str:
    mov_id = "MOV-" + uuid.uuid4().hex[:8].upper()
    con.execute(
        "INSERT INTO movimientos VALUES (?,?,?,?,?,?,?,'kg',?,?,?,?,?,?,?)",
        (mov_id, tipo, sku, lote_id, df, dr, db, canal, pedido_id, responsable, ahora(),
         clave_unica, ref, detalle),
    )
    return mov_id


# ---------------------------------------------------------------- A1 recepción

@dataclass
class LecturaBascula:
    """Lectura bruta enviada por la báscula. En la demo es FICTICIA."""
    kg: float
    estable: bool


def peso_estable(lecturas: list[LecturaBascula], n: int = 3, tolerancia: float = 0.01) -> float:
    """Devuelve el peso bruto cuando hay n lecturas consecutivas estables dentro de la tolerancia.

    Solo se devuelve UN valor: las lecturas repetidas no se guardan.
    """
    ventana: list[float] = []
    for l in lecturas:
        if not l.estable:
            ventana.clear()
            continue
        ventana.append(l.kg)
        ventana = ventana[-n:]
        if len(ventana) == n and max(ventana) - min(ventana) <= tolerancia:
            return round(sum(ventana) / n, 3)
    raise ErrorInventario("Peso no estable: repetir pesaje o registrar manualmente con justificación")


def registrar_recepcion(con, *, captura_id: str, sku: str, proveedor: str, lote_id: str,
                        vencimiento: str, bruto_kg: float, tara_kg: float, responsable: str,
                        confirmado_por_persona: bool) -> str:
    """Registra UNA entrada por captura. La persona confirma identidad y aceptación."""
    if not confirmado_por_persona:
        raise ErrorInventario("La recepción requiere confirmación humana (producto, estado, proveedor)")
    if tara_kg < 0 or tara_kg >= bruto_kg:
        raise ErrorInventario(f"Tara inválida ({tara_kg} kg) para bruto {bruto_kg} kg: revisar")
    neto = round(bruto_kg - tara_kg, 3)
    con.execute("BEGIN IMMEDIATE")
    try:
        if con.execute("SELECT 1 FROM movimientos WHERE clave_unica = ?", (captura_id,)).fetchone():
            con.execute("ROLLBACK")
            raise ErrorInventario(f"Captura {captura_id} ya registrada: se ignora el duplicado")
        con.execute("INSERT OR IGNORE INTO lotes VALUES (?,?,?,?)", (lote_id, sku, proveedor, vencimiento))
        mov = _insertar_mov(con, tipo="RECEPCION", sku=sku, lote_id=lote_id, df=neto,
                            canal="bascula_recepcion", responsable=responsable, clave_unica=captura_id,
                            detalle=f"bruto={bruto_kg} tara={tara_kg} neto={neto} proveedor={proveedor}")
        con.execute("COMMIT")
        return mov
    except sqlite3.Error:
        con.execute("ROLLBACK")
        raise


def corregir_recepcion(con, *, mov_original: str, neto_correcto: float, responsable: str,
                       rol: str, motivo: str) -> str:
    """Corrección autorizada: no borra el original, agrega un AJUSTE que lo referencia."""
    if rol not in ROLES_CORRECCION:
        raise ErrorInventario(f"Rol '{rol}' no autorizado para corregir recepciones")
    orig = con.execute("SELECT * FROM movimientos WHERE mov_id = ?", (mov_original,)).fetchone()
    if orig is None or orig["tipo"] != "RECEPCION":
        raise ErrorInventario("Movimiento original inexistente o no es una recepción")
    diferencia = round(neto_correcto - orig["delta_fisico"], 3)
    return _insertar_mov(con, tipo="AJUSTE", sku=orig["sku"], lote_id=orig["lote_id"], df=diferencia,
                         canal="admin", responsable=responsable, ref=mov_original,
                         detalle=f"motivo={motivo}; neto {orig['delta_fisico']} -> {neto_correcto}")


# ---------------------------------------------------------------- A2 reservas

def reservar(con, *, pedido_id: str, canal: str, sku: str, kg: float, responsable: str) -> str:
    """Comprueba y reserva en la MISMA transacción: dos canales no comprometen el mismo saldo."""
    con.execute("BEGIN IMMEDIATE")  # bloqueo de escritura: lectura+escritura atómicas
    try:
        if con.execute("SELECT 1 FROM pedidos WHERE pedido_id = ?", (pedido_id,)).fetchone():
            con.execute("ROLLBACK")
            raise ErrorInventario(f"Pedido {pedido_id} ya existe (posible doble envío)")
        disp = saldo(con, sku).vendible
        if kg > disp:
            con.execute("ROLLBACK")
            raise ErrorInventario(
                f"Solicitado {kg} kg > vendible {disp} kg. Ofrecer ajustar a {disp} kg o escalar al equipo")
        con.execute("INSERT INTO pedidos VALUES (?,?,?,?, 'RESERVADO')", (pedido_id, canal, sku, kg))
        mov = _insertar_mov(con, tipo="RESERVA", sku=sku, dr=kg, canal=canal, pedido_id=pedido_id,
                            responsable=responsable, clave_unica=f"RES-{pedido_id}")
        con.execute("COMMIT")
        return mov
    except sqlite3.Error:
        con.execute("ROLLBACK")
        raise


def _pedido(con, pedido_id):
    p = con.execute("SELECT * FROM pedidos WHERE pedido_id = ?", (pedido_id,)).fetchone()
    if p is None:
        raise ErrorInventario(f"Pedido {pedido_id} no existe")
    return p


def despachar(con, *, pedido_id: str, kg_real: float, responsable: str,
              cliente_acepta_cambio: bool | None = None) -> str:
    """Salida con peso real. Consume la reserva y descuenta el físico en un solo movimiento."""
    p = _pedido(con, pedido_id)
    if p["estado"] not in ("RESERVADO", "PENDIENTE_CLIENTE"):
        raise ErrorInventario(f"Pedido {pedido_id} en estado {p['estado']}: no se puede despachar")
    variacion = abs(kg_real - p["kg_reservado"]) / p["kg_reservado"]
    if variacion > TOLERANCIA_PESO_FINAL and not cliente_acepta_cambio:
        con.execute("UPDATE pedidos SET estado='PENDIENTE_CLIENTE' WHERE pedido_id=?", (pedido_id,))
        raise ErrorInventario(
            f"Peso real {kg_real} kg difiere {variacion:.0%} de lo reservado ({p['kg_reservado']} kg): "
            "confirmar nuevo precio con el cliente antes de despachar")
    s = saldo(con, p["sku"])
    extra = max(0.0, kg_real - p["kg_reservado"])
    if extra > s.vendible:
        raise ErrorInventario("El exceso de peso no tiene saldo vendible")
    precio = con.execute("SELECT precio_kg FROM productos WHERE sku=?", (p["sku"],)).fetchone()[0]
    mov = _insertar_mov(con, tipo="SALIDA", sku=p["sku"], df=-kg_real, dr=-p["kg_reservado"],
                        canal=p["canal"], pedido_id=pedido_id, responsable=responsable,
                        clave_unica=f"SAL-{pedido_id}",
                        detalle=f"reservado={p['kg_reservado']} real={kg_real} cobro={kg_real*precio:,.0f} COP")
    con.execute("UPDATE pedidos SET estado='DESPACHADO' WHERE pedido_id=?", (pedido_id,))
    return mov


def cancelar(con, *, pedido_id: str, responsable: str) -> str:
    p = _pedido(con, pedido_id)
    if p["estado"] not in ("RESERVADO", "PENDIENTE_CLIENTE"):
        raise ErrorInventario(f"Pedido {pedido_id} en estado {p['estado']}: no hay reserva que liberar")
    mov = _insertar_mov(con, tipo="LIBERACION", sku=p["sku"], dr=-p["kg_reservado"], canal=p["canal"],
                        pedido_id=pedido_id, responsable=responsable, clave_unica=f"LIB-{pedido_id}")
    con.execute("UPDATE pedidos SET estado='CANCELADO' WHERE pedido_id=?", (pedido_id,))
    return mov


def bloquear(con, *, sku: str, lote_id: str | None, kg: float, responsable: str, motivo: str) -> str:
    return _insertar_mov(con, tipo="BLOQUEO", sku=sku, lote_id=lote_id, db=kg, canal="admin",
                         responsable=responsable, detalle=motivo)


def registrar_merma(con, *, sku: str, lote_id: str | None, kg: float, responsable: str, motivo: str,
                    desde_bloqueado: bool = False) -> str:
    """Toda merma se registra. Si venía de un bloqueo, también libera ese bloqueo."""
    return _insertar_mov(con, tipo="MERMA", sku=sku, lote_id=lote_id, df=-kg,
                         db=-kg if desde_bloqueado else 0.0, canal="admin",
                         responsable=responsable, detalle=motivo)


# ---------------------------------------------------------------- A3 alertas

def evaluar_alertas(con, *, hoy: date, destinatario: str = "administradora") -> list[sqlite3.Row]:
    """Reglas simples (no predicción). No duplica una alerta que sigue ABIERTA."""
    nuevas = []
    for p in con.execute("SELECT * FROM productos").fetchall():
        s = saldo(con, p["sku"])
        if p["minimo_kg"] is not None and s.vendible < p["minimo_kg"]:
            nuevas.append(("MINIMO", p["sku"], None, "ALTA",
                           f"{p['nombre']}: vendible {s.vendible} kg < mínimo {p['minimo_kg']} kg (SUPUESTO)"))
        if p["dias_aviso_venc"] is None:
            continue
        for l in con.execute("SELECT * FROM lotes WHERE sku=?", (p["sku"],)).fetchall():
            dias = (date.fromisoformat(l["vencimiento"]) - hoy).days
            if dias <= p["dias_aviso_venc"]:
                nuevas.append(("VENCIMIENTO", p["sku"], l["lote_id"], "ALTA" if dias <= 1 else "MEDIA",
                               f"{p['nombre']} lote {l['lote_id']} vence en {dias} día(s)"))
    creadas = []
    for regla, sku, lote, prioridad, msg in nuevas:
        abierta = con.execute(
            "SELECT 1 FROM alertas WHERE regla=? AND sku=? AND COALESCE(lote_id,'')=COALESCE(?,'') "
            "AND estado='ABIERTA'", (regla, sku, lote)).fetchone()
        if abierta:
            continue
        aid = "ALR-" + uuid.uuid4().hex[:6].upper()
        con.execute("INSERT INTO alertas VALUES (?,?,?,?,?,?,?,?, 'ABIERTA', ?, NULL)",
                    (aid, regla, sku, lote, msg, destinatario, prioridad, "responsable de inventario", ahora()))
        creadas.append(con.execute("SELECT * FROM alertas WHERE alerta_id=?", (aid,)).fetchone())
    return creadas


def atender_alerta(con, alerta_id: str) -> None:
    con.execute("UPDATE alertas SET estado='ATENDIDA', atendida=? WHERE alerta_id=?", (ahora(), alerta_id))
