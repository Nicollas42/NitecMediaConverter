import ffmpeg
import os
import subprocess
import re
import sys

class ConversorService:
    def __init__(self):
        self.ffmpeg_path = self._obter_caminho_ffmpeg()

    def _obter_caminho_ffmpeg(self):
        nome_exe = "ffmpeg.exe"
        if getattr(sys, 'frozen', False):
            caminho_base = sys._MEIPASS
        else:
            caminho_base = os.getcwd()
        
        caminho_final = os.path.join(caminho_base, nome_exe)
        
        if not os.path.exists(caminho_final):
            caminho_final = nome_exe 
            
        return caminho_final

    def obter_duracao(self, caminho_arquivo: str) -> float:
        try:
            probe = ffmpeg.probe(caminho_arquivo, cmd=self.ffmpeg_path)
            duracao = float(probe['format']['duration'])
            return duracao
        except Exception:
            return 0.0

    def converter_com_progresso(self, caminho_entrada: str, formato_saida: str, pasta_temp: str):
        nome_arquivo = os.path.basename(caminho_entrada)
        nome_base = os.path.splitext(nome_arquivo)[0]
        caminho_saida = os.path.join(pasta_temp, f"{nome_base}.{formato_saida}")
        os.makedirs(pasta_temp, exist_ok=True)

        duracao_total = self.obter_duracao(caminho_entrada)
        
        comando = [
            self.ffmpeg_path,
            '-i', caminho_entrada,
            '-y',
            caminho_saida
        ]

        # Lista expandida de formatos apenas de áudio
        # Isso garante que não dê erro tentando converter vídeo para esses formatos
        formatos_audio = ['mp3', 'wav', 'aac', 'ogg', 'flac', 'wma', 'm4a', 'opus']
        
        if formato_saida in formatos_audio:
             comando.insert(3, '-vn')

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        processo = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            startupinfo=startupinfo
        )

        padrao_tempo = re.compile(r'time=(\d{2}):(\d{2}):(\d{2})\.\d+')

        while True:
            linha = processo.stderr.readline()
            if not linha and processo.poll() is not None:
                break

            if linha:
                match = padrao_tempo.search(linha)
                if match and duracao_total > 0:
                    h, m, s = map(int, match.groups())
                    segundos_atuais = h * 3600 + m * 60 + s
                    porcentagem = (segundos_atuais / duracao_total)
                    yield porcentagem, None

        yield 1.0, caminho_saida