from pathlib import Path
from src.motion import MotionSettings,SPEEDS

def test_pacing_presets_are_distinct_and_readable():
    assert SPEEDS['Quick'] < SPEEDS['Standard'] < SPEEDS['Gentle']
    assert SPEEDS['Standard'] >= 3000
    steps=[MotionSettings(speed=s).payload()['physicsStep'] for s in SPEEDS]
    assert steps[0] > steps[1] > steps[2]

def test_guided_motion_is_not_flash_speed():
    import inspect
    from src.guided_motion import render_player,player_html
    assert inspect.signature(render_player).parameters['delay'].default >= 1500
    assert inspect.signature(player_html).parameters['delay'].default >= 1500
