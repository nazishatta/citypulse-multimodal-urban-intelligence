from pathlib import Path
import ast

def test_live_network_is_rendered_and_periodically_reenergized():
    source=(Path(__file__).resolve().parents[1]/'app.py').read_text(encoding='utf-8')
    ast.parse(source)
    assert 'galaxy_html = net.generate_html(notebook=False)' in source
    assert "child_motion_html(galaxy_html, motion, 'pyvis', allow_physics=physics_enabled)" in source
    assert 'network.moveNode' in source
    assert 'network.startSimulation()' in source
    assert 'document.hidden' in source
    assert 'network.physics.physicsEnabled' in source
    assert "if physics_enabled:" in source
