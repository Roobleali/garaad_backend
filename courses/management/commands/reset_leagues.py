from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.services import LeagueService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Reset weekly league standings and handle promotions/demotions'

    def handle(self, *args, **options):
        try:
            # Reset weekly standings
            LeagueService.reset_weekly_standings()
            
            self.stdout.write(
                self.style.SUCCESS('Successfully reset league standings')
            )
            
        except Exception as e:
            logger.error(f"Error resetting league standings: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error resetting league standings: {str(e)}')
            ) 