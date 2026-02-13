DROP DATABASE IF EXISTS student_bridge_db;
CREATE DATABASE student_bridge_db;
\connect student_bridge_db


DROP TABLE IF EXISTS saves;
DROP TABLE IF EXISTS verifications;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS users;

DROP TYPE IF EXISTS resource_category;
DROP TYPE IF EXISTS verification_status;
-- ---------------USERS ------------------------------------------------

CREATE TABLE users (
  id           SERIAL PRIMARY KEY,
  username     VARCHAR(50)  NOT NULL UNIQUE,
  password     VARCHAR(255) NOT NULL,
  is_moderator BOOLEAN      NOT NULL DEFAULT FALSE
);

-- --------------- ENUM ---------
CREATE TYPE resource_category AS ENUM (
  'Food',
  'Housing',
  'Health',
  'Education'
); 

CREATE TYPE verification_status AS ENUM (
  'Active',
  'Temporarily Closed',
  'No Longer Available',
  'Info Needs Update'
);
-- -------------- RESOURCES ---------------------------------------------

CREATE TABLE resources (
  id            SERIAL PRIMARY KEY,
  created_by    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title         VARCHAR(120) NOT NULL,
  description   TEXT,
  category      resource_category NOT NULL,
  address       TEXT         NOT NULL,
  city          VARCHAR(80)  NOT NULL,
  lat           NUMERIC(9,6) NOT NULL,
  lng           NUMERIC(9,6) NOT NULL,
  requirements  TEXT,
  hidden_reason TEXT,
  hidden_at     TIMESTAMPTZ,             
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------- VERIFICATIONS 

CREATE TABLE verifications (
  id          SERIAL PRIMARY KEY,
  resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status      verification_status NOT NULL DEFAULT 'Active',
  note        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE verifications
ADD CONSTRAINT uq_verification_once UNIQUE (resource_id, user_id);
-- ------------------- SAVES -----

CREATE TABLE saves (
  id          SERIAL PRIMARY KEY,
  resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_save UNIQUE (resource_id, user_id)
);
