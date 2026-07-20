#!/bin/bash
set -e
cd /tmp/claude-0/-home-user-staff-wc2026/00e9bf4b-1013-52b1-b5fa-20eaffb893a8/scratchpad/reel
SRC=src
W=work
COVER="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
ENC="-c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -preset medium -crf 16 -an"

# S1 OPEN 5.0s
ffmpeg -v error -y -ss 0 -t 5.0 -i $SRC/01_open.mp4 -vf "${COVER},fps=30,format=yuv420p" $ENC $W/n1.mp4
# S2 STATS 5.0s
ffmpeg -v error -y -ss 0 -t 5.0 -i $SRC/02_stats.mp4 -vf "${COVER},fps=30,format=yuv420p" $ENC $W/n2.mp4
# S3 FINAL 5.0s
ffmpeg -v error -y -ss 0 -t 5.0 -i $SRC/03_final.mp4 -vf "${COVER},fps=30,format=yuv420p" $ENC $W/n3.mp4
# S4 LEADERBOARD 5.0s, fade to black last 0.18s (dip into champion)
ffmpeg -v error -y -ss 0 -t 5.0 -i $SRC/04_leaderboard.mp4 -vf "${COVER},fps=30,fade=t=out:st=4.82:d=0.18,format=yuv420p" $ENC $W/n4.mp4
# S5 CHAMPION ~5.2s, slowed 1.05x for gravitas, fade in from black first 0.18s
ffmpeg -v error -y -i $SRC/05_champion.mp4 -vf "${COVER},setpts=1.05*PTS,fps=30,fade=t=in:st=0:d=0.18,format=yuv420p" -t 5.2 $ENC $W/n5.mp4
# S6 MALDIVES 4.4s (skip first 0.2s), gentle slow 1.08x for luxury
ffmpeg -v error -y -ss 0.2 -i $SRC/b_maldives.mp4 -vf "${COVER},setpts=1.08*PTS,fps=30,format=yuv420p" -t 4.4 $ENC $W/n6.mp4

echo "=== NORMALIZED SEGMENTS ==="
for f in $W/n{1,2,3,4,5,6}.mp4; do
  printf "%-14s " "$(basename $f)"
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,pix_fmt -show_entries format=duration -of default=nw=1:nk=1 "$f" | tr '\n' ' '
  echo ""
done

# Extract a mid-frame from each for visual QC
mkdir -p $W/qc
for n in 1 2 3 4 5 6; do
  ffmpeg -v error -y -ss 1.0 -i $W/n$n.mp4 -frames:v 1 $W/qc/n${n}.jpg
done
echo "QC frames written."