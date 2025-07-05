-- SQL script to fix the referral system in production
-- Run this on your production database to add the missing referral_code column

-- Add the referral_code column
ALTER TABLE accounts_user ADD COLUMN referral_code VARCHAR(8) DEFAULT '';

-- Add the referred_by column
ALTER TABLE accounts_user ADD COLUMN referred_by_id INTEGER NULL;

-- Add the referral_points column
ALTER TABLE accounts_user ADD COLUMN referral_points INTEGER DEFAULT 0;

-- Add foreign key constraint for referred_by
ALTER TABLE accounts_user 
ADD CONSTRAINT fk_user_referred_by 
FOREIGN KEY (referred_by_id) REFERENCES accounts_user(id) ON DELETE SET NULL;

-- Add unique constraint for referral_code
ALTER TABLE accounts_user ADD CONSTRAINT unique_referral_code UNIQUE (referral_code);

-- Create index for referral_code
CREATE INDEX idx_user_referral_code ON accounts_user(referral_code);

-- Create index for referred_by
CREATE INDEX idx_user_referred_by ON accounts_user(referred_by_id);

-- Populate referral codes for existing users
-- This will be handled by the Django migration, but you can run this as a backup
-- UPDATE accounts_user SET referral_code = 'temp' || id WHERE referral_code = '';

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'accounts_user' 
AND column_name IN ('referral_code', 'referred_by_id', 'referral_points')
ORDER BY column_name; 