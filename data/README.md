# MyCoach — Référentiels de Salles de Sport

Ce dossier contient les données de référence des salles de sport,
extraites depuis les sites officiels des franchises et normalisées au format canonique.

## Fichiers disponibles

| Fichier | Franchise | Clubs | Adresses | Lat/Lng | Dernière extraction |
|---------|-----------|------:|--------:|--------:|---------------------|
| `basic_fit.json` | Basic-Fit | 900 | 900 | 900 | 2026-02-26 |
| `fitness_park.json` | Fitness Park | 346 | 346 | 66 | 2026-02-26 |
| `keep_cool.json` | Keep Cool | 251 | 223 | 0 | 2026-02-26 |
| `orange_bleue.json` | L'Orange Bleue | 374 | 286 | 362 | 2026-02-26 |
| `magic_form.json` | Magic Form | 44 | 44 | 0 | 2026-02-26 |
| **Total** | | **1 915** | | | |

## Format canonique — Enveloppe

```json
{
  "franchise":    "basic_fit",
  "name":         "Basic-Fit",
  "source_url":   "https://...",
  "extracted_at": "2026-02-26T06:00:00+00:00",
  "country":      "FR",
  "total":        900,
  "clubs":        [ ... ]
}
```

## Format canonique — Club (toutes les clés présentes, `null` si inconnue)

```json
{
  "external_id":  "BF-abc123",
  "name":         "Basic-Fit Paris — Rue de Rivoli",
  "address":      "1 Rue de Rivoli",
  "zip_code":     "75001",
  "city":         "Paris",
  "country":      "FR",
  "latitude":     48.8603,
  "longitude":    2.3477,
  "phone":        "+33123456789",
  "email":        null,
  "website_url":  "https://www.basic-fit.com/fr-fr/clubs/...",
  "open_24h":     false,
  "services":     ["Climatisation", "Wifi gratuit"]
}
```

### Règles de format

| Champ | Type | Règle |
|-------|------|-------|
| `external_id` | string | Préfixe franchise + ID source (`BF-`, `FP-`, `KC-`, `LOB-`, `MF-`) |
| `name` | string | `"[Franchise] [Ville] — [Rue]"` |
| `address` | string | Numéro + rue — vide `""` si inconnu |
| `zip_code` | string | 5 chiffres FR — vide `""` si inconnu |
| `city` | string | Title Case |
| `country` | string | ISO 3166-1 alpha-2 (toujours `"FR"` pour ce répertoire) |
| `latitude` | float\|null | WGS84 — `null` si inconnu |
| `longitude` | float\|null | WGS84 — `null` si inconnu |
| `phone` | string\|null | Format E.164 (`+33XXXXXXXXX`) — `null` si inconnu |
| `email` | string\|null | `null` si inconnu |
| `website_url` | string\|null | URL complète — `null` si inconnue |
| `open_24h` | bool | `false` si inconnu |
| `services` | list\[str\] | Liste vide `[]` si inconnu |

## Ajouter une nouvelle franchise

1. Créer `scripts/scrape_<franchise_slug>.py` (reprendre un script existant comme base)
2. Générer `data/<franchise_slug>.json` au format canonique ci-dessus
3. Valider le format : `python scripts/import_gyms.py --franchise <slug> --dry-run --verbose`
4. Importer en base : `python scripts/import_gyms.py --franchise <slug>`

## Importer en base de données

```bash
# Tout importer (tous les fichiers data/*.json)
python scripts/import_gyms.py

# Une seule franchise
python scripts/import_gyms.py --franchise basic_fit

# Valider sans écrire
python scripts/import_gyms.py --dry-run --verbose

# Réimporter (supprime les données existantes puis réinsère)
python scripts/import_gyms.py --franchise keep_cool --reset
```
