from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection


class Command(BaseCommand):
    help = 'Apply the diagrams field migration to the Problem model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force apply the migration even if it appears to be already applied',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting diagrams migration...'))
        
        try:
            # Check if the column already exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='courses_problem' 
                    AND column_name='diagrams';
                """)
                result = cursor.fetchone()
                
                if result and not options['force']:
                    self.stdout.write(
                        self.style.WARNING('Diagrams column already exists. Use --force to rerun.')
                    )
                    return
                
                if not result:
                    self.stdout.write('Adding diagrams column to courses_problem table...')
                    
                    # Apply the specific migration
                    call_command('migrate', 'courses', '0016', verbosity=2)
                    
                    self.stdout.write(
                        self.style.SUCCESS('Successfully added diagrams field to Problem model!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Column exists, but migration forced.')
                    )
                    call_command('migrate', 'courses', '0016', verbosity=2)
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error applying diagrams migration: {str(e)}')
            )
            
            # Fallback: try to run all pending migrations
            self.stdout.write('Trying to run all pending migrations...')
            try:
                call_command('migrate', verbosity=2)
                self.stdout.write(
                    self.style.SUCCESS('All migrations applied successfully!')
                )
            except Exception as migrate_error:
                self.stdout.write(
                    self.style.ERROR(f'Failed to apply migrations: {str(migrate_error)}')
                )
                raise migrate_error 