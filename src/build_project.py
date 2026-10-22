from pathlib import Path
import json,re,csv,math
ROOT=Path(__file__).resolve().parents[1]
# Editorial groups, reviewed against 183 half-second reference frames and native subtitle crops.
# REF seconds | scene | shot/acting | cast | observed reference function | original adaptation
DATA='''0|galaxy|vista|none|宇宙星云与旋涡星系大景|红蓝颜料星云铺开，微小航标唤醒星海
3|planets|vista|none|镜头纵深推进到多行星系统|环形星门将观众送入多行星航道
5.7|planet|vista|none|蓝绿行星成为画面中心|旋转蓝绿行星与远处飞船建立目的地
8.45|sky|run|boy|奔跑脚步特写，尘土飞起|红衣少年在发光轨道上加速奔跑
9.7|sky|wrist|boy|手臂和腕部饰物的运动插入|盘扣与红色腕星特写随步伐前甩
10.4|sky|portrait|boy|少年奔跑侧脸，目光向前|棕发侧脸转向驶离的星帆船
11.85|sky|reach|boy|抬手呼喊追逐风筝|少年伸手追向飞船留下的彗尾
12.6|sky|shipwide|both|小人物与高空风筝的大尺度关系|飞船起航；少女在船头，少年在远处追赶
14.85|sky|title|both|蓝天风筝长镜头叠入片名|《再飞行》手写片名在星帆航迹上展开
23.1|mirror|portrait|boy|闪白后低头少年正面，面部在阴影中|低头的少年被绿色星门光托起
25.933|mirror|mirrors|boy|少年面对镜中自己的侧面|六面镜映出孤独少年，蓝色信号藏在镜后
26.85|mirror|back|boy|背影与两侧镜像|背面红衣被镜中蓝色倒影包围
27.767|mirror|overhead|boy|俯视六边形镜室|镜头升高，六面镜围成星门囚笼
29.25|nebula|comet|none|绿色星空中的单颗流星|蓝色信标像彗星一样划过少年视线
30.567|mirror|wrist|boy|腕环与倒影的交错构图|腕星回应蓝色信号，反光中看见少女
32.6|mirror|hand|boy|手掌靠近光滑镜面|少年张开手指，试着触到镜后的人
33.933|mirror|touch|both|手指触镜，裂纹开始传播|红蓝两只手隔着星晶相对，裂纹连成星座
34.967|mirror|shatter|boy|镜面碎片落下，人物仰视|镜室破开，少女的身影碎成星尘
36.167|mirror|portrait|boy|少年仰望碎片的脸部近景|少年望向消散的蓝光，神情由惊讶变坚定
36.883|mirror|overhead|boy|顶视镜室倾斜旋转|六面晶墙从上方向外崩解
38.2|mirror|fall|boy|镜室失衡，人物失去立足点|失重将少年与碎片抛进紫色宇宙
39.283|battle|defend|boy|双臂遮住脸部抵御碎片|少年交叉护臂穿过迎面碎星
39.883|battle|shatter|boy|破碎白片占满画面，紫色空间显现|晶体星门爆碎，红蓝光从缝隙穿出
41.083|battle|fall|boy|小人物坠入紫色深场|少年从宇宙大景中坠向引力井
41.483|battle|silhouettes|boy|强大暗影和陌生人物围住少年|抽象装甲剪影遮住少女的信号
42.65|battle|overhead|boy|环绕人物的辐射状构图|少年置身星形力场中心，敌影围成一圈
43.967|vortex|vortex|boy|黑色卷曲形状吞没人物|黑洞的墨色旋臂吞没航道
44.85|vortex|fall|boy|人物在黑暗旋涡中翻滚|少年逆着旋涡翻身，红围巾指向出口
45.717|vortex|portrait|boy|旋涡中露出坚定的面部|眼神特写；恐惧转为咬牙前进
46.65|vortex|reach|boy|朝镜头伸手但被黑暗淹没|伸向蓝光的手被黑洞阴影拉开
48.317|void|wrist|boy|手掌和腕环特写|红宝石腕星映出微弱的少女信号
49|void|fist|boy|握拳反抗，身体蓄力|手指收紧成拳，少年扭腰蓄力
49.65|void|punch|boy|出拳击出蓝色裂纹|红拳打破引力壁，青蓝裂缝横贯画面
51.6|void|tiny|boy|巨手离去，人物缩回黑暗远景|能量耗尽，少年独自坠入无边深空
53.2|void|orbit|none|上下对称能量形状与水平光线|红蓝信号在黑暗两端沿同一轨道自转
54.45|void|fall|boy|失重侧身翻滚|镜头跟随失重的少年由远推近
55.8|void|reach|boy|人物伸展手脚，求援动作|他在坠落中伸向少女曾经出现的方向
57|void|hand|boy|手腕近景，手掌向上展开|腕星附近掠过一粒金色星尘
58.1|void|spark|boy|光点落在手上并映亮腕环|金色光点落在掌心，重新点亮约定
59.967|void|comet|none|金色光束在黑暗中移动|光点化为彗星，沿黑洞边缘寻找出口
61.8|void|portrait|boy|少年抬眼看见金光|少年抬眼，瞳孔里的微光逐渐放大
62.683|starburst|explosion|both|强光与碎片构成纵深爆发|星门被红蓝合力击穿，光束与碎片冲向镜头
63.767|starburst|eyes|boy|被光照亮的惊讶眼部特写|少年眼中的金色星点变成少女的倒影
65.167|starburst|memory|girl|逆光中的成年引路者伸出手|蓝发少女从逆光星门中出现并伸手
67.367|nebula|hand|girl|伸出的手与手指动作插入|少女翻转手掌，示意一起出发
68.6|nebula|approach|both|少年向伸出的手游去|少年与少女在失重中相向冲刺
69.65|starburst|join|both|两只拳头接触，金色粒子爆散|两人碰拳回应，红蓝星环从接触点爆开
70.4|starburst|beam|both|金色闪光承接下一段动作|并肩起跳，能量沿飞行方向拉成长线
71.2|vortex|mast|none|风筝骨架与黑色包围物|飞船星帆展开，切开黑洞旋臂
72.083|vortex|defend|boy|人物用力挣脱包围|少年交叉护臂冲开最后的引力束缚
73.283|vortex|shatter|both|黑色碎片撕裂，白色天空出现|黑洞外壳爆碎，彩虹海在裂缝后展开
74.6|sky|breakout|both|碎片转为亮天空中的风筝与人物|两人从白光星门跃入彩虹星海
75.25|sky|flightwide|both|小人物由风筝牵引向高空飞升|星帆船带着红蓝双轨迹在宇宙中升起
76.45|sky|feet|boy|低角度腿脚与飞行牵引|镜头从少年脚底仰拍加速飞行
77.167|sky|flight|boy|少年抓着线飞行，四肢大幅展开|少年前扑追上飞船，围巾被气流拉长
78.2|sky|dive|boy|身体从飞升转为俯冲|少年转身俯冲，镜头沿弧线跟随
79.8|sky|ship|none|黄红飞船驶近|金色船身从小点推近，青蓝帆面翻起
80.65|sky|approach|both|飞船与少年形成迎接关系|少女在船头接应，少年伸手跳向甲板
81.8|sky|flight|boy|逆着太阳的大幅飞行动作|少年从光环前掠过，红色身影完成最后冲刺
83.05|sky|eyes|boy|眼睛倒映飞船，动作细节特写|眼中倒映星帆，确认已经追上
83.65|deck|land|both|落上甲板，伙伴反应|落地缓冲后抬头，两人在甲板重逢
84.717|deck|portrait|girl|蓝发少女近景，头发随风飘动|蓝发少女回头微笑，发丝与围巾向后飘起
86.45|sky|ship|none|飞船正面特写后切回少年|飞船穿过最后一道星门，航向彩虹海
87.117|deck|portrait|boy|少年抬头的正面近景|少年抬眼与少女相望，神情平静而坚定
88.567|sky|final|both|手指指向蓝天中的风筝，开放式结尾|两人指向远方；星帆、彗星与彩虹星河继续前行'''

def main():
    old=(ROOT/'src/music-data.js').read_text(encoding='utf-8')
    music=json.loads(old.split('=',1)[1].strip().rstrip(';'))
    alignment=json.loads((ROOT/'analysis/audio-alignment.json').read_text(encoding='utf-8'))
    offset=alignment['offset_seconds'];duration=alignment['decoded_song_duration']
    # Phrases are retained from the supplied LRC/onset analysis, not claimed as forced alignment.
    music['duration']=duration
    (ROOT/'src/music-data.js').write_text('window.MUSIC='+json.dumps(music,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    rows=[]
    trans={'vista':'zoom','run':'cut','wrist':'cut','portrait':'cut','reach':'comet','shipwide':'iris','title':'cut','mirrors':'cut','back':'cut','overhead':'spin','comet':'comet','hand':'cut','touch':'iris','shatter':'flash','fall':'cut','defend':'whip','silhouettes':'cut','vortex':'spin','fist':'cut','punch':'shock','tiny':'cut','orbit':'iris','spark':'cut','explosion':'flash','eyes':'cut','memory':'star','approach':'zoom','join':'shock','beam':'whip','mast':'cut','breakout':'flash','flightwide':'zoom','feet':'cut','flight':'comet','dive':'spin','ship':'iris','land':'shock','final':'iris'}
    camera={'vista':'缓推 / 多层视差','portrait':'面部近景 / 轻推','wrist':'手腕局部特写','hand':'手掌特写','eyes':'眼睛特写','overhead':'俯视 / 缓旋','tiny':'急拉远','fall':'跟随翻滚 / 变焦','flight':'跟拍 / 斜向推进','ship':'由远及近','title':'长镜头 / 缓移','final':'慢拉远 / 开放结尾'}
    for i,line in enumerate(DATA.splitlines()):
        rt,theme,view,cast,obs,story=line.split('|');rt=float(rt);st=max(0,rt-offset)
        rows.append({'id':i+1,'ref_start':rt,'start':round(st*24)/24 if i else 0,'theme':theme,'view':view,'cast':cast,'reference':obs,'story':story,'camera':camera.get(view,'中近景切换 / 动作跟随'),'transition':trans[view],'timestamp_confidence':'候选切点 + 人工0.5秒网格复核；镜头分组非逐帧剪辑EDL'})
    for i,s in enumerate(rows):
        s['end']=rows[i+1]['start'] if i+1<len(rows) else duration
        s['ref_end']=rows[i+1]['ref_start'] if i+1<len(rows) else 91.399
        l=next((l for l in music['lyrics'] if l['start']<=((s['start']+s['end'])/2)<l['end']),None)
        s['lyric']=l['text'] if l else '器乐 / 余韵'
        s['heat']=1 if s['start']>=51.5 and s['start']<79.0 else .35
    (ROOT/'src/timeline.js').write_text('window.SHOTS='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    for name in ['analysis/reference-shotlist.json','analysis/shotlist.json']:(ROOT/name).write_text(json.dumps({'shots':rows,'count':len(rows),'audio_offset':offset,'note':'65个语义镜头组；不将257个画面差异候选都当成剪辑。'},ensure_ascii=False,indent=2),encoding='utf-8')
    with (ROOT/'analysis/shotlist.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    def fmt(t):return f'{int(t)//60:02d}:{t%60:06.3f}'
    md=['# 《再飞行》参考重绘分镜','',f'全曲 {duration:.6f} 秒；1920×1080 / 24 fps；{len(rows)} 个语义镜头组。参考时间映射为歌曲时间 = 参考时间 − {offset:.6f}s，切点量化至24fps。', '', '表中“参考观察”和“本版重绘”分别记录实际参考画面与原创改编。参考的引路者伸手改为蓝发少女回应；宇宙追逐、星门与彩虹海由代码重新绘制。时间精度为候选切点结合0.5秒采样复核，非原工程逐帧EDL。','', '|镜头|歌曲时间|参考时间|参考观察|本版重绘 / 动作|镜头运动|进入转场|歌词|','|---|---|---|---|---|---|---|---|']
    for s in rows:md.append(f"|{s['id']:02d}|{fmt(s['start'])}–{fmt(s['end'])}|{fmt(s['ref_start'])}–{fmt(s['ref_end'])}|{s['reference']}|{s['story']}|{s['camera']}|{s['transition']}|{s['lyric']}|")
    md+=['','## 字幕与节奏','', '逐句时间取自提供的本地 LRC；短语时间沿用本地起音估计，属于估计，不宣称逐字强制对齐。画面内短语以 5–7 帧弹入，关键词放大；提供完整句级 SRT 旁挂字幕。主体脸部预留独立空间，字幕在左上、右上、侧中部切换，不采用固定底条。', '', '副歌高潮样片统一取歌曲 60.000–75.000 秒，以覆盖光点、爆发、逆光回应、碰拳和冲出星门。']
    (ROOT/'STORYBOARD.md').write_text('\n'.join(md),encoding='utf-8')
    def srt(t):
        ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    (ROOT/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{srt(l["start"])} --> {srt(l["end"])}\n{l["text"]}' for i,l in enumerate(music['lyrics']))+'\n',encoding='utf-8')
    design='''# 角色与场景设计

棕发红衣少年：保留蓬松尖发、红色中式立领、金色盘扣和红色腕星。比例调整为约4.5头身，深红阴影、米金勾线；用肩、肘、腕、胯、膝、踝连接的骨架实现跑、跃、护臂、握拳与失重翻滚。

蓝发少女：保留长蓝发、蓝白服装、青绿色额饰与蓝围巾；背发在肩后分层，发梢与围巾以连续曲线随速度摆动。与少年用冷暖光区分，只有在重逢和并肩飞行时合为红蓝双轨迹。

角色在太空漂浮阶段不画地面、山丘或植物。全片空间分为远景星云/行星、中景晶体/星门/星帆船、近景碎片/星尘；近景速度为远景的数倍。画面以深靛、墨绿与紫灰为基底，米白线与红蓝金光形成高潮。

场景组：宇宙星河、多行星航道、蓝绿行星、星帆出航、六面镜室、晶体碎裂、紫色围困、墨色黑洞、深空失重、掌心光点、星门爆发、逆光重逢、彩虹海、船头甲板。

星帆船由曲面金红船体、三角白青帆、金色桅杆、蓝光舷窗和尾焰构成。代码绘制，不使用参考帧或封面。黑洞采用旋转的墨色不规则臂；星云为半透明多层曲线、颗粒和冷暖色块。字幕使用本地字体，其余视觉全部为 Canvas 路径、渐变与程序纹理。

镜头语言：起航的缓推 → 镜室的近景/俯视 → 黑洞的旋转/骤拉远 → 失重段的留白 → 掌心光点的极近景 → 强光空间大景 → 重逢的对切 → 飞行跟拍 → 甲板回望与远方星海。手、眼、腕星插入镜头承担动作因果关系。
'''
    (ROOT/'assets/DESIGN.md').write_text(design,encoding='utf-8')
    print(json.dumps({'shots':len(rows),'duration':duration,'offset':offset,'sample_range':[60,75]}))
if __name__=='__main__':main()
