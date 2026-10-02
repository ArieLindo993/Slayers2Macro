"""Read local recorded frames through the production detectors without input.

Example: python tools/replay_video.py recording.mp4 --client 0 0 800 599
         --seconds 10 25 49 --output test-results/replay.json
The report contains no source path or captured image; recordings stay local.
"""
import argparse
import json
from pathlib import Path
import sys
import time

import cv2

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from calibration import locate_bar
from detector import detect
from item_history import RewardReader
from signals import Signals


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video',type=Path)
    parser.add_argument('--client',nargs=4,type=int,metavar=('X','Y','W','H'),required=True)
    parser.add_argument('--seconds',nargs='+',type=float,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    cap=cv2.VideoCapture(str(args.video))
    if not cap.isOpened():parser.error('Cannot open the local video')
    x,y,w,h=args.client
    if min(x,y)<0 or min(w,h)<=0:parser.error('Invalid client rectangle')
    signals=Signals(ROOT/'src/assets');reader=RewardReader();rows=[]
    try:
        for seconds in args.seconds:
            cap.set(cv2.CAP_PROP_POS_MSEC,seconds*1000);ok,frame=cap.read()
            if not ok:parser.error('Requested time is outside the recording')
            if x+w>frame.shape[1] or y+h>frame.shape[0]:parser.error('Client extends outside video')
            rgb=frame[y:y+h,x:x+w,::-1].copy();scene=signals.scan(rgb)
            candidate=locate_bar(rgb) if scene['fishing'] else None
            reading=None
            if candidate:
                a,b,c,d=[int(v*s) for v,s in zip(candidate['roi'],(w,h,w,h))]
                reading=detect(rgb[b:b+d,a:a+c])
            start=time.monotonic()
            crop=scene['reward_crop']
            if crop is None:crop=scene['reward_crop_candidate']
            if crop is None:crop=RewardReader.crop(rgb)
            payload=reader.read_with_diagnostics(crop,RewardReader.fallback_crop(rgb))
            row={'seconds':seconds,'client_size':[w,h],'fishing':scene['fishing'],
                 'collect_prompt':bool(scene['loot']),'calibration':candidate,
                 'bar':vars(reading) if reading else None,'reward':payload['reading'],
                 'ocr_seconds':round(time.monotonic()-start,3),'ocr':payload['__ocr_debug__']}
            rows.append(row);print(json.dumps(row,ensure_ascii=True),flush=True)
    finally:cap.release()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
