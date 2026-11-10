// ============================================================================
// TRABAJO PRÁCTICO · UNIDAD 7: NoSQL y nuevas formas de almacenamiento
// Archivo: ejecutar_mongodb.js
// Ejecutor automatizado y generador de evidencia en Node.js + MongoDB
// ============================================================================

const { MongoMemoryServer } = require('mongodb-memory-server');
const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

async function main() {
    console.log("=====================================================================");
    console.log("INICIANDO MOTOR MONGODB Y ENTORNO DE PRUEBAS (UNIDAD 7)");
    console.log("=====================================================================");

    const mongod = await MongoMemoryServer.create();
    const uri = mongod.getUri();
    console.log(`[+] Instancia MongoDB activa en: ${uri}`);

    const client = new MongoClient(uri);
    await client.connect();

    const db = client.db('foodstore_nosql');
    const pedidosColl = db.collection('pedidos');

    let outputLog = "";
    function log(msg) {
        console.log(msg);
        outputLog += msg + "\n";
    }

    log(`MongoDB Server URI: ${uri}`);
    log(`Base de datos: foodstore_nosql | Colección: pedidos\n`);

    // 1. Limpieza
    await pedidosColl.drop().catch(() => {});

    // 2. Migración (Consigna 2)
    const documentos = [
        {
            _id: 2,
            fecha: new Date("2025-10-30T18:44:05.346Z"),
            forma_pago: "EFECTIVO",
            estado: "ENTREGADO",
            cliente: { id_cliente: 1, nombre: "Juan", email: "juan@test.com" },
            lineas: [
                { id_producto: 3, nombre: "Producto masivo 3", categoria: "Pizzas", cantidad: 1, precio_unitario: 500.00, subtotal: 500.00 },
                { id_producto: 4, nombre: "Producto masivo 4", categoria: "Categoria masiva 1", cantidad: 2, precio_unitario: 600.00, subtotal: 1200.00 }
            ],
            total: 1700.00
        },
        {
            _id: 3,
            fecha: new Date("2025-10-18T08:27:36.346Z"),
            forma_pago: "EFECTIVO",
            estado: "PENDIENTE",
            cliente: { id_cliente: 2, nombre: "Cliente masivo 2", email: "cliente_2@mail.com" },
            lineas: [
                { id_producto: 4, nombre: "Producto masivo 4", categoria: "Categoria masiva 1", cantidad: 2, precio_unitario: 500.00, subtotal: 1000.00 }
            ],
            total: 1000.00
        },
        {
            _id: 4,
            fecha: new Date("2025-10-17T17:02:22.346Z"),
            forma_pago: "EFECTIVO",
            estado: "ENTREGADO",
            cliente: { id_cliente: 3, nombre: "Cliente masivo 3", email: "cliente_3@mail.com" },
            lineas: [
                { id_producto: 3, nombre: "Producto masivo 3", categoria: "Pizzas", cantidad: 1, precio_unitario: 550.00, subtotal: 550.00 },
                { id_producto: 5, nombre: "Producto masivo 5", categoria: "Categoria masiva 2", cantidad: 3, precio_unitario: 500.00, subtotal: 1500.00 }
            ],
            total: 2050.00
        },
        {
            _id: 5,
            fecha: new Date("2026-06-21T04:29:47.346Z"),
            forma_pago: "EFECTIVO",
            estado: "CANCELADO",
            cliente: { id_cliente: 4, nombre: "Cliente masivo 4", email: "cliente_4@mail.com" },
            lineas: [
                { id_producto: 6, nombre: "Producto masivo 6", categoria: "Categoria masiva 3", cantidad: 4, precio_unitario: 500.00, subtotal: 2000.00 }
            ],
            total: 2000.00
        },
        {
            _id: 6,
            fecha: new Date("2026-07-06T04:47:13.346Z"),
            forma_pago: "EFECTIVO",
            estado: "PENDIENTE",
            cliente: { id_cliente: 5, nombre: "Cliente masivo 5", email: "cliente_5@mail.com" },
            lineas: [
                { id_producto: 3, nombre: "Producto masivo 3", categoria: "Pizzas", cantidad: 2, precio_unitario: 500.00, subtotal: 1000.00 },
                { id_producto: 7, nombre: "Producto masivo 7", categoria: "Categoria masiva 4", cantidad: 5, precio_unitario: 500.00, subtotal: 2500.00 }
            ],
            total: 3500.00
        },
        {
            _id: 7,
            fecha: new Date("2026-03-22T21:38:34.346Z"),
            forma_pago: "EFECTIVO",
            estado: "ENTREGADO",
            cliente: { id_cliente: 6, nombre: "Cliente masivo 6", email: "cliente_6@mail.com" },
            lineas: [
                { id_producto: 8, nombre: "Producto masivo 8", categoria: "Categoria masiva 5", cantidad: 1, precio_unitario: 500.00, subtotal: 500.00 }
            ],
            total: 500.00
        }
    ];

    log("[-] Ejecutando insertMany() con 6 pedidos...");
    const insertResult = await pedidosColl.insertMany(documentos);
    log(`[+] Documentos insertados con éxito: ${insertResult.insertedCount}`);

    // Índices
    await pedidosColl.createIndex({ estado: 1 });
    await pedidosColl.createIndex({ "lineas.id_producto": 1 });
    await pedidosColl.createIndex({ total: 1 });

    log("\n=====================================================================");
    log("CONSULTA 4.a: Todos los pedidos con identificador y estado");
    log("db.pedidos.find({}, { _id: 1, estado: 1 })");
    log("=====================================================================");
    const resA = await pedidosColl.find({}, { projection: { _id: 1, estado: 1 } }).sort({ _id: 1 }).toArray();
    log(JSON.stringify(resA, null, 2));

    log("\n=====================================================================");
    log("CONSULTA 4.b: Filtrar pedidos por estado = 'ENTREGADO'");
    log("db.pedidos.find({ estado: 'ENTREGADO' }, { _id: 1, fecha: 1, estado: 1, 'cliente.nombre': 1, total: 1 })");
    log("=====================================================================");
    const resB = await pedidosColl.find(
        { estado: "ENTREGADO" },
        { projection: { _id: 1, fecha: 1, estado: 1, "cliente.nombre": 1, total: 1 } }
    ).sort({ _id: 1 }).toArray();
    log(JSON.stringify(resB, null, 2));
    log(`Cantidad recuperada: ${resB.length} pedidos (IDs: ${resB.map(p => p._id).join(', ')})`);

    log("\n=====================================================================");
    log("CONSULTA 4.c: Buscar pedidos con id_producto = 3 dentro del arreglo de líneas");
    log("db.pedidos.find({ 'lineas.id_producto': 3 })");
    log("=====================================================================");
    const resC = await pedidosColl.find(
        { "lineas.id_producto": 3 },
        { projection: { _id: 1, estado: 1, "cliente.nombre": 1, total: 1, lineas: { $elemMatch: { id_producto: 3 } } } }
    ).sort({ _id: 1 }).toArray();
    log(JSON.stringify(resC, null, 2));
    log(`Cantidad recuperada: ${resC.length} pedidos (IDs: ${resC.map(p => p._id).join(', ')})`);

    log("\n=====================================================================");
    log("CONSULTA 4.d: Pedidos con total > $2000.00 (Justificado: Segmento Mayorista)");
    log("db.pedidos.find({ total: { $gt: 2000.00 } }, { _id: 1, 'cliente.nombre': 1, estado: 1, total: 1 })");
    log("=====================================================================");
    const resD = await pedidosColl.find(
        { total: { $gt: 2000.00 } },
        { projection: { _id: 1, "cliente.nombre": 1, estado: 1, total: 1 } }
    ).sort({ _id: 1 }).toArray();
    log(JSON.stringify(resD, null, 2));
    log(`Cantidad recuperada: ${resD.length} pedidos (IDs: ${resD.map(p => p._id).join(', ')})`);

    log("\n=====================================================================");
    log("RESUMEN DE VERIFICACIÓN (CONSIGNA 5)");
    log("=====================================================================");
    log(`Filtro Estado ENTREGADO    : Cantidad = ${resB.length} | IDs = [${resB.map(p => p._id).join(', ')}]`);
    log(`Filtro Producto con ID 3   : Cantidad = ${resC.length} | IDs = [${resC.map(p => p._id).join(', ')}]`);

    // Guardar log de evidencia
    const logPath = path.join(__dirname, 'evidencia_mongodb.txt');
    fs.writeFileSync(logPath, outputLog, 'utf8');
    console.log(`\n[+] Evidencia guardada en: ${logPath}`);

    await client.close();
    await mongod.stop();
    console.log("[+] Servidor MongoDB cerrado limpiamente.");
}

main().catch(err => {
    console.error("ERROR:", err);
    process.exit(1);
});
