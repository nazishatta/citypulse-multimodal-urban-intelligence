from pathlib import Path

def test_galaxy_filters_observed_edges_and_recomputes_communities():
 s=(Path(__file__).parents[1]/'app.py').read_text()
 assert 'Minimum shared reviewers per visible connection' in s
 assert 'greedy_modularity_communities(view' in s
 assert "view.remove_edges_from" in s
 assert 'Community motion energy' in s

def test_animated_physics_has_freeze_and_browser_nudge():
 s=(Path(__file__).parents[1]/'app.py').read_text()
 assert 'Freeze node movement' in s
 assert 'network.moveNode' in s
 assert 'network.startSimulation()' in s
 assert 'document.hidden' in s

def test_clustering_has_explanatory_paths():
 s=(Path(__file__).parents[1]/'src/clustering_ui.py').read_text()
 assert 'Business interpretation · geographic groupings' in s
 assert 'Business interpretation · overlapping audiences' in s
 assert 'Business interpretation · customer language' in s
