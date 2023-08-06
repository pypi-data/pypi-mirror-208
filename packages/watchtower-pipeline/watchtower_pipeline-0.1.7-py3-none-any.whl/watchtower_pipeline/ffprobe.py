import pathlib
import subprocess


def get_frames_count(input_path: pathlib.Path) -> int:
    ffprobe_command = [
        'ffprobe',
        '-v',
        'error',
        '-select_streams',
        'v:0',
        '-count_packets',
        '-show_entries',
        'stream=nb_read_packets',
        '-of',
        'csv=p=0',
        f'{input_path}',
    ]
    result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE).stdout.decode('utf-8')
    return int(result)
