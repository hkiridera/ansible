sudo apt-get update
sudo apt-get -y --force-yes install autoconf automake build-essential libass-dev libfreetype6-dev \
  libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev \
  libxcb-xfixes0-dev pkg-config texinfo zlib1g-dev yasm libx264-dev

mkdir $HOME/work/ffmpeg
cd $HOME/work/ffmpeg/
wget -O fdk-aac.tar.gz https://github.com/mstorsjo/fdk-aac/tarball/master
tar xvzf fdk-aac.tar.gz
cd mstorsjo-fdk-*/
autoreconf -fiv
./configure
make -j4
sudo make install

cd $HOME/work/ffmpeg/
wget https://www.ffmpeg.org/releases/ffmpeg-2.7.2.tar.xz
tar xf ffmpeg-2.7.2.tar.xz
cd ffmpeg-2.7.2/
cp ../../myconfig.sh ./
sh myconfig.sh
time make -j4 2>&1 |tee make.log
sudo make install

sudo /sbin/ldconfig
