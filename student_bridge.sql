CREATE DATABASE student_bridge_db;
\connect student_bridge_db


DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS verifications;


-- ---------------USERS ------------------------------------------------

CREATE TABLE users (
  id           SERIAL PRIMARY KEY,
  username     VARCHAR(50)  NOT NULL UNIQUE,
  password     VARCHAR(255) NOT NULL,
  is_moderator BOOLEAN      NOT NULL DEFAULT FALSE
);


-- -------------- RESOURCES ---------------------------------------------

CREATE TABLE resources (
  id            SERIAL PRIMARY KEY,
  created_by    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title         VARCHAR(120) NOT NULL,
  description   TEXT,
  category      VARCHAR(30)  NOT NULL,
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
  status      VARCHAR(30) NOT NULL,
  note        TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
