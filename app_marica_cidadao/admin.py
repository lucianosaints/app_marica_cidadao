from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
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
    list_display = ('id_protocolo', 'prioridade_badge', 'status_badge', 'categoria_com_emoji', 'cidadao', 'criado_em')
    list_filter = ('status_atual', 'prioridade', 'categoria', 'bairro', 'criado_em')
    search_fields = ('id', 'descricao', 'endereco_aproximado', 'cidadao__username', 'cidadao__first_name')
    readonly_fields = ('criado_em', 'atualizado_em', 'mapa_localizacao_v2', 'justificativa_ia', 'avaliacao_cidadao')
    inlines = [HistoricoStatusInline]
    list_per_page = 20

    fieldsets = (
        ('🔍 Identificação do Chamado', {
            'fields': (('categoria', 'prioridade'), 'status_atual')
        }),
        ('📝 Detalhes do Problema', {
            'fields': ('descricao', 'foto_problema', 'justificativa_ia')
        }),
        ('📍 Localização e Precisão', {
            'fields': ('endereco_aproximado', 'mapa_localizacao_v2', ('latitude', 'longitude'))
        }),
        ('👤 Dados do Solicitante', {
            'fields': ('cidadao',)
        }),
        ('🏠 Propriedade Privada (Se Aplicável)', {
            'classes': ('collapse',),
            'fields': ('e_propriedade_privada', 'comprovante_titularidade', 'aceite_termo_ambiental')
        }),
        ('⭐ Encerramento e Feedback', {
            'fields': ('avaliacao', 'comentario_cidadao', 'criado_em', 'atualizado_em')
        }),
    )

    def id_protocolo(self, obj):
        return f"#{obj.id}"
    id_protocolo.short_description = "ID"

    def categoria_com_emoji(self, obj):
        return f"{obj.categoria.emoji or ''} {obj.categoria.nome}"
    categoria_com_emoji.short_description = "Categoria"

    def status_badge(self, obj):
        colors = {
            'recebido': '#7f8c8d',
            'em_analise': '#3498db',
            'equipe_despachada': '#f1c40f',
            'resolvido': '#2ecc71',
            'rejeitado': '#e74c3c',
        }
        color = colors.get(obj.status_atual, '#000')
        return mark_safe(f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 11px; text-transform: uppercase;">{obj.get_status_atual_display()}</span>')
    status_badge.short_description = "Status"
    status_badge.admin_order_field = 'status_atual'

    def prioridade_badge(self, obj):
        colors = {
            'baixa': '#bdc3c7',
            'media': '#e67e22',
            'alta': '#c0392b',
        }
        color = colors.get(obj.prioridade, '#000')
        return mark_safe(f'<span style="color: {color}; font-weight: 800; font-size: 12px; letter-spacing: 0.5px;">● {obj.get_prioridade_display().upper()}</span>')
    prioridade_badge.short_description = "Prioridade"
    prioridade_badge.admin_order_field = 'prioridade'

    def avaliacao_cidadao(self, obj):
        if obj.avaliacao:
            stars = "⭐" * obj.avaliacao
            return mark_safe(f'<div style="font-size: 16px;">{stars}</div><p style="font-style: italic;">"{obj.comentario_cidadao or ""}"</p>')
        return "Aguardando avaliação"
    avaliacao_cidadao.short_description = "Feedback do Cidadão"

    def mapa_localizacao_v2(self, obj):
        if obj.latitude and obj.longitude:
            html = f"""
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <div id="map_admin" style="width: 100%; height: 350px; border-radius: 15px; border: 2px solid #ecf0f1; box-shadow: 0 4px 15px rgba(0,0,0,0.05);"></div>
            <script>
                (function() {{
                    window.addEventListener('load', function() {{
                        var mapDiv = document.getElementById('map_admin');
                        if (mapDiv) {{
                            var map = L.map('map_admin').setView([{obj.latitude}, {obj.longitude}], 17);
                            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                            L.marker([{obj.latitude}, {obj.longitude}]).addTo(map).bindPopup('<b>{obj.categoria.nome}</b>').openPopup();
                        }}
                    }});
                }})();
            </script>
            """
            return mark_safe(html)
        return mark_safe('<span style="color: #95a5a6; font-style: italic;">📍 GPS não disponível</span>')
    mapa_localizacao_v2.short_description = "Mapa de Precisão"

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = RelatoZeladoria.objects.get(pk=obj.pk)
            if old_obj.status_atual != obj.status_atual:
                HistoricoStatus.objects.create(
                    relato=obj,
                    status=obj.status_atual,
                    observacao_prefeitura=f"Status alterado via Painel Administrativo por {request.user.username}.",
                    atualizado_por=request.user
                )
        super().save_model(request, obj, form, change)

@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ('relato', 'status', 'data_atualizacao', 'atualizado_por')
    list_filter = ('status', 'data_atualizacao')
