from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

User = get_user_model()

class Command(BaseCommand):
    help = 'Check and report on the referral system status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information about each user',
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        
        self.stdout.write("🔍 Checking Referral System Status...")
        
        # Basic statistics
        total_users = User.objects.count()
        users_with_codes = User.objects.filter(
            referral_code__isnull=False
        ).exclude(referral_code='').count()
        users_without_codes = total_users - users_with_codes
        
        self.stdout.write(f"\n📊 Basic Statistics:")
        self.stdout.write(f"  - Total users: {total_users}")
        self.stdout.write(f"  - Users with referral codes: {users_with_codes}")
        self.stdout.write(f"  - Users without referral codes: {users_without_codes}")
        
        # Referral activity
        users_with_referrals = User.objects.filter(referrals__isnull=False).distinct().count()
        total_referrals = User.objects.filter(referred_by__isnull=False).count()
        total_points = User.objects.aggregate(total=Sum('referral_points'))['total'] or 0
        
        self.stdout.write(f"\n📈 Referral Activity:")
        self.stdout.write(f"  - Users who have referred others: {users_with_referrals}")
        self.stdout.write(f"  - Total users referred: {total_referrals}")
        self.stdout.write(f"  - Total referral points awarded: {total_points}")
        
        # Top referrers
        top_referrers = User.objects.annotate(
            referral_count=Count('referrals')
        ).filter(referral_count__gt=0).order_by('-referral_count', '-referral_points')[:5]
        
        if top_referrers.exists():
            self.stdout.write(f"\n🏆 Top Referrers:")
            for i, user in enumerate(top_referrers, 1):
                self.stdout.write(
                    f"  {i}. {user.username} ({user.referral_code}): "
                    f"{user.referral_count} referrals, {user.referral_points} points"
                )
        
        # Recent referrals
        recent_referrals = User.objects.filter(
            referred_by__isnull=False
        ).order_by('-date_joined')[:5]
        
        if recent_referrals.exists():
            self.stdout.write(f"\n🆕 Recent Referrals:")
            for user in recent_referrals:
                self.stdout.write(
                    f"  - {user.username} referred by {user.referred_by.username} "
                    f"({user.date_joined.strftime('%Y-%m-%d %H:%M')})"
                )
        
        # Referral code format check
        invalid_codes = []
        for user in User.objects.all():
            if user.referral_code:
                code = user.referral_code
                if len(code) != 8 or not code.isalnum() or not code.islower():
                    invalid_codes.append(f"{user.username}: {code}")
        
        if invalid_codes:
            self.stdout.write(
                self.style.WARNING(f"\n⚠️  Invalid referral codes found:")
            )
            for invalid in invalid_codes:
                self.stdout.write(f"  - {invalid}")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ All referral codes are properly formatted!")
            )
        
        # Duplicate codes check
        duplicate_codes = User.objects.values('referral_code').annotate(
            count=Count('id')
        ).filter(count__gt=1, referral_code__isnull=False).exclude(referral_code='')
        
        if duplicate_codes.exists():
            self.stdout.write(
                self.style.ERROR(f"\n❌ Duplicate referral codes found:")
            )
            for dup in duplicate_codes:
                code = dup['referral_code']
                users_with_code = User.objects.filter(referral_code=code)
                self.stdout.write(f"  - Code '{code}' used by: {', '.join([u.username for u in users_with_code])}")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ All referral codes are unique!")
            )
        
        # Detailed information
        if detailed:
            self.stdout.write(f"\n📋 Detailed User Information:")
            for user in User.objects.all().order_by('username'):
                referral_info = f"referred by {user.referred_by.username}" if user.referred_by else "not referred"
                self.stdout.write(
                    f"  - {user.username}: {user.referral_code} | "
                    f"{referral_info} | {user.referral_points} points"
                )
        
        # System health summary
        self.stdout.write(f"\n🎯 System Health Summary:")
        
        if users_without_codes == 0:
            self.stdout.write(self.style.SUCCESS("  ✅ All users have referral codes"))
        else:
            self.stdout.write(self.style.WARNING(f"  ⚠️  {users_without_codes} users need referral codes"))
        
        if not invalid_codes:
            self.stdout.write(self.style.SUCCESS("  ✅ All referral codes are properly formatted"))
        else:
            self.stdout.write(self.style.ERROR("  ❌ Some referral codes are invalid"))
        
        if not duplicate_codes.exists():
            self.stdout.write(self.style.SUCCESS("  ✅ All referral codes are unique"))
        else:
            self.stdout.write(self.style.ERROR("  ❌ Duplicate referral codes found"))
        
        if total_referrals > 0:
            self.stdout.write(self.style.SUCCESS(f"  ✅ Referral system is active ({total_referrals} referrals)"))
        else:
            self.stdout.write(self.style.WARNING("  ⚠️  No referrals have been made yet"))
        
        self.stdout.write(f"\n🎉 Referral system check completed!") 