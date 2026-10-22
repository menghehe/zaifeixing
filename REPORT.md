# 《再飞行》完整代码动画 MV · 交付报告

日期：2026-10-21。制作与所有新增文件均位于 `mv/zaifeixing-reference/`；未使用子agent。

## 交付结果

`final.mp4` 已完成。以棕发红衣少年、蓝发蓝白衣少女为原创主角，重建宇宙开场、星帆起航、镜室分离、黑洞围困、掌心微光、逆光回应、碰拳、飞行突破与甲板重逢。采用65个参考语义镜头组、17句歌词和48个动态短语事件。

先完成参考分析、分镜、角色场景设计，渲染歌曲60–75秒的15秒样片。修正手部接触与星帆遮挡后重新渲染、复检，再进行完整成片渲染。样片检查是内部验收，不冒充用户已经审片。

可双击 `review.html` 播放完整视频和样片。画面内已包含动态歌词；`subtitles.srt` 是另外提供的17句外挂字幕，不需要加载它才能看到歌词。

## 实测媒体参数

|项目|实测值|
|---|---|
|分辨率|1920×1080，方形像素，16:9|
|帧率|恒定24/1 fps|
|帧数|2185|
|视频编码|H.264 High，yuv420p，MP4，faststart|
|视频时长|91.041667秒|
|音频编码|AAC LC，44100 Hz，stereo，约256 kb/s|
|音频时长|91.022222秒|
|音画末端差|19.445毫秒，小于24fps的一帧41.667毫秒|
|起始时间|视频0.000000秒；音频0.000000秒|
|成片大小|87,350,674字节，约83.30 MiB|

本地歌曲从0秒开始使用，未截断、变速、循环或人为补尾。原始歌曲与 assets/song.mp3 的SHA-256一致；原曲和AAC成片各解码出每声道4,014,080个采样。源MP3仍原样保留，成片按交付规格转为AAC，因此不把AAC编码后的字节误称为无损原文件。

六个零延迟音频比较窗起于0、20、40、60、85、90秒，相关系数最低0.998924，最后一个覆盖90秒至歌曲结束。帧数向上取整产生约19.45毫秒的画面余量，没有裁掉歌曲末尾。

## 验收

|检查|结果|证据|
|---|---|---|
|ffprobe媒体规格|通过|analysis/full-probe.json|
|blackdetect|无报告黑场；d=0.04，pix_th=0.08|logs/full-blackdetect.log|
|freezedetect|无报告冻结；n=-50dB，d=1|logs/full-freezedetect.log|
|原曲身份、完整长度和对齐|通过|qa/full/results.json|
|65个镜头代表帧|全部已提取并查看联系表|qa/full/shots/，shots-page-01至06.jpg|
|64处转场连续帧|每处12帧；全部总览已查看，关键段放大检查|qa/full/transitions/，transitions-page-01至08.jpg|
|帧证据总数|822个不重复的编码后解码帧|qa/full/frame-manifest.json|
|字幕文本与触发序列|17句、48短语，结构检查通过|qa/subtitle-results.json；analysis/subtitle-cues.csv|
|15秒样片|360帧，音画均15秒，无黑帧/冻结|qa/sample-15s.mp4；qa/SAMPLE_REVIEW.md|

详细视觉记录见 `qa/VISUAL_REVIEW.md`；可浏览 `qa/full/index.html` 查看镜头和转场。验收覆盖联系表、连续帧和重点原尺寸画面，不声称人工检查了每个像素。

## 参考分析与改编范围

实际参考文件位于用户所给同名目录内，真实参数为91.399秒、1920×1080、约60fps、H.264/AAC。参考没有内嵌字幕轨；画面烧录中英歌词。旁挂ASS是50条弹幕，不是歌词字幕。

歌曲与参考的精确音频关系为：参考时间=歌曲时间+1.1305秒。65组切点换算后量化至24fps。参考场景是宇宙、奔跑与风筝、镜室、围困、引路者、天空突破与飞船；本版将引路者功能改为少女回应，将风筝关系改为星帆，将天空扩展为彩虹星海。实际观察与原创改编在分镜表中分列。

抽取的原片画面只存于分析和参考验收目录。制作页面没有加载原片帧、封面或外部图片；角色、船、行星、星门、旋臂、星尘、碎片、字幕贴纸均由Canvas代码绘制。字体和歌曲使用本地资产。

## 源码与复现

工具链：项目现有Node.js、puppeteer-core、无头Chrome、Canvas2D与FFmpeg。Canvas直接勾线、平涂、渐变、颗粒、骨架姿态与时间函数生成画面；本次没有调用p5.brush，不把现有依赖的存在写成实际使用。

|文件|作用|
|---|---|
|src/analyze_reference.py|ffprobe、互相关、参考抽帧、差异候选及弹幕解析|
|src/build_project.py|生成65组分镜、时间表、句级SRT和设计说明|
|src/cast.js|原创角色、关节姿态、手部、面部及背影|
|src/reference-scenes.js|程序宇宙、星门、船、镜室、黑洞、碎片和彩虹海|
|src/timeline.js / music-data.js|镜头时间与音乐/歌词触发|
|src/typography.js / main.js|动态字幕、确定性绘制和转场|
|src/render.mjs|3个Chrome页面渲染、帧缓存、FFmpeg编码|
|src/qa.py|编码后探测、黑帧/冻结、音频核验与验收抽帧|
|studio.html|代码画面的实时预览；仅视觉循环预览|
|review.html|成片与样片的带音频播放器|

在项目工作目录运行：

```powershell
node mv/zaifeixing-reference/src/render.mjs --mode=design
node mv/zaifeixing-reference/src/render.mjs --mode=boards
node mv/zaifeixing-reference/src/render.mjs --mode=sample
& 'C:\Users\mengh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' mv/zaifeixing-reference/src/qa.py --mode sample
node mv/zaifeixing-reference/src/render.mjs --mode=full
& 'C:\Users\mengh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' mv/zaifeixing-reference/src/qa.py --mode full
```

渲染器会复用已有JPEG。修改画面代码后，应先把本输出目录内的 `frames/` 和 `qa/sample-frames/` 重命名为历史版本，再重新渲染，避免复用旧画面。不要移动或删除输出目录外的项目文件。Python分析/验收需要numpy、scipy、Pillow，以上命令使用已经验证可用的本地运行时。

本次完整渲染/编码用时记录为136.1秒；最终命令参数与页面错误列表见 `analysis/full-render.json`，页面错误数为0。工具版本在logs/，制作源文件哈希在analysis/production-manifest.json。

## 精度与视觉限制

65个节点是参考的语义镜头组，不是官方逐帧EDL。候选切点结合半秒采样复核，原片部分微切和动画曝光被合并。复杂透视、战斗及表情以平面造型和代码姿态简化表达；本版属于参考节奏与构图功能的原创重绘，不宣称逐帧还原官方动画作画。

整句歌词时间来自本地LRC；句内短语为起音估计，未宣称逐字音素强制对齐。参考字幕字号是烧录图像估计值，未伪称掌握官方字体样式。

## 文件校验

final.mp4 SHA-256：`8e3e156193c4396fe2baf4c7e01bdb8e766cdd6dadeaa07b96a0b275fb66aea2`

源歌曲SHA-256：`9fb18d8e6579363be2c4cb23f425808641f78ed5d3f05e69d01442deb19b05bb`

交付目录包含final.mp4、STORYBOARD.md、subtitles.srt、REPORT.md、analysis/、assets/、src/、qa/和logs/，另保留frames/及可直接打开的预览页面。初期废弃草稿和样片已明确归档，不作为当前验收依据。
