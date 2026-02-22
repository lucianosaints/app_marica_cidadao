from django.contrib import admin
from .models import CategoriaProblema, RelatoZeladoria, HistoricoStatus

class HistoricoStatusInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 1

@admin.register(CategoriaProblema)
class CategoriaProblemaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tempo_estimado_resolucao')
    search_fields = ('nome',)

@admin.register(RelatoZeladoria)
class RelatoZeladoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'status_atual', 'criado_em', 'cidadao')
    list_filter = ('status_atual', 'categoria', 'criado_em')
    search_fields = ('descricao', 'endereco_aproximado', 'cidadao__username')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = [HistoricoStatusInline]

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = RelatoZeladoria.objects.get(pk=obj.pk)
            if old_obj.status_atual != obj.status_atual:
                HistoricoStatus.objects.create(
                    relato=obj,
                    status=obj.status_atual,
                    observacao_prefeitura=f"Status atualizado via painel administrativo.",
                    atualizado_por=request.user
                )
        super().save_model(request, obj, form, change)

@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ('relato', 'status', 'data_atualizacao', 'atualizado_por')
    list_filter = ('status', 'data_atualizacao')
