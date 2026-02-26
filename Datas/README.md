# MyCoach — Référentiels de Salles de Sport

Ce dossier contient les données de référence des salles de sport, extraites depuis les sites officiels des franchises.

## Fichiers disponibles

| Fichier | Franchise | Clubs | Dernière extraction |
|---------|-----------|-------|---------------------|
| `basic_fit.json` | Basic-Fit | 900 | 2026-02-25 |
| `magic_form.json` | Magic Form | 44 | 2026-02-25 |

## Format des fichiers

Chaque fichier respecte le schéma suivant (documenté dans `scripts/import_gyms.py`) :

```json
{
  "franchise": "basic_fit",
  "name": "Basic-Fit",
  "source_url": "https://...",
  "extracted_at": "2026-02-25T19:00:00Z",
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

1. Créer un fichier `Datas/<franchise_slug>.json` au même format
2. Lancer l'import : `python scripts/import_gyms.py --franchise <slug> --dry-run`
3. Si OK : `python scripts/import_gyms.py --franchise <slug>`

## Importer en base

```bash
# Tout importer
python scripts/import_gyms.py

# Une seule franchise
python scripts/import_gyms.py --franchise basic_fit

# Valider sans écrire
python scripts/import_gyms.py --dry-run --verbose
```
