from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_ad_sync_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='ADConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('server_name', models.CharField(help_text='AD server hostname or IP address', max_length=255)),
                ('server_port', models.IntegerField(default=389, help_text='LDAP port (389 for standard, 636 for SSL)')),
                ('use_ssl', models.BooleanField(default=False, help_text='Use SSL/TLS for connection')),
                ('bind_username', models.CharField(help_text='Service account DN (e.g., CN=admin,DC=company,DC=com)', max_length=255)),
                ('bind_password', models.CharField(help_text='Service account password', max_length=255)),
                ('search_base', models.CharField(help_text='Base DN for user search (e.g., OU=Users,DC=company,DC=com)', max_length=255)),
                ('search_filter', models.CharField(default='(objectClass=user)', help_text='LDAP filter for users', max_length=500)),
                ('username_attribute', models.CharField(default='sAMAccountName', help_text='AD attribute for username', max_length=100)),
                ('email_attribute', models.CharField(default='mail', help_text='AD attribute for email', max_length=100)),
                ('first_name_attribute', models.CharField(default='givenName', help_text='AD attribute for first name', max_length=100)),
                ('last_name_attribute', models.CharField(default='sn', help_text='AD attribute for last name', max_length=100)),
                ('phone_attribute', models.CharField(default='telephoneNumber', help_text='AD attribute for phone', max_length=100)),
                ('group_base', models.CharField(blank=True, help_text='Base DN for group search', max_length=255, null=True)),
                ('group_member_attribute', models.CharField(default='member', help_text='Attribute containing group members', max_length=100)),
                ('auto_create_users', models.BooleanField(default=True, help_text='Automatically create users not in system')),
                ('auto_update_users', models.BooleanField(default=True, help_text='Automatically update user information')),
                ('auto_disable_missing_users', models.BooleanField(default=False, help_text='Automatically disable users not in AD')),
                ('is_enabled', models.BooleanField(default=True, help_text='Enable/disable AD sync')),
                ('last_sync_at', models.DateTimeField(blank=True, help_text='Timestamp of last sync', null=True)),
                ('last_sync_status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('success', 'Success'), ('failed', 'Failed')], default='pending', help_text='Status of last sync', max_length=20)),
                ('last_sync_error', models.TextField(blank=True, help_text='Error message from last sync', null=True)),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='organizations.organization')),
            ],
            options={
                'verbose_name': 'AD Configuration',
                'verbose_name_plural': 'AD Configurations',
            },
        ),
    ]
