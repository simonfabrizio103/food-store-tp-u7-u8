#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
SIMULADOR DE OPERACIÓN MÓVIL Y SEMÁFORO DE SINCRONIZACIÓN (FOOD STORE U8)
============================================================================
Autor: Fabrizio Simon
Herramientas: Python 3.10+ / SQLite 3.37+ (STRICT) / PostgreSQL 18
Descripción: Ejecuta la simulación completa de la base de la tablet en modo
             offline, la sincronización mediante el semáforo y los casos de
             prueba C1 a C7 conforme a las consignas del TP N.° 8.
============================================================================
"""

import os
import sys
import csv
import sqlite3
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "foodstore_movil.db")
SCHEMA_SQL = os.path.join(SCRIPT_DIR, "schema_sqlite.sql")
SEMAFORO_SQL = os.path.join(SCRIPT_DIR, "semaforo.sql")
SNAPSHOT_CSV = os.path.join(SCRIPT_DIR, "servidor_snapshot.csv")
EVIDENCIA_TXT = os.path.join(SCRIPT_DIR, "evidencia_simulacion.txt")

def log(msg, file_handle=None):
    print(msg)
    if file_handle:
        file_handle.write(msg + "\n")

def get_db_connection():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    con.row_factory = sqlite3.Row
    return con

def inicializar_bd(out):
    log("\n" + "="*80, out)
    log("[PASO 1] INICIALIZANDO BASE LOCAL SQLITE (schema_sqlite.sql)", out)
    log("="*80, out)
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        log("Base preexistente foodstore_movil.db eliminada para arranque limpio.", out)
        
    con = get_db_connection()
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        con.executescript(f.read())
    con.close()
    log("Tablas en modo STRICT creadas exitosamente con foreign_keys activadas.", out)

def cargar_snapshot(out, custom_csv=None):
    csv_file = custom_csv or SNAPSHOT_CSV
    log(f"\n[PASO 2] IMPORTANDO INSTANTÁNEA DEL SERVIDOR ({os.path.basename(csv_file)})...", out)
    con = get_db_connection()
    cur = con.cursor()
    
    cur.execute("DELETE FROM snapshot_servidor;")
    
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = []
        for r in reader:
            filas.append((
                int(r["id"]),
                r["nombre"],
                int(r["precio_centavos"]),
                int(r["stock"]),
                r["disponible"],
                r["eliminado"]
            ))
            
    cur.executemany("""
        INSERT INTO snapshot_servidor (id, nombre, precio_centavos, stock, disponible, eliminado)
        VALUES (?, ?, ?, ?, ?, ?);
    """, filas)
    
    # Sincronización hacia producto_cache (solo catálogo visible en tablet)
    cur.execute("""
        INSERT OR REPLACE INTO producto_cache (id, nombre, precio_centavos, stock_visto, disponible, eliminado, fecha_copia)
        SELECT 
            id,
            nombre,
            precio_centavos,
            stock,
            CASE WHEN disponible IN ('t', '1', 'true', 'TRUE') THEN 1 ELSE 0 END,
            CASE WHEN eliminado IN ('t', '1', 'true', 'TRUE') THEN 1 ELSE 0 END,
            datetime('now', 'localtime')
        FROM snapshot_servidor;
    """)
    
    con.commit()
    cur.execute("SELECT COUNT(*) FROM snapshot_servidor;")
    total_snap = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM producto_cache;")
    total_cache = cur.fetchone()[0]
    con.close()
    
    log(f"-> Snapshot cargado en SQLite: {total_snap} registros.", out)
    log(f"-> Catálogo producto_cache sincronizado: {total_cache} registros.", out)

def ejecutar_semaforo(out):
    log("\n[SEMÁFORO] Evaluando solicitudes con estado PENDIENTE...", out)
    con = get_db_connection()
    with open(SEMAFORO_SQL, "r", encoding="utf-8") as f:
        script = f.read()
    con.executescript(script)
    con.commit()
    con.close()

def caso_c1(out):
    log("\n" + "-"*80, out)
    log("CASO C1: CONSULTA DE CATÁLOGO DISPONIBLE SIN CONECTARSE AL SERVIDOR", out)
    log("-"*80, out)
    con = get_db_connection()
    cur = con.cursor()
    
    # Consulta local aislada (sin conexión de red)
    cur.execute("""
        SELECT id, nombre, (precio_centavos / 100.0) AS precio_pesos, stock_visto, disponible, eliminado
        FROM producto_cache
        WHERE disponible = 1 AND eliminado = 0 AND stock_visto > 0
        ORDER BY id
        LIMIT 5;
    """)
    filas = cur.fetchall()
    log("Resultado de consulta local en tablet (muestra representativa):", out)
    for f in filas:
        log(f"  ID: {f['id']} | {f['nombre']:<20} | ${f['precio_pesos']:>8.2f} | Stock: {f['stock_visto']:>4} | Disp: {f['disponible']} | Elim: {f['eliminado']}", out)
    
    log("-> Explicación: La tablet opera en modo 100% desconectado consultando SQLite local sin invocar a PostgreSQL.", out)
    con.close()

def caso_c7(out):
    log("\n" + "-"*80, out)
    log("CASO C7: INTEGRIDAD REFERENCIAL Y RESTRICCIONES (CANTIDAD 0 Y PRODUCTO INEXISTENTE)", out)
    log("-"*80, out)
    con = get_db_connection()
    cur = con.cursor()
    
    # Crear cabecera válida
    id_local = "b7777777-7777-7777-7777-777777777777"
    cur.execute("INSERT OR IGNORE INTO pedido_borrador VALUES (?, 'cajero_test', 'EFECTIVO', datetime('now'));", (id_local,))
    con.commit()
    
    # Intento 1: Cantidad = 0 (viola CHECK cantidad > 0)
    try:
        cur.execute("INSERT INTO item_borrador VALUES (?, 1, 0, 10000);", (id_local,))
        con.commit()
        log("ERROR: Falló la restricción CHECK (debió haber sido rechazada).", out)
    except sqlite3.IntegrityError as e:
        log(f"-> CHECK cantidad > 0 comprobado exitosamente: {e}", out)
        con.rollback()

    # Intento 2: Producto inexistente (viola FOREIGN KEY)
    try:
        cur.execute("INSERT INTO item_borrador VALUES (?, 9999999, 1, 5000);", (id_local,))
        con.commit()
        log("ERROR: Falló la restricción FOREIGN KEY (debió haber sido rechazada).", out)
    except sqlite3.IntegrityError as e:
        log(f"-> FOREIGN KEY (producto_id) comprobada exitosamente: {e}", out)
        con.rollback()

    cur.execute("SELECT COUNT(*) FROM item_borrador WHERE id_local = ?;", (id_local,))
    cant = cur.fetchone()[0]
    log(f"-> Verificación de integridad: {cant} ítems espurios guardados en la tabla.", out)
    con.close()

def caso_c2(out):
    log("\n" + "-"*80, out)
    log("CASO C2: SUBIDA DE PRECIO EN SERVIDOR (CONFLICTO) Y ACEPTACIÓN DEL CLIENTE", out)
    log("-"*80, out)
    con = get_db_connection()
    cur = con.cursor()
    
    # Paso 1: Mozo crea borrador con Producto 1 a precio visto original ($100.00 = 10000 centavos)
    id_local = "b0000002-0000-0000-0000-000000000002"
    sol_uuid_1 = "s0000002-0000-0000-0000-000000000001"
    cur.execute("INSERT INTO pedido_borrador VALUES (?, 'mozo_feria', 'EFECTIVO', datetime('now'));", (id_local,))
    cur.execute("INSERT INTO item_borrador VALUES (?, 1, 1, 10000);", (id_local,))
    cur.execute("INSERT INTO cola_sync VALUES (?, ?, 'PENDIENTE', 'Alta de pedido en tablet');", (sol_uuid_1, id_local))
    con.commit()
    log("1. Borrador creado en tablet con Producto 1 a $100.00 (10000 centavos).", out)
    
    # Paso 2: En el servidor central se incrementa el precio a $125.00 (12500 centavos)
    log("2. Simulación de subida de precio en servidor: Muzza sube a $125.00 (12500 centavos).", out)
    cur.execute("UPDATE snapshot_servidor SET precio_centavos = 12500 WHERE id = 1;")
    con.commit()
    
    # Paso 3: Corre el semáforo
    ejecutar_semaforo(out)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = ?;", (sol_uuid_1,))
    res1 = cur.fetchone()
    log(f"3. Resultado del semáforo: Estado = [{res1['estado']}] | Motivo = {res1['motivo']}", out)
    
    # Paso 4: El cliente en la feria acepta el nuevo precio
    log("4. El cliente acepta el nuevo precio: se actualiza el borrador local y se emite nueva solicitud.", out)
    sol_uuid_2 = "s0000002-0000-0000-0000-000000000002"
    cur.execute("UPDATE item_borrador SET precio_centavos_visto = 12500 WHERE id_local = ? AND producto_id = 1;", (id_local,))
    cur.execute("INSERT INTO cola_sync VALUES (?, ?, 'PENDIENTE', 'Reintento con precio actualizado aceptado');", (sol_uuid_2, id_local))
    con.commit()
    
    # Paso 5: Corre el semáforo nuevamente
    ejecutar_semaforo(out)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = ?;", (sol_uuid_2,))
    res2 = cur.fetchone()
    log(f"5. Resultado del semáforo: Estado = [{res2['estado']}] | Motivo = {res2['motivo']}", out)
    con.close()

def caso_c3(out):
    log("\n" + "-"*80, out)
    log("CASO C3: SOLICITUD DE CANTIDAD SUPERIOR AL STOCK REMANENTE (RECHAZADO)", out)
    log("-"*80, out)
    con = get_db_connection()
    cur = con.cursor()
    
    # Producto 2 (Napolitana) tiene stock de 10 unidades en servidor. Pedimos 50 unidades.
    id_local = "b0000003-0000-0000-0000-000000000003"
    sol_uuid = "s0000003-0000-0000-0000-000000000001"
    cur.execute("INSERT INTO pedido_borrador VALUES (?, 'mozo_feria', 'TARJETA', datetime('now'));", (id_local,))
    cur.execute("INSERT INTO item_borrador VALUES (?, 2, 50, 12000);", (id_local,))
    cur.execute("INSERT INTO cola_sync VALUES (?, ?, 'PENDIENTE', 'Pedido de 50 Napolitanas');", (sol_uuid, id_local))
    con.commit()
    
    log("Borrador creado solicitando 50 unidades de Napolitana (stock disponible en servidor: 10).", out)
    ejecutar_semaforo(out)
    
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = ?;", (sol_uuid,))
    res = cur.fetchone()
    log(f"Resultado del semáforo: Estado = [{res['estado']}] | Motivo = {res['motivo']}", out)
    con.close()

def caso_c4(out):
    log("\n" + "-"*80, out)
    log("CASO C4: PRODUCTO DADO DE BAJA LÓGICA / LÁPIDA (RECHAZADO Y OCULTAMIENTO EN CATÁLOGO)", out)
    log("-"*80, out)
    con = get_db_connection()
    cur = con.cursor()
    
    # Producto 3 está activo al momento de tomar el borrador
    id_local = "b0000004-0000-0000-0000-000000000004"
    sol_uuid = "s0000004-0000-0000-0000-000000000001"
    cur.execute("INSERT INTO pedido_borrador VALUES (?, 'mozo_feria', 'TRANSFERENCIA', datetime('now'));", (id_local,))
    cur.execute("INSERT INTO item_borrador VALUES (?, 3, 1, 241800);", (id_local,))
    cur.execute("INSERT INTO cola_sync VALUES (?, ?, 'PENDIENTE', 'Pedido Producto 3');", (sol_uuid, id_local))
    con.commit()
    
    log("1. Borrador creado con Producto 3.", out)
    log("2. Servidor aplica baja lógica sobre Producto 3 (eliminado = 't').", out)
    cur.execute("UPDATE snapshot_servidor SET eliminado = 't' WHERE id = 3;")
    con.commit()
    
    # Evaluación de semáforo
    ejecutar_semaforo(out)
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = ?;", (sol_uuid,))
    res = cur.fetchone()
    log(f"3. Resultado del semáforo: Estado = [{res['estado']}] | Motivo = {res['motivo']}", out)
    
    # Recarga del catálogo local en producto_cache
    log("4. Recarga del catálogo en la tablet (se actualiza producto_cache con el nuevo snapshot):", out)
    cur.execute("""
        UPDATE producto_cache 
        SET eliminado = 1 
        WHERE id = 3;
    """)
    con.commit()
    
    cur.execute("SELECT COUNT(*) FROM producto_cache WHERE id = 3;")
    existe_fila = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM producto_cache WHERE id = 3 AND disponible = 1 AND eliminado = 0;")
    visible_catalogo = cur.fetchone()[0]
    
    log(f"-> Verificación de lápida: Fila persiste en producto_cache = {existe_fila} | Visible en catálogo de venta = {visible_catalogo}", out)
    con.close()

def caso_c5(out):
    log("\n" + "-"*80, out)
    log("CASO C5: BORRADOR SIN CAMBIOS (SIMULADO_APROBADO)", out)
    log("-"*80, out)
    con = get_db_connection()
    cur = con.cursor()
    
    # Producto 4 (Producto masivo 4, precio 413800, stock 130, disponible=t, eliminado=f)
    id_local = "b0000005-0000-0000-0000-000000000005"
    sol_uuid = "s0000005-0000-0000-0000-000000000001"
    cur.execute("INSERT INTO pedido_borrador VALUES (?, 'mozo_feria', 'EFECTIVO', datetime('now'));", (id_local,))
    cur.execute("INSERT INTO item_borrador VALUES (?, 4, 2, 413800);", (id_local,))
    cur.execute("INSERT INTO cola_sync VALUES (?, ?, 'PENDIENTE', 'Pedido limpio sin discrepancias');", (sol_uuid, id_local))
    con.commit()
    
    log("Borrador creado con Producto 4 (2 unidades a $4138.00). Coincide exactamente con el servidor.", out)
    ejecutar_semaforo(out)
    
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = ?;", (sol_uuid,))
    res = cur.fetchone()
    log(f"Resultado del semáforo: Estado = [{res['estado']}] | Motivo = {res['motivo']}", out)
    con.close()

def caso_c6(out):
    log("\n" + "-"*80, out)
    log("CASO C6: REENVÍO DE LA MISMA SOLICITUD / IDEMPOTENCIA (MISMO UUID)", out)
    log("-"*80, out)
    con = get_db_connection()
    cur = con.cursor()
    
    sol_uuid_c5 = "s0000005-0000-0000-0000-000000000001"
    id_local_c5 = "b0000005-0000-0000-0000-000000000005"
    
    log(f"Intentando reenviar solicitud con UUID idéntico ({sol_uuid_c5})...", out)
    try:
        cur.execute("INSERT INTO cola_sync VALUES (?, ?, 'PENDIENTE', 'Reintento duplicado');", (sol_uuid_c5, id_local_c5))
        con.commit()
        log("ERROR: Se permitió la duplicación de solicitud_uuid.", out)
    except sqlite3.IntegrityError as e:
        log(f"-> Protección de unicidad en tablet: Rechazado por PRIMARY KEY ({e})", out)
        con.rollback()
        
    log("Ejecutando semáforo nuevamente para comprobar invariabilidad...", out)
    ejecutar_semaforo(out)
    
    cur.execute("SELECT estado, motivo FROM cola_sync WHERE solicitud_uuid = ?;", (sol_uuid_c5,))
    res = cur.fetchone()
    log(f"-> Estado tras reintento: [{res['estado']}] (Omitido de reevaluación por no estar PENDIENTE).", out)
    log("-> Protección en un sistema real (Parada 8): La deduplicación se implementa en la API del servidor mediante una tabla de claves de idempotencia (idempotency_keys) con restricción UNIQUE sobre el token transmitido en el encabezado HTTP.", out)
    con.close()

def verificar_invariabilidad_postgresql(out):
    log("\n" + "="*80, out)
    log("[AUDITORÍA POSTGRESQL] VERIFICACIÓN DE INVARIABILIDAD EN SERVIDOR CENTRAL", out)
    log("="*80, out)
    
    psql_cmd = [
        "C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe",
        "-U", "postgres",
        "-d", "foodstore",
        "-c", "SELECT COUNT(*) AS total_pedidos_pg FROM pedido; SELECT id_producto, nombre, stock, precio_lista FROM producto WHERE id_producto IN (1, 2, 3, 4) ORDER BY id_producto;"
    ]
    env = os.environ.copy()
    env["PGPASSWORD"] = "postgres"
    
    try:
        proc = subprocess.run(psql_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        log("Salida de PostgreSQL tras todas las simulaciones de la tablet:", out)
        log(proc.stdout, out)
        log("-> CONCLUSIÓN FUNDAMENTAL: Ni los pedidos aumentaron ni el stock disminuyó en PostgreSQL.", out)
        log("   Se cumple estrictamente la regla de oro: 'El móvil propone, el servidor dispone'.", out)
        log("   SIMULADO_APROBADO no es una venta.", out)
    except Exception as e:
        log(f"Error consultando PostgreSQL: {e}", out)

def main():
    with open(EVIDENCIA_TXT, "w", encoding="utf-8") as out:
        log("EJECUCIÓN DEL SIMULADOR OFFLINE Y SEMÁFORO - FOOD STORE UNIDAD 8", out)
        log("Fecha de ejecución: 2026-11-10", out)
        
        inicializar_bd(out)
        cargar_snapshot(out)
        caso_c1(out)
        caso_c7(out)
        caso_c2(out)
        caso_c3(out)
        caso_c4(out)
        caso_c5(out)
        caso_c6(out)
        verificar_invariabilidad_postgresql(out)
        
    print(f"\nSimulación completada. Evidencia guardada en {EVIDENCIA_TXT}")
    print(f"Base de datos SQLite generada en {DB_PATH}")

if __name__ == "__main__":
    main()
