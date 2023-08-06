## A  Wrapper for mediainfo tool

#### Prerequisites

This tool needs mediainfo to be installed inorder to work properly.

On Ubuntu/Debian:

```
sudo apt install mediainfo
```

On Mac:

```
brew install mediainfo
```

#### Usage
##### To get the Information about the Video file

To get all available info about a particular track of the  video file. It works with all media types.

```
GetFileinfo_Audio_Video --file="some_video.mp4" --type={General/Audio/Video} --list_All_keys 

(or)

GetFileinfo_Audio_Video --file="some_video.mp4" --type={General/Audio/Video} -l

```

To get all available  tracks of the  video file.

```
GetFileinfo_Audio_Video -file=test.mp4 --type -h

(or)

GetFileinfo_Audio_Video -file=test.mp4 --type --help

```


To get all available info about the particular track option in the  video file.

```
GetFileinfo_Audio_Video -file=test.mp4 --type={General/Audio/Video} --options

```

To get  info about the particular track and particular option in the  video file.

```
GetFileinfo_Audio_Video -file=test.mp4 --type={General/Audio/Video} --option={Your track option}

```
