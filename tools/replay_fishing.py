"""Replay a recorded fishing flow without sending mouse/keyboard input.

Water coordinates are normalized (0..1). Reports contain no recording paths or
images. A recorded player's actions are fixed; replay cannot prove that the
proposed inputs would have won a live round.
"""
import argparse,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from circular import CircularReader
from circular_engine import CircularEngine
from splash import SplashReader
from claim import ClaimReader


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('videos',nargs='+',type=Path)
    parser.add_argument('--water',type=float,nargs=2,default=(.59,.30))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--interval',type=float,default=.1)
    args=parser.parse_args()
    if args.interval<=0 or not all(0<v<1 for v in args.water):parser.error('Invalid interval or water point')
    import imageio_ffmpeg
    report=[]
    for number,path in enumerate(args.videos,1):
        reader=CircularReader(ROOT/'src/assets');splash=SplashReader();claim=ClaimReader(ROOT/'src/assets')
        cfg={'cast':args.water,'max_cast':3,'cast_hold':.25,'wait_seconds':20.,'result_wait':2.,
             'max_collect':5,'t_hold':3.,'collect_timeout':35.,'recast_seconds':1.5,'auto_calibrate':True}
        engine=CircularEngine(cfg);engine.state='ESPERANDO';engine.deadline=20.;engine.splash_armed_at=0.
        frames=imageio_ffmpeg.read_frames(str(path),output_params=['-vf',f'fps={1/args.interval}'])
        meta=next(frames);w,h=meta['size'];rows=[]
        try:
            for index,data in enumerate(frames):
                now=index*args.interval;image=np.frombuffer(data,np.uint8).reshape(h,w,3)
                started=time.perf_counter();reading=reader.read(image)
                bite=splash.observe(image,args.water,now,engine.state=='ESPERANDO')
                found=claim.scan(image) if reading is None or reading.complete else None
                before=engine.state
                actions=engine.step(now,reading,loot=found['point'] if found else None,splash=bite,
                                    impact_activity=splash.stats.get('signal_active',False))
                rows.append({'seconds':round(now,3),'state':engine.state,'changed':before!=engine.state,
                             'circle':reading is not None,'completed_circle':bool(reading and reading.complete),
                             'key':reading.key if reading else None,'presses':reading.presses if reading else 0,
                             'splash':bite,'claim':found is not None,'actions':actions,
                             'analysis_ms':round((time.perf_counter()-started)*1000,2)})
        finally:frames.close()
        report.append({'clip':number,'resolution':[w,h],'cycles':engine.cycles,'collected':engine.collected,'frames':rows})
        print(f'Clip {number}: {len(rows)} frames, {engine.cycles} cycles, {engine.collected} collections',flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')


if __name__=='__main__':main()
