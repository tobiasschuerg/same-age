from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(
                    model_name='timelineimage',
                    old_name='person_name',
                    new_name='person',
                ),
                migrations.AlterField(
                    model_name='timelineimage',
                    name='person',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='timeline.person',
                        db_column='person_name_id',
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
