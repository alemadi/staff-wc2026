#!/bin/bash
set -e
cd /tmp/claude-0/-home-user-staff-wc2026/00e9bf4b-1013-52b1-b5fa-20eaffb893a8/scratchpad/reel
GOLD=0xE7C765
ffmpeg -y -v error \
 -stream_loop -1 -t 3.4 -i src/b_particles.mp4 \
 -filter_complex "
  [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=-0.015:saturation=1.15,setsar=1,vignette=a=PI/4.2,format=yuv420p[bg];
  [bg]drawtext=fontfile=fonts/Anton.ttf:text='STAFF CHALLENGE':fontcolor=${GOLD}:fontsize=120:x=(w-text_w)/2:y=740:shadowcolor=black@0.55:shadowx=2:shadowy=4[t1];
  [t1]drawtext=fontfile=fonts/Bebas.ttf:text='WORLD CUP 2026  ·  STAFF PREDICTION LEAGUE':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=890[t2];
  [t2]drawbox=x=(iw-400)/2:y=985:w=400:h=3:color=${GOLD}:t=fill[t3];
  [t3]drawtext=fontfile=fonts/Anton.ttf:text='SEE YOU IN 2030':fontcolor=${GOLD}:fontsize=92:x=(w-text_w)/2:y=1030:shadowcolor=black@0.55:shadowx=2:shadowy=4[t4];
  [t4]drawtext=fontfile=fonts/Bebas.ttf:text='STAFFCHALLENGE26.COM':fontcolor=white@0.9:fontsize=48:x=(w-text_w)/2:y=1770[t5];
  [t5]fade=t=out:st=3.05:d=0.35[v]
 " -map "[v]" -c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -preset medium -crf 16 -an work/n7.mp4
echo "endcard dur: $(ffprobe -v error -show_entries format=duration -of csv=p=0 work/n7.mp4)"
ffmpeg -v error -y -ss 1.2 -i work/n7.mp4 -frames:v 1 work/qc/n7.jpg
echo "done"