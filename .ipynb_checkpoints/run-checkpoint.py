# -*- coding: utf-8 -*-
import os
from music21 import converter
from mido import MidiFile
from glob import glob
import subprocess
from humanize import time_error
from sequencer import Sequencer
import sox
from random import uniform


#'''
#depend：
#apt-get install sox
#apt-get install fluidsynth

#pip install sox
#pip install music21
#pip install mido
#'''



SF2 = "./SC55_Piano_V2.sf2"
TIME_ERROR_list = [0] #[0, 0.05, 0.1, 0.15, 1.0, 0.2]  # 时间错位程度，0为无错位 #0.2
SOURCE_DIR = 'bgm_resource'
# bgm_vol = uniform(0.5, 1.0) # uniform(0, 0.5) # bgm 音量范围
# pno_vol = uniform(0, 0.5) # uniform(0.5, 1.0) # 钢琴音量范围
# dst_path = "bgm_resource_%s_%.2f_%.2f" % (TIME_ERROR, bgm_vol, pno_vol)

def merge_audio(bgm_file, piano_file, output_file, bgm_vol, pno_vol):
    cbn = sox.Combiner()
    
    # mix_name = "mix.wav"
    # output_file = os.path.join(output_path, mix_name)
    print('mix_fn: ', output_file)
    cbn.build([bgm_file, piano_file], output_file, 'mix', [bgm_vol, pno_vol])


def run():
  path = SOURCE_DIR+'/*/*.musicxml'
  print(path)
  x = glob(SOURCE_DIR+'/*/*.musicxml')
  print(x)
  if not os.path.isdir(dst_path):
    os.makedirs(dst_path)
  for fn in glob(SOURCE_DIR+'/*/*.musicxml'):
    m = converter.parse(fn)
    file, ext= os.path.splitext(fn)

    midi_fn = dst_path+"/play.mid"
    m.write('midi', midi_fn)
    print('midi_fn: ', midi_fn)

    midi = MidiFile(midi_fn)
    for track in midi.tracks:
        for event in track:
            if event.type == 'program_change':
                event.program = 0

    seq = Sequencer.from_midi(midi)
    time_error(seq, TIME_ERROR)

    midi = seq.render()

    midi.save(midi_fn)

    piano_fn = os.path.join(os.path.dirname(fn), 'piano_%s_%.2f_%.2f.wav'%(TIME_ERROR, bgm_vol, pno_vol))
    cmd = f"fluidsynth -g2 -R0 -C0 -F {piano_fn} {SF2} {midi_fn}"
    subprocess.run(cmd, shell=True)

    bgm_fn = glob(os.path.dirname(fn) + '/*.mp3')[0]
    print('bgm_fn: ', bgm_fn)
    mix_fn = os.path.dirname(midi_fn)
    merge_audio(bgm_fn, piano_fn, mix_fn)

def new_run():
    paths = os.listdir(SOURCE_DIR)
    for path in paths:
        if path == '.DS_Store' or not os.path.isdir(path):
            continue
        for fn in glob(SOURCE_DIR+'/'+path+'/*.musicxml'):
            m = converter.parse(fn)
            midi_fn = dst_path + path +'.mid'
            m.write('midi', midi_fn)
            print('midi_fn: ', midi_fn)

            midi = MidiFile(midi_fn)
            for track in midi.tracks:
                for event in track:
                    if event.type == 'program_change':
                        event.program = 0
            
            seq = Sequencer.from_midi(midi)
            time_error(seq, TIME_ERROR)
            midi = seq.render()
            midi.save(midi_fn)

            piano_fn = os.path.join(os.path.dirname(fn), 'piano_%s_%.2f_%.2f.wav'%(TIME_ERROR, bgm_vol, pno_vol))
            cmd = f"fluidsynth -g2 -R0 -C0 -F {piano_fn} {SF2} {midi_fn}"
            subprocess.run(cmd, shell=True)
            bgm_fn = glob(os.path.dirname(fn) + '/*.mp3')[0]
            print('bgm_fn: ', bgm_fn)
            mix_fn = dst_path + path + '.wav'
            merge_audio(bgm_fn, piano_fn, mix_fn)


def dst_resource_run():
  src_path = SOURCE_DIR+'/*.xml'
  print(src_path)
  for TIME_ERROR in TIME_ERROR_list:
    bgm_vol = uniform(0, 0.5) # uniform(0, 0.5) # bgm 音量范围
    pno_vol = uniform(0.5, 1.0) # uniform(0.5, 1.0) # 钢琴音量范围
    dst_path = "bgm_resource_%s_%.2f_%.2f" % (TIME_ERROR, bgm_vol, pno_vol)
    if not os.path.isdir(dst_path):
        os.makedirs(dst_path)
    for fn in glob(src_path):
        m = converter.parse(fn)
        dir, file_name = os.path.split(fn)
        file, ext= os.path.splitext(file_name)

        midi_fn = dst_path+'/'+file+'.mid'
        m.write('midi', midi_fn)
        print('midi_fn: ', midi_fn)

        midi = MidiFile(midi_fn)
        for track in midi.tracks:
            for event in track:
                if event.type == 'program_change':
                    event.program = 0

        seq = Sequencer.from_midi(midi)
        time_error(seq, TIME_ERROR)

        midi = seq.render()

        midi.save(midi_fn)

        piano_fn = os.path.join(dst_path, '%s.wav'%file)
        print('piano_fn: ', piano_fn)
        cmd = f"fluidsynth -g2 -R0 -C0 -F {piano_fn} {SF2} {midi_fn}"
        subprocess.run(cmd, shell=True)

        # bgm_fn = SOURCE_DIR+'/'+file+'.mp3'
        # print('bgm_fn: ', bgm_fn)
        # mix_fn = dst_path+'/'+file+'_mix.wav'
        # merge_audio(bgm_fn, piano_fn, mix_fn, bgm_vol, pno_vol)


if __name__ == '__main__':
    print("start run")
    # new_run()
    dst_resource_run()
