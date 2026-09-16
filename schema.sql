-- ============================================================
--  Sistema de Gestion Hospitalaria / Clinica  -  PostgreSQL
--  Esquema de referencia (equivalente a los modelos SQLAlchemy).
--  Uso rapido:  createdb hospital_mvc  &&  psql hospital_mvc -f schema.sql
--  (La app tambien puede crear las tablas con:  flask --app run.py init-db)
-- ============================================================

DROP TABLE IF EXISTS facturas CASCADE;
DROP TABLE IF EXISTS examenes CASCADE;
DROP TABLE IF EXISTS recetas CASCADE;
DROP TABLE IF EXISTS historiales_clinicos CASCADE;
DROP TABLE IF EXISTS citas CASCADE;
DROP TABLE IF EXISTS pacientes CASCADE;
DROP TABLE IF EXISTS medicos CASCADE;
DROP TABLE IF EXISTS especialidades CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- ------------------------------------------------------------
CREATE TABLE usuarios (
    id            SERIAL PRIMARY KEY,
    nombre        VARCHAR(80)  NOT NULL,
    apellido      VARCHAR(80)  NOT NULL,
    email         VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol           VARCHAR(20)  NOT NULL DEFAULT 'recepcionista'
                  CHECK (rol IN ('administrador','medico','recepcionista','paciente')),
    activo        BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en     TIMESTAMP    DEFAULT NOW()
);

CREATE TABLE especialidades (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL UNIQUE,
    descripcion     TEXT,
    precio_consulta NUMERIC(10,2) NOT NULL DEFAULT 0
);

CREATE TABLE medicos (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER UNIQUE REFERENCES usuarios(id),
    especialidad_id INTEGER NOT NULL REFERENCES especialidades(id),
    nombres         VARCHAR(120) NOT NULL,
    apellidos       VARCHAR(120) NOT NULL,
    colegiatura     VARCHAR(40)  NOT NULL UNIQUE,
    telefono        VARCHAR(30),
    activo          BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE pacientes (
    id               SERIAL PRIMARY KEY,
    usuario_id       INTEGER UNIQUE REFERENCES usuarios(id),
    nombres          VARCHAR(120) NOT NULL,
    apellidos        VARCHAR(120) NOT NULL,
    dni              VARCHAR(20)  NOT NULL UNIQUE,
    fecha_nacimiento DATE,
    sexo             VARCHAR(1) CHECK (sexo IN ('M','F','O')),
    telefono         VARCHAR(30),
    direccion        VARCHAR(200),
    email            VARCHAR(160),
    tipo_sangre      VARCHAR(4),
    alergias         TEXT,
    creado_en        TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_pacientes_dni ON pacientes(dni);

CREATE TABLE citas (
    id           SERIAL PRIMARY KEY,
    paciente_id  INTEGER NOT NULL REFERENCES pacientes(id),
    medico_id    INTEGER NOT NULL REFERENCES medicos(id),
    fecha_hora   TIMESTAMP NOT NULL,
    duracion_min INTEGER NOT NULL DEFAULT 30,
    motivo       VARCHAR(255),
    estado       VARCHAR(20) NOT NULL DEFAULT 'programada'
                 CHECK (estado IN ('programada','atendida','cancelada','no_asistio')),
    notas        TEXT,
    creado_en    TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_citas_fecha ON citas(fecha_hora);

CREATE TABLE historiales_clinicos (
    id              SERIAL PRIMARY KEY,
    paciente_id     INTEGER NOT NULL REFERENCES pacientes(id),
    medico_id       INTEGER NOT NULL REFERENCES medicos(id),
    cita_id         INTEGER REFERENCES citas(id),
    fecha           TIMESTAMP NOT NULL DEFAULT NOW(),
    motivo_consulta VARCHAR(255),
    diagnostico     TEXT NOT NULL,
    tratamiento     TEXT,
    observaciones   TEXT,
    alergias        TEXT
);

CREATE TABLE recetas (
    id           SERIAL PRIMARY KEY,
    paciente_id  INTEGER NOT NULL REFERENCES pacientes(id),
    medico_id    INTEGER NOT NULL REFERENCES medicos(id),
    historial_id INTEGER REFERENCES historiales_clinicos(id),
    fecha        TIMESTAMP NOT NULL DEFAULT NOW(),
    diagnostico  VARCHAR(255),
    indicaciones TEXT,
    medicamentos JSONB NOT NULL DEFAULT '[]'
);

CREATE TABLE examenes (
    id              SERIAL PRIMARY KEY,
    paciente_id     INTEGER NOT NULL REFERENCES pacientes(id),
    medico_id       INTEGER NOT NULL REFERENCES medicos(id),
    cita_id         INTEGER REFERENCES citas(id),
    tipo            VARCHAR(120) NOT NULL,
    descripcion     TEXT,
    resultado       TEXT,
    estado          VARCHAR(20) NOT NULL DEFAULT 'solicitado'
                    CHECK (estado IN ('solicitado','en_proceso','completado','anulado')),
    fecha_solicitud TIMESTAMP DEFAULT NOW(),
    fecha_resultado TIMESTAMP
);

CREATE TABLE facturas (
    id          SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
    cita_id     INTEGER REFERENCES citas(id),
    numero      VARCHAR(20) UNIQUE,
    fecha       TIMESTAMP NOT NULL DEFAULT NOW(),
    subtotal    NUMERIC(10,2) NOT NULL DEFAULT 0,
    impuesto    NUMERIC(10,2) NOT NULL DEFAULT 0,
    total       NUMERIC(10,2) NOT NULL DEFAULT 0,
    estado      VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                CHECK (estado IN ('pendiente','pagada','anulada')),
    metodo_pago VARCHAR(30),
    detalle     JSONB NOT NULL DEFAULT '[]'
);

-- ------------------------------------------------------------
-- Datos de referencia
-- ------------------------------------------------------------
INSERT INTO especialidades (nombre, descripcion, precio_consulta) VALUES
  ('Medicina General', 'Atencion primaria', 60),
  ('Cardiologia',      'Corazon y sistema circulatorio', 120),
  ('Pediatria',        'Salud infantil', 90),
  ('Dermatologia',     'Piel', 100),
  ('Traumatologia',    'Huesos y articulaciones', 110);

-- Para usuarios/medicos/pacientes de demostracion usa:  flask --app run.py seed
