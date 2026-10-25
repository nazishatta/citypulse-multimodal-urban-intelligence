"""Policy validation and integration of shared motion without changing evidence."""
import pytest
from src.motion import MotionSettings,SPEEDS,child_motion_html

@pytest.mark.parametrize('speed,ms',SPEEDS.items())
def test_shared_duration_and_easing(speed,ms):
 p=MotionSettings(speed=speed).payload()
 assert p['duration']==ms and p['updateDuration']==400 and p['reducedDuration']==120
 assert p['easing']=='cubic-bezier(0.22, 1, 0.36, 1)'

@pytest.mark.parametrize('kwargs',[{'mode':'invalid'},{'speed':'invalid'}])
def test_invalid_policy_rejected(kwargs):
 with pytest.raises(ValueError):MotionSettings(**kwargs)

def test_embed_requires_supported_kind_and_preserves_generated_document():
 doc='<html><body><p>Exact source</p></body></html>'
 result=child_motion_html(doc,MotionSettings(mode='Off'),'pyvis',True)
 assert '<p>Exact source</p>' in result
 assert 'CITYPULSE_CHILD_MOTION' in result and 'Show final state' in result
 assert result.index('CITYPULSE_CHILD_MOTION')<result.index('</body>')
 with pytest.raises(ValueError):child_motion_html(doc,MotionSettings(),'unknown')
