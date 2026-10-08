"""Demostración ejecutable: recepción con báscula y efectos en saldo/reservas.

    python3 demo/demo_recepcion.py

TODAS LAS LECTURAS, PRODUCTOS, PRECIOS, UMBRALES Y PEDIDOS SON FICTICIOS.
Cada paso compara el resultado con la SALIDA ESPERADA y falla si no coincide.
La evidencia queda en demo/evidencia/.
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import threading
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import inventario as inv  # noqa: E402

EVIDENCIA = Path(__file__).parent / "evidencia"
SKU = "PECH-001"
log_lineas: list[str] = []


def log(texto: str = "") -> None:
    print(texto)
    log_lineas.append(texto)


def paso(titulo: str) -> None:
    log()
    log("=" * 78)
    log(titulo)
    log("=" * 78)


def verificar(con, esperado: tuple[float, float, float, float]) -> None:
    s = inv.saldo(con, SKU)
    log(f"  Saldo {SKU}: {s}")
    obtenido = (s.fisico, s.reservado, s.bloqueado, s.vendible)
    estado = "OK" if all(abs(a - b) < 1e-6 for a, b in zip(obtenido, esperado)) else "FALLA"
    log(f"  Esperado: físico={esperado[0]} reservado={esperado[1]} bloqueado={esperado[2]} "
        f"vendible={esperado[3]}  -> {estado}")
    if estado != "OK":
        raise SystemExit("La salida no coincide con la esperada")


def intentar(descripcion: str, fn, **kw) -> bool:
    try:
        fn(**kw)
        log(f"  [aceptado] {descripcion}")
        return True
    except inv.ErrorInventario as e:
        log(f"  [rechazado] {descripcion}: {e}")
        return False


def main() -> None:
    EVIDENCIA.mkdir(exist_ok=True)
    # Base en archivo temporal para poder probar concurrencia con varias conexiones.
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    con = inv.conectar(tmp.name)

    log("DEMO CHICKENMART - DATOS FICTICIOS - prototipo académico, no es un sistema instalado")
    con.execute("INSERT INTO productos VALUES (?,?,?,?,?,?)",
                (SKU, "Pechuga de pollo (ficticio)", "kg", 18000, 8.0, 2))
    log(f"  Producto ficticio: {SKU}, precio 18.000 COP/kg, mínimo SUPUESTO 8 kg, aviso venc. SUPUESTO 2 días")

    # ------------------------------------------------------------------ A1
    paso("1. A1 Recepción: lecturas FICTICIAS de la báscula -> peso estable -> tara -> confirmación")
    lecturas = [inv.LecturaBascula(kg, est) for kg, est in
                [(12.40, False), (20.95, False), (21.70, True), (21.58, True),
                 (21.62, True), (21.62, True), (21.62, True), (21.62, True)]]
    log("  Lecturas (kg, estable): " + ", ".join(f"({l.kg}, {l.estable})" for l in lecturas))
    bruto = inv.peso_estable(lecturas)
    log(f"  Peso bruto estable: {bruto} kg (se guarda 1 valor, no las 8 lecturas)")
    tara = 1.62  # canastilla, FICTICIO
    entrada = dict(captura_id="CAP-0001", sku=SKU, proveedor="Proveedor A (ficticio)",
                   lote_id="L-2026-1007", vencimiento="2026-10-10", bruto_kg=bruto, tara_kg=tara,
                   responsable="auxiliar_recepcion", confirmado_por_persona=True)
    log(f"  Entrada: {entrada}")
    mov_recepcion = inv.registrar_recepcion(con, **entrada)
    log(f"  Movimiento creado: {mov_recepcion} (neto = {bruto} - {tara} = 20.00 kg)")
    verificar(con, (20.0, 0.0, 0.0, 20.0))

    paso("2. Control: la cola offline reenvía la misma captura (reintento) -> no duplica")
    intentar("reenvío de CAP-0001", inv.registrar_recepcion, con=con, **entrada)
    intentar("tara mayor que el bruto", inv.registrar_recepcion, con=con,
             **{**entrada, "captura_id": "CAP-0002", "tara_kg": 25.0})
    intentar("recepción sin confirmación humana", inv.registrar_recepcion, con=con,
             **{**entrada, "captura_id": "CAP-0003", "confirmado_por_persona": False})
    verificar(con, (20.0, 0.0, 0.0, 20.0))

    # ------------------------------------------------------------------ A2
    paso("3. A2 Reservas: web 2,5 kg + WhatsApp 1,5 kg + bloqueo 1 kg -> 15 kg vendibles")
    inv.reservar(con, pedido_id="WEB-101", canal="web", sku=SKU, kg=2.5, responsable="sistema_web")
    inv.reservar(con, pedido_id="WA-201", canal="whatsapp", sku=SKU, kg=1.5, responsable="asesor_whatsapp")
    inv.bloquear(con, sku=SKU, lote_id="L-2026-1007", kg=1.0, responsable="administradora",
                 motivo="empaque dañado en revisión (ficticio)")
    verificar(con, (20.0, 4.0, 1.0, 15.0))

    paso("4. Caja pide 16 kg con 15 vendibles -> se rechaza y se ofrece ajustar")
    intentar("caja reserva 16 kg", inv.reservar, con=con, pedido_id="POS-301", canal="caja",
             sku=SKU, kg=16, responsable="cajero")
    verificar(con, (20.0, 4.0, 1.0, 15.0))

    paso("5. Ventas simultáneas: web y WhatsApp piden 10 kg cada uno AL MISMO TIEMPO")
    resultados: dict[str, bool] = {}
    barrera = threading.Barrier(2)

    def cliente(pid: str, canal: str) -> None:
        c = inv.conectar(tmp.name)
        barrera.wait()
        try:
            inv.reservar(c, pedido_id=pid, canal=canal, sku=SKU, kg=10, responsable=canal)
            resultados[pid] = True
        except inv.ErrorInventario as e:
            resultados[pid] = False
            resultados[pid + "_motivo"] = str(e)  # type: ignore[assignment]
        finally:
            c.close()

    hilos = [threading.Thread(target=cliente, args=a) for a in (("WEB-102", "web"), ("WA-202", "whatsapp"))]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    ganadores = [p for p in ("WEB-102", "WA-202") if resultados[p]]
    for p in ("WEB-102", "WA-202"):
        log(f"  {p}: {'reservado' if resultados[p] else 'rechazado -> ' + resultados[p + '_motivo']}")
    log(f"  Solo {len(ganadores)} reserva aceptada: el mismo saldo no se compromete dos veces")
    assert len(ganadores) == 1
    pedido_grande = ganadores[0]
    verificar(con, (20.0, 14.0, 1.0, 5.0))

    paso("6. Despacho WEB-101: reservado 2,5 kg, peso real 2,58 kg (dentro de ±5 % SUPUESTO)")
    inv.despachar(con, pedido_id="WEB-101", kg_real=2.58, responsable="alistador")
    log("  Un solo movimiento SALIDA: físico -2,58 y reservado -2,5 (no hay doble descuento)")
    verificar(con, (17.42, 11.5, 1.0, 4.92))

    paso(f"7. Despacho {pedido_grande}: reservado 10 kg, peso real 11,2 kg (+12 %) -> validar con cliente")
    intentar("despacho sin aceptación del cliente", inv.despachar, con=con, pedido_id=pedido_grande,
             kg_real=11.2, responsable="alistador")
    log("  Pedido queda PENDIENTE_CLIENTE. Cliente acepta el nuevo valor (11,2 kg x 18.000 = 201.600 COP)")
    inv.despachar(con, pedido_id=pedido_grande, kg_real=11.2, responsable="alistador",
                  cliente_acepta_cambio=True)
    verificar(con, (6.22, 1.5, 1.0, 3.72))

    paso("8. Cancelación WA-201 -> se libera la reserva")
    inv.cancelar(con, pedido_id="WA-201", responsable="asesor_whatsapp")
    intentar("cancelar WA-201 otra vez", inv.cancelar, con=con, pedido_id="WA-201", responsable="asesor_whatsapp")
    verificar(con, (6.22, 0.0, 1.0, 5.22))

    paso("9. Merma: el kg bloqueado se descarta y se registra (toda merma queda en el libro)")
    inv.registrar_merma(con, sku=SKU, lote_id="L-2026-1007", kg=1.0, responsable="administradora",
                        motivo="empaque dañado descartado (ficticio)", desde_bloqueado=True)
    verificar(con, (5.22, 0.0, 0.0, 5.22))

    paso("10. Corrección autorizada: la tara real era 1,82 kg -> neto 19,80 kg")
    intentar("auxiliar intenta corregir", inv.corregir_recepcion, con=con, mov_original=mov_recepcion,
             neto_correcto=19.80, responsable="auxiliar_recepcion", rol="auxiliar",
             motivo="tara mal configurada")
    intentar("administradora corrige", inv.corregir_recepcion, con=con, mov_original=mov_recepcion,
             neto_correcto=19.80, responsable="administradora", rol="administradora",
             motivo="tara mal configurada")
    log("  El movimiento original NO se borra: se agrega un AJUSTE que lo referencia (trazabilidad)")
    verificar(con, (5.02, 0.0, 0.0, 5.02))

    # ------------------------------------------------------------------ A3
    paso("11. A3 Alertas por reglas (fecha de evaluación ficticia: 2026-10-08)")
    for a in inv.evaluar_alertas(con, hoy=date(2026, 10, 8)):
        log(f"  {a['alerta_id']} [{a['prioridad']}] {a['regla']}: {a['mensaje']} -> {a['destinatario']}")
    repetidas = inv.evaluar_alertas(con, hoy=date(2026, 10, 8))
    log(f"  Segunda evaluación: {len(repetidas)} alertas nuevas (no se duplican mientras sigan abiertas)")
    assert not repetidas
    primera = con.execute("SELECT alerta_id FROM alertas ORDER BY creada LIMIT 1").fetchone()[0]
    inv.atender_alerta(con, primera)
    log(f"  {primera} marcada ATENDIDA (sirve para el indicador 'alertas atendidas / tiempo de respuesta')")

    # ------------------------------------------------------------------ export
    paso("12. Exportación para Orozco (Data Hub / Power BI)")
    for tabla in ("movimientos", "pedidos", "alertas", "lotes", "productos"):
        filas = con.execute(f"SELECT * FROM {tabla}").fetchall()
        with open(EVIDENCIA / f"{tabla}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(filas[0].keys() if filas else [])
            w.writerows(tuple(r) for r in filas)
        log(f"  demo/evidencia/{tabla}.csv ({len(filas)} filas)")
    (EVIDENCIA / "esquema.sql").write_text(inv.ESQUEMA.strip() + "\n", encoding="utf-8")
    log("  demo/evidencia/esquema.sql")

    log()
    log("RESULTADO: todos los pasos coinciden con la salida esperada.")
    log("LIMITACIONES: datos ficticios; sin báscula, web, caja ni WhatsApp reales; SQLite local en vez de")
    log("un servidor; sin autenticación real (los roles se pasan como texto); umbrales y tolerancias SUPUESTOS.")
    con.close()
    os.unlink(tmp.name)
    (EVIDENCIA / "salida_demo.txt").write_text("\n".join(log_lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
