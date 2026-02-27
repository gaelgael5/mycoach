"""
Génération de codes OTP pour la vérification téléphonique.

Algorithme :
  - Alphabet : chiffres (0-9) + lettres minuscules (a-z) = 36 caractères
  - Longueur  : 6 caractères
  - Entropie  : 36^6 = 2 176 782 336 combinaisons ≈ 31 bits
  - Source    : secrets.choice (CSPRNG, cryptographiquement sécurisé)

Format SMS Android SMS Retriever compatible :
  "<#> Votre code MyCoach : {code}\\nExpire dans 10 minutes.\\n{app_hash}"
"""
import secrets
import string

OTP_ALPHABET = string.digits + string.ascii_lowercase  # "0123456789abcdefghijklmnopqrstuvwxyz"
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 3
OTP_RATE_LIMIT_HOUR = 3  # max 3 OTPs envoyés par heure par numéro

# Hash applicatif Android SMS Retriever (à remplacer par le vrai hash en prod)
# Généré depuis le certificat de signature de l'APK
ANDROID_APP_HASH = "FA+9qCX9VSu"  # placeholder — 11 chars


def generate_otp(length: int = OTP_LENGTH) -> str:
    """
    Génère un code OTP sécurisé de `length` caractères.

    Exemples : "a3f7k2", "9x2m4p", "b0z5r1"
    """
    return "".join(secrets.choice(OTP_ALPHABET) for _ in range(length))


def format_sms(code: str) -> str:
    """
    Formate le message SMS compatible Android SMS Retriever API.

    Le préfixe '<#> ' et le hash en fin de message permettent à l'app Android
    de lire automatiquement le code sans intervention de l'utilisateur.
    """
    return (
        f"<#> Votre code MyCoach : {code}\n"
        f"Expire dans {OTP_EXPIRY_MINUTES} minutes.\n"
        f"{ANDROID_APP_HASH}"
    )
