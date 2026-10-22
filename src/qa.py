"""Encoded-media QA, original audio identity and shot/transition frame evidence."""
from pathlib import Path
import argparse, json, subprocess, math, re, hashlib, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
SMALL = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 14)

def call(args, log=None):
    p = subprocess.run(args, capture_output=True)
    if log: (ROOT/log).write_bytes(p.stderr)
    if p.returncode: raise RuntimeError(p.stderr.decode('utf-8', 'replace')[-5000:])
    return p.stdout, p.stderr.decode('utf-8', 'replace')

def save(path, value):
    (ROOT/path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def tile_frames(items, outfile, cols=4, width=480):
    height=round(width*9/16); rowh=height+34
    out=Image.new('RGB', (cols*width, math.ceil(len(items)/cols)*rowh), '#101a2b')
    d=ImageDraw.Draw(out)
    for i,(path,label) in enumerate(items):
        x=i%cols*width; y=i//cols*rowh
        with Image.open(path) as im: out.paste(im.resize((width,height),Image.Resampling.LANCZOS),(x,y))
        d.text((x+8,y+height+4),label,font=FONT if width>=320 else SMALL,fill='#f2ddbb')
    out.save(outfile,quality=94)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--mode',choices=['sample','full'],default='sample');args=parser.parse_args()
    mode=args.mode; sample=mode=='sample'; offset=60 if sample else 0
    video=ROOT/('qa/sample-15s.mp4' if sample else 'final.mp4')
    q=ROOT/'qa'/mode; q.mkdir(exist_ok=True)
    raw,_=call(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)])
    probe=json.loads(raw); save(f'analysis/{mode}-probe.json',probe)
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    a=next(s for s in probe['streams'] if s['codec_type']=='audio')
    _,black=call(['ffmpeg','-hide_banner','-i',str(video),'-an','-vf','blackdetect=d=0.04:pix_th=0.08','-f','null','-'],f'logs/{mode}-blackdetect.log')
    _,freeze=call(['ffmpeg','-hide_banner','-i',str(video),'-an','-vf','freezedetect=n=-50dB:d=1','-f','null','-'],f'logs/{mode}-freezedetect.log')
    blacks=re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',black)
    freezes=re.findall(r'lavfi\.freezedetect\.freeze_(?:start|end|duration): [\d.]+',freeze)
    shots=json.loads((ROOT/'analysis/shotlist.json').read_text(encoding='utf-8'))['shots']
    selected=[s for s in shots if s['end']>offset and (not sample or s['start']<75)]
    count=int(v['nb_frames']); reps=[]; trans=[]
    for s in selected:
        st=max(offset,s['start']); en=min(75,s['end']) if sample else s['end']
        frame=min(count-1,max(0,math.floor(((st+en)/2-offset)*24)))
        reps.append({'shot':s['id'],'frame':frame,'song_time':offset+frame/24,'view':s['view']})
    for s in selected:
        if s['start']<=offset: continue
        boundary=round((s['start']-offset)*24)
        indices=list(range(max(0,boundary-3),min(count,boundary+9)))
        trans.append({'shot':s['id'],'boundary_frame':boundary,'song_time':s['start'],'transition':s['transition'],'frames':indices})
    wanted={0,count-1}|{s['frame'] for s in reps}
    for t in trans: wanted.update(t['frames'])
    wanted=sorted(wanted)
    terms=[f'eq(n,{r["frame"]})' for r in reps]+[f'between(n,{t["frames"][0]},{t["frames"][-1]})' for t in trans]+[f'eq(n,0)',f'eq(n,{count-1})']
    # A balanced tree avoids FFmpeg's expression recursion limit on 65-shot selections.
    def combine(xs):
        if len(xs)==1:return xs[0]
        mid=len(xs)//2
        return '('+combine(xs[:mid])+'+'+combine(xs[mid:])+')'
    expr=combine(terms)
    decoded=q/'decoded'; decoded.mkdir(exist_ok=True)
    call(['ffmpeg','-y','-hide_banner','-i',str(video),'-an','-vf',f"select='{expr}'",'-fps_mode','vfr','-q:v','2',str(decoded/'d%05d.jpg')],f'logs/{mode}-extract.log')
    mapping={frame:decoded/f'd{i+1:05d}.jpg' for i,frame in enumerate(wanted)}
    assert len(list(decoded.glob('d*.jpg')))==len(wanted), 'Decoded selection count mismatch'
    repdir=q/'shots'; repdir.mkdir(exist_ok=True)
    for r in reps:
        dest=repdir/f'shot-{r["shot"]:02d}.jpg'; shutil.copyfile(mapping[r['frame']],dest);r['file']=str(dest.relative_to(ROOT))
    for pg in range(math.ceil(len(reps)/12)):
        subset=reps[pg*12:(pg+1)*12]
        tile_frames([(ROOT/r['file'],f'SHOT {r["shot"]:02d} | {r["song_time"]:.3f}s | {r["view"]}') for r in subset],q/f'shots-page-{pg+1:02d}.jpg',3,640)
    tdir=q/'transitions'; tdir.mkdir(exist_ok=True)
    for t in trans:
        folder=tdir/f'to-{t["shot"]:02d}';folder.mkdir(exist_ok=True)
        items=[]
        for k,frame in enumerate(t['frames']):
            dest=folder/f'f{frame:05d}.jpg';shutil.copyfile(mapping[frame],dest)
            items.append((dest,f'{offset+frame/24:.3f}s  frame {frame}'))
        tile_frames(items,tdir/f'to-{t["shot"]:02d}.jpg',4,480)
    # All 12 consecutive frames per transition, eight transitions per overview.
    for pg in range(math.ceil(len(trans)/8)):
        subset=trans[pg*8:(pg+1)*8]; board=Image.new('RGB',(1920,len(subset)*126),'#101a2b');d=ImageDraw.Draw(board)
        for row,t in enumerate(subset):
            d.text((8,row*126+3),f'TO {t["shot"]:02d} | {t["song_time"]:.3f}s | {t["transition"]}',font=FONT,fill='#f2ddbb')
            for col,frame in enumerate(t['frames']):
                with Image.open(mapping[frame]) as im: board.paste(im.resize((160,90),Image.Resampling.LANCZOS),(col*160,row*126+28))
        board.save(q/f'transitions-page-{pg+1:02d}.jpg',quality=94)
    tile_frames([(mapping[0],f'FIRST / {offset:.3f}s'),(mapping[count-1],f'LAST / {offset+(count-1)/24:.3f}s')],q/'endpoints.jpg',2,960)
    checks={'resolution':v['width']==1920 and v['height']==1080,'fps':v['r_frame_rate']=='24/1' and v['avg_frame_rate']=='24/1','codec':v['codec_name']=='h264','audio':a['codec_name']=='aac' and a['sample_rate']=='44100' and a['channels']==2,'frames':count==(360 if sample else 2185),'end_difference_under_one_frame':abs(float(v['duration'])-float(a['duration']))<1/24,'blackdetect_clear':not blacks,'freezedetect_clear':not freezes}
    audio_check={}
    if not sample:
        src=ROOT/'assets/song.mp3'; origin=ROOT.parent/'zaifeixing/assets/song.mp3'
        decoded_audio,_=call(['ffmpeg','-v','error','-i',str(video),'-vn','-ac','2','-ar','44100','-f','f32le','-'])
        source_audio,_=call(['ffmpeg','-v','error','-i',str(src),'-ac','2','-ar','44100','-f','f32le','-'])
        source=np.frombuffer(source_audio,dtype='<f4').reshape(-1,2); delivery=np.frombuffer(decoded_audio,dtype='<f4').reshape(-1,2)
        audio_check={'source_sha256':sha(src),'original_sha256':sha(origin),'source_samples':len(source),'delivery_decoded_samples_including_AAC_padding':len(delivery),'windows':[]}
        for start in [0,20,40,60,85,90]:
            n=min(44100*4,len(source)-start*44100);aa=source[start*44100:start*44100+n].mean(axis=1);bb=delivery[start*44100:start*44100+n].mean(axis=1)
            audio_check['windows'].append({'start':start,'seconds':n/44100,'correlation_at_zero_lag':float(np.corrcoef(aa,bb)[0,1])})
        checks['original_audio_identical']=audio_check['source_sha256']==audio_check['original_sha256']
        checks['entire_audio_duration']=abs(float(a['duration'])-len(source)/44100)<1/44100*2
        checks['audio_alignment']=min(w['correlation_at_zero_lag'] for w in audio_check['windows'])>.98
    result={'mode':mode,'video':str(video),'checks':checks,'technical_pass':all(checks.values()),'video_seconds':float(v['duration']),'audio_seconds':float(a['duration']),'end_difference_ms':abs(float(v['duration'])-float(a['duration']))*1000,'black_events':blacks,'freeze_events':freezes,'representative_count':len(reps),'transition_count':len(trans),'consecutive_frames_per_transition':12,'extracted_unique_frames':len(wanted),'audio_identity':audio_check,'visual_review':'Contact sheets exported; human/model visual review documented separately.'}
    save(f'qa/{mode}/results.json',result);save(f'qa/{mode}/frame-manifest.json',{'representatives':reps,'transitions':trans})
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
