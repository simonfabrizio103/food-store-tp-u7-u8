// ============================================================================
// TRABAJO PRÁCTICO · UNIDAD 7: NoSQL y nuevas formas de almacenamiento
// Proyecto: Food Store | Base NoSQL: MongoDB
// Archivo: consultas_mongodb.js
// Compatible con mongosh y Node.js (MongoDB Driver)
// ============================================================================

// ----------------------------------------------------------------------------
// 1. SELECCIÓN DE BASE DE DATOS Y LIMPIEZA
// ----------------------------------------------------------------------------
// use foodstore_nosql;
db.pedidos.drop();

// ----------------------------------------------------------------------------
// 2. MIGRACIÓN: INSERCIÓN DE PEDIDOS (Consigna 2)
// Subconjunto representativo de pedidos de Food Store con líneas y cliente embebidos.
// Se conservan los IDs relacionales de origen (_id = id_pedido).
// ----------------------------------------------------------------------------

db.pedidos.insertMany([
  {
    _id: 2,
    fecha: ISODate("2025-10-30T18:44:05.346Z"),
    forma_pago: "EFECTIVO",
    estado: "ENTREGADO",
    cliente: {
      id_cliente: 1,
      nombre: "Juan",
      email: "juan@test.com"
    },
    lineas: [
      {
        id_producto: 3,
        nombre: "Producto masivo 3",
        categoria: "Pizzas",
        cantidad: 1,
        precio_unitario: 500.00,
        subtotal: 500.00
      },
      {
        id_producto: 4,
        nombre: "Producto masivo 4",
        categoria: "Categoria masiva 1",
        cantidad: 2,
        precio_unitario: 600.00,
        subtotal: 1200.00
      }
    ],
    total: 1700.00
  },
  {
    _id: 3,
    fecha: ISODate("2025-10-18T08:27:36.346Z"),
    forma_pago: "EFECTIVO",
    estado: "PENDIENTE",
    cliente: {
      id_cliente: 2,
      nombre: "Cliente masivo 2",
      email: "cliente_2@mail.com"
    },
    lineas: [
      {
        id_producto: 4,
        nombre: "Producto masivo 4",
        categoria: "Categoria masiva 1",
        cantidad: 2,
        precio_unitario: 500.00,
        subtotal: 1000.00
      }
    ],
    total: 1000.00
  },
  {
    _id: 4,
    fecha: ISODate("2025-10-17T17:02:22.346Z"),
    forma_pago: "EFECTIVO",
    estado: "ENTREGADO",
    cliente: {
      id_cliente: 3,
      nombre: "Cliente masivo 3",
      email: "cliente_3@mail.com"
    },
    lineas: [
      {
        id_producto: 3,
        nombre: "Producto masivo 3",
        categoria: "Pizzas",
        cantidad: 1,
        precio_unitario: 550.00,
        subtotal: 550.00
      },
      {
        id_producto: 5,
        nombre: "Producto masivo 5",
        categoria: "Categoria masiva 2",
        cantidad: 3,
        precio_unitario: 500.00,
        subtotal: 1500.00
      }
    ],
    total: 2050.00
  },
  {
    _id: 5,
    fecha: ISODate("2026-06-21T04:29:47.346Z"),
    forma_pago: "EFECTIVO",
    estado: "CANCELADO",
    cliente: {
      id_cliente: 4,
      nombre: "Cliente masivo 4",
      email: "cliente_4@mail.com"
    },
    lineas: [
      {
        id_producto: 6,
        nombre: "Producto masivo 6",
        categoria: "Categoria masiva 3",
        cantidad: 4,
        precio_unitario: 500.00,
        subtotal: 2000.00
      }
    ],
    total: 2000.00
  },
  {
    _id: 6,
    fecha: ISODate("2026-07-06T04:47:13.346Z"),
    forma_pago: "EFECTIVO",
    estado: "PENDIENTE",
    cliente: {
      id_cliente: 5,
      nombre: "Cliente masivo 5",
      email: "cliente_5@mail.com"
    },
    lineas: [
      {
        id_producto: 3,
        nombre: "Producto masivo 3",
        categoria: "Pizzas",
        cantidad: 2,
        precio_unitario: 500.00,
        subtotal: 1000.00
      },
      {
        id_producto: 7,
        nombre: "Producto masivo 7",
        categoria: "Categoria masiva 4",
        cantidad: 5,
        precio_unitario: 500.00,
        subtotal: 2500.00
      }
    ],
    total: 3500.00
  },
  {
    _id: 7,
    fecha: ISODate("2026-03-22T21:38:34.346Z"),
    forma_pago: "EFECTIVO",
    estado: "ENTREGADO",
    cliente: {
      id_cliente: 6,
      nombre: "Cliente masivo 6",
      email: "cliente_6@mail.com"
    },
    lineas: [
      {
        id_producto: 8,
        nombre: "Producto masivo 8",
        categoria: "Categoria masiva 5",
        cantidad: 1,
        precio_unitario: 500.00,
        subtotal: 500.00
      }
    ],
    total: 500.00
  }
]);

// ----------------------------------------------------------------------------
// 3. ÍNDICES DE RENDIMIENTO RECOMENDADOS
// ----------------------------------------------------------------------------
db.pedidos.createIndex({ estado: 1 });
db.pedidos.createIndex({ "lineas.id_producto": 1 });
db.pedidos.createIndex({ total: 1 });

// ============================================================================
// 4. CONSULTAS REQUERIDAS (Consigna 4)
// ============================================================================

// a) Mostrar todos los pedidos, incluyendo su identificador y estado
print("--- Consulta 4.a: Todos los pedidos con identificador y estado ---");
db.pedidos.find(
  {},
  { _id: 1, estado: 1 }
).sort({ _id: 1 });

// b) Filtrar pedidos por un estado que exista en los datos migrados ('ENTREGADO')
print("--- Consulta 4.b: Pedidos con estado 'ENTREGADO' ---");
db.pedidos.find(
  { estado: "ENTREGADO" },
  { _id: 1, fecha: 1, estado: 1, "cliente.nombre": 1, total: 1 }
).sort({ _id: 1 });

// c) Buscar pedidos que contengan un producto determinado dentro del arreglo de líneas (id_producto: 3)
print("--- Consulta 4.c: Pedidos que contienen el producto con ID 3 ---");
db.pedidos.find(
  { "lineas.id_producto": 3 },
  { _id: 1, estado: 1, "cliente.nombre": 1, total: 1, "lineas.$": 1 }
).sort({ _id: 1 });

// d) Buscar pedidos cuyo total sea superior a un importe elegido ($2000.00) y justificar el umbral
// Justificación: El umbral de $2000.00 separa compras cotidianas/individuales de pedidos
// mayoristas o de grupos familiares en el contexto de Food Store.
print("--- Consulta 4.d: Pedidos con total superior a $2000.00 ---");
db.pedidos.find(
  { total: { $gt: 2000.00 } },
  { _id: 1, "cliente.nombre": 1, estado: 1, total: 1 }
).sort({ _id: 1 });
