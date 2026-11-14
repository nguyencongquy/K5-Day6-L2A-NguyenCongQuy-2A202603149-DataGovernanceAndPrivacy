import json
import numpy as np
import pytest
from scipy.ndimage import gaussian_filter
from src.pipeline import features, score_features
from src import main


def test_blur_reduces_sharpness():
    rng=np.random.default_rng(42)
    image=rng.integers(40,210,(64,64,3),dtype=np.uint8)
    blurred=gaussian_filter(image.astype(float),sigma=(3,3,0)).astype('uint8')
    assert features(blurred)['normalized_sharpness'] < features(image)['normalized_sharpness']
    assert score_features(features(blurred))[0] > score_features(features(image))[0]


def test_small_image_rejected():
    with pytest.raises(ValueError,match='16x16'):
        features(np.zeros((8,8,3),dtype='uint8'))


def test_poc_offline_reproducible_and_holds(tmp_path):
    for name in ['a','b']:
        assert main.main(['--offline','--seed','42','--output',str(tmp_path/name)])==0
    assert (tmp_path/'a/ranked_review.csv').read_bytes()==(tmp_path/'b/ranked_review.csv').read_bytes()
    assert json.loads((tmp_path/'a/decision.json').read_text())['status']=='HOLD'


def test_review_override_and_audit(tmp_path):
    import pandas as pd
    assert main.main(['--offline','--output',str(tmp_path)])==0
    q=pd.read_csv(tmp_path/'review_queue.csv').fillna('')
    q['reviewer']='test-reviewer'
    q['reviewer_decision']='approve'
    q.loc[0,['reviewer_decision','override_value','review_note']]=['edit','KEEP','synthetic test override']
    q.to_csv(tmp_path/'review_queue_reviewed.csv',index=False)
    assert main.main(['--offline','--output',str(tmp_path)])==0
    out=pd.read_csv(tmp_path/'ranked_review.csv')
    assert out.set_index('image_id').loc[q.loc[0,'item_id'],'pred_action']=='KEEP'
    assert 'override:edit' in (tmp_path/'audit_log.jsonl').read_text()
    assert json.loads((tmp_path/'decision.json').read_text())['status']=='GO'


def test_anonymous_review_fails(tmp_path):
    import pandas as pd
    assert main.main(['--offline','--output',str(tmp_path)])==0
    q=pd.read_csv(tmp_path/'review_queue.csv').fillna('')
    q.loc[0,'reviewer_decision']='approve'
    q.to_csv(tmp_path/'review_queue_reviewed.csv',index=False)
    assert main.main(['--offline','--output',str(tmp_path)])==2


def test_stale_review_is_rejected(tmp_path):
    import pandas as pd
    assert main.main(['--offline','--output',str(tmp_path)])==0
    q=pd.read_csv(tmp_path/'review_queue.csv').fillna('')
    q.loc[0,['reviewer','reviewer_decision','score']]=['test-reviewer','approve',-100]
    q.to_csv(tmp_path/'review_queue_reviewed.csv',index=False)
    assert main.main(['--offline','--output',str(tmp_path)])==2


def test_escalation_keeps_hold(tmp_path):
    import pandas as pd
    assert main.main(['--offline','--output',str(tmp_path)])==0
    q=pd.read_csv(tmp_path/'review_queue.csv').fillna('')
    q['reviewer']='test-reviewer';q['reviewer_decision']='approve'
    q.loc[0,'reviewer_decision']='escalate'
    q.to_csv(tmp_path/'review_queue_reviewed.csv',index=False)
    assert main.main(['--offline','--output',str(tmp_path)])==0
    assert json.loads((tmp_path/'decision.json').read_text())['status']=='HOLD'
