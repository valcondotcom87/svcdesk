from django.contrib import admin
from apps.knowledge.models import KnowledgeArticle


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'owner', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'summary', 'content')
