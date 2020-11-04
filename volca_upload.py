#!/usr/bin/env python3

import os
import subprocess
import argparse
import sys
import subprocess
import re

player_string = 'mpv'
makesyro_path = os.path.expanduser('~') + 'bin' + os.sep + 'makesyro_gnulinux.sh'
parser = argparse.ArgumentParser()
parser.set_defaults()
parser.add_argument('-i', '--input', required=True, type=str, help="Specifies a folder containing all of the samples to upload.")
parser.add_argument('-o', '--output', type=str, help="Specifies a folder where to save all the converted samples.")
parser.add_argument('-p', '--playsamplesafter', type=str, help="After generating the samples then play back the audio file for upload to the volca")
parser.add_argument('-P', '--playonly', type=str, help="Do not generate samples but play from the input folder specified.")
args = parser.parse_args()

# Initial checks
if not os.path.isdir(args.input):
    print('Invalid file or directory specified.  Press ENTER to continue and this script will exit')
    input()
    sys.exit()

if args.playonly:
    if args.playsamplesafter or args.output:
        print('Specified options do not make sense.  If you are using play only mode, then just give an input folder only')

def validate_sample_number():
    # Check that no more than 100 samples
    for root, dirs, files in os.walk(args.input):
        if len(files) > 100:
            return False
        else:
            return True

def validate_sample_size():
    # Checks if the samples exceed the size of 4MB.
    tally = 0
    for root, dirs, files in os.walk(args.input):
        for file in files:
            tally = tally + os.path.getsize(root + file)
    if tally > 4096:
        return False
    else:
        return True

def get_sample_length(sample):
    # Determine sample length of 1 sample.
    output = subprocess.check_output(['ffprobe', sample], stderr=subprocess.STDOUT).decode()
    duration = output.split('Duration')[1].split(',')[0].replace(': ','')
    hours = duration.split(':')[0]
    minutes = duration.split(':')[1]
    seconds = duration.split(':')[2]

    return float(hours * 3600 + minutes * 60 + seconds)

def build_arg():
    pass

def generate_samples():
    counter = 0
    for root, dirs, files in os.walk(args.input):
        for file in files:
            counter = counter + 1
            print(counter, end=' ')
            target = root + os.sep + file
            subprocess.call([makesyro_path, '-d', '-n', counter, '-o', counter + '.wav'])
    print()

def play_samples():
    print('This will play the .wav.  Please ensure the volca is in a mode to receive audio input via sync in.')
    print('Press ENTER to start.')
    #subprocess.call('')

def main():

    state = validate_sample_number()
    if not state:
        sys.exit('The samples exceed the maximum of 100 in number.  Please remove some.')

    state = validate_sample_size()
    if not state:
        sys.exit('The samples exceed the maximum size of 4MB.  Please remove some or modify some to fit.')

    # Iterate through samples
    length_count=0 # Counts up the cumulative audio file lengths in seconds
    for root, files, dirs in os.walk(args.input):
        for file in files:
            target = root + os.sep + files
            sample_length = get_sample_length(target)
            length_cum = float(length_count) + float(sample_length)
    if length_cum > 65:
        sys.exit('Cumulative length of samples exceeded.  These have {} seconds of audio, whereas the maximum limit is 65.'.format(length_cum))

    # Now safe to generate volca compatible audio file for upload
    # This uses the tooling provided by the official Korg Volca Sample
    if not args.playonly():
        generate_samples()

    # Now upload by playing using audio folder
    if args.playafter:
        play_samples()

if __name__ == '__main__':
    main()

