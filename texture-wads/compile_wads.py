import subprocess
import glob

def make():
    wads_list = [
        'lq_dev',
        'lq_dev_legacy',
        'lq_flesh',
        'lq_greek',
        'lq_health_ammo',
        'lq_legacy',
        'lq_liquidsky',
        'lq_mayan',
        'lq_medieval',
        'lq_palette',
        'lq_metal',
        'lq_props',
        'lq_tech',
        'lq_terra',
        'lq_utility',
        'lq_wood',
    ]
    for wad in wads_list:
        filepaths = glob.glob(f'{wad}/*')
        command = ['qpakman']
        command.extend(filepaths)
        command.extend(['-o', f'{wad}.wad'])
        subprocess.call(command)

if __name__ == "__main__":
    make()

if __name__ == "__build__":
    make()
