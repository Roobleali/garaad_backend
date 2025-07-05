from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate referral codes for existing users who do not have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of referral codes for all users',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write("🔍 Checking users for referral codes...")
        
        # Find users without referral codes
        if force:
            users_without_codes = User.objects.all()
            self.stdout.write(f"⚠️  Force mode: Will regenerate codes for ALL {users_without_codes.count()} users")
        else:
            users_without_codes = User.objects.filter(
                referral_code=''
            ) | User.objects.filter(
                referral_code__isnull=True
            )
            self.stdout.write(f"📊 Found {users_without_codes.count()} users without referral codes")
        
        if not users_without_codes.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ All users already have referral codes!")
            )
            return
        
        # Show users that will be updated
        self.stdout.write("\n📋 Users to update:")
        for user in users_without_codes:
            current_code = user.referral_code or "None"
            self.stdout.write(f"  - {user.username} ({user.email}): {current_code}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n🔍 DRY RUN: No changes will be made")
            )
            return
        
        # Confirm before proceeding
        if not force:
            confirm = input("\n❓ Proceed with generating referral codes? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("❌ Operation cancelled")
                return
        
        # Generate referral codes
        updated_count = 0
        with transaction.atomic():
            for user in users_without_codes:
                old_code = user.referral_code or "None"
                
                if force or not user.referral_code:
                    user.referral_code = User.generate_referral_code()
                    user.save()
                    updated_count += 1
                    
                    self.stdout.write(
                        f"✅ {user.username}: {old_code} → {user.referral_code}"
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Successfully updated {updated_count} users!")
        )
        
        # Show final statistics
        total_users = User.objects.count()
        users_with_codes = User.objects.filter(
            referral_code__isnull=False
        ).exclude(referral_code='').count()
        
        self.stdout.write(f"📊 Final statistics:")
        self.stdout.write(f"  - Total users: {total_users}")
        self.stdout.write(f"  - Users with referral codes: {users_with_codes}")
        self.stdout.write(f"  - Users without referral codes: {total_users - users_with_codes}") 