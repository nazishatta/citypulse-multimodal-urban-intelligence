from pathlib import Path


def test_plotly_tooltip_contrast_contract():
    src = (Path(__file__).resolve().parents[1] / 'src' / 'visuals.py').read_text()
    assert "bgcolor='#111A23'" in src
    assert "font=dict(color='#F5FAFC',size=14)" in src


def test_clustering_map_offline_and_looped():
    src = (Path(__file__).resolve().parents[1] / 'src' / 'clustering_ui.py').read_text()
    assert "fig=px.scatter(grouped,x='longitude',y='latitude'" in src
    assert 'map_style=' not in src
    assert 'loop=True' in src


def test_player_loop_opt_in_and_reduced_motion():
    src = (Path(__file__).resolve().parents[1] / 'src' / 'guided_motion.py').read_text()
    assert 'loop:bool=False' in src
    assert 'prefers-reduced-motion: reduce' in src
    assert 'if(loop)repeat=setTimeout' in src
