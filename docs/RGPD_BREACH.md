# Procédure Notification Violation de Données — MyCoach

> RGPD Art. 33 (notification CNIL) et Art. 34 (notification personnes concernées)
> Version : 1.0 | Date : 2026-02-26

---

## 1. Définition d'une Violation

Une **violation de données personnelles** est tout incident de sécurité entraînant :
- La **destruction** accidentelle ou illicite de données
- La **perte** ou l'**altération** de données
- La **divulgation non autorisée** ou l'accès non autorisé à des données

> Exemples : fuite de la base PostgreSQL, accès à `FIELD_ENCRYPTION_KEY`, interception de tokens OAuth.

---

## 2. Délais Réglementaires

| Action | Délai | Destinataire |
|--------|-------|--------------|
| Notification CNIL | **72 heures** max après prise de connaissance | CNIL (notifications.cnil.fr) |
| Notification utilisateurs | **Sans délai indu** si risque élevé | Utilisateurs concernés |
| Documentation interne | Immédiate | Registre des incidents |

> **Important** : Le délai de 72h court dès la prise de connaissance de la violation, même si l'ampleur n'est pas encore connue. Notifier d'abord, compléter ensuite.

---

## 3. Procédure de Réponse

### Étape 1 — Détection et Confinement (H+0 à H+2)

1. **Isoler** le système compromis (désactiver le container, révoquer les clés API exposées)
2. **Documenter** l'heure de détection, la nature de l'incident
3. **Alerter** le responsable de traitement et le DPO immédiatement
4. **Préserver les logs** pour investigation forensique (ne pas effacer)

```bash
# Révoquer les clés d'API exposées
# Dans la DB PostgreSQL :
UPDATE api_keys SET revoked_at = now() WHERE created_at < '[timestamp_compromise]';

# Rotation des secrets (FIELD_ENCRYPTION_KEY, TOKEN_ENCRYPTION_KEY)
# 1. Générer nouvelles clés Fernet
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# 2. Re-chiffrer toutes les colonnes (script de migration à préparer en avance)
# 3. Redéployer avec les nouvelles clés
```

### Étape 2 — Évaluation (H+2 à H+8)

Remplir le tableau d'évaluation :

| Critère | Questions |
|---------|-----------|
| **Nature** | Confidentialité ? Intégrité ? Disponibilité ? |
| **Catégories concernées** | PII ? Données de santé ? Tokens OAuth ? |
| **Volume** | Nombre d'utilisateurs affectés ? |
| **Probabilité de risque** | Faible / Moyen / Élevé / Très élevé |
| **Conséquences potentielles** | Discrimination ? Préjudice financier ? |

### Étape 3 — Notification CNIL (avant H+72)

**URL** : https://notifications.cnil.fr/notifications/index

**Informations à fournir** :
- Nature de la violation (ex : "Accès non autorisé à la base de données")
- Catégories et nombre approximatif de personnes concernées
- Coordonnées du DPO
- Description des conséquences probables
- Mesures prises ou envisagées

**Template notification CNIL** :

```
Objet : Notification de violation de données personnelles — MyCoach

Date et heure de la violation (si connue) : [DATE_HEURE]
Date et heure de prise de connaissance : [DATE_HEURE]

Nature de la violation : [TYPE : confidentialité / intégrité / disponibilité]

Catégories de données concernées :
☐ Identité (nom, prénom, email)
☐ Données de santé (mesures corporelles)
☐ Données financières (paiements)
☐ Tokens d'accès (OAuth)
☐ Données de localisation (gyms)

Nombre approximatif de personnes concernées : [NOMBRE]

Conséquences probables : [DESCRIPTION]

Mesures prises :
1. [ACTION 1]
2. [ACTION 2]

Mesures envisagées :
1. [ACTION 1]
2. [ACTION 2]

Coordonnées DPO : dpo@mycoach.app
```

### Étape 4 — Notification Utilisateurs (si risque élevé)

**Critères de risque élevé** requérant notification aux utilisateurs :
- Exposition de données de santé (mesures corporelles)
- Exposition de mots de passe ou tokens OAuth
- Exposition de données financières
- Usurpation d'identité possible

**Template email utilisateurs** :

```
Objet : Information importante concernant votre compte MyCoach

Madame, Monsieur,

Nous vous contactons pour vous informer d'un incident de sécurité survenu le [DATE].

Nature de l'incident : [DESCRIPTION CLAIRE ET NON TECHNIQUE]

Données potentiellement concernées : [LISTE]

Ce que nous avons fait :
- [ACTION 1]
- [ACTION 2]

Ce que nous vous recommandons :
- Changer votre mot de passe dès que possible
- Vérifier vos tokens Strava / Withings / Google Calendar et les révoquer si nécessaire
- Être vigilant face à d'éventuels emails d'hameçonnage

Pour toute question : dpo@mycoach.app

Cordialement,
L'équipe MyCoach
```

### Étape 5 — Post-Incident (J+7 à J+30)

1. **Rapport complet** documentant l'incident, l'impact, les mesures correctives
2. **Mise à jour** du plan de réponse aux incidents
3. **Formation** de l'équipe sur le point de défaillance identifié
4. **Audit de sécurité** ciblé sur la vulnérabilité exploitée
5. **Mise à jour** du registre des traitements si nécessaire

---

## 4. Registre Interne des Incidents

Maintenir un fichier `incidents/YYYY-MM-DD_[type].md` pour chaque incident :

| Champ | Description |
|-------|-------------|
| Date détection | ISO 8601 |
| Date notification CNIL | ISO 8601 (ou N/A si seuil non atteint) |
| Nature | confidentialité / intégrité / disponibilité |
| Données concernées | Liste des champs exposés |
| Utilisateurs affectés | Nombre (ou estimation) |
| Mesures immédiates | Actions prises dans les 72h |
| Mesures correctrices | Actions à plus long terme |
| Clôture | Date de résolution complète |

---

## 5. Contacts d'Urgence

| Rôle | Contact |
|------|---------|
| DPO | dpo@mycoach.app |
| CNIL | https://notifications.cnil.fr |
| Hébergeur | Support d'urgence Hetzner/OVH |
| Responsable technique | CTO (à compléter) |

---

## 6. Tests Annuels

La procédure doit être testée au minimum une fois par an via un **exercice tabletop** simulant une violation de données.

Checklist de test :
- [ ] Équipe informée de la procédure
- [ ] Accès au formulaire CNIL testé
- [ ] Template email utilisateurs validé juridiquement
- [ ] Procédure de rotation des clés testée
- [ ] Registre des incidents à jour
