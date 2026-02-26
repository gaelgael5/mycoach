-- Extensions PostgreSQL requises par MyCoach
-- Exécuté automatiquement au premier démarrage du container

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "unaccent";     -- unaccent() pour search_token
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- Index GIN trigram pour recherche fulltext
CREATE EXTENSION IF NOT EXISTS "btree_gin";    -- Index GIN sur types scalaires
