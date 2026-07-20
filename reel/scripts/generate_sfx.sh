#!/bin/bash
set -e
cd /tmp/claude-0/-home-user-staff-wc2026/00e9bf4b-1013-52b1-b5fa-20eaffb893a8/scratchpad/reel/audio
SR=48000

# BIG BOOM / impact — layered low sines, fast attack, long-ish decay tail
ffmpeg -y -v error -f lavfi -i "aevalsrc='(0.95*sin(2*PI*50*t)+0.6*sin(2*PI*33*t)+0.35*sin(2*PI*78*t))*exp(-2.2*t)':d=2.2:s=${SR}" \
  -af "afade=t=in:d=0.004,alimiter=limit=0.97,aformat=channel_layouts=stereo" sfx_boom.wav

# RISER — pink-noise air building over 2s (leads into the drop)
ffmpeg -y -v error -f lavfi -i "anoisesrc=d=2.1:c=pink:a=0.6:r=${SR}" \
  -af "highpass=f=350,afade=t=in:st=0:d=2.0:curve=qua,afade=t=out:st=2.0:d=0.1,volume=1.1,aformat=channel_layouts=stereo" sfx_riser.wav

# SUB DROP — deep sub swell that lands with the boom and rolls under the reveal
ffmpeg -y -v error -f lavfi -i "aevalsrc='(0.8*sin(2*PI*41*t)+0.5*sin(2*PI*28*t))*exp(-1.1*t)':d=2.8:s=${SR}" \
  -af "afade=t=in:d=0.01,lowpass=f=140,volume=0.9,aformat=channel_layouts=stereo" sfx_subdrop.wav

# SHIMMER — high bell sparkle into the Maldives payoff
ffmpeg -y -v error -f lavfi -i "aevalsrc='(0.25*sin(2*PI*2100*t)+0.18*sin(2*PI*3150*t)+0.12*sin(2*PI*4700*t))*exp(-3.5*t)':d=1.2:s=${SR}" \
  -af "afade=t=in:d=0.01,volume=0.8,aformat=channel_layouts=stereo" sfx_shimmer.wav

echo "=== SFX built ==="
for f in sfx_*.wav; do printf "%-18s %ss\n" "$f" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)"; done