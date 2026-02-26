-- MyCoach — Initialisation PostgreSQL
-- Exécuté une seule fois à la création du volume

-- Extensions utiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS "unaccent";     -- recherche sans accent
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- recherche full-text fuzzy (LIKE rapide)
CREATE EXTENSION IF NOT EXISTS "btree_gin";    -- index GIN sur types scalaires

-- Timezone par défaut
SET timezone = 'UTC';

-- Note : les tables sont créées par Alembic (alembic upgrade head)
-- Ce script prépare uniquement les extensions et paramètres globaux
