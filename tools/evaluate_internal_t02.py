"""Independent controlled-corruption benchmark, NOT instructor ground truth.
Fixed scoring policy is declared in src.pipeline before this benchmark is run.
Labels describe applied transformations, not real-world usability judgments.
"""
from pathlib import Path
import io
import time
import json
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter
from src.pipeline import features, score_features
from src.metrics.tracks import eval_t02
from src.common.report import write_metrics, compare_runs


def main():
    root=Path('out/internal_t02'); root.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(20261114)
    rows=[]; images=[]
    # 12 independent scenes x 5 transforms. Each scene remains grouped.
    for scene in range(12):
        a=Image.new('RGB',(320,180),(75,90,105)); d=ImageDraw.Draw(a)
        for _ in range(70):
            x,y=rng.integers([0,0],[300,160]); w,h=rng.integers(4,25,2)
            color=tuple(int(v) for v in rng.integers(35,215,3))
            d.rectangle((int(x),int(y),int(x+w),int(y+h)),fill=color)
        for kind in ['none','blur','dark','glare','compression']:
            im=a.copy()
            if kind=='blur': im=im.filter(ImageFilter.GaussianBlur(3))
            elif kind=='dark': im=Image.fromarray((np.asarray(im)*.1).astype('uint8'))
            elif kind=='glare': ImageDraw.Draw(im).rectangle((100,65,155,105),fill='white')
            elif kind=='compression':
                b=io.BytesIO(); im.save(b,format='JPEG',quality=3); b.seek(0); im=Image.open(b).convert('RGB')
            images.append(np.asarray(im).copy())
            rows.append(dict(image_id=f's{scene:02}_{kind}',split='eval',light='controlled',defect_type=kind,is_defect=int(kind!='none'),scene=scene))
    labels=pd.DataFrame(rows); labels.to_csv(root/'labels.csv',index=False)
    summaries={}
    for name in ['baseline','poc','ablation_no_glare']:
        t=time.perf_counter(); pred=[]
        for row,img in zip(rows,images):
            score,kind=score_features(features(img),baseline=name=='baseline',ablate_glare=name=='ablation_no_glare')
            pred.append(dict(image_id=row['image_id'],score=score,pred_defect_type=kind))
        seconds=time.perf_counter()-t
        path=root/f'{name}.csv';pd.DataFrame(pred).to_csv(path,index=False)
        result=eval_t02(root/'labels.csv',path,{'budget':20,'split':'eval'})
        write_metrics(f'reports/metrics_{name}.json',name,'t02',result.metrics,seed=42,runtime_seconds=seconds,n_items=len(rows),extra={'scope':'independent controlled-corruption benchmark; NOT hidden fixture evaluation','generator_seed':20261114,'notes':result.notes})
        result.slices.to_csv(f'reports/slices_{name}.csv',index=False)
        summaries[name]={m.name:m.value for m in result.metrics if m.slice=='all'}
    Path('reports/table1_baseline_vs_poc.md').write_text(compare_runs('reports/metrics_baseline.json','reports/metrics_poc.json'))
    Path('reports/table2_ablation.md').write_text(compare_runs('reports/metrics_ablation_no_glare.json','reports/metrics_poc.json'))
    # Cluster bootstrap by scene: preserve transformation correlation.
    boot=np.random.default_rng(42); stats=[]
    p=pd.read_csv(root/'poc.csv').merge(labels,on='image_id')
    for _ in range(500):
        sample=pd.concat([p[p.scene.eq(s)] for s in boot.choice(12,12,replace=True)],ignore_index=True)
        top=sample.sort_values('score',ascending=False,kind='mergesort').head(20)
        stats.append(float(top.is_defect.sum()/sample.is_defect.sum()))
    Path('reports/internal_protocol.json').write_text(json.dumps({'scope':'controlled transforms only','n':60,'scenes':12,'budget':20,'defects':48,'bootstrap_scene_recall_ci95':np.quantile(stats,[.025,.975]).tolist(),'runs':summaries},indent=2))
    print(json.dumps(summaries,indent=2))

if __name__=='__main__': main()
