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
            name='KnowledgeArticle',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('title', models.CharField(max_length=255)),
                ('summary', models.TextField(blank=True)),
                ('content', models.TextField()),
                ('category', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('review', 'Review'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('tags', models.TextField(blank=True)),
                ('version', models.IntegerField(default=1)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='knowledgearticle_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='knowledgearticle_updated', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='knowledge_articles', to='organizations.organization')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_articles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='knowledgearticle',
            index=models.Index(fields=['organization', 'status'], name='knowledge_a_org_sta_28f9d4_idx'),
        ),
        migrations.AddIndex(
            model_name='knowledgearticle',
            index=models.Index(fields=['organization', 'category'], name='knowledge_a_org_cat_9c2c54_idx'),
        ),
        migrations.AddIndex(
            model_name='knowledgearticle',
            index=models.Index(fields=['-updated_at'], name='knowledge_a_upd_13a3a1_idx'),
        ),
    ]
