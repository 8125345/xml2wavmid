
import random
from shutil import move
import glob
import os
import subprocess
from music21 import converter
from mido import MidiFile

SF2 = "./SC55_Piano_V2.sf2"

all_dirs = []
def iter_dirs(rootDir):
  for root, dirs, files in os.walk(rootDir):
    if dirs != []:
      for dirname in dirs:
        full_dirname = os.path.join(root, dirname)
        all_dirs.append(full_dirname)
        iter_dirs(full_dirname)

src_dir = './raw'
dst_dir = './raw_wav_mid'
iter_dirs(src_dir)

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

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

### 陪练
src_dir = '/deepiano_data/guolijun/deepiano/bgm_xml' 
dst_dir = '/deepiano_data/dataset/Peilian_xml_SC55'

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

all_bgm_xml_list = glob.glob(src_dir+'/*.xml')
xml_list = random.sample(all_bgm_xml_list, 100)
if __name__ == '__main__':
    cnt = 0
    for file in xml_list:
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


