-- ============================================================================
-- SCRIPT: schema_sqlite.sql
-- DESCRIPCIÓN: Esquema DDL para la base de datos local de la tablet (SQLite 3.37+)
-- PROYECTO: Food Store Móvil - Unidad 8
-- AUTOR: Fabrizio Simon
-- ============================================================================

-- Activación obligatoria de integridad referencial
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. Tabla: producto_cache
-- Catálogo local descargado desde la instantánea del servidor central.
-- Modo STRICT para forzar tipos estáticos y evitar inconsistencias de tipado.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS item_borrador;
DROP TABLE IF EXISTS cola_sync;
DROP TABLE IF EXISTS pedido_borrador;
DROP TABLE IF EXISTS producto_cache;
DROP TABLE IF EXISTS snapshot_servidor;

CREATE TABLE producto_cache (
    id INT PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio_centavos INT NOT NULL,
    stock_visto INT NOT NULL,
    disponible INT NOT NULL,
    eliminado INT NOT NULL,
    fecha_copia TEXT NOT NULL,
    CHECK (precio_centavos >= 0),
    CHECK (disponible IN (0, 1)),
    CHECK (eliminado IN (0, 1))
) STRICT;

-- ----------------------------------------------------------------------------
-- 2. Tabla: pedido_borrador
-- Cabecera del pedido tomado fuera de línea por el cajero/mozo en la feria.
-- ----------------------------------------------------------------------------
CREATE TABLE pedido_borrador (
    id_local TEXT PRIMARY KEY,
    usuario TEXT NOT NULL,
    forma_pago TEXT NOT NULL,
    fecha TEXT NOT NULL,
    CHECK (forma_pago IN ('EFECTIVO', 'TARJETA', 'TRANSFERENCIA'))
) STRICT;

-- ----------------------------------------------------------------------------
-- 3. Tabla: item_borrador
-- Líneas de detalle asociadas a un pedido local con precio congelado visto.
-- ----------------------------------------------------------------------------
CREATE TABLE item_borrador (
    id_local TEXT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_centavos_visto INT NOT NULL,
    PRIMARY KEY (id_local, producto_id),
    FOREIGN KEY (id_local) REFERENCES pedido_borrador(id_local) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto_cache(id),
    CHECK (cantidad > 0),
    CHECK (precio_centavos_visto >= 0)
) STRICT;

-- ----------------------------------------------------------------------------
-- 4. Tabla: cola_sync
-- Registro de solicitudes de sincronización remitidas a evaluación del servidor.
-- ----------------------------------------------------------------------------
CREATE TABLE cola_sync (
    solicitud_uuid TEXT PRIMARY KEY,
    id_local TEXT NOT NULL,
    estado TEXT NOT NULL,
    motivo TEXT,
    FOREIGN KEY (id_local) REFERENCES pedido_borrador(id_local) ON DELETE CASCADE,
    CHECK (estado IN ('PENDIENTE', 'CONFLICTO', 'RECHAZADO', 'SIMULADO_APROBADO'))
) STRICT;

-- ----------------------------------------------------------------------------
-- 5. Tabla auxiliar: snapshot_servidor
-- Recepción de la instantánea cruda exportada desde PostgreSQL (consigna 2.a).
-- ----------------------------------------------------------------------------
CREATE TABLE snapshot_servidor (
    id INT PRIMARY KEY,
    nombre TEXT NOT NULL,
    precio_centavos INT NOT NULL,
    stock INT NOT NULL,
    disponible TEXT NOT NULL,
    eliminado TEXT NOT NULL
) STRICT;
