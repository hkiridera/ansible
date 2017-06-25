#!/bin/sh

while :
do
rm /tmp/encord.tmp
ls -tr | grep .ts | grep -v .err | awk '{{sub(".ts","")}{print $0}}' >> /tmp/encord.tmp
cd /mnt/nas/エンコード中

awk '{{sub(".ts","")}{print $0}}' /tmp/encord.tmp | xargs -i ffmpeg -i '{}.ts'  -c:v libx264 -b:v 2000k -s 1280x720 -r 29.97 -aspect 16:9 -preset medium  '../エンコード済/{}.mp4' >> /tmp/encord.log
#awk '{{sub(".ts","")}{print $0}}' /tmp/encord.tmp | xargs -i ls {}.ts



#cat /tmp/encord.tmp
#cat /tmp/encord.tmp | awk '{print "../エンコード済/"$0".mp4"}' |xargs -i ls -la {}
#cat /tmp/encord.tmp | awk '{print "../エンコード済/"$0".mp4"}' |xargs -i rm {}
done
