import ffmpeg
import numpy as np
import json
import tempfile
import os
from scipy.io import wavfile
import argparse


def generate_peaks_3(audio_file, output_json, max_samples=1000000, peaks_per_second=20):

    # out, _ = ffmpeg.input(audio_file).output('pipe:1', format='s16le', ac=1, ar=44100).run(capture_stdout=True, capture_stderr=True)
    out, _ = ffmpeg.input(audio_file, loglevel='quiet').output('pipe:1', format='s16le', ac=1, ar=44100).run(capture_stdout=True)

    audio_data = np.frombuffer(out, dtype=np.int16)


    # Вычисление duration
    sample_rate = 44100
    duration = len(audio_data) / sample_rate


    # Авто-расчет количества чанков
    samples = int(duration * peaks_per_second)
    samples = min(samples, max_samples)  # Ограничение сверху


    # Подсчёт пиков с учётом всех данных
    chunks = np.array_split(audio_data, samples)

    peaks = []
    for chunk in chunks:
        if len(chunk) > 0:
            max_val = int(np.max(chunk))
            min_val = int(np.min(chunk))

            # Нормализация значений пиков
            normalized_max = max_val / 32768.0
            normalized_min = min_val / 32768.0
            peaks.extend([normalized_max, normalized_min])

    # Сохраняем JSON
    with open(output_json, 'w') as f:
        json.dump({
            "sample_rate": sample_rate,
            "peaks": peaks,
            "bits": 16,
            "duration": duration
        }, f)


def main():
    parser = argparse.ArgumentParser(description='Generate audio peaks JSON from an audio file.')
    parser.add_argument('audio_file', type=str, help='Path to the input audio file')
    parser.add_argument('--output', type=str, default=None, help='Path to the output JSON file (optional)')
    args = parser.parse_args()

    audio_file = args.audio_file
    output_json = args.output if args.output else os.path.splitext(os.path.basename(audio_file))[0] + '.json'

    generate_peaks_3(audio_file, output_json)


if __name__ == '__main__':
    main()