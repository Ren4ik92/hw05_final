# Generated by Django 2.2.16 on 2022-10-19 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='like',
            field=models.ImageField(default=0, upload_to=''),
        ),
    ]