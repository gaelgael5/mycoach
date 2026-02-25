# MyCoach — Tâches Android (Kotlin)

> Répertoire : `android/`
> Stack : Kotlin 1.9+, Material Design 3, Hilt, Retrofit 2, Room, Navigation Component, Coroutines/Flow
>
> **Ordre d'exécution obligatoire au sein de chaque phase :**
> Couche Data (ApiService + DTO + Repository) → ViewModel → UI (Fragment + Layout) → Tests
>
> **Dépendance inter-plateformes :**
> La couche Data de chaque phase Android ne peut être développée que lorsque les endpoints backend correspondants sont **déployés et testables**.
> La couche UI peut être maquettée en parallèle avec des données mockées.

---

## Structure du répertoire `android/`

```
android/
└── app/
    ├── build.gradle.kts
    └── src/
        ├── main/
        │   ├── AndroidManifest.xml
        │   ├── kotlin/com/mycoach/app/
        │   │   ├── MyCoachApplication.kt          ← Init Hilt, Timber
        │   │   ├── MainActivity.kt                ← NavHost, sélection thème Coach/Client
        │   │   │
        │   │   ├── core/                          ← Composants partagés (indépendants du domaine)
        │   │   │   ├── network/
        │   │   │   │   ├── ApiClient.kt           ← Retrofit singleton
        │   │   │   │   ├── ApiKeyInterceptor.kt   ← Injecte X-API-Key + Accept-Language
        │   │   │   │   └── ApiException.kt        ← Exceptions réseau typées
        │   │   │   ├── auth/
        │   │   │   │   ├── ApiKeyStore.kt         ← EncryptedSharedPreferences
        │   │   │   │   └── SessionManager.kt      ← isLoggedIn, getUserRole, clear
        │   │   │   ├── ui/
        │   │   │   │   ├── theme/
        │   │   │   │   │   ├── Color.kt           ← Palettes Coach + Client
        │   │   │   │   │   ├── Typography.kt      ← Space Grotesk
        │   │   │   │   │   └── Theme.kt           ← CoachTheme + ClientTheme
        │   │   │   │   ├── components/            ← Composants réutilisables
        │   │   │   │   │   ├── LoadingView.kt
        │   │   │   │   │   ├── ErrorView.kt
        │   │   │   │   │   ├── EmptyStateView.kt
        │   │   │   │   │   └── PaginatedList.kt
        │   │   │   │   └── UiState.kt             ← sealed class UiState<T>
        │   │   │   ├── utils/
        │   │   │   │   ├── PriceFormatter.kt      ← centimes + ISO 4217 → String localisé
        │   │   │   │   ├── DateTimeFormatter.kt   ← UTC Instant → String localisé + timezone
        │   │   │   │   ├── WeightFormatter.kt     ← kg ↔ lb selon préférence
        │   │   │   │   └── LocaleHelper.kt        ← Applique la locale utilisateur à l'app
        │   │   │   └── di/
        │   │   │       ├── NetworkModule.kt       ← Retrofit, OkHttp, intercepteurs
        │   │   │       └── StorageModule.kt       ← Room, DataStore, EncryptedSharedPreferences
        │   │   │
        │   │   ├── auth/                          ← Authentification
        │   │   │   ├── data/
        │   │   │   │   ├── AuthApiService.kt
        │   │   │   │   ├── dto/
        │   │   │   │   └── AuthRepository.kt
        │   │   │   └── ui/
        │   │   │       ├── LoginFragment.kt + LoginViewModel.kt
        │   │   │       ├── RegisterFragment.kt + RegisterViewModel.kt
        │   │   │       ├── EmailVerificationFragment.kt
        │   │   │       ├── RoleSelectionFragment.kt
        │   │   │       └── ForgotPasswordFragment.kt
        │   │   │
        │   │   ├── coach/                         ← Espace Coach
        │   │   │   ├── data/
        │   │   │   │   ├── CoachApiService.kt
        │   │   │   │   ├── dto/
        │   │   │   │   ├── local/ (Room DAOs)
        │   │   │   │   └── CoachRepository.kt
        │   │   │   └── ui/
        │   │   │       ├── dashboard/
        │   │   │       ├── onboarding/            ← 5 écrans setup profil
        │   │   │       ├── clients/               ← Liste + Fiche (5 onglets)
        │   │   │       ├── agenda/                ← Calendrier + Détail séance
        │   │   │       ├── programs/              ← Bibliothèque + Builder
        │   │   │       └── payments/
        │   │   │
        │   │   ├── client/                        ← Espace Client
        │   │   │   ├── data/
        │   │   │   │   ├── ClientApiService.kt
        │   │   │   │   ├── dto/
        │   │   │   │   ├── local/
        │   │   │   │   └── ClientRepository.kt
        │   │   │   └── ui/
        │   │   │       ├── dashboard/
        │   │   │       ├── onboarding/            ← 6 écrans questionnaire
        │   │   │       ├── search/                ← Recherche coach
        │   │   │       ├── booking/               ← Calendrier dispo + confirmation
        │   │   │       ├── agenda/                ← Vue séances + liste d'attente
        │   │   │       ├── performances/          ← Saisie + historique + graphiques
        │   │   │       ├── solo/                  ← Programme IA + séance guidée
        │   │   │       └── body/                  ← Balance connectée + composition
        │   │   │
        │   │   └── shared/                        ← Fonctionnalités partagées coach+client
        │   │       ├── integrations/              ← Strava, Google Calendar
        │   │       ├── notifications/             ← Firebase push handling
        │   │       └── settings/                  ← Profil, langue, thème
        │   │
        │   └── res/
        │       ├── values/strings.xml             ← Langue par défaut (EN)
        │       ├── values-fr/strings.xml
        │       ├── values-es/strings.xml
        │       ├── values-pt/strings.xml
        │       ├── values/colors.xml
        │       ├── values/themes.xml
        │       ├── navigation/nav_graph.xml
        │       └── xml/
        │           ├── network_security_config.xml
        │           └── backup_rules.xml
        │
        └── test/                                  ← Tests unitaires (JVM)
            └── kotlin/com/mycoach/app/
                ├── auth/
                ├── coach/
                ├── client/
                └── shared/
```

---

## PHASE 0 — Fondations Android

> Pré-requis back : Phase 0 back déployée (endpoints `/auth/*` disponibles)
> Peut démarrer en parallèle avec la Phase 1 back (UI maquettable avec mocks)

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **A0-01** | Init projet : package `com.mycoach.app`, minSdk 26, targetSdk 34, Kotlin 1.9+, Gradle Kotlin DSL | — | 🔴 |
| **A0-02** | `build.gradle.kts` : dépendances (Hilt, Retrofit, Moshi, OkHttp, Room, Navigation, Coroutines, EncryptedSharedPreferences, Lottie, Glide, MPAndroidChart, Timber, ExoPlayer) | A0-01 | 🔴 |
| **A0-03** | `res/xml/network_security_config.xml` : `cleartextTrafficPermitted="false"` (HTTP interdit sauf localhost en debug) | A0-01 | 🔴 |
| **A0-04** | `res/xml/backup_rules.xml` : exclure `mycoach_secure_prefs.xml` et la base Room des sauvegardes automatiques | A0-01 | 🔴 |
| **A0-05** | `core/ui/theme/Color.kt` : couleurs Coach (`#0A0E1A` bg, `#7B2FFF` accent) + Client (`#F0F4FF` bg, `#00C2FF` accent) + couleur commune `#FF6B2F` (orange) | A0-01 | 🔴 |
| **A0-06** | `core/ui/theme/Typography.kt` : Space Grotesk (import Google Fonts), hiérarchie typographique Material 3 | A0-05 | 🔴 |
| **A0-07** | `core/ui/theme/Theme.kt` : `CoachTheme` (dark) + `ClientTheme` (light), sélection automatique selon `user.role` | A0-05, A0-06 | 🔴 |
| **A0-08** | `core/ui/UiState.kt` : sealed class `UiState<out T> { Loading, Success<T>, Error(message, code?), Empty }` | A0-01 | 🔴 |
| **A0-09** | `core/ui/components/` : `LoadingView`, `ErrorView` (message + retry), `EmptyStateView` (illustration + message) | A0-08 | 🟡 |
| **A0-10** | `core/auth/ApiKeyStore.kt` : `EncryptedSharedPreferences` AES-256-GCM, méthodes `store`, `get`, `clear`, `isPresent` | A0-01 | 🔴 |
| **A0-11** | `core/auth/SessionManager.kt` : `isLoggedIn()`, `getUserRole()`, `getUserLocale()`, `getUserTimezone()`, `logout()` (clear store + Room) | A0-10 | 🔴 |
| **A0-12** | `core/network/ApiKeyInterceptor.kt` : ajoute `X-API-Key` + `Accept-Language` (depuis `SessionManager`) sur chaque requête | A0-10, A0-11 | 🔴 |
| **A0-13** | `core/network/ApiClient.kt` : OkHttpClient (intercepteur, timeout 30s, certificate pinner en release), Retrofit (Moshi converter, URL depuis BuildConfig) | A0-12 | 🔴 |
| **A0-14** | `core/di/NetworkModule.kt` : Hilt module Singleton pour OkHttpClient, Retrofit, ApiKeyStore, SessionManager | A0-13 | 🔴 |
| **A0-15** | `core/utils/LocaleHelper.kt` : applique `Locale` depuis `SessionManager` au démarrage (via `AppCompatDelegate.setApplicationLocales`) | A0-11 | 🔴 |
| **A0-16** | `core/utils/PriceFormatter.kt` : `format(cents: Int, currency: String, locale: Locale): String` | A0-01 | 🔴 |
| **A0-17** | `core/utils/DateTimeFormatter.kt` : `format(instant: Instant, zoneId: ZoneId, locale: Locale): String` | A0-01 | 🔴 |
| **A0-18** | `core/utils/WeightFormatter.kt` : `format(kg: Double, unit: WeightUnit, locale: Locale): String` (conversion kg↔lb) | A0-01 | 🔴 |
| **A0-19** | `auth/data/AuthApiService.kt` : interface Retrofit pour POST /auth/register, /auth/login, /auth/google, DELETE /auth/logout, /auth/logout-all, GET /auth/me | A0-13 | 🔴 |
| **A0-20** | `auth/data/dto/` : `LoginRequest`, `RegisterRequest`, `GoogleLoginRequest`, `AuthResponse` (api_key + UserDto), `UserDto` (id, email, name, role, locale, timezone) | A0-19 | 🔴 |
| **A0-21** | `auth/data/AuthRepository.kt` : `loginWithEmail`, `loginWithGoogle`, `register`, `logout`, `getMe` → utilise `ApiKeyStore` pour stocker la clé retournée | A0-19, A0-20, A0-10 | 🔴 |
| **A0-22** | `auth/di/AuthModule.kt` : fournit `AuthRepository` via Hilt | A0-21 | 🔴 |
| **A0-23** | `SplashFragment` : vérifie `isLoggedIn()` → `GET /auth/me` → si 200 navigate vers Dashboard (coach ou client selon rôle), si 401 navigate vers Login | A0-11, A0-21 | 🔴 |
| **A0-24** | `auth/ui/LoginFragment.kt` + `LoginViewModel.kt` : champs email/password, bouton Google (Google Sign-In SDK), lien "Mot de passe oublié", lien "Créer un compte" — UiState géré | A0-21, A0-08 | 🔴 |
| **A0-25** | `auth/ui/RegisterFragment.kt` + `RegisterViewModel.kt` : prénom, nom, email, password, confirm, pays (sélecteur), locale (auto-détecté, modifiable), rôle Coach/Client — validations en temps réel | A0-21 | 🔴 |
| **A0-26** | `auth/ui/EmailVerificationFragment.kt` : affiche email, bouton "Renvoyer" (cooldown 60s), lien "Mauvais email" | A0-24 | 🔴 |
| **A0-27** | `auth/ui/RoleSelectionFragment.kt` : affiché après Google login si nouveau compte, sélection Coach / Client | A0-24 | 🔴 |
| **A0-28** | `auth/ui/ForgotPasswordFragment.kt` + `ResetPasswordFragment.kt` | A0-24 | 🟡 |
| **A0-29** | `nav_graph.xml` : destinations Splash, Login, Register, EmailVerification, RoleSelection, ForgotPassword, CoachDashboard, ClientDashboard — actions typées avec SafeArgs | A0-23 → A0-28 | 🔴 |
| **A0-30** | `res/values/strings.xml` (EN) + `res/values-fr/strings.xml` : toutes les chaînes de la Phase 0 (auth, validations, messages d'erreur) | A0-24, A0-25 | 🔴 |
| **A0-31** | Tests unitaires `test/auth/` : `LoginViewModel` (login OK, credentials incorrects, compte non vérifié), `RegisterViewModel` (validations, email dupe) — avec mocks Retrofit | A0-24, A0-25 | 🔴 |

---

## PHASE 1 — Espace Coach Android

> Pré-requis back : Phase 1 back déployée
> Pré-requis Android : Phase 0 Android 100% ✅

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **A1-01** | `coach/data/CoachApiService.kt` : interface Retrofit pour tous les endpoints coach (profil, salles, tarification, disponibilités, clients, paiements) | A0-13 | 🔴 |
| **A1-02** | `coach/data/dto/` : CoachProfileDto, GymDto, GymChainDto, PricingDto, AvailabilityDto, CancellationPolicyDto, ClientSummaryDto, ClientDetailDto, PackageDto, PaymentDto | A1-01 | 🔴 |
| **A1-03** | Domain models `coach/domain/` : CoachProfile, Gym, Pricing, ClientSummary, ClientDetail, Package, Payment — mappers depuis DTO | A1-02 | 🔴 |
| **A1-04** | `coach/data/CoachRepository.kt` : getProfile, updateProfile, searchGyms, createPricing, updatePricing, deletePricing, setAvailability, setCancellationPolicy, getClients (paginé), getClientDetail, updateClientRelation, updateClientNote | A1-01, A1-02 | 🔴 |
| **A1-05** | `coach/data/PaymentRepository.kt` : createPackage, recordPayment, getPaymentHistory, getHoursSummary | A1-01 | 🔴 |
| **A1-06** | `coach/di/CoachModule.kt` : Hilt bindings pour CoachRepository, PaymentRepository | A1-04, A1-05 | 🔴 |
| **A1-07** | `coach/ui/onboarding/CoachOnboardingActivity.kt` : navigation entre 5 fragments avec barre de progression | A1-04 | 🔴 |
| **A1-08** | Écran Coach 1/5 : photo profil (Camera + Galerie + crop circulaire), prénom/nom, bio (compteur chars) — `OnboardingStep1Fragment` + VM | A1-07 | 🔴 |
| **A1-09** | Écran Coach 2/5 : spécialités multi-select (chips Material 3) — `OnboardingStep2Fragment` | A1-07 | 🔴 |
| **A1-10** | Écran Coach 3/5 : certifications (liste ajoutables, upload photo optionnel) — `OnboardingStep3Fragment` | A1-07 | 🟡 |
| **A1-11** | Écran Coach 4/5 : sélection salles (chaîne → pays → recherche ville/CP → multi-select clubs) — `OnboardingStep4Fragment` | A1-07, A1-04 | 🔴 |
| **A1-12** | Écran Coach 5/5 : devise, tarif unitaire, forfaits (lignes dynamiques : nb séances + prix + validité + visibilité), découverte (toggle + tarif), durée standard, disponibilités (jours + plages horaires + nb places + horizon) — `OnboardingStep5Fragment` | A1-07 | 🔴 |
| **A1-13** | `coach/ui/dashboard/CoachDashboardFragment.kt` + `CoachDashboardViewModel.kt` : KPIs (formatés via PriceFormatter + DateTimeFormatter), prochaines séances (3), réservations à valider (badge), alertes forfaits | A1-04 | 🔴 |
| **A1-14** | `coach/ui/clients/ClientListFragment.kt` + VM : tabs (Tous/Actifs/En pause/Terminés), tri, recherche, scroll infini | A1-04 | 🔴 |
| **A1-15** | `coach/ui/clients/ClientDetailFragment.kt` + VM : ViewPager2 avec 5 onglets (Profil, Séances, Programme, Performances, Paiements) | A1-04 | 🔴 |
| **A1-16** | Onglet Profil client : infos, note privée, boutons Suspendre/Terminer relation | A1-15 | 🔴 |
| **A1-17** | Onglet Paiements client : solde forfait (barre progression), historique, `CreatePackageBottomSheet` (sélection forfait prédéfini ou ad hoc), `RecordPaymentBottomSheet`, bouton Export (PDF/CSV) | A1-05, A1-15 | 🔴 |
| **A1-18** | `coach/ui/CoachProfileFragment.kt` + VM : édition profil, politique d'annulation (délai, mode, no-show), partage profil (deep link + QR code) | A1-04 | 🔴 |
| **A1-19** | `res/values/strings.xml` (EN) + `values-fr/` : toutes les chaînes Phase 1 coach | A1-07 → A1-18 | 🔴 |
| **A1-20** | Tests unitaires `test/coach/` : `CoachDashboardViewModel`, `ClientListViewModel`, `ClientDetailViewModel` (mocks) | A1-13 → A1-17 | 🔴 |

---

## PHASE 2 — Espace Client Android

> Pré-requis back : Phase 2 back déployée
> Pré-requis Android : Phase 0 Android 100% ✅

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **A2-01** | `client/data/ClientApiService.kt` : interface Retrofit (profil, questionnaire, recherche coach, slots, réservations, liste d'attente) | A0-13 | 🔴 |
| **A2-02** | `client/data/dto/` : ClientProfileDto, QuestionnaireDto, CoachSummaryDto, CoachPublicProfileDto, SlotDto, BookingDto, WaitlistDto | A2-01 | 🔴 |
| **A2-03** | Domain models `client/domain/` : ClientProfile, Questionnaire, CoachSummary, Slot (🟢🟠🔴⬛🟡), Booking, BookingStatus | A2-02 | 🔴 |
| **A2-04** | `client/data/ClientRepository.kt` : createProfile, updateProfile, createQuestionnaire, searchCoaches (avec filtres paginés), getCoachPublicProfile, getCoachSlots | A2-01, A2-02 | 🔴 |
| **A2-05** | `client/data/BookingRepository.kt` : createBooking, cancelBooking, getUpcomingBookings, getPastBookings, joinWaitlist, leaveWaitlist, confirmFromWaitlist | A2-01 | 🔴 |
| **A2-06** | `client/di/ClientModule.kt` : Hilt bindings | A2-04, A2-05 | 🔴 |
| **A2-07** | `client/ui/onboarding/ClientOnboardingActivity.kt` : navigation 6 fragments avec progress bar | A2-04 | 🔴 |
| **A2-08** | Questionnaire 1/6 : objectif (cards sélectionnables) | A2-07 | 🔴 |
| **A2-09** | Questionnaire 2/6 : niveau (Débutant / Intermédiaire / Confirmé) | A2-07 | 🔴 |
| **A2-10** | Questionnaire 3/6 : fréquence (stepper 1-7) + durée préférée | A2-07 | 🔴 |
| **A2-11** | Questionnaire 4/6 : équipements (multi-select chips) | A2-07 | 🔴 |
| **A2-12** | Questionnaire 5/6 : zones corps (multi-select) | A2-07 | 🔴 |
| **A2-13** | Questionnaire 6/6 : blessures (toggle + zones + texte libre) | A2-07 | 🔴 |
| **A2-14** | `client/ui/dashboard/ClientDashboardFragment.kt` + VM : programme semaine (aperçu 3 jours), prochaines séances, accès rapide "Nouvelle séance +" | A2-04 | 🔴 |
| **A2-15** | `client/ui/search/CoachSearchFragment.kt` + VM : barre recherche, filtres drawer (chaîne, spécialité, tarif max, découverte, certifié), résultats paginés | A2-04 | 🔴 |
| **A2-16** | `client/ui/search/CoachPublicProfileFragment.kt` + VM : profil complet, bouton principal dynamique (Demander découverte / Réserver / Demande en cours / Votre coach) | A2-04 | 🔴 |
| **A2-17** | `DiscoveryRequestBottomSheet.kt` : message optionnel + récap tarif + confirmer | A2-04 | 🔴 |
| **A2-18** | `client/ui/booking/CoachSlotsFragment.kt` + VM : calendrier hebdo, créneaux colorés (🟢🟠🔴⬛🟡), navigation avant/arrière, tap → BookingConfirmBottomSheet | A2-04 | 🔴 |
| **A2-19** | `BookingConfirmBottomSheet.kt` : récap (coach, date formatée, durée, salle, tarif formaté), sélection tarif (unitaire / forfait / forfait actif), message optionnel, confirmer | A2-05 | 🔴 |
| **A2-20** | `WaitlistBottomSheet.kt` : position dans file, règle 30 min, boutons Rejoindre / Quitter | A2-05 | 🔴 |
| **A2-21** | `WaitlistConfirmationFragment.kt` : deep link depuis notification push, countdown 30 min, bouton "Confirmer ma place" | A2-05 | 🔴 |
| **A2-22** | `client/ui/agenda/ClientAgendaFragment.kt` + VM : vue semaine multi-coach (couleurs auto), points jours avec séances, tap → `SessionDetailBottomSheet` | A2-05 | 🔴 |
| **A2-23** | `SessionDetailBottomSheet.kt` (client) : infos séance, actions selon statut (Accepter/Décliner/Annuler), avertissement pénalité si < délai configuré | A2-05 | 🔴 |
| **A2-24** | `shared/notifications/NotificationHandler.kt` : réception Firebase, routing vers le bon Fragment selon type de notif (deep links) | A0-13 | 🔴 |
| **A2-25** | `res/values/strings.xml` (EN) + `values-fr/` : toutes les chaînes Phase 2 (questionnaire, recherche, réservation, annulation, liste d'attente, notifications) | A2-07 → A2-23 | 🔴 |
| **A2-26** | Tests unitaires `test/client/` : `CoachSearchViewModel` (filtres, pagination), `BookingViewModel` (réservation, annulation, pénalité), `AgendaViewModel` | A2-15, A2-18, A2-22 | 🔴 |

---

## PHASE 3 — Performances Android

> Pré-requis back : Phase 3 back déployée
> Pré-requis Android : Phase 0 + Phase 1 ou 2 (selon si coach ou client en premier)

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **A3-01** | `shared/performance/data/PerformanceApiService.kt` : interface Retrofit (créer session, modifier, supprimer, historique, stats, exercices, machines) | A0-13 | 🔴 |
| **A3-02** | `shared/performance/data/dto/` : PerformanceSessionDto, ExerciseSetDto, ExerciseTypeDto, MachineDto, ProgressionStatsDto, WeekStatsDto | A3-01 | 🔴 |
| **A3-03** | Domain models : PerformanceSession, ExerciseSet, ExerciseType, Machine, ProgressionPoint, WeekStats, PersonalRecord | A3-02 | 🔴 |
| **A3-04** | `shared/performance/data/PerformanceRepository.kt` : createSession, updateSession (check 48h), deleteSession, getHistory, getStats, getWeekStats, submitMachine | A3-01, A3-02 | 🔴 |
| **A3-05** | `shared/performance/data/ExerciseRepository.kt` : searchExercises, getByQRCode, getMachineTypes | A3-01 | 🔴 |
| **A3-06** | `shared/performance/di/PerformanceModule.kt` | A3-04, A3-05 | 🔴 |
| **A3-07** | `WorkoutSessionFragment.kt` + `WorkoutSessionViewModel.kt` : liste exercices (drag & drop RecyclerView ItemTouchHelper), chrono, bouton "Terminer" sticky | A3-04 | 🔴 |
| **A3-08** | `AddExerciseBottomSheet.kt` : onglets Scanner / Manuel | A3-05 | 🔴 |
| **A3-09** | QR Code scanner : ML Kit Barcode Scanning, overlay caméra personnalisé, feedback vibration + son, gestion permission CAMERA | A3-08 | 🔴 |
| **A3-10** | Fallback manuel : RecyclerView type machine → marque → modèle → photo (Camera/Galerie) → upload async | A3-08 | 🔴 |
| **A3-11** | `ExerciseSetBottomSheet.kt` : steppers répétitions + poids (par série), ajout/suppression série (swipe gauche), note texte, bouton 📹 → VideoPlayerBottomSheet | A3-07 | 🔴 |
| **A3-12** | `VideoPlayerBottomSheet.kt` : ExoPlayer en loop, légendes texte, overlay ou plein écran (tap), silencieux par défaut | A3-11 | 🔴 |
| **A3-13** | `SessionSummaryFragment.kt` : récap (durée, exercices, volume formaté), ressenti 1-5 étoiles, animation Lottie, sauvegarder, bottom sheet "Pousser vers Strava ?" | A3-04 | 🔴 |
| **A3-14** | `PerformanceHistoryFragment.kt` + VM : liste chronologique (filtres période/type/muscle), items avec volume en kg ou lb selon préférence | A3-04 | 🔴 |
| **A3-15** | `PerformanceDetailFragment.kt` : détail séance, bouton Modifier (< 48h), bouton Supprimer (< 48h + confirmation), vidéo guide sur chaque exercice | A3-04 | 🔴 |
| **A3-16** | `PerformanceStatsFragment.kt` + VM : sélecteur exercice (dropdown searchable), MPAndroidChart (courbe poids max + barres volume), sélecteur période, badges PR ⭐ | A3-04 | 🔴 |
| **A3-17** | `WeekDashboardFragment.kt` : jauge circulaire séances/objectif, radar muscles (MPAndroidChart), streak 🔥, volume mensuel (poids formaté selon unité) | A3-04 | 🔴 |
| **A3-18** | Saisie coach pour client : banner "Saisie pour [Nom]", même UI WorkoutSession, notification envoyée au client à la sauvegarde | A3-07 | 🟡 |
| **A3-19** | `res/values/strings.xml` (EN) + `values-fr/` : toutes les chaînes Phase 3 | A3-07 → A3-17 | 🔴 |
| **A3-20** | Tests unitaires `test/performance/` : `WorkoutSessionViewModel`, `PerformanceHistoryViewModel`, `StatsViewModel` | A3-07, A3-14, A3-16 | 🔴 |

---

## PHASE 4 — Intelligence IA & Programmes Android

> Pré-requis back : Phase 4 back déployée
> Pré-requis Android : Phase 3 Android 100% ✅

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **A4-01** | `client/data/ProgramApiService.kt` : GET /clients/program, POST /clients/program/recalibrate, CRUD /coaches/programs, POST assign, GET progress | A0-13 | 🔴 |
| **A4-02** | DTOs et mappers : WorkoutPlanDto, PlannedSessionDto, PlannedExerciseDto, ProgramProgressDto | A4-01 | 🔴 |
| **A4-03** | `client/data/ProgramRepository.kt` + `coach/data/ProgramRepository.kt` | A4-01, A4-02 | 🔴 |
| **A4-04** | `client/ui/solo/ProgramWeekFragment.kt` + VM : vue semaine (7 jours, statuts ✓/✗/⏳, badge IA/Coach), recalibration rapide (3 questions) | A4-03 | 🔴 |
| **A4-05** | `ProgramSessionPreviewFragment.kt` : liste exercices (nom, muscles, sets×reps×poids cibles), durée, bouton "Commencer" | A4-04 | 🔴 |
| **A4-06** | `GuidedSessionFragment.kt` + `GuidedSessionViewModel.kt` : navigation exercice par exercice, progress bar, gestion état (exercice courant, set courant) | A4-05 | 🔴 |
| **A4-07** | Sets guidés : poids pré-remplis (cibles), saisie poids réel, bouton "✓ Set réalisé" → déclenche timer | A4-06 | 🔴 |
| **A4-08** | Timer de repos : `CountDownTimer`, vibration (`VibrationEffect`), son (`SoundPool`), boutons "Ignorer" + "Prolonger +30s" | A4-07 | 🔴 |
| **A4-09** | Modification inline : changer poids/reps sur un exercice en cours, passer exercice + motif | A4-06 | 🔴 |
| **A4-10** | `GuidedSessionSummaryFragment.kt` : animation Lottie 🎉, réalisé/skippé, sauvegarde, Strava bottom sheet | A4-06 | 🔴 |
| **A4-11** | Suggestion ajustement progressif : notification locale + bottom sheet "Programme mis à jour" → confirmer/refuser | A4-03 | 🔴 |
| **A4-12** | `coach/ui/programs/CoachProgramLibraryFragment.kt` + VM : liste programmes (nb clients assignés), boutons dupliquer/archiver, bouton "+" → Builder | A4-03 | 🔴 |
| **A4-13** | `coach/ui/programs/CoachProgramBuilderFragment.kt` + VM : vue semaine (7 colonnes), ajout séances, ajout exercices (recherche), drag & drop, sets/reps/poids cibles, temps repos | A4-03 | 🔴 |
| **A4-14** | `AssignProgramBottomSheet.kt` : sélection client + date départ + mode (replace/complement) | A4-03 | 🔴 |
| **A4-15** | `coach/ui/clients/ClientProgramProgressFragment.kt` : semaine en cours ✓/✗, perfs réelles vs cibles par exercice | A4-03 | 🟡 |
| **A4-16** | `res/values/strings.xml` (EN) + `values-fr/` : Phase 4 | A4-04 → A4-15 | 🔴 |
| **A4-17** | Tests unitaires `test/solo/` : `GuidedSessionViewModel` (navigation, timer, sauvegarde), `ProgramBuilderViewModel` | A4-06, A4-13 | 🔴 |

---

## PHASE 5 — Intégrations Android

> Pré-requis back : Phase 5 back déployée
> Peut démarrer en parallèle avec Phase 4

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **A5-01** | `shared/integrations/data/IntegrationsApiService.kt` : endpoints OAuth Strava, Calendar, Withings, push/import | A0-13 | 🔴 |
| **A5-02** | `shared/integrations/IntegrationsRepository.kt` : connectStrava, disconnectStrava, pushSession, importActivities, connectCalendar, connectScale, importMeasurements, manualEntry | A5-01 | 🔴 |
| **A5-03** | `shared/integrations/ui/IntegrationsFragment.kt` + VM : liste intégrations avec statut connecté/déconnecté, bouton connect/disconnect par service | A5-02 | 🔴 |
| **A5-04** | Strava OAuth : Chrome Custom Tab → callback deep link `mycoach://auth/strava/callback` → stocker token | A5-02 | 🔴 |
| **A5-05** | `StravaBottomSheet.kt` : "Pousser vers Strava ?" après sauvegarde séance, feedback succès avec lien activité | A5-02 | 🟡 |
| **A5-06** | Google Calendar OAuth : même flow, sync bidirectionnelle optionnelle | A5-02 | 🟡 |
| **A5-07** | Balance Withings OAuth + import automatique (WorkManager, toutes les 6h) | A5-02 | 🟡 |
| **A5-08** | `client/ui/body/BodyCompositionFragment.kt` + VM : sélecteur métrique (chips), MPAndroidChart courbes (poids, % graisse, masse musculaire), sélecteur période, saisie manuelle | A5-02 | 🟡 |
| **A5-09** | `BodyMeasurementBottomSheet.kt` : saisie manuelle (date + poids + métriques optionnelles), poids affiché en kg ou lb selon préférence | A5-08 | 🟡 |
| **A5-10** | `shared/notifications/` : configuration Firebase Cloud Messaging, `MyCoachFirebaseService.kt` (réception + routing selon `type` dans le payload), channel Notification Android | A0-13 | 🔴 |
| **A5-11** | `res/values/strings.xml` (EN) + `values-fr/` : Phase 5 | A5-03 → A5-09 | 🔴 |
| **A5-12** | Tests `test/integrations/` : `IntegrationsViewModel`, `BodyCompositionViewModel` | A5-03, A5-08 | 🟡 |

---

## PHASE 6 — Polish & Launch Android

> Pré-requis : Phases 4 + 5 Android 100% ✅

| # | Tâche | Dépend de | Priorité |
|---|-------|-----------|----------|
| **A6-01** | Animations Lottie : splash screen, completion séance guidée, nouveau PR, onboarding (transitions entre écrans) | Toutes | 🟡 |
| **A6-02** | Glassmorphism + effets visuels : cartes Dashboard (shader/backdrop blur), barres de progression animées, accents néon | Toutes | 🟡 |
| **A6-03** | `FLAG_SECURE` : activer sur Login, paiements, données balance | Toutes | 🔴 |
| **A6-04** | Accessibilité : `contentDescription` sur toutes les images et icônes, `importantForAccessibility`, taille de texte adaptable (sp) | Toutes | 🔴 |
| **A6-05** | ProGuard/R8 release : activer minification + shrinking, règles Moshi/Retrofit | Toutes | 🔴 |
| **A6-06** | Audit OWASP Mobile Top 10 : checklist par écran sensible | Toutes | 🔴 |
| **A6-07** | Tests E2E Espresso : flows critiques (login → réservation → confirmation → saisie perf → sauvegarde) | Toutes | 🔴 |
| **A6-08** | `res/values-es/strings.xml` + `values-pt/strings.xml` : traductions espagnol + portugais | Toutes | 🟡 |
| **A6-09** | Fiche Play Store : titre, description courte/longue (fr + en), captures d'écran (Phone + Tablet), icône 512px, feature graphic | Toutes | 🔴 |
| **A6-10** | Firebase App Distribution : build de beta, distribution à 10 coachs + 50 clients | Toutes | 🔴 |
| **A6-11** | Correction bugs remontés en beta + polish final | A6-10 | 🔴 |
| **A6-12** | 🚀 Publication Google Play Store (release track) | A6-11 | 🔴 |

---

## Légende priorités

| Symbole | Signification |
|---------|---------------|
| 🔴 | Bloquant — ne pas passer à la suite sans cette tâche |
| 🟡 | Important — à faire dans la phase mais non bloquant pour les suivantes |
| 🟢 | Optionnel — amélioration, peut être différé |
