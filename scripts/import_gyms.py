#!/usr/bin/env python3
"""
MyCoach — Script d'intégration des données de salles de sport
═══════════════════════════════════════════════════════════════
Usage :
  python scripts/import_gyms.py [--franchise <nom>] [--dry-run] [--reset]

Options :
  --franchise <nom>  Importer uniquement cette franchise (ex: basic_fit)
  --dry-run          Valider les données sans écrire en base
  --reset            Supprimer les données existantes avant import (DANGER)
  --verbose          Afficher le détail de chaque salle

Description :
  Lit tous les fichiers JSON du dossier Datas/*.json et les importe
  dans la table `gyms` de la base PostgreSQL.

  Chaque fichier JSON doit respecter le schéma suivant :
  {
    "franchise": "basic_fit",           ← slug de la franchise (correspond à gym_chains.slug)
    "source_url": "https://...",        ← URL d'où les données ont été extraites
    "extracted_at": "2026-02-25T...",   ← Date d'extraction ISO 8601
    "clubs": [
      {
        "external_id": "BF-1234",       ← ID unique dans le système source
        "name": "Basic-Fit Paris ...",  ← Nom complet du club
        "address": "12 rue de la Paix", ← Adresse (sans CP ni ville)
        "zip_code": "75002",            ← Code postal
        "city": "Paris",                ← Ville
        "country": "FR",                ← ISO 3166-1 alpha-2
        "latitude": 48.8698,            ← Optionnel
        "longitude": 2.3315,            ← Optionnel
        "phone": "+33 1 23 45 67 89",   ← Optionnel
        "email": null,                  ← Optionnel
        "website_url": "https://...",   ← Optionnel
        "open_24h": true,               ← Optionnel
        "services": ["parking", ...]    ← Optionnel
      }
    ]
  }

Exit codes :
  0 = succès
  1 = erreur de fichier/validation
  2 = erreur base de données
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import asyncpg

# ─── Configuration ────────────────────────────────────────────────────────────

DATAS_DIR = Path(__file__).parent.parent / "Datas"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://mycoach:mycoach_dev@localhost:5432/mycoach"
).replace("postgresql+asyncpg://", "postgresql://")  # asyncpg ne veut pas le préfixe +asyncpg

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("import_gyms")

# ─── Schéma attendu ───────────────────────────────────────────────────────────

REQUIRED_CLUB_FIELDS = {"name", "city", "country"}
OPTIONAL_CLUB_FIELDS = {
    "external_id", "address", "zip_code", "latitude", "longitude",
    "phone", "email", "website_url", "open_24h", "services"
}


# ─── Validation ───────────────────────────────────────────────────────────────

def validate_file(data: dict, filepath: Path) -> list[str]:
    """Retourne la liste des erreurs de validation."""
    errors = []

    if "franchise" not in data:
        errors.append("Champ manquant : 'franchise'")
    if "clubs" not in data:
        errors.append("Champ manquant : 'clubs'")
        return errors

    if not isinstance(data["clubs"], list):
        errors.append("'clubs' doit être une liste")
        return errors

    if len(data["clubs"]) == 0:
        errors.append("La liste 'clubs' est vide")

    for i, club in enumerate(data["clubs"]):
        prefix = f"clubs[{i}]"
        for field in REQUIRED_CLUB_FIELDS:
            if field not in club or not club[field]:
                errors.append(f"{prefix} : champ obligatoire manquant ou vide : '{field}'")

        country = club.get("country", "")
        if country and len(country) != 2:
            errors.append(f"{prefix} : 'country' doit être ISO 3166-1 alpha-2 (ex: 'FR'), reçu: '{country}'")

        lat = club.get("latitude")
        lng = club.get("longitude")
        if lat is not None and not (-90 <= float(lat) <= 90):
            errors.append(f"{prefix} : latitude invalide: {lat}")
        if lng is not None and not (-180 <= float(lng) <= 180):
            errors.append(f"{prefix} : longitude invalide: {lng}")

    return errors


# ─── Import DB ────────────────────────────────────────────────────────────────

async def get_or_create_chain(conn: asyncpg.Connection, franchise_slug: str) -> int:
    """Retourne l'ID de la chaîne, la crée si elle n'existe pas."""
    row = await conn.fetchrow(
        "SELECT id FROM gym_chains WHERE slug = $1", franchise_slug
    )
    if row:
        return row["id"]

    # Créer avec nom = slug humanisé (peut être mis à jour manuellement ensuite)
    name = franchise_slug.replace("_", " ").title()
    row = await conn.fetchrow(
        """
        INSERT INTO gym_chains (name, slug, country, created_at, updated_at)
        VALUES ($1, $2, 'FR', NOW(), NOW())
        RETURNING id
        """,
        name, franchise_slug
    )
    log.info(f"Chaîne créée : '{name}' (slug={franchise_slug}, id={row['id']})")
    return row["id"]


async def import_clubs(
    conn: asyncpg.Connection,
    chain_id: int,
    franchise_slug: str,
    clubs: list[dict],
    dry_run: bool,
    verbose: bool,
) -> dict[str, int]:
    """Import une liste de clubs. Retourne stats {inserted, updated, skipped}."""
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "error": 0}

    for club in clubs:
        external_id = club.get("external_id") or f"{franchise_slug}_{club['name'][:30]}"
        name = club["name"].strip()
        city = club["city"].strip()
        country = club["country"].upper()
        address = (club.get("address") or "").strip() or None
        zip_code = (club.get("zip_code") or "").strip() or None
        lat = club.get("latitude")
        lng = club.get("longitude")
        phone = club.get("phone")
        email = club.get("email")
        website_url = club.get("website_url")
        open_24h = club.get("open_24h", False)

        try:
            if dry_run:
                if verbose:
                    log.info(f"  [DRY-RUN] {name} — {city} ({country})")
                stats["inserted"] += 1
                continue

            # Upsert : si external_id existe → update, sinon insert
            existing = await conn.fetchrow(
                "SELECT id FROM gyms WHERE chain_id = $1 AND external_id = $2",
                chain_id, external_id
            )

            if existing:
                await conn.execute(
                    """
                    UPDATE gyms SET
                        name = $1, address = $2, zip_code = $3, city = $4,
                        country = $5, latitude = $6, longitude = $7,
                        phone = $8, email = $9, website_url = $10,
                        open_24h = $11, updated_at = NOW()
                    WHERE id = $12
                    """,
                    name, address, zip_code, city, country,
                    lat, lng, phone, email, website_url, open_24h,
                    existing["id"]
                )
                if verbose:
                    log.info(f"  ✏️  UPDATED  {name} — {city}")
                stats["updated"] += 1
            else:
                await conn.execute(
                    """
                    INSERT INTO gyms (
                        chain_id, external_id, name, address, zip_code,
                        city, country, latitude, longitude, phone, email,
                        website_url, open_24h, validated, created_at, updated_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                        TRUE, NOW(), NOW()
                    )
                    """,
                    chain_id, external_id, name, address, zip_code,
                    city, country, lat, lng, phone, email, website_url, open_24h
                )
                if verbose:
                    log.info(f"  ✅ INSERTED {name} — {city}")
                stats["inserted"] += 1

        except asyncpg.exceptions.UniqueViolationError:
            log.warning(f"  ⚠️  SKIP (doublon) {name} — {city}")
            stats["skipped"] += 1
        except Exception as e:
            log.error(f"  ❌ ERREUR {name}: {e}")
            stats["error"] += 1

    return stats


async def reset_franchise(conn: asyncpg.Connection, chain_id: int):
    count = await conn.fetchval("DELETE FROM gyms WHERE chain_id = $1 RETURNING id", chain_id)
    log.warning(f"  ⚠️  {count or 0} clubs supprimés pour chain_id={chain_id}")


# ─── Main ─────────────────────────────────────────────────────────────────────

async def main(args: argparse.Namespace):
    # Découvrir les fichiers JSON
    json_files = sorted(DATAS_DIR.glob("*.json"))
    if not json_files:
        log.error(f"Aucun fichier JSON trouvé dans {DATAS_DIR}")
        sys.exit(1)

    if args.franchise:
        json_files = [f for f in json_files if args.franchise in f.stem]
        if not json_files:
            log.error(f"Aucun fichier trouvé pour la franchise '{args.franchise}'")
            sys.exit(1)

    log.info(f"{'[DRY-RUN] ' if args.dry_run else ''}Fichiers à importer : {[f.name for f in json_files]}")

    # Charger et valider
    datasets: list[tuple[Path, dict]] = []
    for filepath in json_files:
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            log.error(f"JSON invalide dans {filepath.name}: {e}")
            sys.exit(1)

        errors = validate_file(data, filepath)
        if errors:
            log.error(f"Validation échouée pour {filepath.name}:")
            for err in errors:
                log.error(f"  - {err}")
            sys.exit(1)

        log.info(f"✅ {filepath.name} : {len(data['clubs'])} clubs (franchise={data['franchise']})")
        datasets.append((filepath, data))

    if args.dry_run:
        log.info("\n[DRY-RUN] Validation OK — aucune écriture en base")
        total = sum(len(d["clubs"]) for _, d in datasets)
        log.info(f"Total clubs validés : {total}")
        return

    # Connexion DB
    try:
        conn = await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        log.error(f"Connexion DB impossible: {e}")
        log.error(f"DATABASE_URL utilisée: {DATABASE_URL}")
        sys.exit(2)

    global_stats = {"inserted": 0, "updated": 0, "skipped": 0, "error": 0}

    try:
        for filepath, data in datasets:
            franchise = data["franchise"]
            clubs = data["clubs"]
            extracted_at = data.get("extracted_at", "?")

            log.info(f"\n{'─'*60}")
            log.info(f"Franchise : {franchise}")
            log.info(f"Clubs     : {len(clubs)}")
            log.info(f"Source    : {data.get('source_url', 'N/A')}")
            log.info(f"Extrait   : {extracted_at}")

            chain_id = await get_or_create_chain(conn, franchise)

            if args.reset:
                await reset_franchise(conn, chain_id)

            stats = await import_clubs(conn, chain_id, franchise, clubs, args.dry_run, args.verbose)

            log.info(f"Résultat  : ✅ {stats['inserted']} insérés | ✏️  {stats['updated']} MàJ | ⚠️  {stats['skipped']} doublons | ❌ {stats['error']} erreurs")

            for k, v in stats.items():
                global_stats[k] += v

    finally:
        await conn.close()

    log.info(f"\n{'═'*60}")
    log.info(f"TOTAL : ✅ {global_stats['inserted']} insérés | ✏️  {global_stats['updated']} MàJ | ⚠️  {global_stats['skipped']} doublons | ❌ {global_stats['error']} erreurs")

    if global_stats["error"] > 0:
        sys.exit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MyCoach — Import des salles de sport depuis Datas/*.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--franchise", help="Importer uniquement cette franchise (slug)")
    parser.add_argument("--dry-run", action="store_true", help="Valider sans écrire en base")
    parser.add_argument("--reset", action="store_true", help="Supprimer les données existantes avant import")
    parser.add_argument("--verbose", "-v", action="store_true", help="Détail de chaque salle")

    args = parser.parse_args()

    if args.reset and args.dry_run:
        parser.error("--reset et --dry-run sont incompatibles")

    asyncio.run(main(args))
