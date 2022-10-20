# -*- coding: utf-8 -*-
import os
import random
from shutil import copyfile,move
from music21 import converter
from mido import MidiFile
from glob import glob
import subprocess
import audio_utils as audt
# from humanize import time_error
# from sequencer import Sequencer
import sox
from random import uniform, randint
import soundfile as sf

import multiprocessing
import numpy as np


#'''
#depend：
#apt-get install sox
#apt-get install fluidsynth

#pip install sox
#pip install music21
#pip install mido
#'''



SF2 = "./SC55_Piano_V2.sf2"


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


def process_bgm_xml_run():

    bgm_xml_path = '/deepiano_data/guolijun/deepiano/bgm_xml' #'./bgm_xml' # 
    metronome_solfege_path = '/deepiano_data/guolijun/deepiano/deepiano_data_tools/mixed' # './metronome_solfege' # 
    dst_path = '/deepiano_data/bgm_xml_res' #'./res' #

    bgm_xml_list = glob(bgm_xml_path+'/*.xml')
    metronome_solfege_list = glob(metronome_solfege_path+'/*.wav')

    no_match_solfege_num = 0
    no_bgm_num = 0 
    cbn = sox.Combiner()
    crt = 0
    for xml_fn in bgm_xml_list:
        crt +=1
        print('File %dth in %d'% (crt, len(bgm_xml_list)))
        dir, file = os.path.split(xml_fn)
        filename, ext = os.path.splitext(file) 

        dst_file_path = os.path.join(dst_path, filename)
        if not os.path.exists(dst_file_path):
            os.makedirs(dst_file_path)

        m = converter.parse(xml_fn)
        dst_midi_fn = dst_file_path+'/'+filename+'.mid'
        try:
            m.write('midi', dst_midi_fn)
            print('midi_fn: ', dst_midi_fn)

            midi = MidiFile(dst_midi_fn)
            midi.save(dst_midi_fn)
            
            dst_piano_fn = os.path.join(dst_file_path, '%s.wav'%filename)
            cmd = f"fluidsynth -g2 -R0 -C0 -F {dst_piano_fn} {SF2} {dst_midi_fn}"
            subprocess.run(cmd, shell=True)
            resampling_file(dst_piano_fn, dst_file_path)
            piano_audio = audt.file2arr(dst_piano_fn)
            piano_len = len(piano_audio)

            bgm_fn = os.path.join(dir, '%s.mp3'%filename)
            dst_bgm_fn = os.path.join(dst_file_path, '%s_bgm.wav'%filename)
            bgm_flag=False
            if os.path.exists(bgm_fn):
                bgm_flag=True
                copyfile(bgm_fn, dst_bgm_fn)
                bgm_audio = audt.file2arr(dst_bgm_fn)
                resampling_file(dst_bgm_fn, dst_file_path)
                bgm_len = len(bgm_audio)
            if bgm_flag==False:
                no_bgm_num += 1

            metro_solfege_fn = os.path.join(metronome_solfege_path, 'singScore_%s.wav'%filename)
            if metro_solfege_fn not in metronome_solfege_list:
                idx = randint(0,len(metronome_solfege_list)-1)
                metro_solfege_fn = metronome_solfege_list[idx]
                no_match_solfege_num += 1
            dst_metro_solfege_fn = os.path.join(dst_file_path, '%s_metronome_solfege.wav'%filename)
            copyfile(metro_solfege_fn, dst_metro_solfege_fn)
            metro_solfege_audio = audt.file2arr(dst_metro_solfege_fn)
            resampling_file(dst_metro_solfege_fn, dst_file_path)
            metro_solfege_len = len(metro_solfege_audio)
            
            if bgm_flag:
                if bgm_len > piano_len:
                    bgm_audio = bgm_audio[:piano_len]
                if metro_solfege_len > piano_len:
                    metro_solfege_audio = metro_solfege_audio[: piano_len]
                # min_len = min(piano_len, bgm_len, metro_solfege_len)
                # bgm_audio = bgm_audio[: min_len]
                # piano_audio = piano_audio[: min_len]
                # metro_solfege_audio = metro_solfege_audio[: min_len]
                sf.write(dst_piano_fn, piano_audio, 16000)
                sf.write(dst_bgm_fn, bgm_audio, 16000)
                sf.write(dst_metro_solfege_fn, metro_solfege_audio, 16000)

                dst_mix_bgm_metro_solfege_fn = os.path.join(dst_file_path, '%s_mix_bgm_metronome_solfege.wav'%filename)
                cbn.build([dst_bgm_fn, dst_metro_solfege_fn], dst_mix_bgm_metro_solfege_fn, 'mix')

                bgm_vol = uniform(0.1, 1.0)
                metro_solfege_vol = uniform(0.1, 1.0)
                pno_vol = uniform(0.1, 1.0)
                dst_mix_piano_bgm_metro_solfege_fn = os.path.join(dst_file_path, '%s_mix_piano_%.2f_bgm_%.2f_metro_solfege_%.2f.wav'%(filename,pno_vol,bgm_vol,metro_solfege_vol))
                cbn.build([dst_piano_fn, dst_bgm_fn, dst_metro_solfege_fn], dst_mix_piano_bgm_metro_solfege_fn, 'mix', [pno_vol, bgm_vol, metro_solfege_vol])
            else:
                if metro_solfege_len > piano_len:
                    metro_solfege_audio = metro_solfege_audio[:piano_len]
                # min_len = min(piano_len, metro_solfege_len)
                # piano_audio = piano_audio[: min_len]
                # metro_solfege_audio = metro_solfege_audio[: min_len]
                sf.write(dst_piano_fn, piano_audio, 16000)
                sf.write(dst_metro_solfege_fn, metro_solfege_audio, 16000)

                metro_solfege_vol = uniform(0.1, 1.0)
                pno_vol = uniform(0.1, 1.0)
                dst_mix_piano_bgm_metro_solfege_fn = os.path.join(dst_file_path, '%s_mix_piano_%.2f_metro_solfege_%.2f.wav'%(filename,pno_vol,metro_solfege_vol))
                cbn.build([dst_piano_fn, dst_metro_solfege_fn], dst_mix_piano_bgm_metro_solfege_fn, 'mix', [pno_vol, metro_solfege_vol])
        except:
            print('False to write midi file: %s'%xml_fn )

    print('no bgm num: %d, no match solfege num: %d, total wav num %d' % (no_bgm_num, no_match_solfege_num, len(bgm_xml_list)))


bgm_xml_path = '/deepiano_data/guolijun/deepiano/bgm_xml' #'./bgm_xml' # 
metronome_solfege_path = '/deepiano_data/guolijun/deepiano/deepiano_data_tools/mixed' # './metronome_solfege' # 
dst_path = '/deepiano_data/peilian_bgm_xml_res_SC55' #'./res' #

all_bgm_xml_list = glob(bgm_xml_path+'/*.xml')
metronome_solfege_list = glob(metronome_solfege_path+'/*.wav')

# all_dst_bgm_list = os.listdir('/deepiano_data/bgm_xml_res_pool')


def func(bgm_xml_list):
    no_match_solfege_num = 0
    no_bgm_num = 0 
    cbn = sox.Combiner()
    for xml_fn in bgm_xml_list:
        dir, file = os.path.split(xml_fn)
        filename, ext = os.path.splitext(file) 

        # if filename in all_dst_bgm_list:
        #     continue

        metro_solfege_fn = os.path.join(metronome_solfege_path, 'singScore_%s.wav'%filename)
        if metro_solfege_fn not in metronome_solfege_list:
            print('no metro_solfege file: ', metro_solfege_fn)
            continue

        dst_file_path = os.path.join(dst_path, filename)
        if not os.path.exists(dst_file_path):
            os.makedirs(dst_file_path)

        m = converter.parse(xml_fn)
        dst_midi_fn = dst_file_path+'/'+filename+'.mid'
        try:
            m.write('midi', dst_midi_fn)
            print('midi_fn: ', dst_midi_fn)

            midi = MidiFile(dst_midi_fn)
            midi.save(dst_midi_fn)
            
            dst_piano_fn = os.path.join(dst_file_path, '%s.wav'%filename)
            cmd = f"fluidsynth -g2 -R0 -C0 -F {dst_piano_fn} {SF2} {dst_midi_fn}"
            subprocess.run(cmd, shell=True)
            resampling_file(dst_piano_fn, dst_file_path)
            piano_audio = audt.file2arr(dst_piano_fn)
            piano_len = len(piano_audio)

            bgm_fn = os.path.join(dir, '%s.mp3'%filename)
            dst_bgm_fn = os.path.join(dst_file_path, '%s_bgm.wav'%filename)
            bgm_flag=False
            if os.path.exists(bgm_fn):
                bgm_flag=True
                copyfile(bgm_fn, dst_bgm_fn)
                bgm_audio = audt.file2arr(dst_bgm_fn)
                resampling_file(dst_bgm_fn, dst_file_path)
                bgm_len = len(bgm_audio)
            if bgm_flag==False:
                print('no bgm file: ', filename)
                no_bgm_num += 1

            # metro_solfege_fn = os.path.join(metronome_solfege_path, 'singScore_%s.wav'%filename)
            if metro_solfege_fn not in metronome_solfege_list:
                idx = randint(0,len(metronome_solfege_list)-1)
                metro_solfege_fn = metronome_solfege_list[idx]
                no_match_solfege_num += 1
            dst_metro_solfege_fn = os.path.join(dst_file_path, '%s_metronome_solfege.wav'%filename)
            copyfile(metro_solfege_fn, dst_metro_solfege_fn)
            metro_solfege_audio = audt.file2arr(dst_metro_solfege_fn)
            resampling_file(dst_metro_solfege_fn, dst_file_path)
            metro_solfege_len = len(metro_solfege_audio)
            
            if bgm_flag:
                if bgm_len > piano_len:
                    bgm_audio = bgm_audio[:piano_len]
                if metro_solfege_len > piano_len:
                    metro_solfege_audio = metro_solfege_audio[: piano_len]
                # min_len = min(piano_len, bgm_len, metro_solfege_len)
                # bgm_audio = bgm_audio[: min_len]
                # piano_audio = piano_audio[: min_len]
                # metro_solfege_audio = metro_solfege_audio[: min_len]
                sf.write(dst_piano_fn, piano_audio, 16000)
                sf.write(dst_bgm_fn, bgm_audio, 16000)
                sf.write(dst_metro_solfege_fn, metro_solfege_audio, 16000)

                dst_mix_bgm_metro_solfege_fn = os.path.join(dst_file_path, '%s_mix_bgm_metronome_solfege.wav'%filename)
                cbn.build([dst_bgm_fn, dst_metro_solfege_fn], dst_mix_bgm_metro_solfege_fn, 'mix')

                bgm_vol = uniform(0.1, 1.0)
                metro_solfege_vol = uniform(0.1, 1.0)
                pno_vol = uniform(0.1, 1.0)
                dst_mix_piano_bgm_metro_solfege_fn = os.path.join(dst_file_path, '%s_mix_piano_%.2f_bgm_%.2f_metro_solfege_%.2f.wav'%(filename,pno_vol,bgm_vol,metro_solfege_vol))
                cbn.build([dst_piano_fn, dst_bgm_fn, dst_metro_solfege_fn], dst_mix_piano_bgm_metro_solfege_fn, 'mix', [pno_vol, bgm_vol, metro_solfege_vol])
            else:
                if metro_solfege_len > piano_len:
                    metro_solfege_audio = metro_solfege_audio[:piano_len]
                # min_len = min(piano_len, metro_solfege_len)
                # piano_audio = piano_audio[: min_len]
                # metro_solfege_audio = metro_solfege_audio[: min_len]
                sf.write(dst_piano_fn, piano_audio, 16000)
                sf.write(dst_metro_solfege_fn, metro_solfege_audio, 16000)

                metro_solfege_vol = uniform(0.1, 1.0)
                pno_vol = uniform(0.1, 1.0)
                dst_mix_piano_bgm_metro_solfege_fn = os.path.join(dst_file_path, '%s_mix_piano_%.2f_metro_solfege_%.2f.wav'%(filename,pno_vol,metro_solfege_vol))
                cbn.build([dst_piano_fn, dst_metro_solfege_fn], dst_mix_piano_bgm_metro_solfege_fn, 'mix', [pno_vol, metro_solfege_vol])
        
        except:
            print('False to write midi file: %s'%xml_fn )
    print('no bgm num: %d, no match solfege num: %d, total wav num %d' % (no_bgm_num, no_match_solfege_num, len(bgm_xml_list)))

def process_pool():
    pool = multiprocessing.Pool(5)
    select_xml_list = random.sample(range(0, len(all_bgm_xml_list)), 1000)
    bgm_xml_lists = [all_bgm_xml_list[select_xml_list[0:200]], all_bgm_xml_list[select_xml_list[200:400]], all_bgm_xml_list[select_xml_list[400:600]], all_bgm_xml_list[select_xml_list[600:800]], all_bgm_xml_list[select_xml_list[800:1000]]]
    result = pool.map(func,bgm_xml_lists)
    # pool.apply_async(func, (all_bgm_xml_list,))
    pool.close()
    pool.join()
    return result

if __name__ == '__main__':
    print("start run")
    # new_run()
    # dst_resource_run()
    # process_bgm_xml_run()

    # t2 = time.time()
    result = process_pool()
    # print('time: ', time.time()-t2)
    res = np.array(result)
    nums = np.sum(res, axis=0)
    print('all no bgm num: %d, all no match solfege num: %d, all total wav num %d' % (nums[0], nums[1], nums[2]))
    print('all done')
