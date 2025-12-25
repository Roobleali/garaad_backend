from .models import MomentumState, GamificationProgress, EnergyWallet, ActivityLog, Notification
from leagues.models import League, UserLeague
import math
from django.utils import timezone
from datetime import timedelta
from django.db import models

class GamificationEngine:
    """
    The heart of the gamification system.
    Deterministic, append-only, and idempotent where possible.
    """
    
    # 🛡️ Anti-Exploit Hard Caps (Daily UTC)
    DAILY_XP_CAP = 250
    DAILY_ENERGY_EARN_CAP = 10
    ACTION_LIMIT_HELP = 5

    @staticmethod
    def update_activity(user, action_type, problems_solved=0, energy_spent=0, request_id=None):
        """
        The authoritative mutator for user engagement.
        🛡️ Checkpoint: Idempotency, Deterministic rules, UTC Authority, Hard Caps.
        """
        now = timezone.now() # System UTC
        
        # 🛡️ 1. Idempotency Check
        if request_id:
            if ActivityLog.objects.filter(request_id=request_id).exists():
                return {'error': 'Duplicate request', 'idempotent': True}

        # 2. Get or Create States
        progress, _ = GamificationProgress.objects.get_or_create(user=user)
        momentum, _ = MomentumState.objects.get_or_create(user=user)
        wallet, _ = EnergyWallet.objects.get_or_create(user=user)

        # 🛡️ 3. Calculate Daily Consumed Quantities (UTC Day)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_logs = ActivityLog.objects.filter(user=user, created_at__gte=today_start)
        
        today_xp = daily_logs.aggregate(models.Sum('xp_delta'))['xp_delta__sum'] or 0
        today_energy_earned = daily_logs.filter(energy_delta__gt=0).aggregate(models.Sum('energy_delta'))['energy_delta__sum'] or 0
        today_help_count = daily_logs.filter(action_type='help').count()

        # 4. Determine Deltas based on Rule Engine
        xp_delta = 0
        energy_delta = 0

        if action_type == 'problem_attempt':
            xp_delta = 5
        elif action_type == 'solve':
            xp_delta = 15
        elif action_type == 'return':
            xp_delta = 20
        elif action_type == 'help':
            if today_help_count < GamificationEngine.ACTION_LIMIT_HELP:
                xp_delta = 10
                energy_delta = 1
            else:
                xp_delta = 2 # Diminishing returns after cap

        # 🛡️ apply Hard Caps
        if today_xp + xp_delta > GamificationEngine.DAILY_XP_CAP:
            xp_delta = max(0, GamificationEngine.DAILY_XP_CAP - today_xp)
        
        if energy_delta > 0 and (today_energy_earned + energy_delta > GamificationEngine.DAILY_ENERGY_EARN_CAP):
            energy_delta = max(0, GamificationEngine.DAILY_ENERGY_EARN_CAP - today_energy_earned)

        # 5. Apply Momentum Logic (Soft Decay)
        time_since_last = now - momentum.last_active_at
        
        if time_since_last.total_seconds() < 24 * 3600:
            # Within 24h: Maintain or Increment if it's a new "day" window
            # Simple check: if last_active was yesterday (different day)
            if momentum.last_active_at.date() < now.date():
                momentum.streak_count += 1
                momentum.state = 'stable'
        elif 24 * 3600 <= time_since_last.total_seconds() < 48 * 3600:
            # 24h - 48h: Enter unstable state
            momentum.state = 'unstable'
            # No count increase, but no decay yet
        elif 48 * 3600 <= time_since_last.total_seconds() < 72 * 3600:
            # 48h - 72h: Soft Decay (Count *= 0.5)
            if momentum.state != 'unstable': # If they skipped a state
                 momentum.streak_count *= 0.5
            momentum.state = 'dormant'
        else:
            # > 72h: Dormant
            momentum.streak_count = 0
            momentum.state = 'dormant'

        # If returning from unstable/dormant, mark as restored
        if action_type in ['solve', 'problem_attempt'] and momentum.state in ['unstable', 'dormant']:
            momentum.state = 'restored'
            xp_delta += 10 # Bonus for restoring rhythm

        # 6. Apply XP and Energy Consumption
        energy_delta -= energy_spent
        
        # Update Models
        progress.xp_total += xp_delta
        # Simple level calculation: Level = 1 + floor(XP/100)
        old_level = progress.level
        progress.level = 1 + math.floor(progress.xp_total / 100)
        
        wallet.energy_balance += energy_delta
        if energy_delta > 0:
            wallet.lifetime_earned += energy_delta

        momentum.last_active_at = now
        
        # 🛡️ Phase 11: Energy Full Notification
        if energy_delta > 0 and wallet.energy_balance >= 10: # Assuming 10 is the soft max
            Notification.objects.create(
                user=user,
                type='energy_full',
                title='Tamartaada waa buuxdaa!',
                message='Waxa aad haysataa tamar buuxda. Isticmaal hadda si aad u badbaadiso xariggaaga!',
                data={'balance': wallet.energy_balance}
            )
        
        # Calculate Weekly Velocity
        week_ago = now - timedelta(days=7)
        progress.weekly_velocity = ActivityLog.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).aggregate(models.Sum('xp_delta'))['xp_delta__sum'] or 0
        
        # 7. Save Changes
        progress.save()
        momentum.save()
        wallet.save()

        # 8. League Updates & Notifications
        if xp_delta > 0:
            user_league, _ = UserLeague.objects.get_or_create(
                user=user,
                defaults={'current_league': League.objects.order_by('min_xp').first()}
            )
            user_league.update_weekly_points(xp_delta)
            
            # Check for league promotion
            next_league = League.objects.filter(min_xp__gt=user_league.current_league.min_xp).order_by('min_xp').first()
            if next_league and progress.xp_total >= next_league.min_xp:
                old_league_name = user_league.current_league.somali_name
                user_league.current_league = next_league
                user_league.save()
                
                Notification.objects.create(
                    user=user,
                    type='league',
                    title='League Promotion!',
                    message=f'Waad ku mahadsantahay kor u kacista {next_league.somali_name}!',
                    data={'old_league': old_league_name, 'new_league': next_league.somali_name}
                )

        if progress.level > old_level:
            Notification.objects.create(
                user=user,
                type='achievement',
                title='Level Up!',
                message=f'Hambalyo! Waxaad gaartay heerka {progress.level}!',
                data={'level': progress.level}
            )

        if momentum.state == 'restored':
             Notification.objects.create(
                user=user,
                type='streak',
                title='Momentum Restored!',
                message='Xariggaaga waa la soo celiyay! Aan sii wadno dadaalka.',
                data={'streak_count': momentum.streak_count}
            )

        # 9. Append to Log (Idempotent Record)
        log = ActivityLog.objects.create(
            user=user,
            action_type=action_type,
            xp_delta=xp_delta,
            energy_delta=energy_delta,
            request_id=request_id,
            created_at=now
        )

        return {
            'xp_earned': xp_delta,
            'energy_delta': energy_delta,
            'new_total_xp': progress.xp_total,
            'new_level': progress.level,
            'streak_count': momentum.streak_count,
            'state': momentum.state,
            'energy_balance': wallet.energy_balance
        }

    @staticmethod
    def apply_daily_decay():
        """
        Cron-based logic to transition states for inactive users.
        🛡️ Checkpoint: Auditable Decay Logs.
        """
        now = timezone.now()
        # Users who haven't been active for > 24h
        cutoff_24 = now - timedelta(hours=24)
        cutoff_48 = now - timedelta(hours=48)
        
        # 1. stable -> unstable (24h)
        # Note: We use an iterator to create logs for each mutation
        unstable_targets = MomentumState.objects.filter(last_active_at__lt=cutoff_24, state='stable')
        for state in unstable_targets:
            state.state = 'unstable'
            state.save()
            ActivityLog.objects.create(
                user=state.user,
                action_type='momentum_decay',
                xp_delta=0,
                energy_delta=0,
                created_at=now
            )
            # 🛡️ Phase 11: Notification Mapping
            Notification.objects.create(
                user=state.user,
                type='streak_decay_warning',
                title='Xariggaagu waa jilicsanyahay!',
                message='Xariggaagu wuxuu halis ugu jiraa inuu jabo. Xali hal dhibaato hadda si aad u badbaadiso!',
                data={'streak_count': state.streak_count}
            )

        # 2. unstable -> dormant + halving (48h)
        dormant_targets = MomentumState.objects.filter(last_active_at__lt=cutoff_48, state='unstable')
        for state in dormant_targets:
            state.state = 'dormant'
            state.streak_count *= 0.5
            state.save()
            ActivityLog.objects.create(
                user=state.user,
                action_type='momentum_decay',
                xp_delta=0,
                energy_delta=0,
                created_at=now
            )
