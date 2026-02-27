"""
Import de tous les modèles SQLAlchemy.
Ce fichier est importé par alembic/env.py pour que target_metadata
contienne toutes les tables lors de la génération des migrations.
"""
# Phase 3 — Performances & Exercices
from app.models.exercise_type import ExerciseType, ExerciseTypeMuscle
from app.models.machine import Machine, MachineExercise
from app.models.performance_session import PerformanceSession
from app.models.exercise_set import ExerciseSet

# Phase 4 — Programmes d'entraînement
from app.models.workout_plan import (
    WorkoutPlan, PlanAssignment, PlannedSession, PlannedExercise, ExerciseVideo
)

# Phase 5 — Intégrations OAuth
from app.models.integration import OAuthToken, BodyMeasurement

# Phase 6 — RGPD
from app.models.consent import Consent

# Phase 7 — Réseaux sociaux
from app.models.social_link import SocialLink

# Phase 7 — Blocklist domaines email
from app.models.blocked_email_domain import BlockedEmailDomain

# Phase 0 — Auth
from app.models.user import User
from app.models.api_key import ApiKey
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken

# Phase 2 — Réservations & SMS
from app.models.client_questionnaire import ClientQuestionnaire
from app.models.client_gym import ClientGym
from app.models.coaching_request import CoachingRequest
from app.models.booking import Booking
from app.models.waitlist_entry import WaitlistEntry
from app.models.push_token import PushToken
from app.models.sms_log import SmsLog

# Phase 1 — Profils & Gyms
from app.models.gym_chain import GymChain
from app.models.gym import Gym
from app.models.coach_profile import CoachProfile
from app.models.coach_specialty import CoachSpecialty
from app.models.coach_certification import CoachCertification
from app.models.coach_gym import CoachGym
from app.models.coach_pricing import CoachPricing
from app.models.coach_work_schedule import CoachWorkSchedule
from app.models.coach_availability import CoachAvailability
from app.models.cancellation_policy import CancellationPolicy
from app.models.coaching_relation import CoachingRelation
from app.models.coach_client_note import CoachClientNote
from app.models.client_profile import ClientProfile
from app.models.package import Package
from app.models.payment import Payment
from app.models.cancellation_message_template import CancellationMessageTemplate

__all__ = [
    # Phase 0
    "User",
    "ApiKey",
    "EmailVerificationToken",
    "PasswordResetToken",
    # Phase 2
    "ClientQuestionnaire",
    "ClientGym",
    "CoachingRequest",
    "Booking",
    "WaitlistEntry",
    "PushToken",
    "SmsLog",
    # Phase 1
    "GymChain",
    "Gym",
    "CoachProfile",
    "CoachSpecialty",
    "CoachCertification",
    "CoachGym",
    "CoachPricing",
    "CoachWorkSchedule",
    "CoachAvailability",
    "CancellationPolicy",
    "CoachingRelation",
    "CoachClientNote",
    "ClientProfile",
    "Package",
    "Payment",
    "CancellationMessageTemplate",
    # Phase 3
    "ExerciseType",
    "ExerciseTypeMuscle",
    "Machine",
    "MachineExercise",
    "PerformanceSession",
    "ExerciseSet",
    # Phase 4
    "WorkoutPlan",
    "PlanAssignment",
    "PlannedSession",
    "PlannedExercise",
    "ExerciseVideo",
    # Phase 5
    "OAuthToken",
    "BodyMeasurement",
    # Phase 6
    "Consent",
    # Phase 7
    "SocialLink",
    "BlockedEmailDomain",
]
