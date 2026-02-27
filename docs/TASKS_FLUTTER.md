# MyCoach — Flutter Tasks (Android + iOS + Web)

## Stack technique Flutter
- **SDK** : Flutter 3.x (Dart 3.x)
- **Plateformes** : Android (minSdk 21) · iOS (min iOS 14) · Web
- **State management** : Riverpod (flutter_riverpod 2.x)
- **Navigation** : go_router
- **HTTP** : dio + retrofit (dio_generator)
- **Stockage sécurisé** : flutter_secure_storage (équivalent EncryptedSharedPreferences)
- **Cache local** : drift (SQLite type-safe)
- **Push notifications** : firebase_messaging + flutter_local_notifications
- **Agenda** : device_calendar
- **Bluetooth** : flutter_blue_plus (BLE pour balances)
- **Caméra / photo** : image_picker
- **Biométrie** : local_auth
- **QR Code** : qr_flutter (génération) + mobile_scanner (scan)
- **Deep links** : go_router (universal links / app links)
- **SMS OTP** : sms_autofill (Android SMS Retriever + iOS AutoFill)
- **i18n** : flutter_localizations + intl

## Architecture
Pattern : Feature-first + MVVM + Repository

```
lib/
  core/
    api/          # Client Dio, intercepteurs, modèles API
    storage/      # flutter_secure_storage wrapper
    theme/        # ThemeData, couleurs, typographie
    router/       # go_router configuration
    providers/    # Providers globaux (dio, storage, etc.)
  features/
    auth/         # Login, register, OTP, email verify
    home/         # Dashboard client / coach
    booking/      # Réservation, agenda, liste d'attente
    profile/      # Profil, liens sociaux, paramètres santé
    performances/ # Saisie, historique, graphiques, PRs
    programs/     # Programmes assignés (client) / création (coach)
    payments/     # Forfaits, paiements, solde
    integrations/ # Strava, Withings, Google Calendar
    feedback/     # Suggestions, bug reports
    health/       # Paramètres de santé, partage
    admin/        # Back-office admin (web uniquement)
  shared/
    widgets/      # Widgets réutilisables
    models/       # Modèles Dart partagés
    utils/        # Helpers, formatters, validators
test/
  unit/
  widget/
  integration/
```

## Phase A0 — Setup & infrastructure ✅ COMPLETE
- [x] A0-01 : Initialiser le projet Flutter (`flutter create mycoach`) — scaffold existant
- [x] A0-02 : Configurer pubspec.yaml avec toutes les dépendances (+ google_fonts, equatable)
- [x] A0-03 : Architecture dossiers (feature-first) — scaffold existant
- [x] A0-04 : Client Dio avec intercepteur API Key (X-API-Key header) + AppDioException
- [x] A0-05 : flutter_secure_storage — wrapper AppSecureStorage + StorageKeys
- [x] A0-06 : go_router — 24 routes complètes + ShellRoute client/coach + auth redirect
- [x] A0-07 : ThemeData dark — palette JSX (#FF4D00 orange, #0A0A0F dark) + AppColors + AppTextStyles (Outfit + JetBrains Mono)
- [x] A0-08 : i18n — l10n.yaml + app_fr.arb + app_en.arb (200+ clés couvrant tous les écrans)
- [x] A0-09 : Modèles Dart — User, CoachProfile, Gym, Booking, Workout, SocialLink (fromJson/toJson)
- [x] A0-10 : CI/CD GitHub Actions — flutter analyze + unit tests + widget tests + APK debug + Web build

## Phase A1 — Authentification
- [ ] A1-01 : RegisterScreen (rôle coach / client, genre, année naissance)
- [ ] A1-02 : LoginScreen (email / Google OAuth)
- [ ] A1-03 : EmailVerificationScreen
- [ ] A1-04 : ForgotPasswordScreen + ResetPasswordScreen
- [ ] A1-05 : OTP SMS — sms_autofill (Android auto-read + iOS AutoFill)
- [ ] A1-06 : Google Sign-In (google_sign_in package)
- [ ] A1-07 : Auto-login (API Key stockée → direct home)
- [ ] A1-08 : Logout + révocation API Key

## Phase A2 — Onboarding
- [ ] A2-01 : ClientOnboardingScreen (questionnaire 6 étapes)
- [ ] A2-02 : CoachOnboardingScreen (wizard 7 étapes)
- [ ] A2-03 : EnrollmentLinkScreen (inscription via lien coach)
- [ ] A2-04 : Bandeau complétion de profil

## Phase A3 — Profil & Paramètres
- [ ] A3-01 : ProfileScreen (photo, nom, genre, âge)
- [ ] A3-02 : Avatar par défaut selon genre (male/female/neutral SVG)
- [ ] A3-03 : SocialLinksScreen (liste + ajout/modif/suppression)
- [ ] A3-04 : HealthParamsScreen (historique mesures + graphiques)
- [ ] A3-05 : HealthSharingScreen (partage par coach + par paramètre)
- [ ] A3-06 : PrivacySettingsScreen (consentements RGPD)
- [ ] A3-07 : NotificationPreferencesScreen
- [ ] A3-08 : FeedbackScreen (suggestion / bug report)

## Phase A4 — Fonctionnalités Client
- [ ] A4-01 : CoachSearchScreen (filtres, géoloc)
- [ ] A4-02 : CoachProfileScreen (fiche publique, liens sociaux, réservation)
- [ ] A4-03 : BookingScreen (calendrier, sélection créneau)
- [ ] A4-04 : MyBookingsScreen (liste réservations + annulation)
- [ ] A4-05 : WaitlistScreen
- [ ] A4-06 : ClientAgendaScreen (vue semaine/mois)
- [ ] A4-07 : PackagesScreen (achat forfait, solde)
- [ ] A4-08 : PaymentHistoryScreen
- [ ] A4-09 : PerformanceHistoryScreen (graphiques)
- [ ] A4-10 : MyProgramScreen (programme assigné)

## Phase A5 — Fonctionnalités Coach
- [ ] A5-01 : CoachDashboardScreen
- [ ] A5-02 : CoachAgendaScreen (gestion créneaux, vue jour/semaine)
- [ ] A5-03 : BookingRequestsScreen (accepter/refuser)
- [ ] A5-04 : ClientListScreen (liste clients, notes)
- [ ] A5-05 : PerformanceEntryScreen (saisir séance client)
- [ ] A5-06 : BulkCancelScreen (annulation en masse)
- [ ] A5-07 : SmsBroadcastScreen (SMS diffusion)
- [ ] A5-08 : EnrollmentTokensScreen (liens d'enrôlement + QR)
- [ ] A5-09 : ProgramCreatorScreen (créer/assigner programmes)
- [ ] A5-10 : EarningsScreen (revenus, RIB)

## Phase A6 — Intégrations & Features avancées
- [ ] A6-01 : GoogleCalendarSyncScreen
- [ ] A6-02 : StravaSyncScreen (OAuth)
- [ ] A6-03 : WithingsScreen (Bluetooth BLE via flutter_blue_plus)
- [ ] A6-04 : QRCodeScreen (partage profil coach)
- [ ] A6-05 : DeepLinkHandler (mycoach:// scheme)
- [ ] A6-06 : PushNotificationsSetup (firebase_messaging)
- [ ] A6-07 : BiometricLockScreen (local_auth pour accès RIB/données sensibles)
- [ ] A6-08 : OfflineMode (drift cache + sync)

## Phase A7 — Web-specific (plateforme web)
- [ ] A7-01 : Responsive layout (mobile / tablet / desktop breakpoints)
- [ ] A7-02 : AdminDashboard web (back-office)
- [ ] A7-03 : Google Calendar OAuth flow (web redirect)
- [ ] A7-04 : SEO (meta tags, Flutter web rendering mode)
- [ ] A7-05 : PWA manifest + service worker
