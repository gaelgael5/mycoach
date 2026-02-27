# MyCoach — CHANGELOG

| Version | Date | Changements |
|---------|------|-------------|
| 1.0 | 26/02/2026 | Initialisation du projet backend — fondations, auth, profils, réservations, paiements, performances, programmes, intégrations OAuth, RGPD, réseaux sociaux |
| 2.1 | 27/02/2026 | Blocklist domaines email : refus à l'inscription des adresses jetables (yopmail, mailinator…) · Table blocked_email_domains · seed 55 domaines · admin CRUD /admin/blocked-domains · insensible à la casse |
| 2.5 | 27/02/2026 | Liens d'enrôlement coach (Phase 9) : table `coach_enrollment_tokens`, migration 011, `enrollment_token` optionnel à l'inscription, coaching_relation auto, 13 nouveaux tests (304 total) |
| 2.6 | 27/02/2026 | Validation téléphone OTP SMS + genre/année de naissance + avatar par défaut : migration 012, table `phone_verification_tokens`, OTP 6 chars `[0-9a-z]` (36^6 combos), format SMS Android SMS Retriever, rate limit 3/h, max 3 tentatives, champs `gender`/`birth_year`/`phone_hash`/`phone_verified_at` sur User, `resolved_avatar_url` dans toutes les réponses, PATCH `/users/me/profile`, 18 nouveaux tests (322 total) |
