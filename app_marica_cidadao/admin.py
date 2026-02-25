from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import CategoriaProblema, RelatoZeladoria, HistoricoStatus, PerfilCidadao

class PerfilCidadaoInline(admin.StackedInline):
    model = PerfilCidadao
    can_delete = False
    verbose_name_plural = 'Perfil do Cidadão'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilCidadaoInline,)

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(PerfilCidadao)
class PerfilCidadaoAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'telefone', 'cidade')
    search_fields = ('user__username', 'cpf', 'user__email')

class HistoricoStatusInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0

@admin.register(CategoriaProblema)
class CategoriaProblemaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tempo_estimado_resolucao')
    search_fields = ('nome',)

@admin.register(RelatoZeladoria)
class RelatoZeladoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'status_atual', 'criado_em', 'cidadao')
    list_filter = ('status_atual', 'categoria', 'criado_em')
    search_fields = ('descricao', 'endereco_aproximado', 'cidadao__username')
    readonly_fields = ('criado_em', 'atualizado_em', 'mapa_localizacao')
    inlines = [HistoricoStatusInline]

    from django.utils.safestring import mark_safe

    def mapa_localizacao(self, obj):
        if obj.latitude and obj.longitude:
            html = f"""
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <div id="map" style="width: 100%; height: 400px; border-radius: 10px; border: 1px solid #ccc;"></div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var map = L.map('map').setView([{obj.latitude}, {obj.longitude}], 16);
                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '&copy; OpenStreetMap contributors'
                    }}).addTo(map);
                    L.marker([{obj.latitude}, {obj.longitude}]).addTo(map)
                        .bindPopup('{obj.categoria.nome}')
                        .openPopup();
                }});
            </script>
            """
            return mark_safe(html)
        return "Coordenadas não disponíveis"
    mapa_localizacao.short_description = "Mapa de Precisão (Leaflet)"

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
