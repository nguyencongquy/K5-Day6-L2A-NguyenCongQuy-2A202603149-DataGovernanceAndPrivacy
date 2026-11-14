"""Predeclared ten-image synthetic domain stress pack. No fixture/GT/model inputs.

New camera IDs, dimensions, textures and overhead geometry differ from fixture
street scenes. Reference actions are engineering expectations from applied
transforms; they are not human usability gold or real-world OOD evidence.
"""
from pathlib import Path
import io,json,hashlib
import numpy as np
import pandas as pd
from PIL import Image,ImageDraw,ImageFilter
from src.common.manifest import build_manifest,write_manifest

CASES=[
 ('ood01','day','none','KEEP',(480,270)),
 ('ood02','day','soft_optics','KEEP',(480,270)),
 ('ood03','night','none','KEEP',(512,288)),
 ('ood04','night','underexpose','RECAPTURE',(512,288)),
 ('ood05','day','local_glare','RECAPTURE',(640,360)),
 ('ood06','day','texture','KEEP',(640,360)),
 ('ood07','day','jpeg3','RECAPTURE',(480,270)),
 ('ood08','dusk','smooth','KEEP',(360,240)),
 ('ood09','day','blur4','RECAPTURE',(480,270)),
 ('ood10','dusk','blur6','RECAPTURE',(600,240)),
]


def scene(size,light,seed):
    w,h=size;rng=np.random.default_rng(seed)
    yy,xx=np.mgrid[:h,:w]
    level=22 if light=='night' else (105 if light=='dusk' else 155)
    arr=np.zeros((h,w,3),dtype=np.uint8)
    for c in range(3): arr[:,:,c]=np.clip(level+12*np.sin(xx/37)+8*np.cos(yy/23)+c*5,0,255)
    im=Image.fromarray(arr);d=ImageDraw.Draw(im)
    # Overhead inspection-board geometry; deliberately outside road-scene domain.
    for i in range(6):
        x=int(w*(.06+.15*i)); y=int(h*(.2+.45*(i%2)))
        d.rounded_rectangle((x,y,x+int(w*.1),y+int(h*.17)),radius=7,fill=tuple(int(v) for v in rng.integers(80,235,3)),outline='white',width=2)
        d.text((x+5,y+5),f'TARGET-{i}',fill='black')
    d.line((12,h//2,w-12,h//2),fill=(180,190,190),width=2)
    return im


def main():
    root=Path('data/ood_synthetic');(root/'images').mkdir(parents=True,exist_ok=True)
    meta=[];ref=[]
    for i,(item,light,transform,action,size) in enumerate(CASES):
        im=scene(size,light,700+i)
        if transform=='soft_optics': im=im.filter(ImageFilter.GaussianBlur(.55))
        elif transform=='underexpose': im=Image.fromarray((np.asarray(im)*.06).astype('uint8'))
        elif transform=='local_glare':
            w,h=size;ImageDraw.Draw(im).ellipse((w*.3,h*.16,w*.64,h*.75),fill='white')
        elif transform=='texture':
            a=np.asarray(im).astype(float);rng=np.random.default_rng(800+i)
            im=Image.fromarray(np.clip(a+rng.normal(0,8,a.shape),0,255).astype('uint8'))
        elif transform=='jpeg3':
            b=io.BytesIO();im.save(b,format='JPEG',quality=3);b.seek(0);im=Image.open(b).convert('RGB')
        elif transform.startswith('blur'):im=im.filter(ImageFilter.GaussianBlur(int(transform[4:])))
        rel=f'images/{item}.png';im.save(root/rel)
        meta.append(dict(image_id=item,path=rel,camera_id='cam_OOD_'+str(i%2),light=light,split='eval'))
        ref.append(dict(image_id=item,transform=transform,reference_action=action,reference_basis='predeclared engineering expectation, not human gold',width=size[0],height=size[1],seed=700+i))
    pd.DataFrame(meta).to_csv(root/'images.csv',index=False)
    pd.DataFrame(ref).to_csv(root/'reference_actions.csv',index=False)
    files=[p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name!='manifest.csv']
    write_manifest(build_manifest(root,files,source='Procedural inspection-board scenes; tools/prepare_ood_t02.py; independent of fixture',license='CC0-1.0',split='ood_stress',group_id='synthetic_OOD'),root/'manifest.csv')
    spec={'scope':'10 synthetic shifted-domain stress cases; NOT natural-image OOD validation','cases':CASES,'seed':42,'frozen_scoring_sha256':hashlib.sha256(Path('src/pipeline.py').read_bytes()).hexdigest(),'no_threshold_tuning_on_ood':True,'comparison':'per-image action agreement, false KEEP and false RECAPTURE; no Recall@20 claim on N=10'}
    Path('reports/ood_protocol.json').write_text(json.dumps(spec,indent=2))
    print('Generated 10 independent synthetic OOD stress images and manifest')

if __name__=='__main__': main()
