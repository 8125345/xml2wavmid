import random
from shutil import move
import glob
import os
import subprocess
from music21 import converter
from mido import MidiFile

# SF2 = "./SC55_Piano_V2.sf2"
SF2 = 'arachno_modified.sf2'


def resampling_file(file, dst_folder):
    """
    acc转wav 16k
    :param file:
    :return:
    """
    folder, filename = os.path.split(file)
    name, ext = os.path.splitext(filename)
    wav_path = os.path.join(dst_folder, name + "_16k" + ".wav")
    if not os.path.exists(wav_path):
        try:
            subprocess.run(
                ['ffmpeg', '-y', '-loglevel', 'fatal', '-i', f'{file}', '-ac', '1', '-ar', '16000', f"{wav_path}"],
                # cwd='/home/user/Desktop/myProject/',   # current working directory
                # timeout=5,                             # timeout
                check=True  # check for errors
            )
        except Exception:
            print(f"出错跳过，path: {file}")
        os.unlink(file)
        move(wav_path, file)

    ### 清晨


''' 
if __name__ == '__main__':
    cnt = 0
    for dir in all_dirs:
        files = glob.glob(os.path.join(dir, '*.xml'))
        for file in files:
            dir, file = os.path.split(file)
            filename, ext = os.path.splitext(file) 

            m = converter.parse(os.path.join(dir, file))
            dst_midi_fn = dst_dir+'/'+ '%03d.mid'%cnt 
            try:
                m.write('midi', dst_midi_fn)
                print('midi_fn: ', dst_midi_fn)

                midi = MidiFile(dst_midi_fn)
                midi.save(dst_midi_fn)

                dst_piano_fn = os.path.join(dst_dir, '%03d.wav'%cnt)
                cmd = f"fluidsynth -g2 -R0 -C0 -F {dst_piano_fn} {SF2} {dst_midi_fn}"
                subprocess.run(cmd, shell=True)
                resampling_file(dst_piano_fn, dst_dir)
                cnt+=1
            except:
                print('False to write midi file: %s'%file )

'''


if __name__ == '__main__':
    xml_file = '/deepiano_data/guolijun/deepiano/bgm_xml/70332.xml'
    dst_dir = '/deepiano_data/zhaoliang/'
    # xml_file = '/deepiano_data/guolijun/deepiano/bgm_xml/36252.xml'
    assert os.path.exists(xml_file)
    # dir_, file = os.path.split(xml_file)
    # filename, ext = os.path.splitext(file)
    m = converter.parse(xml_file)
    dst_midi_fn = '/deepiano_data/zhaoliang/' + 'arachno_3_70332.mid'
    try:
        m.write('midi', dst_midi_fn)
        print('midi_fn: ', dst_midi_fn)

        midi = MidiFile(dst_midi_fn)
        midi.save(dst_midi_fn)
        dst_piano_fn = '/deepiano_data/zhaoliang/' + 'arachno_3_70332.wav'
        cmd = f"fluidsynth -g2 -R0 -C0 -F {dst_piano_fn} {SF2} {dst_midi_fn}"
        subprocess.run(cmd, shell=True)
        resampling_file(dst_piano_fn, dst_dir)
    except:
        print('False to write midi file: arachno_3_70332.mid')


