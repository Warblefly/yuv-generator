# yuv-generator
Generate test patterns for TV, natively in YUV, output to YUV4MPEG file

Convert the output to something useful for a display with a line such as:

ffmpeg -stream_loop -1 -i .\output.y4m -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -vf format=yuv444p10le -crf 0 .\output.mp4

The result will be a beautiful ten-bit test pattern with blank audio tracks.
