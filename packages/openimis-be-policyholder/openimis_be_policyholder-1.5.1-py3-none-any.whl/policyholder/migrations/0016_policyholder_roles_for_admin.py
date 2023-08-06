import logging

from django.db import migrations

from core.utils import insert_role_right_for_system

logger = logging.getLogger(__name__)


def add_rights(apps, schema_editor):
    insert_role_right_for_system(64, 150101)  # search
    insert_role_right_for_system(64, 150102)  # create
    insert_role_right_for_system(64, 150103)  # update
    insert_role_right_for_system(64, 150104)  # delete

    insert_role_right_for_system(64, 150201)  # search
    insert_role_right_for_system(64, 150202)  # create
    insert_role_right_for_system(64, 150203)  # update
    insert_role_right_for_system(64, 150204)  # delete
    insert_role_right_for_system(64, 150206)  # refund

    insert_role_right_for_system(64, 150301)  # search
    insert_role_right_for_system(64, 150302)  # create
    insert_role_right_for_system(64, 150303)  # update
    insert_role_right_for_system(64, 150304)  # delete
    insert_role_right_for_system(64, 150306)  # message

    insert_role_right_for_system(64, 150401)  # search
    insert_role_right_for_system(64, 150402)  # create
    insert_role_right_for_system(64, 150403)  # update
    insert_role_right_for_system(64, 150404)  # delete
    insert_role_right_for_system(64, 150406)  # message


class Migration(migrations.Migration):
    dependencies = [
        ('policyholder', '0015_auto_20210624_1243')
    ]

    operations = [
        migrations.RunPython(add_rights),
    ]
