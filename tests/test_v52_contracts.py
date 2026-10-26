from pathlib import Path

def test_network_defaults_to_physics_renderer():
    code=Path('app.py').read_text()
    assert "['PyVis · moving nodes','Plotly · select nodes']" in code
    assert "bgcolor='#18212B'" in code
    assert "Freeze node movement" in code

def test_cluster_has_single_coordinate_scene_and_size_comparison():
    code=Path('src/clustering_ui.py').read_text()
    assert "cluster_size_comparison_v52" in code
    assert "cluster_inspect_v52" in code
    assert 'cluster_entrance(grouped)' in code
    assert "px.scatter(grouped" not in code
    assert "scatter_map(grouped" not in code
