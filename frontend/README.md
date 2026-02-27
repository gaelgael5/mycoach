# MyCoach — Frontend Flutter

Application multi-plateforme : **Android · iOS · Web**

## Stack
- Flutter 3.x / Dart 3.x
- Riverpod 2.x (state management)
- go_router (navigation)
- Dio (HTTP client)
- flutter_secure_storage (API Key)

## Démarrage rapide

```bash
flutter pub get
flutter run -d chrome          # Web
flutter run -d android         # Android
flutter run -d ios             # iOS (macOS requis)
```

## Structure

```
lib/
  core/       # Infrastructure (API, storage, theme, router)
  features/   # Fonctionnalités par domaine (auth, booking, profile…)
  shared/     # Widgets et utilitaires partagés
```

## Variables d'environnement

```bash
flutter run --dart-define=API_BASE_URL=http://192.168.10.63:8200
```

## Documentation

Voir `docs/TASKS_FLUTTER.md` pour le plan de développement complet.
