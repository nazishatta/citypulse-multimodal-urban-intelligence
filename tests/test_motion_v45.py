"""Source-contract checks for activation-aware motion; browser verification remains required."""
from pathlib import Path


def test_tab_activation_is_not_conflated_with_figure_update():
    js = (Path(__file__).parents[1] / 'src/frontend/motion.js').read_text()
    assert 'const activated=memory.activeTab!==tab;' in js
    assert 'memory.activeTab=tab;' in js
    assert 'unit.pending=first||changed||activated;' in js
    assert "unit.autoKind=(first||activated)?'entry':'update';" in js


def test_motion_has_fallback_and_user_controls():
    js = (Path(__file__).parents[1] / 'src/frontend/motion.js').read_text()
    for key in ('prefers-reduced-motion: reduce', "['Play','play']", "['Pause','pause']", "['Replay','replay']", "['Show final state','inspect']", 'IntersectionObserver'):
        assert key in js
