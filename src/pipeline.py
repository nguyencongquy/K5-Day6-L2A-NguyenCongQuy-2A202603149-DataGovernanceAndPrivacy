"""T02 CPU quality triage. Fixed heuristics; no hidden-label access."""
import numpy as np
import pandas as pd
from .common.image_ops import load_rgb, to_gray, laplacian_variance
from .common.manifest import verify_manifest
from .common.review import make_review_queue, write_review_queue, load_review_decisions, apply_overrides
from .common.contact_sheet import render_contact_sheet
from .common.decision import Decision, write_decision


def features(img):
    g = to_gray(img)
    if min(g.shape) < 16:
        raise ValueError('Image must be at least 16x16')
    lap = laplacian_variance(img)
    mean = float(g.mean())
    # Contrast-normalized sharpness protects useful low-light images.
    sharp = lap / max(float(g.var()), 100.0)
    tiles = [g[y:y+16, x:x+16] for y in range(0, g.shape[0]-15, 16) for x in range(0, g.shape[1]-15, 16)]
    glare = max(float((t > 245).mean()) for t in tiles)
    boundary = np.abs(np.diff(g, axis=1))
    block = max(0., float(boundary[:, 7::8].mean() - boundary.mean()))
    return dict(laplacian=lap, normalized_sharpness=sharp, brightness=mean, glare_fraction=glare, blockiness=block)


def score_features(f, baseline=False, ablate_glare=False):
    if baseline:
        components = {'blur': max(0., 1. - f['laplacian'] / 80.)}
    else:
        components = {
            'blur': float(np.clip(1.-f['normalized_sharpness']/0.04, 0, 1)),
            'dark': float(np.clip((18.-f['brightness'])/18., 0, 1)),
            'glare': 0. if ablate_glare else float(np.clip((f['glare_fraction']-0.65)/0.35, 0, 1)),
            'compression': float(np.clip(f['blockiness']/12., 0, 1)),
        }
    kind = max(components, key=components.get)
    score = components[kind]
    return score, kind if score >= 0.5 else 'none'


def run(ctx):
    if ctx.track != 't02':
        raise ValueError('This submission implements T02 only')
    if not isinstance(ctx.config.get('owner'), str) or not ctx.config['owner'].strip():
        raise ValueError('owner is required')
    problems = verify_manifest(ctx.input_dir/'manifest.csv')
    if problems:
        raise ValueError(f'provenance check failed: {problems[:3]}')
    items = pd.read_csv(ctx.input_dir/'images.csv')
    needed = {'image_id','path','split','camera_id','light'}
    if not needed.issubset(items.columns) or items.empty or items.image_id.duplicated().any():
        raise ValueError('Invalid images.csv: missing columns, empty input, or duplicate IDs')
    budget = int(ctx.param('budget', 20))
    if budget < 1:
        raise ValueError('budget must be positive')
    baseline = bool(ctx.param('baseline', False))
    records = []
    root = ctx.input_dir.resolve()
    for r in items.itertuples(index=False):
        path = (root/r.path).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Image path escapes input directory')
        f = features(load_rgb(path))
        score, kind = score_features(f, baseline, bool(ctx.param('ablate_glare',False)))
        records.append(dict(image_id=r.image_id, score=score, pred_defect_type=kind,
            pred_action='RECAPTURE' if score >= .5 else 'KEEP', reason=kind,
            path=r.path, split=r.split, light=r.light, camera_id=r.camera_id, **f))
    raw = pd.DataFrame(records).sort_values(['score','image_id'], ascending=[False,True])
    raw.to_csv(ctx.out('raw_predictions.csv'), index=False)
    # Evaluation budget is defined on eval only, not on a mixed dev/eval pool.
    pool = raw[raw.split.eq('eval')]
    if pool.empty:
        raise ValueError('No eval candidates')
    q = make_review_queue(pool, 'image_id', 'score', budget,
        reason_col='reason', action_col='pred_action', slice_col='light', evidence_col='path')
    write_review_queue(q, ctx.out('review_queue.csv'))
    render_contact_sheet(q, ctx.out('contact_sheet.html'), image_root=root, title='T02: review required before release')
    final = raw.copy()
    reviewed_path = ctx.output_dir/'review_queue_reviewed.csv'
    reviewed = pd.DataFrame()
    if reviewed_path.exists():
        reviewed = load_review_decisions(reviewed_path)
        if reviewed.item_id.duplicated().any() or not set(reviewed.item_id).issubset(set(q.item_id)):
            raise ValueError('Review IDs must be unique and belong to current queue')
        snapshot = q.set_index('item_id')
        for r in reviewed.itertuples(index=False):
            expected = snapshot.loc[r.item_id]
            if (not np.isfinite(float(r.score)) or abs(float(r.score)-float(expected.score)) > 1e-6
                    or str(r.suggested_action) != str(expected.suggested_action)
                    or str(r.evidence_path) != str(expected.evidence_path)):
                raise ValueError('Stale review: score, suggested action or evidence differs from current queue')
        if set(reviewed.override_value)-{'','KEEP','RECAPTURE'}:
            raise ValueError('override_value must be KEEP or RECAPTURE')
        if ((reviewed.reviewer_decision.isin(['edit','reject'])) & reviewed.override_value.eq('')).any():
            raise ValueError('edit/reject requires explicit KEEP or RECAPTURE override')
        final = apply_overrides(final, reviewed, 'image_id', 'pred_action', ctx.audit)
        for r in reviewed.itertuples(index=False):
            ctx.audit.log(actor=r.reviewer, action='review:'+r.reviewer_decision, item_id=r.item_id, reason=r.review_note)
    final.to_csv(ctx.out('ranked_review.csv'), index=False)
    complete = len(reviewed)==len(q) and len(q)>0 and reviewed.reviewer_decision.isin(['approve','edit','reject']).all()
    ctx.stats.update(n_items=len(raw), n_eval=len(pool), n_reviewed=len(reviewed), budget=len(q))
    ctx.audit.log(actor='pipeline', action='triage', after=ctx.stats, reason='Fixed policy; no hidden labels')
    write_decision(Decision(status='GO' if complete else 'HOLD',
        reason_code='REVIEW_COMPLETE' if complete else 'HUMAN_REVIEW_REQUIRED',
        reason='Release triage results only after the whole queue is reviewed; GO does not certify privacy compliance.',
        owner=ctx.config['owner'], scope='t02-triage-output', evidence=['ranked_review.csv','review_queue.csv','audit_log.jsonl']),
        ctx.out('decision.json'),ctx.out('decision_log.csv'))
