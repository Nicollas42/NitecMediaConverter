import ffmpeg
import os
import subprocess
import re
import sys
import shutil

class ConversorService:
    """
    Serviço responsável pela conversão com rastreamento de progresso real.
    """

    def obter_duracao(self, caminho_arquivo: str) -> float:
        """
        Usa o ffprobe para descobrir a duração total do vídeo em segundos.
        """
        try:
            probe = ffmpeg.probe(caminho_arquivo)
            duracao = float(probe['format']['duration'])
            return duracao
        except Exception:
            return 0.0

    def converter_com_progresso(self, caminho_entrada: str, formato_saida: str, pasta_temp: str):
        """
        Executa a conversão e retorna o progresso passo a passo (Generator).
        
        Yields:
            int: Porcentagem de conclusão (0 a 100).
            str: Caminho do arquivo final quando terminar.
        """
        nome_arquivo = os.path.basename(caminho_entrada)
        nome_base = os.path.splitext(nome_arquivo)[0]
        
        # Define o caminho temporário
        caminho_saida = os.path.join(pasta_temp, f"{nome_base}.{formato_saida}")
        
        # Garante que a pasta temp existe
        os.makedirs(pasta_temp, exist_ok=True)

        # Pega a duração total para calcular a %
        duracao_total = self.obter_duracao(caminho_entrada)
        
        # Comando FFmpeg manual para termos controle total do output
        comando = [
            'ffmpeg',
            '-i', caminho_entrada,
            '-y', # Sobrescreve sem perguntar
            caminho_saida
        ]

        # Configuração para extrair apenas áudio se necessário
        if formato_saida in ['mp3', 'wav', 'aac', 'ogg']:
             comando.insert(3, '-vn')

        # Inicia o processo lendo o erro (o ffmpeg joga o log no stderr)
        processo = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8' # Importante para Windows
        )

        # Regex para achar o tempo: time=00:00:05.20
        padrao_tempo = re.compile(r'time=(\d{2}):(\d{2}):(\d{2})\.\d+')

        # Loop de leitura linha a linha
        while True:
            linha = processo.stderr.readline()
            if not linha and processo.poll() is not None:
                break

            if linha:
                # Procura a info de tempo
                match = padrao_tempo.search(linha)
                if match and duracao_total > 0:
                    h, m, s = map(int, match.groups())
                    segundos_atuais = h * 3600 + m * 60 + s
                    
                    porcentagem = (segundos_atuais / duracao_total)
                    yield porcentagem, None # Retorna só a %

        # Retorna 100% e o caminho final
        yield 1.0, caminho_saida