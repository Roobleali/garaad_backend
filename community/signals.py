# Simplified signals for refactored community models
# The old complex signals have been removed to match the new simple Post/Reply/Reaction structure

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

# Signals can be added here as needed for the simplified structure
# For now, keeping this minimal to avoid import errors