from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programme", "0013_auto_20220324_1737"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contribution",
            name="can_be_published",
            field=models.BooleanField(
                choices=[(True, "Yes"), (False, "No")],
                null=True,
                help_text="Can the abstract be made publicly available for non-communitymembers after the assembly under a <a href='https://creativecommons.org/licenses/by/4.0/'>CC BY 4.0</a> license?",
            ),
        ),
    ]
