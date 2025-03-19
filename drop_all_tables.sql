-- Drop all tables in the correct order
DROP TABLE IF EXISTS django_admin_log CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
DROP TABLE IF EXISTS accounts_useronboarding CASCADE;
DROP TABLE IF EXISTS accounts_studentprofile CASCADE;
DROP TABLE IF EXISTS accounts_user_groups CASCADE;
DROP TABLE IF EXISTS accounts_user_user_permissions CASCADE;
DROP TABLE IF EXISTS accounts_user CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE; 