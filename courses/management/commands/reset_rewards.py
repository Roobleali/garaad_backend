from django.core.management.base import BaseCommand
from django.db import transaction
from courses.models import UserReward, UserProgress, CourseEnrollment, LeaderboardEntry
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset rewards and progress for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID of the user to reset')

    def handle(self, *args, **options):
        user_id = options['user_id']
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist'))
            return

        # Ask for confirmation
        question = "Are you sure you want to reset all rewards and progress for this user? This action cannot be undone. (yes/no): "
        answer = input(question)
        
        if answer.lower() != 'yes':
            self.stdout.write(self.style.WARNING('Reset cancelled by user'))
            return
        
        with transaction.atomic():
            # Delete all rewards
            rewards_deleted = UserReward.objects.filter(user=user).delete()[0]
            self.stdout.write(f"Deleted {rewards_deleted} rewards")
            
            # Delete all progress records
            progress_deleted = UserProgress.objects.filter(user=user).delete()[0]
            self.stdout.write(f"Deleted {progress_deleted} progress records")
            
            # Reset course enrollments progress to 0
            enrollments = CourseEnrollment.objects.filter(user=user)
            for enrollment in enrollments:
                enrollment.progress_percent = 0
                enrollment.save()
            self.stdout.write(f"Reset progress for {enrollments.count()} course enrollments")
            
            # Update leaderboard entries (this will set points to 0 since all rewards are deleted)
            LeaderboardEntry.update_points(user)
            self.stdout.write("Updated leaderboard entries")
            
            self.stdout.write(self.style.SUCCESS(f'Successfully reset all rewards and progress for user {user_id}')) 