import argparse
from pgo_parser import parse_pgo_file, save_pgo_file, Word
from srt_parser import parse_srt_file

def adjust_phonemes_in_word(word):
    """
    Ajusta os fonemas existentes em uma palavra para serem distribuídos uniformemente
    entre start_frame e end_frame.

    :param word: Um objeto Word cuja lista de fonemas será ajustada.
    """
    total_frames = word.end_frame - word.start_frame + 1  # Inclui o frame final
    num_phonemes = len(word.phonemes)

    if num_phonemes == 0:
        return  # Sem fonemas para ajustar

    frames_per_phoneme = total_frames // num_phonemes
    remaining_frames = total_frames % num_phonemes  # Frames extras para distribuir
    start_frame = word.start_frame

    for i, phoneme in enumerate(word.phonemes):
        # Distribuir frames extras uniformemente
        extra_frame = 1 if i < remaining_frames else 0
        phoneme.frame = start_frame + i * (frames_per_phoneme + extra_frame)

def adjust_phonemes_in_segment(segment):
    """
    Ajusta os fonemas de cada palavra no segmento.
    """
    for word in segment.words:
        adjust_phonemes_in_word(word)

def adjust_words_in_segment(segment):
    """Ajusta os start_frame e end_frame das palavras existentes no segmento sem sobreposição."""
    num_words = len(segment.words)
    if num_words == 0:
        return  # Se não há palavras, não há nada para ajustar

    total_frames = segment.end_frame - segment.start_frame
    frames_per_word = total_frames // num_words
    remaining_frames = total_frames % num_words  # Para lidar com divisão que não é exata
    start_frame = segment.start_frame

    for i, word in enumerate(segment.words):
        # Distribuir frames extras uniformemente
        extra_frame = 1 if i < remaining_frames else 0
        end_frame = start_frame + frames_per_word + extra_frame

        word.start_frame = start_frame
        word.end_frame = end_frame - 1  # End frame é inclusivo, então ajustamos para evitar sobreposição
        start_frame = end_frame

def update_segments_with_srt(pgo_content, srt_lines, fps):
    """
    Atualiza os segmentos do arquivo PGO com base nas legendas do arquivo SRT.
    """
    for voice in pgo_content.voices:
        for segment in voice.segments:
            # Procurar o texto no SRT, mas ignorar linhas já usadas
            matching_lines = [line for line in srt_lines if line.text == segment.text and not line.used]
            if not matching_lines:
                print(f"Texto não encontrado no SRT ou já usado: {segment.text}")
                continue

            # Usar a primeira linha correspondente e marcá-la como usada
            srt_line = matching_lines[0]
            srt_line.used = True

            # Atualizar start_frame e end_frame
            segment.start_frame = int(srt_line.start_time * fps)
            segment.end_frame = int(srt_line.end_time * fps)

            # Ajustar os frames das palavras
            adjust_words_in_segment(segment)

            # Ajustar os fonemas das palavras
            adjust_phonemes_in_segment(segment)

    return pgo_content

def main():
    parser = argparse.ArgumentParser(description="Read and update PGO with SRT data.")
    parser.add_argument("pgo_file", type=str, help="Path to the PGO file")
    parser.add_argument("srt_file", type=str, help="Path to the SRT file")
    parser.add_argument("output_pgo", type=str, help="Path to save the updated PGO file")

    args = parser.parse_args()

    # Lendo os arquivos
    pgo_content = parse_pgo_file(args.pgo_file)
    srt_lines = parse_srt_file(args.srt_file)

    # Atualizar os segmentos no PGO com base no SRT
    updated_pgo_content = update_segments_with_srt(pgo_content, srt_lines, pgo_content.fps)

    # Salvar o PGO atualizado
    save_pgo_file(args.output_pgo, updated_pgo_content)
    print(f"PGO file updated and saved to '{args.output_pgo}'.")

if __name__ == "__main__":
    main()
