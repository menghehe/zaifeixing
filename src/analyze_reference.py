"""Read-only reference analysis. All outputs are confined to this delivery folder."""
from pathlib import Path
import subprocess, json, re, math, hashlib
import numpy as np
from scipy import signal
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(r'C:\Users\mengh\Documents\ChatGPT\素材\再飞行')
VIDEO=next(SOURCE.rglob('*.mp4'))
PYTHON=r'C:\Users\mengh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
for d in ['analysis/reference','analysis/audio','qa/reference','logs']:(ROOT/d).mkdir(parents=True,exist_ok=True)
def run(args):
    p=subprocess.run(args,capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode('utf-8','replace')[-4000:])
    return p.stdout
def save(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def probe(p):return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
save('analysis/reference-probe.json',probe(VIDEO))
save('analysis/song-probe.json',probe(ROOT/'assets/song.mp3'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
# Exact audio sample lengths and lag: same song, no time stretching.
audio=[]
for label,path in [('reference',VIDEO),('song',ROOT/'assets/song.mp3')]:
    raw=run(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','8000','-f','f32le','-'])
    a=np.frombuffer(raw,dtype='<f4').copy();audio.append(a)
    (ROOT/f'analysis/audio/{label}-8k.f32').write_bytes(raw)
fullraw=run(['ffmpeg','-v','error','-i',str(ROOT/'assets/song.mp3'),'-f','s16le','-acodec','pcm_s16le','-'])
duration=len(fullraw)/(44100*2*2)
a,b=audio
corr=signal.correlate(a,b,mode='full',method='fft'); lags=signal.correlation_lags(len(a),len(b),mode='full')
mask=np.abs(lags)<8000*2; peak=np.argmax(corr[mask]);lag=int(lags[mask][peak]);offset=lag/8000
local=[]
for st in [5,25,45,65,80]:
    aa=a[int((st+offset)*8000):int((st+offset+5)*8000)]
    bb=b[st*8000:(st+5)*8000]
    n=min(len(aa),len(bb)); local.append({'song_start':st,'correlation':float(np.corrcoef(aa[:n],bb[:n])[0,1])})
precise=[]
for st in [5,15,25,35,45,55,65,75,82]:
    template=b[int(st*8000):int((st+4)*8000)]
    left=int((st+offset-.035)*8000); segment=a[left:left+len(template)+560]
    scores=signal.correlate(segment,template,mode='valid',method='fft')
    k=int(np.argmax(scores)); value=float(np.corrcoef(segment[k:k+len(template)],template)[0,1])
    precise.append({'song_time':st,'offset_seconds':(left+k)/8000-st,'correlation':value})
save('analysis/audio-alignment.json',{'mapping':'reference_time = song_time + offset_seconds','offset_seconds':offset,'decoded_song_samples_per_channel':len(fullraw)//4,'decoded_song_duration':duration,'reference_decoded_duration_8k':len(a)/8000,'window_correlations':local,'precision_windows':precise,'speed_changed':False,'note':'Independent sample-precise FFT windows. No retiming of song.'})
# Two frames per second, labeled with their true sample positions.
raw=run(['ffmpeg','-v','error','-i',str(VIDEO),'-vf','fps=2,scale=384:216','-f','rawvideo','-pix_fmt','rgb24','-'])
frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,216,384,3)
for i,arr in enumerate(frames):
    Image.fromarray(arr).save(ROOT/f'analysis/reference/t{i/2:06.2f}.jpg',quality=91)
for pg in range(math.ceil(len(frames)/24)):
    subset=frames[pg*24:(pg+1)*24]; sheet=Image.new('RGB',(4*400,math.ceil(len(subset)/4)*248),'#101b2b');d=ImageDraw.Draw(sheet)
    for j,arr in enumerate(subset):
        x=j%4*400+8;y=j//4*248+6;sheet.paste(Image.fromarray(arr),(x,y));d.text((x+4,y+218),f'REF {(pg*24+j)/2:05.2f}s',fill='white',font=font)
    sheet.save(ROOT/f'qa/reference/page-{pg+1:02d}.jpg',quality=92)
# Decoded pixel scene scores at native frame rate, retaining all candidates, not claiming all as edits.
p=subprocess.run(['ffmpeg','-hide_banner','-i',str(VIDEO),'-an','-vf',"scale=320:180,select='gt(scene,0.20)',showinfo",'-f','null','-'],capture_output=True)
log=p.stderr.decode('utf-8','replace');(ROOT/'logs/reference-scene-detection.log').write_text(log,encoding='utf-8')
cut_times=[float(x) for x in re.findall(r'pts_time:([\d.]+)',log)]
save('analysis/cut-candidates.json',{'threshold':.20,'times':cut_times,'note':'Candidates include animation exposure changes, flashes, zooms. Human-reviewed grouping is stored separately.'})
# The sidecar contains danmaku, not a lyric track.
ass=(ROOT/'assets/reference.ass').read_text(encoding='utf-8-sig')
events=[]
def secs(s):
    h,m,ss=s.split(':');return int(h)*3600+int(m)*60+float(ss)
for ln in ass.splitlines():
    if ln.startswith('Dialogue:'):
        v=ln.split(':',1)[1].split(',',9)
        events.append({'start':secs(v[1]),'end':secs(v[2]),'style':v[3],'text':re.sub(r'\{.*?\}','',v[9])})
save('analysis/sidecar-danmaku.json',{'is_lyrics':False,'events':events})
print(json.dumps({'reference_seconds':probe(VIDEO)['format']['duration'],'song_decoded_seconds':duration,'offset_seconds':offset,'windows':local,'reference_frames':len(frames),'candidate_count':len(cut_times)},indent=2))
