"""Inspect the circular UI in local recordings; never sends game input."""
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from circular import CircularReader,CircularCommand,KeyPromptCommand


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('videos',nargs='+',type=Path)
    parser.add_argument('--interval',type=float,default=.5)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.interval<=0:parser.error('Interval must be positive')
    try:import imageio_ffmpeg
    except ImportError:parser.error('Install the developer-only imageio-ffmpeg package to decode local videos')
    report=[]
    for number,path in enumerate(args.videos,1):
        frames=imageio_ffmpeg.read_frames(str(path),output_params=['-vf',f'fps={1/args.interval}'])
        metadata=next(frames)
        width,height=metadata['size']
        reader=CircularReader(ROOT/'src/assets');command=CircularCommand();key_command=KeyPromptCommand();rows=[]
        seconds=0.
        try:
            for data in frames:
                rgb=np.frombuffer(data,np.uint8).reshape(height,width,3)
                start=time.perf_counter()
                reading=reader.read(rgb)
                rows.append({'seconds':round(seconds,3),'visible':reading is not None,
                             'hold_instruction':reading.hold if reading else None,
                             'complete':reading.complete if reading else False,
                             'key':reading.key if reading else None,
                             'presses':reading.presses if reading else 0,
                             'proposed_key_taps':key_command.step(reading,seconds),
                             'proposed_mouse_down':command.step(reading,seconds),
                             'analysis_ms':round((time.perf_counter()-start)*1000,2)})
                seconds+=args.interval
        finally:frames.close()
        report.append({'clip':number,'frames':rows})
        print(f'Clip {number}: {len(rows)} sampled frames')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')


if __name__=='__main__':main()
