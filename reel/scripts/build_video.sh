#!/bin/bash
set -e
cd /tmp/claude-0/-home-user-staff-wc2026/00e9bf4b-1013-52b1-b5fa-20eaffb893a8/scratchpad/reel
W=work
# Concatenate n1..n6 (hard cuts; dip-to-black baked between n4/n5), dissolve into endcard n7,
# then apply one consistent cinematic grade over the whole cut.
GRADE="eq=contrast=1.045:saturation=1.06:gamma=0.99,colorbalance=bs=0.015:rh=0.02:bh=-0.015,vignette=a=PI/5.5,noise=alls=6:allf=t,format=yuv420p"

ffmpeg -y -v error \
 -i $W/n1.mp4 -i $W/n2.mp4 -i $W/n3.mp4 -i $W/n4.mp4 -i $W/n5.mp4 -i $W/n6.mp4 -i $W/n7.mp4 \
 -filter_complex "
   [0:v][1:v][2:v][3:v][4:v][5:v]concat=n=6:v=1:a=0,fps=30,settb=AVTB,format=yuv420p[base];
   [6:v]fps=30,settb=AVTB,format=yuv420p[ec];
   [base][ec]xfade=transition=fade:duration=0.5:offset=29.1[cut];
   [cut]${GRADE}[v]
 " -map "[v]" -c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -preset medium -crf 15 -an $W/cut_graded.mp4

echo "cut dur: $(ffprobe -v error -show_entries format=duration -of csv=p=0 $W/cut_graded.mp4)s"
# QC frames across the timeline
mkdir -p $W/qc2
for t in 2 7 12 17 19.9 20.3 22 27 31; do
  ffmpeg -v error -y -ss $t -i $W/cut_graded.mp4 -frames:v 1 $W/qc2/t${t}.jpg
done
echo "QC frames written"