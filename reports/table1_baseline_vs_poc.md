Baseline: `baseline` (git 5b9b38d, seed 42) · PoC: `poc` (git 5b9b38d, seed 42)

| Metric (unit) | Slice | Baseline | PoC | Δ abs | Δ rel | Better | N |
|---|---|---|---|---|---|---|---|
| **Defect Recall@B** (GT defects in top-B / GT defects) | all | 0.4167 | 0.4167 | 0.0000 | +0.0% | higher | 60 |
| Precision@B (GT defects in top-B / B) | all | 1.0000 | 1.0000 | 0.0000 | +0.0% | higher | 60 |
| Defect-type accuracy (GT defects) (fraction) | all | 0.2500 | 0.5208 | 0.2708 | +108.3% | higher | 48 |
| False alarm in top-B (clean images in top-B / clean images) | light=controlled | 0.0000 | 0.0000 | 0.0000 | baseline=0 | lower | 60 |
| Runtime / 100 items (s) | all | 0.1004 | 0.1014 | | | lower | |