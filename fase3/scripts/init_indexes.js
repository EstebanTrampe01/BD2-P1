// se ejecuta automaticamente al iniciar el contenedor de MongoDB para crear los índices necesarios

db = db.getSiblingDB("mundiales");

// Coleccion: mundiales 
// Consulta principal: buscar por año
db.mundiales.createIndex({ anio: 1 }, { unique: true, name: "idx_mundiales_anio" });

// Filtros frecuentes dentro de un mundial
db.mundiales.createIndex({ "partidos.local": 1 },    { name: "idx_mundiales_partido_local" });
db.mundiales.createIndex({ "partidos.visitante": 1 }, { name: "idx_mundiales_partido_visitante" });
db.mundiales.createIndex({ "partidos.etapa": 1 },    { name: "idx_mundiales_partido_etapa" });
db.mundiales.createIndex({ "partidos.fecha": 1 },    { name: "idx_mundiales_partido_fecha" });
db.mundiales.createIndex({ "grupos.grupo": 1 },      { name: "idx_mundiales_grupo" });
db.mundiales.createIndex({ "grupos.seleccion": 1 },  { name: "idx_mundiales_grupo_seleccion" });

//  Coleccion: selecciones 
// Consulta principal: buscar por nombre de pais
db.selecciones.createIndex({ nombre: 1 }, { unique: true, name: "idx_selecciones_nombre" });
db.selecciones.createIndex(
  { nombre: "text" },
  { name: "idx_selecciones_text", default_language: "spanish" }
);

// indices de soporte para la consulta de pais
db.selecciones.createIndex({ "participaciones.anio": 1 },       { name: "idx_sel_part_anio" });
db.selecciones.createIndex({ "participaciones.partidos.local": 1 },
                            { name: "idx_sel_part_partido_local" });
db.selecciones.createIndex({ "participaciones.partidos.visitante": 1 },
                            { name: "idx_sel_part_partido_visitante" });

print("si,  indices creados correctamente en la BD mundiales.");


//este script sirve para crear los indices necesarios en la base de datos de MongoDB, se ejecuta automaticamente al iniciar el contenedor de MongoDB 