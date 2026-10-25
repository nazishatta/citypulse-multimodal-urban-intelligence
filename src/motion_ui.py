"""One progressive motion conductor for native Streamlit charts; no selection bridge."""
from pathlib import Path
import streamlit as st
from src.motion import MotionSettings

ASSETS=Path(__file__).parent/'frontend'
ENGINE=(ASSETS/'motion.js').read_text()
COMPONENT=st.components.v2.component('citypulse_shared_motion',html='<div class="cp-motion-root"></div>',css=(ASSETS/'motion.css').read_text(),js=ENGINE+"\nexport default function(component){window.__citypulseMotionCleanup?.();const cleanup=mountCityPulseMotion(component.parentElement.querySelector('.cp-motion-root'),component.data);window.__citypulseMotionCleanup=cleanup;return ()=>{cleanup();if(window.__citypulseMotionCleanup===cleanup)window.__citypulseMotionCleanup=null;};}",isolate_styles=False)

def render_motion(settings: MotionSettings,tab: str,revision: str):
    return COMPONENT(key='citypulse_shared_motion',data={'settings':settings.payload(),'tab':tab,'revision':revision})
