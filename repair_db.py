import os
import django
from django.db import connection, transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

def repair():
    with connection.cursor() as cursor:
        print("🔍 checking community_post table...")
        
        # 1. Fix community_post columns
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='community_post'")
        col_info = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Handle user_id -> author_id rename
        if 'user_id' in col_info and 'author_id' not in col_info:
            print("🔧 Renaming user_id to author_id...")
            cursor.execute("ALTER TABLE community_post RENAME COLUMN user_id TO author_id")
            col_info['author_id'] = col_info.pop('user_id')
        
        # Handle category_id correctly
        if 'category_id' in col_info:
            curr_type = col_info['category_id'].lower()
            if 'int' in curr_type:
                print(f"🔧 Correcting category_id type (from {curr_type} to VARCHAR)...")
                cursor.execute("ALTER TABLE community_post DROP COLUMN IF EXISTS category_id CASCADE")
                del col_info['category_id']
        
        if 'category_id' not in col_info:
            print("🔧 Adding category_id (VARCHAR) to community_post...")
            cursor.execute("ALTER TABLE community_post ADD COLUMN category_id VARCHAR(50)")
            cursor.execute("SELECT id FROM courses_category LIMIT 1")
            row = cursor.fetchone()
            default_cat = row[0] if row else 'stem'
            
            cursor.execute(f"UPDATE community_post SET category_id = '{default_cat}' WHERE category_id IS NULL")
            cursor.execute("ALTER TABLE community_post ALTER COLUMN category_id SET NOT NULL")
            cursor.execute("ALTER TABLE community_post ADD CONSTRAINT community_post_category_fk FOREIGN KEY (category_id) REFERENCES courses_category(id)")

        # 1b. Detect Post ID type (Integer vs UUID)
        cursor.execute("SELECT data_type FROM information_schema.columns WHERE table_name='community_post' AND column_name='id'")
        post_id_type = cursor.fetchone()[0].upper()
        print(f"📌 Detected Post ID type: {post_id_type}")
        
        # Use matching type for FKs
        fk_type = post_id_type
        if 'UUID' in fk_type:
            fk_type = 'UUID'
        elif 'INT' in fk_type:
            fk_type = 'INTEGER'

        # 2. Create missing tables
        tables_to_create = {
            'community_reply': f"""
                CREATE TABLE IF NOT EXISTS community_reply (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_edited BOOLEAN NOT NULL DEFAULT FALSE,
                    author_id INTEGER NOT NULL REFERENCES accounts_user(id),
                    post_id {fk_type} NOT NULL REFERENCES community_post(id)
                )
            """,
            'community_reaction': f"""
                CREATE TABLE IF NOT EXISTS community_reaction (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    post_id {fk_type} NOT NULL REFERENCES community_post(id),
                    user_id INTEGER NOT NULL REFERENCES accounts_user(id),
                    UNIQUE (post_id, user_id, type)
                )
            """,
            'community_postimage': f"""
                CREATE TABLE IF NOT EXISTS community_postimage (
                    id SERIAL PRIMARY KEY,
                    image VARCHAR(100) NOT NULL,
                    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    post_id {fk_type} NOT NULL REFERENCES community_post(id)
                )
            """
        }
        
        for table, sql in tables_to_create.items():
            print(f"🔍 Checking {table}...")
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
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
        import traceback
        traceback.print_exc()
        print(f"❌ Error: {e}")
