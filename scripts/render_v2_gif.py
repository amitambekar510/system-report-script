#!/usr/bin/env python3
"""Generate a synthetic workflow GIF for System Report Script 2.0."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
out=Path("assets/system-v2-workflow.gif")
out.parent.mkdir(parents=True,exist_ok=True)
fontdir=Path("/usr/share/fonts/truetype/dejavu")
def f(size,bold=False):
 p=fontdir/("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
 return ImageFont.truetype(str(p),size) if p.exists() else ImageFont.load_default()
steps=[("01 / INTAKE","Choose Linux distribution and evidence requirements","Never share credentials or confidential host data"),("02 / APPROVE","Review permissions, scope and output storage","Non-root inventory preferred"),("03 / COLLECT","Gather system, account and SSH MFA hints","Unavailable is not compliant; FIO disabled by default"),("04 / REVIEW","Verify evidence gaps and security implications","MFA enforcement requires manual confirmation"),("05 / EXPORT","Produce HTML, TXT, CSV and JSON artifacts","Protect sensitive host and account information")]
frames=[]
for i,(title,detail,note) in enumerate(steps):
 im=Image.new("RGB",(1200,440),"#091827");d=ImageDraw.Draw(im)
 d.rounded_rectangle((22,22,1178,418),radius=22,fill="#153449",outline="#51d8bd",width=3)
 d.text((55,53),"SYSTEM REPORT SCRIPT 2.0",font=f(29,True),fill="#6de5d0")
 d.text((55,123),title,font=f(36,True),fill="#fff")
 d.text((55,186),detail,font=f(23),fill="#d7ebf1")
 d.text((55,237),note,font=f(19),fill="#b5d0dd")
 for j,label in enumerate(("INTAKE","APPROVE","COLLECT","REVIEW","EXPORT")):
  x=55+j*227
  d.rounded_rectangle((x,306,x+208,356),radius=11,fill="#49d2b8" if j<=i else "#36556a")
  d.text((x+18,320),label,font=f(18,True),fill="#0a2934" if j<=i else "#e6f5f7")
 d.text((55,387),"SYNTHETIC DEMO • NO HOST INSPECTION OR BENCHMARK PERFORMED",font=f(16),fill="#abc9d5")
 frames.append(im)
frames[0].save(out,save_all=True,append_images=frames[1:],duration=1100,loop=0,optimize=True)
assert Image.open(out).n_frames==5
