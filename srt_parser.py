import re
from dataclasses import dataclass

@dataclass
class SrtLine:
    start_time: float  # Tempo de início em segundos
    end_time: float    # Tempo de fim em segundos
    text: str          # Texto da legenda

def parse_srt_file(file_path):
    """
    Lê um arquivo SRT e retorna uma lista de objetos SrtLine.
    """
    srt_lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Dividir o conteúdo do arquivo em blocos
    blocks = content.strip().split('\n\n')

    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue  # Ignorar blocos incompletos

        # Ignorar o número sequencial (primeira linha)
        time_line = lines[1]
        text = " ".join(lines[2:])

        # Regex para capturar os tempos no formato SRT
        match = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})", time_line)
        if match:
            start_time = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3)) + int(match.group(4)) / 1000
            end_time = int(match.group(5)) * 3600 + int(match.group(6)) * 60 + int(match.group(7)) + int(match.group(8)) / 1000

            srt_lines.append(SrtLine(start_time=start_time, end_time=end_time, text=text))

    return srt_lines
