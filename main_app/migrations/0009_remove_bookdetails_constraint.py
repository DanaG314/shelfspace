from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('main_app', '0008_fix_description_field'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE main_app_bookdetails
            DROP CONSTRAINT main_app_bookdetails_book_id_ac5b65a6_fk_main_app_book_id;
            """,
            """
            ALTER TABLE main_app_bookdetails
            ADD CONSTRAINT main_app_bookdetails_book_id_ac5b65a6_fk_main_app_book_id
            FOREIGN KEY (book_id) REFERENCES main_app_book(id);
            """
        ),
    ]
