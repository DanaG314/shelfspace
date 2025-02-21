from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_add_summary_to_book'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'main_app_book' 
                    AND column_name = 'description'
                ) THEN
                    ALTER TABLE main_app_book DROP COLUMN description;
                END IF;
            END $$;
            """,
            """
            ALTER TABLE main_app_book 
            ADD COLUMN description text NULL;
            """
        ),
    ]
