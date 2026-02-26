# MyCoach — Référentiels de Salles de Sport

Ce dossier contient les données de référence des salles de sport, extraites depuis les sites officiels des franchises.

## Fichiers disponibles

| Fichier | Franchise | Clubs | Adresses complètes | Dernière extraction |
|---------|-----------|-------|-------------------|---------------------|
| `basic_fit.json` | Basic-Fit | 900 | 900 | 2026-02-25 |
| `fitness_park.json` | Fitness Park | 223 | 58 | 2026-02-26 |
| `keep_cool.json` | Keep Cool | 251 | 223 | 2026-02-26 |
| `magic_form.json` | Magic Form | 44 | 44 | 2026-02-26 |
| `orange_bleue.json` | L'Orange Bleue | 374 | 286 | 2026-02-26 |

> **Note Fitness Park :** données extraites via OpenStreetMap (site officiel protégé par WAF Cloudfront).
> Adresses partielles pour les clubs non encore référencés sur OSM. Complétion progressive.

## Format des fichiers

Chaque fichier respecte le schéma suivant (documenté dans `scripts/import_gyms.py`) :

```json
{
  "franchise": "basic_fit",
  "name": "Basic-Fit",
  "source_url": "https://...",
  "extracted_at": "2026-02-26T06:00:00Z",
  "country": "FR",
  "total": 900,
  "clubs": [
    {
      "external_id": "abc123",
      "name": "Basic-Fit Paris — Rue de Rivoli",
      "address": "1 Rue de Rivoli",
      "zip_code": "75001",
      "city": "Paris",
      "country": "FR",
      "latitude": 48.8603,
      "longitude": 2.3477,
      "phone": "+33123456789",
      "email": null,
      "website_url": "https://...",
      "open_24h": false,
      "services": ["Climatisation", "Wifi gratuit"]
    }
  ]
}
```

## Ajouter une nouvelle franchise

1. Créer un script `scripts/scrape_<franchise>.py` (reprendre le pattern des existants)
2. Générer le fichier `Datas/<franchise_slug>.json` au format ci-dessus
3. Valider : `python scripts/import_gyms.py --franchise <slug> --dry-run --verbose`
4. Importer : `python scripts/import_gyms.py --franchise <slug>`

## Importer en base

```bash
# Tout importer
python scripts/import_gyms.py

# Une seule franchise
python scripts/import_gyms.py --franchise basic_fit

# Valider sans écrire
python scripts/import_gyms.py --dry-run --verbose

# Réimporter (efface + réinsère)
python scripts/import_gyms.py --franchise keep_cool --reset
```
