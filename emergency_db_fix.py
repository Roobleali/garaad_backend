import os
import sys
import django
from django.db import connection, transaction

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

def run_fix():
    print("🚀 Starting Emergency Database Fix...")
    
    with connection.cursor() as cursor:
        # 1. Ensure uuid-ossp extension is available
        print("Checking for uuid-ossp extension...")
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        
        # 2. Identify tables to drop
        # We need to drop the tables created by the failed 0003 migration
        tables_to_drop = [
            'community_postimage', 
            'community_reply', 
            'community_reaction'
        ]
        
        for table in tables_to_drop:
            print(f"Dropping {table} if it exists...")
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

        # 3. Fix the Post table
        print("Inspecting community_post table...")
        
        # Check column names
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='community_post';")
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        if not columns:
            print("❌ Table community_post not found. Have you run the initial migrations?")
            return

        # Rename user_id to author_id if needed
        if 'user_id' in columns and 'author_id' not in columns:
            print("Renaming user_id to author_id...")
            cursor.execute("ALTER TABLE community_post RENAME COLUMN user_id TO author_id;")
        
        # Convert id to UUID if it's currently an integer
        if columns.get('id') != 'uuid':
            print("Converting community_post.id to UUID...")
            # We must handle Foreign Keys pointing to this table if they exist.
            # In our case, 0003 deletes Comment and Like, so we should too if they exist.
            cursor.execute("DROP TABLE IF EXISTS community_comment, community_like CASCADE;")
            
            # Now convert the id
            # We use uuid_generate_v4() to ensure every row gets a valid UUID
            cursor.execute("ALTER TABLE community_post ALTER COLUMN id DROP DEFAULT;")
            cursor.execute("ALTER TABLE community_post ALTER COLUMN id TYPE uuid USING uuid_generate_v4();")
            cursor.execute("ALTER TABLE community_post ALTER COLUMN id SET DEFAULT uuid_generate_v4();")
            print("✅ ID converted to UUID.")
        else:
            print("✅ ID is already UUID.")

        # 4. Cleanup old tables deleted by 0003
        old_tables = [
            'community_campus', 'community_campusmembership', 'community_comment',
            'community_communitynotification', 'community_like', 'community_message',
            'community_presence', 'community_room', 'community_usercommunityprofile'
        ]
        for table in old_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")

    print("\n✅ Database schema prepped for clean migration.")
    print("\nNext steps on server:")
    print("1. python3 manage.py migrate community 0002 --fake")
    print("2. python3 manage.py migrate community")
    print("3. pm2 restart api-franchisetech")

if __name__ == "__main__":
    try:
        run_fix()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
