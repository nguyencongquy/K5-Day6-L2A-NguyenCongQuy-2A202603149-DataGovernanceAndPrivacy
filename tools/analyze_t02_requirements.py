"""Measure required failure-mode examples; never read hidden labels or retune policy."""
from pathlib import Path
import json,shutil
import pandas as pd
import numpy as np
from PIL import Image,ImageFilter
from src.pipeline import features,score_features


def main():
    root=Path('reports');(root/'examples').mkdir(exist_ok=True)
    p=pd.read_csv('out/poc/ranked_review.csv').set_index('image_id')
    b=pd.read_csv('out/baseline/ranked_review.csv').set_index('image_id')
    chosen=[('night_useful','img_18_1','dev','Targets remain visible at night; a naive mean-brightness cutoff of 60 would reject this useful-looking example. This is a counterfactual rule, not the submitted baseline.'),
            ('small_glare','img_18_2','dev','Local white glare obscures detail near the front plate, although global sharpness stays high. Fixed 16x16 tile saturation does not trigger; both submitted methods KEEP. This is a visual finding, not an instructor GT label.'),
            ('cam_B_soft','img_00_0','dev','cam_B image looks softer than img_00_1 with similar scene geometry; objects remain distinguishable. Current policy KEEP, so no observed false alarm is claimed for this source image.')]
    cases=[]
    for kind,item,split,note in chosen:
        r=p.loc[item]; assert r['split']==split
        shutil.copyfile('fixtures/t02_raw_qc/'+r['path'],root/'examples'/f'{item}.jpg')
        cases.append(dict(case=kind,image_id=item,split=split,camera_id=r.camera_id,light=r.light,
            brightness=float(r.brightness),laplacian=float(r.laplacian),glare_fraction=float(r.glare_fraction),
            baseline_score=float(b.loc[item,'score']),poc_score=float(r.score),baseline_action=b.loc[item,'pred_action'],poc_action=r.pred_action,observation=note))
    pd.DataFrame(cases).to_csv(root/'required_failure_cases.csv',index=False)
    # Sensitivity experiment only on dev. No threshold/model changes follow this sweep.
    base=Image.open('fixtures/t02_raw_qc/images/img_00_1.jpg').convert('RGB');sweep=[]
    for radius in [0.,.5,1.,1.5]:
        im=base.filter(ImageFilter.GaussianBlur(radius));f=features(np.asarray(im));s,k=score_features(f);bs,_=score_features(f,True)
        path=root/'examples'/f'cam_B_optics_{radius:g}.png';im.save(path)
        sweep.append(dict(source='img_00_1',split='dev',radius=radius,laplacian=f['laplacian'],baseline_score=bs,poc_score=s,baseline_action='RECAPTURE' if bs>=.5 else 'KEEP',poc_action='RECAPTURE' if s>=.5 else 'KEEP'))
    pd.DataFrame(sweep).to_csv(root/'cam_B_sensitivity.csv',index=False)
    # Descriptive slices only: no hidden-label accuracy/false-positive claims.
    d=p.reset_index()
    d.groupby(['split','camera_id','light'],as_index=False).agg(n=('image_id','size'),mean_score=('score','mean'),recapture_count=('pred_action',lambda x:int((x=='RECAPTURE').sum()))).to_csv(root/'fixture_descriptive_slices.csv',index=False)
    o=pd.read_csv('out/ood/ranked_review.csv'); ref=pd.read_csv('data/ood_synthetic/reference_actions.csv');m=o.merge(ref,on='image_id')
    m['agrees_with_reference']=m.pred_action.eq(m.reference_action)
    m.to_csv(root/'ood_results.csv',index=False)
    summary={'scope':'10 independent synthetic domain stress cases; reference actions are predeclared engineering expectations, NOT human gold',
        'n':len(m),'agreement_count':int(m.agrees_with_reference.sum()),'agreement':float(m.agrees_with_reference.mean()),
        'false_keep_vs_reference':int(((m.pred_action=='KEEP')&(m.reference_action=='RECAPTURE')).sum()),
        'false_recapture_vs_reference':int(((m.pred_action=='RECAPTURE')&(m.reference_action=='KEEP')).sum()),
        'no_threshold_tuning_after_measurement':True,'ranking_metric_not_reported':'B=20 would include all N=10 and be uninformative'}
    (root/'ood_summary.json').write_text(json.dumps(summary,indent=2))
    shutil.copyfile('out/ood/contact_sheet.html',root/'ood_contact_sheet.html')
    md=['# Ba failure mode bắt buộc của T02','', 'Phân tích dưới đây dùng ảnh dev, thông số đã đóng băng, không dùng GT ẩn. Quan sát trực quan không thay nhãn chính thức.','']
    for r in cases:
        md += [f"## {r['case']} — {r['image_id']}",'',f"![{r['case']}](examples/{r['image_id']}.jpg)",'',r['observation'],'',f"Camera={r['camera_id']}; light={r['light']}; brightness={r['brightness']:.3f}; Laplacian={r['laplacian']:.3f}; saturated tile fraction={r['glare_fraction']:.3f}. Baseline={r['baseline_action']} ({r['baseline_score']:.4f}); PoC={r['poc_action']} ({r['poc_score']:.4f}).",'']
    md += ['## Cam_B: độ nhạy với quang học mềm','', 'Bổ sung Gaussian radius 0/0.5/1/1.5 trên img_00_1 (dev). Đây là stress có kiểm soát, không phải lỗi đã được GT xác nhận. Không thay threshold triển khai sau thử nghiệm.','', '| Radius | Laplacian | Baseline | PoC |','|---|---|---|---|']
    md += [f"| {r['radius']} | {r['laplacian']:.3f} | {r['baseline_action']} ({r['baseline_score']:.3f}) | {r['poc_action']} ({r['poc_score']:.3f}) |" for r in sweep]
    md += ['', 'Root cause: một ngưỡng Laplacian toàn ảnh có thể phản ứng với quang học mềm thay vì mức hữu ích cho gán nhãn. PoC chuẩn hóa tương phản vẫn không miễn nhiễm. Cần đánh giá theo nhiệm vụ và camera trước khi tự động loại ảnh.','']
    (root/'required_failure_cases.md').write_text('\n'.join(md))
    print(json.dumps(summary,indent=2));print(pd.DataFrame(sweep).to_string(index=False))

if __name__=='__main__': main()
