from pathlib import Path


def test_pyvis_options_use_dictionary_not_toggle_method():
    source = Path('app.py').read_text()
    assert "net.options['physics']['enabled'] = not reduced and layout=='Force-directed'" in source
    assert 'net.toggle_physics(' not in source


def test_obsolete_cluster_scatter_is_not_required():
    source = Path('src/clustering_ui.py').read_text()
    assert 'cluster_size_comparison_v52' in source
    assert 'cluster_entrance(grouped)' in source
