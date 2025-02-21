from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_add_summary_to_book'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE main_app_book 
            DROP COLUMN IF EXISTS description;
            """,
            """
            ALTER TABLE main_app_book 
            ADD COLUMN description text;
            """
        ),
    ]
