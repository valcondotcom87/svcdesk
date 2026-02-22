import uuid
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assetcategory_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assetcategory_updated', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_categories', to='organizations.organization')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('organization', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('asset_tag', models.CharField(blank=True, max_length=50, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('in_use', 'In Use'), ('in_stock', 'In Stock'), ('maintenance', 'Maintenance'), ('planned', 'Planned'), ('retired', 'Retired'), ('disposed', 'Disposed')], default='in_use', max_length=20)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('warranty_expires', models.DateField(blank=True, null=True)),
                ('serial_number', models.CharField(blank=True, max_length=255)),
                ('created_by', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asset_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asset_updated', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to='assets.assetcategory')),
                ('current_owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_assets', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='organizations.organization')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AssetDepreciation',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('depreciation_method', models.CharField(choices=[('straight_line', 'Straight Line'), ('declining_balance', 'Declining Balance')], default='straight_line', max_length=30)),
                ('useful_life_years', models.IntegerField(default=3)),
                ('current_value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('accumulated_depreciation', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('residual_value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('last_calculated_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assetdepreciation_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assetdepreciation_updated', to=settings.AUTH_USER_MODEL)),
                ('asset', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='assets.asset')),
            ],
        ),
        migrations.CreateModel(
            name='AssetMaintenance',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('maintenance_type', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('maintenance_date', models.DateField()),
                ('next_due', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assetmaintenance_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assetmaintenance_updated', to=settings.AUTH_USER_MODEL)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.asset')),
                ('performed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AssetTransfer',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('transfer_date', models.DateTimeField()),
                ('transfer_notes', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assettransfer_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assettransfer_updated', to=settings.AUTH_USER_MODEL)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.asset')),
                ('from_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asset_transfers_from', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asset_transfers_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['organization', 'status'], name='assets_asset_org_sta_4f9d2c_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['asset_tag'], name='assets_asset_tag_1c0a2d_idx'),
        ),
    ]
