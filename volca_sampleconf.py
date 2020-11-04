#!/usr/bin/env python3

import os
import subprocess
import argparse
import sys
import subprocess
import re

parser = argparse.ArgumentParser()
parser.set_defaults(speedupfactor=3, trimsilence=True, outdir='/tundra/other/misc/volca_sample/converted')
parser.add_argument('-i', '--input', type=str, help="Specifies the file name or folder to convert")
parser.add_argument('-o', '--outdir', type=str, help="Specifies the destination where the converted files will be copied to")
parser.add_argument('--lq', action='store_true', help="Transcodes all files to 22kHz and crushes bit depth to 8. If not using lq samples will still be crushed to 16 bit at 31250kHz, which is the volca sample limit.")
parser.add_argument('--samplepad', action='store_true', help="Adds additional padding to the sample.  This is to be used when splitting up the start offsets for working with long samples e.g. breaks, as volca sample will not address remaining 10 percent otherwise and the sample willl remain incomplete.")
parser.add_argument('--speedup', action='store_true', help="If this argument is passed, then sample will be pitched and sped by by the given factor.  Default is 3x.  This sample must then be sped up after loading the sample in playback rate on the volca.")
parser.add_argument('--speedupfactor', type=int, help="Specifies the factor by which the original audio file is sped up.  Faster will result in lower quality")
parser.add_argument('--notrimsilence', action='store_true', help="Prevents default activity of trimming silence from all samples at the beginning and end")
args = parser.parse_args()

# Process paths into something valid
args.outdir = os.path.realpath(args.outdir)
args.input = os.path.realpath(args.input)

# Initial checks
if not os.path.isfile(args.input) and not os.path.isdir(args.input):
    print('Invalid file or directory specified.  Press ENTER to continue and this script will exit')
    input()
    sys.exit()

if os.path.isdir(args.input):
    print('Directory passed. Switching to directory mode')
    directory_mode=True
else:
    directory_mode=False

# Make converted dir
if not os.path.isdir(args.outdir):
    try:
        os.mkdir(args.outdir)
    except:
        print('Could not make specified output directory {}'.format(args.outdir))
        sys.exit(1)

def sox_argbuild(target):
    sox_cmd = ['sox', target]
    if args.speedup:
        sox_cmd.append('speed'); sox_cmd.append(args.speedupfactor)
    if args.lq:
        sox_cmd.append('-b'); sox_cmd.append('8'); sox_cmd.append('-r'); sox_cmd.append('22050')
    else:
        sox_cmd.append('-b'); sox_cmd.append('16'); sox_cmd.append('-r'); sox_cmd.append('31250')

    # Specify output file
    sox_cmd.append(args.outdir + os.sep + os.path.basename(target))

    if args.samplepad:
        # Calls sox to get more file info
        cmd=['sox', target, '-n', 'stat']
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        # Gets the length of sample in seconds
        sample_length = re.findall(r"[0-9]{1}\.[0-9]{1,6}", out.split(':')[2])
        # Calculates amount of padding to add
        padding = float(sample_length[0]) * 0.1111111
        # Syntax for padding is pad x y, where x is pre-padding and y is post-padding
        sox_cmd.append('pad'); sox_cmd.append('0'), sox_cmd.append(padding)

    sox_cmd.append(['channels', '1'])

    return sox_cmd

def main():
    def remove_silence(target):
        # Preprocess files by removing silence. This is done before main sox call to prevent removing of intentional padding
        print('Removing silence at start and end of sample...')
        subprocess_list = ['sox', target, args.outdir + os.sep + os.path.basename(target), 'silence', '1', '0.1', '1%', 'reverse silence', '1', '0.1', '1%', 'reverse']
        print(" ".join(subprocess_list))
        subprocess.call(subprocess_list)

    if directory_mode:
        for root, dirs, files in os.walk(args.input):
            for file in files:
                target = root + os.sep + file
                remove_silence(target)
                sys.exit('Exiting after one loop (for testing purposes')
                # Build the subprocess list for the main call
                sox_cmd = sox_argbuild(target)
                print(sox_cmd)
                subprocess.call(sox_cmd)

    elif not directory_mode:
       target = args.input
       remove_silence(target)
       sox_cmd = sox_argbuild(target)
       print(sox_cmd)
       subprocess.call(sox_cmd)

if __name__ == '__main__':
    main()

