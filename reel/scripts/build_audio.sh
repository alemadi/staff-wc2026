#!/bin/bash
cd /tmp/claude-0/-home-user-staff-wc2026/00e9bf4b-1013-52b1-b5fa-20eaffb893a8/scratchpad/reel/audio

ffmpeg -y -v error \
 -ss 34.0 -t 32.7 -i m_heroic.mp3 \
 -i vo1_open_clean.wav -i vo2_stats_clean.wav -i vo3_final_clean.wav -i vo5_champion_clean.wav -i vo6_end_clean.wav \
 -i sfx_boom.wav -i sfx_riser.wav -i sfx_subdrop.wav -i sfx_shimmer.wav -i sfx_boom.wav \
 -filter_complex "
  [0:a]highpass=f=28,aformat=channel_layouts=stereo:sample_rates=48000,volume=0.80,afade=t=in:st=0:d=1.3,afade=t=out:st=30.9:d=1.6[music];

  [1:a]aformat=channel_layouts=stereo:sample_rates=48000,adelay=500|500,volume=1.55[v1];
  [2:a]aformat=channel_layouts=stereo:sample_rates=48000,adelay=6900|6900,volume=1.55[v2];
  [3:a]aformat=channel_layouts=stereo:sample_rates=48000,adelay=12400|12400,volume=1.55[v3];
  [4:a]aformat=channel_layouts=stereo:sample_rates=48000,adelay=21000|21000,volume=1.75[v4];
  [5:a]aformat=channel_layouts=stereo:sample_rates=48000,adelay=26800|26800,volume=1.55[v5];
  [v1][v2][v3][v4][v5]amix=inputs=5:normalize=0:dropout_transition=0,alimiter=limit=0.95[vobus];
  [vobus]asplit=2[vo_key0][vo_mix];
  [vo_key0]apad=whole_dur=32.7[vo_key];

  [music][vo_key]sidechaincompress=threshold=0.06:ratio=7:attack=12:release=320[music_duck];

  [6:a]adelay=20000|20000,volume=1.0[boom];
  [7:a]adelay=18050|18050,volume=0.85[riser];
  [8:a]adelay=20000|20000,volume=0.9[sub];
  [9:a]adelay=25150|25150,volume=0.65[shim];
  [10:a]adelay=0|0,volume=0.5[boom0];
  [boom][riser][sub][shim][boom0]amix=inputs=5:normalize=0,alimiter=limit=0.97[sfxbus];

  [music_duck][vo_mix][sfxbus]amix=inputs=3:normalize=0[premix];
  [premix]alimiter=limit=0.9,loudnorm=I=-14:TP=-1.0:LRA=11,aformat=channel_layouts=stereo:sample_rates=48000[aout]
 " -map "[aout]" -c:a pcm_s16le mix.wav || { echo "FFMPEG MIX FAILED"; exit 1; }

echo "=== MIX built: $(ffprobe -v error -show_entries format=duration -of csv=p=0 mix.wav)s ==="
echo "=== Overall loudness / peak ==="
ffmpeg -v error -i mix.wav -af "volumedetect" -f null - 2>&1 | grep -iE "mean_volume|max_volume" || echo "(volumedetect produced no match)"
echo "--- per-region mean level ---"
for seg in "open:0:5" "stats:7:4" "final:12:5" "drop:20:2" "champ_vo:21:3" "maldives:26:4" "endcard:30:2.5"; do
  IFS=: read name ss dd <<< "$seg"
  mv=$(ffmpeg -v error -ss $ss -t $dd -i mix.wav -af volumedetect -f null - 2>&1 | grep mean_volume | grep -oE '\-?[0-9.]+ dB')
  printf "  %-10s t=%-4s mean=%s\n" "$name" "$ss" "$mv"
done
echo "done"