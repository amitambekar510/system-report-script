"""Build an illustrative terminal GIF and static fallback; requires Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
if not FONT.exists(): raise SystemExit('Install DejaVu Sans Mono to build the demo assets')
def font(size): return ImageFont.truetype(str(FONT),size)
lines=[('$ bash system_check_and_fio.sh --demo','#eaf2ff'),('Preparing synthetic demo','#b6c9df'),('Report status: partial','#f5cb82'),('Reports saved in: ./system_reports/report-...','#b6c9df'),('','#b6c9df'),('HTML  /  TXT  /  CSV  /  JSON','#71e3b7')]
frames=[]
for count in range(1,len(lines)+1):
 im=Image.new('RGB',(1000,420),'#0c1421');d=ImageDraw.Draw(im)
 d.rounded_rectangle((18,18,982,402),radius=16,fill='#101f32',outline='#35506d',width=2)
 d.text((44,36),'THE SAFEHOUSE / SYSTEM REPORT',font=font(17),fill='#71e3b7')
 d.text((44,68),'ILLUSTRATIVE DEMO · NO LIVE SERVER DATA',font=font(14),fill='#a7bdd5')
 d.line((42,102,958,102),fill='#35506d',width=1)
 for i,(line,color) in enumerate(lines[:count]): d.text((44,126+i*34),line,font=font(20),fill=color)
 d.text((44,366),'Partial = review unavailable sections in the report',font=font(15),fill='#f5cb82')
 frames.append(im)
ROOT.joinpath('assets').mkdir(exist_ok=True)
frames[-1].save(ROOT/'assets/demo-still.png')
frames[0].save(ROOT/'assets/report-demo.gif',save_all=True,append_images=frames[1:],duration=[1100,800,900,1000,300,3000],loop=0,optimize=True)
print('Built report-demo.gif and demo-still.png')
