'''Central robot specification helpers for SDF and Xacro generation.'''
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
SPEC_PATH=ROOT/'config/robot-spec.json'

def load_spec():
    return json.loads(SPEC_PATH.read_text(encoding='utf-8'))

def variant(name):
    spec=load_spec()
    return spec['variants'][name]

def dynamic_variants():
    return [name for name,data in load_spec()['variants'].items() if data.get('drive_ready')]
