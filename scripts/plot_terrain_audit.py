#!/usr/bin/env python3
"""Plots from native Gazebo CSV logs; no browser positions or inferred animations."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
LABELS={'grade_0':'0° – Ebene','grade_5':'5° – Rampeneinlauf','grade_10':'10° – Rampeneinlauf','grade_15':'15° – Rampeneinlauf','uneven':'Unebenheiten – 0…20 mm'}
def read(path):
    with path.open() as f:rows=list(csv.DictReader(f))
    return {k:np.array([float(r[k]) for r in rows]) for k in rows[0]}
def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    data={case:read(args.directory/f'{case}_seed11/telemetry.csv') for case in LABELS}
    fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True)
    for case,d in data.items():
        axes[0].plot(d['sim_s'],d['x_m']-d['x_m'][0],label=LABELS[case]);axes[1].plot(d['sim_s'],d['left_rim_speed_mps']-d['left_hub_forward_mps'],label=LABELS[case],alpha=.8)
    axes[0].set_ylabel('Vortrieb in Welt-x [m]');axes[0].legend(ncol=2);axes[1].set_ylabel('Schlupfgeschwindigkeit links [m/s]');axes[1].set_xlabel('Gazebo-Simulationszeit [s]')
    for ax in axes:ax.grid(alpha=.25);ax.axvline(2,color='grey',ls=':');ax.axvline(22,color='grey',ls=':')
    fig.suptitle('Unverändertes Rad-/Stütz-Ersatzmodell · 0,15 m/s Fahrbefehl · Seed 11');fig.tight_layout();fig.savefig(args.output/'terrain-overview.png',dpi=160);plt.close(fig)
    d=data['grade_5'];t=d['sim_s'];fig,axes=plt.subplots(6,1,figsize=(11,14),sharex=True)
    axes[0].plot(t,d['cmd_v_mps'],label='Soll Körper');axes[0].plot(t,d['left_rim_speed_mps'],label='Ist Radumfang links',alpha=.7);axes[0].plot(t,d['v_body_x_mps'],label='Ist Körper vorwärts',alpha=.8);axes[0].set_ylabel('Geschwindigkeit [m/s]');axes[0].legend(ncol=3)
    for side,label in [('left','links'),('right','rechts')]:axes[1].plot(t,d[side+'_axis_torque_Nm'],label=label,alpha=.7)
    axes[1].axhline(40,color='firebrick',ls='--',label='SDF-Grenze ±40 Nm');axes[1].axhline(-40,color='firebrick',ls='--');axes[1].set_ylabel('Achsmoment [Nm]');axes[1].legend(ncol=3)
    for side,label in [('left','links'),('right','rechts')]:axes[2].plot(t,d[side+'_slip_ratio'],label=label,alpha=.65)
    axes[2].set_ylabel('Normierter Schlupf [1]')
    # Display 100 ms block means to reveal load distribution amid contact chatter.
    count=max(1,round(.1/(t[1]-t[0])));end=len(t)//count*count;tm=t[:end].reshape(-1,count).mean(axis=1)
    nw=d['left_wheel_normal_N']+d['right_wheel_normal_N'];nc=sum(d[k] for k in d if k.startswith('caster_') and k.endswith('_normal_N'))
    axes[3].plot(tm,nw[:end].reshape(-1,count).mean(axis=1),label='beide Antriebsräder');axes[3].plot(tm,nc[:end].reshape(-1,count).mean(axis=1),label='vier Stützen');axes[3].set_ylabel('Σ Normalkräfte [N]\n100-ms-Mittel');axes[3].legend(ncol=2)
    for side,offset in [('left',0),('right',1.2)]:axes[4].step(t,(d[side+'_wheel_contacts']>0).astype(float)+offset,label=side,alpha=.65,where='post')
    axes[4].set_yticks([0,1,1.2,2.2],['L: nein','L: ja','R: nein','R: ja']);axes[4].set_ylabel('Radkontakt')
    axes[5].plot(t,d['pitch_deg'],label='Pitch');axes[5].plot(t,d['roll_deg'],label='Roll');axes[5].set_ylabel('Neigung [°]');axes[5].legend(ncol=2);axes[5].set_xlabel('Gazebo-Simulationszeit [s]')
    for ax in axes:ax.grid(alpha=.25);ax.axvline(2,color='grey',ls=':');ax.axvline(22,color='grey',ls=':')
    fig.suptitle('5°-Rampeneinlauf: Räder drehen, während die Stützen die Last übernehmen\nNative Gazebo-Messwerte; Kontaktkräfte auf numerische Konsistenz prüfen');fig.tight_layout();fig.savefig(args.output/'grade-5-diagnostics.png',dpi=160);plt.close(fig)
if __name__=='__main__':main()
