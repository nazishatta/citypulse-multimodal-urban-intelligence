from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from src.pipeline import prepare
from tests.fixtures import make_inputs

@pytest.fixture
def app(tmp_path,monkeypatch):
 raw=tmp_path/'raw';make_inputs(raw);out=tmp_path/'snapshot'
 prepare(raw,out,'Fixture City','TS',raw/'photos.json',raw/'photos')
 monkeypatch.setenv('CITYPULSE_DATA_DIR',str(out));monkeypatch.setenv('CITYPULSE_ASSET_ROOT',str(raw/'photos'))
 return AppTest.from_file(str(Path(__file__).parents[1]/'app.py'),default_timeout=45).run()

def test_no_data_shows_setup_without_fake_results(tmp_path,monkeypatch):
 monkeypatch.setenv('CITYPULSE_DATA_DIR',str(tmp_path/'missing'))
 at=AppTest.from_file(str(Path(__file__).parents[1]/'app.py')).run()
 assert not at.exception
 assert any('No prepared Yelp' in x.value for x in at.info)

def test_initial_counts_and_reset_stay_synchronized(app):
 assert not app.exception
 assert app.metric[0].value=='360'
 app.text_input(key='term').set_value('pizza').run()
 assert app.metric[0].value=='90'
 app.button[0].click().run()
 assert app.text_input(key='term').value==''
 assert app.metric[0].value=='360'
 app.multiselect(key='categories').set_value(['Cafe']).run()
 assert app.metric[0].value=='180'

@pytest.mark.parametrize('name',['Trends','Map','Reviews & Topics','Photos','Networks','Methods'])
def test_each_view_renders_real_schema_fixture(app,name):
 app.session_state['view']=name;app.run()
 assert not app.exception, str(app.exception)

def test_empty_selection_has_no_stale_evidence(app):
 app.text_input(key='term').set_value('zzznomatchzzz').run()
 assert app.metric[0].value=='0' and not app.exception
 for name in ['Reviews & Topics','Photos','Networks','Trends','Map']:
  app.session_state['view']=name;app.run();assert not app.exception

def test_network_focus_survives_navigation_and_explicit_transfer(app):
 app.selectbox(key='focus').set_value('b0').run()
 next(x for x in app.button if x.label=='Explore focused restaurant in network').click().run()
 assert app.session_state['network_focus']=='b0'
 assert app.metric[0].value=='360'
 app.selectbox(key='_pair_widget').set_value('b4').run()
 app.session_state['view']='Trends';app.run()
 assert app.session_state['network_focus']=='b0'
 app.session_state['view']='Networks';app.run()
 assert app.selectbox(key='_network_focus_widget').value=='b0'
 assert app.selectbox(key='_pair_widget').value=='b4'
 assert not app.exception

def test_cached_snapshot_cannot_hide_tampering(app,monkeypatch):
 import os,sqlite3
 from pathlib import Path
 path=Path(os.environ['CITYPULSE_DATA_DIR'])/'citypulse.sqlite'
 with sqlite3.connect(path) as db:db.execute('UPDATE reviews SET stars=5')
 app.run()
 assert not app.exception
 assert any('checksum mismatch' in x.value for x in app.error)

def test_missing_photo_root_has_graceful_fallback(app,tmp_path,monkeypatch):
 monkeypatch.setenv('CITYPULSE_ASSET_ROOT',str(tmp_path/'missing'))
 app.session_state['view']='Photos';app.run()
 assert not app.exception
 assert any('Photo unavailable' in x.value for x in app.warning)

def test_optional_replay_and_offline_map_render(app):
 app.session_state['view']='Trends';app.run()
 app.checkbox(key='timeline_replay').set_value(True).run()
 assert not app.exception
 app.session_state['view']='Map';app.run()
 next(x for x in app.selectbox if x.label=='Map background').set_value('Coordinate canvas · offline').run()
 assert not app.exception
 assert app.metric[3].label=='Prepared photo records'

def test_shared_motion_settings_preserve_population_and_focus(app):
 app.selectbox(key='focus').set_value('b0').run()
 for mode in ['Reduce motion','Off','Follow system']:
  app.selectbox(key='motion_mode').set_value(mode).run()
  assert app.metric[0].value=='360' and app.selectbox(key='focus').value=='b0'
  assert not app.exception
 app.select_slider(key='motion_speed').set_value('Gentle').run()
 app.session_state['view']='Methods';app.run()
 assert app.selectbox(key='motion_mode').value=='Follow system'
 assert app.select_slider(key='motion_speed').value=='Gentle'
 assert not app.exception
