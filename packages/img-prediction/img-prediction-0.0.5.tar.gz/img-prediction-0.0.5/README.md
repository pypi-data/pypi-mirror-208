# 要求
- python >= 3.6

# 安装
```shell
pip3 install img-prediction
```

# 使用

```shell
$ predict -h                                                                                                                                                                                                                                                                         :( 130 23-05-17 - 10:05:44
usage: prediction.py [-h] -w WEIGHT_FILE_PATH -i INPUT [-o OUTPUT_DIR] [-s SCORE_THRESHOLD] [-v] [-l LOG_FILE]

Image Segmentation And Mosaic

options:
  -h, --help            show this help message and exit
  -w WEIGHT_FILE_PATH, --weight-file-path WEIGHT_FILE_PATH
                        The weight file path
  -i INPUT, --input INPUT
                        Input image file
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        The dir of processed images
  -s SCORE_THRESHOLD, --score-threshold SCORE_THRESHOLD
                        The fractional threshold of the identification area
  -v, --verbose         Output detailed log
  -l LOG_FILE, --log-file LOG_FILE
                        The path of log file, default is ./prediction.log
```

* `-w` 指定权重文件
* `-i` 输入的图片文件
* `-o` 输出路径
* `-s` 预测分数阈值(0-1之间, 默认0.5，值越大越精确)
* `-v` 输出日志到文件
* `-l` 日志文件路径