from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("institutions", "0003_auto_20210424_1438"),
        ("programme", "0011_alter_affiliation_organization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sessionmaterial",
            name="name",
            field=models.CharField(
                help_text="Display text for the material",
                max_length=200,
                null=True,
            ),
            preserve_default=False,
        ),
    ]
