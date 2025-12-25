import os
import django
from django.db import connection, transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

def repair():
    with connection.cursor() as cursor:
        print("🔍 checking community_post table...")
        
        # 1. Fix community_post columns
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='community_post'")
        columns = [row[0] for row in cursor.fetchall()]
        
        if 'user_id' in columns and 'author_id' not in columns:
            print("🔧 Renaming user_id to author_id...")
            cursor.execute("ALTER TABLE community_post RENAME COLUMN user_id TO author_id")
        
        if 'category_id' not in columns:
            print("🔧 Adding category_id to community_post...")
            # We assume category 1 exists or just use NULL for now if allowed, 
            # but usually it's easier to just add it.
            cursor.execute("ALTER TABLE community_post ADD COLUMN category_id INTEGER")
            cursor.execute("UPDATE community_post SET category_id = 1 WHERE category_id IS NULL")
            cursor.execute("ALTER TABLE community_post ALTER COLUMN category_id SET NOT NULL")
            cursor.execute("ALTER TABLE community_post ADD CONSTRAINT community_post_category_fk FOREIGN KEY (category_id) REFERENCES courses_category(id)")

        # 2. Create missing tables
        tables_to_create = {
            'community_reply': """
                CREATE TABLE IF NOT EXISTS community_reply (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_edited BOOLEAN NOT NULL DEFAULT FALSE,
                    author_id INTEGER NOT NULL REFERENCES auth_user(id),
                    post_id INTEGER NOT NULL REFERENCES community_post(id)
                )
            """,
            'community_reaction': """
                CREATE TABLE IF NOT EXISTS community_reaction (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    post_id INTEGER NOT NULL REFERENCES community_post(id),
                    user_id INTEGER NOT NULL REFERENCES auth_user(id),
                    UNIQUE (post_id, user_id, type)
                )
            """,
            'community_postimage': """
                CREATE TABLE IF NOT EXISTS community_postimage (
                    id SERIAL PRIMARY KEY,
                    image VARCHAR(100) NOT NULL,
                    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    post_id INTEGER NOT NULL REFERENCES community_post(id)
                )
            """
        }
        
        for table, sql in tables_to_create.items():
            print(f"🔍 Checking {table}...")
            cursor.execute(f"SELECT EXIStS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            if not cursor.fetchone()[0]:
                print(f"🔧 Creating {table}...")
                cursor.execute(sql)

        # 3. Handle old tables (Optional, but helps future migrations)
        old_tables = ['community_campus', 'community_campusmembership', 'community_comment', 'community_communitynotification', 'community_like', 'community_message', 'community_presence', 'community_room', 'community_usercommunityprofile']
        for table in old_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"🧹 Dropped old table {table}")
            except Exception:
                pass

        print("✅ Database repair complete.")

if __name__ == "__main__":
    try:
        repair()
    except Exception as e:
        print(f"❌ Error: {e}")
