import os
import glob

def remove_old(path, save_last=5):
    if not os.path.isdir(path):
        print(f'Для чистке от старого путь "{path}" не существует.')
        return

    for dirname in os.listdir(path):
        full_path = os.path.join(path, dirname)
        if not os.path.isdir(full_path):
            continue

        files = glob.glob(f'{full_path}{os.sep}*.*')
        files.sort(key=os.path.getmtime)

        for fname in files[:-save_last]:
            os.remove(fname)
            print(f'Удален файл: "{fname}"')
            