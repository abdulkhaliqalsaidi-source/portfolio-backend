from django.db import migrations


DMF_TABLES = [
    'dmf_dependency_rule',
    'dmf_value_history',
    'dmf_field_index',
    'dmf_validation_rule',
    'dmf_field_translation',
    'dmf_field_permission',
    'dmf_field_option',
    'dmf_lookup_source',
    'dmf_field',
    'dmf_field_group',
    'dmf_schema',
]


def drop_dmf_tables(apps, schema_editor):
    existing_tables = set(schema_editor.connection.introspection.table_names())
    with schema_editor.connection.constraint_checks_disabled():
        for table in DMF_TABLES:
            if table in existing_tables:
                quoted_table = schema_editor.quote_name(table)
                schema_editor.execute(f'DROP TABLE {quoted_table}')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_blogpost_extra_data_experience_extra_data_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='extra_data',
        ),
        migrations.RemoveField(
            model_name='experience',
            name='extra_data',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='extra_data',
        ),
        migrations.RemoveField(
            model_name='project',
            name='extra_data',
        ),
        migrations.RemoveField(
            model_name='service',
            name='extra_data',
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='extra_data',
        ),
        migrations.RunPython(drop_dmf_tables, migrations.RunPython.noop),
    ]
