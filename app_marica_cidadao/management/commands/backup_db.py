import os
import shutil
import datetime
import glob
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Realiza o backup automático do banco de dados SQLite e limpa cópias antigas.'

    def handle(self, *args, **kwargs):
        # 1. Obter caminho do banco de dados principal
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'Banco de dados não encontrado em: {db_path}'))
            return

        # 2. Garantir que a pasta de backup exista
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # 3. Gerar nome do arquivo com timestamp (Ex: db_backup_20231024_153022.sqlite3)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.sqlite3'
        backup_path = os.path.join(backup_dir, backup_filename)

        # 4. Copiar o arquivo
        try:
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f'✅ Backup realizado com sucesso: {backup_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao realizar o backup: {str(e)}'))
            return

        # 5. Limpar rotina (Deletar arquivos mais velhos que 7 dias)
        self.limpar_backups_antigos(backup_dir, dias=7)

    def limpar_backups_antigos(self, backup_dir, dias):
        limite_tempo = datetime.datetime.now() - datetime.timedelta(days=dias)
        arquivos_backup = glob.glob(os.path.join(backup_dir, 'db_backup_*.sqlite3'))
        
        removidos = 0
        for arquivo in arquivos_backup:
            try:
                # Obtém o tempo de modificação do arquivo
                timestamp_modificacao = os.path.getmtime(arquivo)
                data_modificacao = datetime.datetime.fromtimestamp(timestamp_modificacao)
                
                # Se for mais velho que o limite, deleta
                if data_modificacao < limite_tempo:
                    os.remove(arquivo)
                    removidos += 1
                    self.stdout.write(self.style.WARNING(f'🗑️ Backup antigo removido: {os.path.basename(arquivo)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao remover backup antigo {arquivo}: {str(e)}'))
                
        if removidos > 0:
            self.stdout.write(self.style.SUCCESS(f'🧹 Limpeza concluída: {removidos} backups deletados.'))
