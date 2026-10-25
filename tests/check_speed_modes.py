#!/usr/bin/env python3
"""Measure work and transport drive from Gazebo poses, including transport stop distance."""
import argparse
import json
import time
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8088')
args = parser.parse_args()
base = args.url.rstrip('/')
sequence = 0

def state():
    with urllib.request.urlopen(base + '/api/state', timeout=3) as response:
        return json.load(response)

def post(path, payload):
    request = urllib.request.Request(
        base + '/api/' + path,
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json', 'Origin': base},
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)

def wait_ready():
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        sample = state()
        if sample['control_ready'] and sample['sim_time'] > 1:
            return sample
        time.sleep(.1)
    raise RuntimeError('Gazebo did not become ready')

def wait_sim_seconds(start, seconds, callback=None):
    deadline = time.monotonic() + 70
    samples = []
    while True:
        sample = state()
        samples.append(sample)
        if sample['sim_time'] - start >= seconds:
            return samples
        if time.monotonic() >= deadline:
            raise RuntimeError('Gazebo simulation time stalled')
        if callback:
            callback()
        time.sleep(.12)

def run(mode):
    global sequence
    post('profile', {'profile': 'potato_ridge'})
    sample = wait_ready()
    revision = sample['revision']
    post('speed_mode', {'revision': revision, 'mode': mode})
    if state()['speed_mode'] != mode:
        raise AssertionError('Speed mode did not change')
    sequence += 1
    drive_sequence = sequence
    envelope = {'revision': revision, 'client_id': 'speed-regression', 'sequence': drive_sequence}
    post('motion', {**envelope, 'command': 'forward'})
    start = state()['sim_time']
    try:
        samples = wait_sim_seconds(start, 4, lambda: post('heartbeat', envelope))
    finally:
        sequence += 1
        post('motion', {'revision': revision, 'client_id': 'speed-regression', 'sequence': sequence, 'command': 'stop'})
    before = min(samples, key=lambda s: abs(s['sim_time'] - start - 2))
    last = samples[-1]
    velocity = (last['poses']['robot']['position'][0] - before['poses']['robot']['position'][0]) / (last['sim_time'] - before['sim_time'])
    stopped = state()
    after = wait_sim_seconds(stopped['sim_time'], 2)[-1]
    stop_distance = after['poses']['robot']['position'][0] - stopped['poses']['robot']['position'][0]
    result = {'mode': mode, 'measured_mps': round(velocity, 3), 'stop_distance_m': round(stop_distance, 3), 'end_x_m': round(after['poses']['robot']['position'][0], 3), 'end_z_m': round(after['poses']['robot']['position'][2], 3), 'end_tilt_deg': round(after['body_tilt_deg'], 2)}
    print(json.dumps(result, ensure_ascii=False), flush=True)
    assert abs(after['poses']['robot']['position'][2]) < .10 and abs(after['body_tilt_deg']) < 10
    return result

work = run('work')
transport = run('transport')
assert .20 < work['measured_mps'] < .35
assert .85 < transport['measured_mps'] < 1.10
assert transport['stop_distance_m'] < .65
assert transport['end_x_m'] < 10
print('PASS: two Gazebo speeds, stop distance, field stability')
