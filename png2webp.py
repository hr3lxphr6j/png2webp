import os
import sys
import getopt
import logging
import functools
import subprocess
from queue import Queue
from multiprocessing.dummy import Pool

logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)


def log(func: callable) -> callable:
    """
    装饰器，打印信息
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args: list, **kw: dict):
        i = args[0] or kw.get('input_file')
        lossless = args[2] or kw.get('lossless')
        input_file_size, output_file_size = func(*args, **kw)
        compression_ratio = output_file_size / input_file_size
        logging.info('%.2f%% %s %s' % (compression_ratio * 100, lossless, i))

    return wrapper


def get_pics(path: str, exts: tuple, recursive: bool = True) -> iter:
    """
    bfs搜索给定路径下图片文件
    :param path: 路径
    :param exts: 图片扩展名
    :param recursive: 是否递归处理子文件夹
    :return: 迭代器
    """
    queue = Queue()
    queue.put(path)
    while not queue.empty():
        root = queue.get()
        for f in os.listdir(root):
            full_name = os.path.join(root, f)
            if os.path.isdir(full_name) and recursive:
                queue.put(full_name)
            else:
                if os.path.splitext(f)[-1] in exts:
                    yield full_name


@log
def encode_to_webp(input_file: str, output_file: str, lossless: bool, quality: float, delete: bool) -> tuple:
    """
    编码输入图片到webp格式
    :param input_file: 输入文件名
    :param output_file: 输出文件名
    :param lossless: 是否使用无损编码
    :param quality: 有损编码质量
    :param delete: 是否删除源文件
    :return: 输入文件大小，输出文件大小
    """
    command = [
        'cwebp',
        '-preset', 'drawing',
        '-z', '9',
        '-m', '6',
        '-f', '0',
        '-mt',
        '-lossless' if lossless else '-q %.2f' % quality,
        input_file,
        '-o', output_file
    ]
    child = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    child.communicate()
    input_file_size = os.path.getsize(input_file)
    output_file_size = os.path.getsize(output_file)
    if delete:
        os.remove(input_file)
    return input_file_size, output_file_size


def print_help():
    """
    打印帮助
    :return:
    """
    print('''A script that can help you convert Pictures to Webp format.

usage: png2webp.py [options] -i <directory>
    
[Options]
-h  print this help.
-d  delete original files
-r  recursive process children directory.
-q  also process .jpg .jpeg .tiff files, quality factor of these file (0:small..100:big).
-i  input directory.''')


def print_error():
    """
    打印简易说明
    :return:
    """
    print('''usage: png2webp.py [options] -i <directory>
Use -h to get full help''', file=sys.stderr)


def parse_arg(argv: list) -> dict:
    """
    参数解析
    :param argv: 控制台参数列表
    :return: 参数字典
    """
    try:
        opts, args = getopt.getopt(argv, 'hdrq:i:')
    except getopt.GetoptError:
        print_error()
        exit(2)
    flag = {}
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            exit(0)
        elif opt == '-d':
            flag['delete'] = True
        elif opt == '-r':
            flag['recursive'] = True
        elif opt == '-q':
            flag['quality'] = arg
        elif opt == '-i':
            flag['input'] = arg
        pass
    return flag


def check_program(name: str) -> bool:
    """
    检查给定程序是否存在
    :param name: 程序名
    :return: 存在情况
    """
    try:
        subprocess.call(name, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False
    return True


def main(argv: list):
    """
    主函数
    :param argv: 控制台参数列表
    :return:
    """
    if not check_program('cwebp'):
        print('Can`t find "cwebp".\nPlease visit https://developers.google.com/speed/webp/ and download it.',
              file=sys.stderr)
        exit(2)
    if len(argv) == 0:
        print_error()
        exit(2)
    flag = parse_arg(argv)
    if not os.path.isdir(flag.get('input')):
        print('Can`t parse input "%s".' % flag.get('input'), file=sys.stderr)
        exit(2)
    pool = Pool()
    for f in get_pics(flag['input'],
                      ('.png', '.jpg', '.jpeg', '.tiff') if flag.get('quality') else ('.png',),
                      flag.get('recursive', False)):
        o, ext = os.path.splitext(f)
        o += '.webp'
        pool.apply_async(encode_to_webp, (f, o, ext == '.png', flag.get('quality', '100'), flag.get('delete', False)))
    pool.close()
    pool.join()


if __name__ == '__main__':
    main(sys.argv[1:])
