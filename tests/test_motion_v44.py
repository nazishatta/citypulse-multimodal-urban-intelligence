"""Regression tests for motion readability and evidence preservation."""
from pathlib import Path
from src.motion import MotionSettings, SPEEDS, child_motion_html

def test_intro_duration_readable():
    assert SPEEDS['Quick'] >= 1000
    assert SPEEDS['Standard'] > SPEEDS['Quick']
    assert SPEEDS['Gentle'] > SPEEDS['Standard']

def test_timeline_has_minimum_per_frame_duration():
    result = child_motion_html('<html><body></body></html>', MotionSettings(), 'timeline')
    assert 'Math.max(90,' in result
    assert 'citypulseFrameNames.length' in result

def test_native_animation_stagger_is_bounded():
    js=(Path(__file__).parents[1]/'src/frontend/motion.js').read_text()
    assert 'Math.min(800,' in js
    assert 'prefers-reduced-motion: reduce' in js
    assert "'inspect'" in js
