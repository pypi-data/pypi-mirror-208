import argparse
import asyncio
import sys

from . import trans

parser = argparse.ArgumentParser(
    prog='python -m markji_wordcard_assistant',
    epilog='More examples see README.md')
parser.add_argument('-f',
                    required=True,
                    metavar='',
                    help="指定输入的文件", )
parser.add_argument("-v", "--voice",
                    metavar='',
                    default="en-GB",
                    help="[可选]指定英式美式发英,默认`en-GB`,可选`en-US`", )
parser.add_argument("-b", "--by",
                    metavar='',
                    default="default",
                    help="[可选]指定选定的语音来源,默认default,可选youdao edge", )
args = parser.parse_args()

try:
    asyncio.run(trans.trans(args.f, args.voice, args.by))
except FileNotFoundError as e:
    print(e)
    sys.exit(-1)
