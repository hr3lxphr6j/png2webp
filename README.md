### png2webp
![image](https://github.com/hr3lxphr6j/png2webp/raw/master/screenshot.png)

一个批量把图片并行转webp格式的脚本（因为XnConvert单线程处理太慢。。。）   
png使用无损压缩，jpg等使用有损压缩
#### 依赖
- python3
- cwebp
#### 使用
```
png2webp.py [options] -i <directory>

[Options]
-h  打印帮助
-d  删除源文件
-r  处理子文件夹
-q  有损处理jpg,jpeg,tiff文件, 编码质量(0:small..100:big)
```