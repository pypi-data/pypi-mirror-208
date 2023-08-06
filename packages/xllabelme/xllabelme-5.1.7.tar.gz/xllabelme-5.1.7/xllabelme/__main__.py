import argparse
import codecs
import logging
import os
import os.path as osp
import sys
import yaml

import cv2  # 这个库也要打包，所以import进来

# from qtpy import QtCore
# from qtpy import QtWidgets  # ckz 220831周三14:39，debug模式下运行有问题
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QCoreApplication

from xllabelme import __appname__, __version__
from xllabelme.app import MainWindow
from xllabelme.xlapp import XlMainWindow
from xllabelme.config import get_config
from xllabelme.logger import logger
from xllabelme.utils import newIcon
import xllabelme.ts

from pyxllib.prog.pupil import dprint  # 在任意地方均可以使用dprint调试
from pyxllib.prog.pupil import format_exception
from pyxllib.ext.qt import show_message_box


def default_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", "-V", action="store_true", help="show version"
    )
    parser.add_argument(
        "--reset-config", action="store_true", help="reset qt config"
    )
    parser.add_argument(
        "--logger-level",
        default="info",
        choices=["debug", "info", "warning", "fatal", "error"],
        help="logger level",
    )
    # 位置参数，可以直接输入 文件/目录，自动 open/open dir
    parser.add_argument("filename", nargs="?", help="image or label filename")
    parser.add_argument(
        "--output",
        "-O",
        "-o",
        help="output file or directory (if it ends with .json it is "
             "recognized as file, else as directory)",
    )
    # 从配置文件读取一套默认配置参数
    default_config_file = os.path.join(os.path.expanduser("~"), ".labelmerc")
    parser.add_argument(
        "--config",
        dest="config",
        help="config file or yaml-format string (default: {})".format(
            default_config_file
        ),
        default=default_config_file,
    )
    # config for the gui
    parser.add_argument(
        "--nodata",
        dest="store_data",
        action="store_false",
        help="stop storing image data to JSON file",
        default=False,
    )
    parser.add_argument(
        "--autosave",
        dest="auto_save",
        action="store_true",
        help="auto save",
        # argparse.SUPPRESS作用：未设置--nodata时不存在nodata变量，区别于nodata默认值是False
        # 目的在于后面要在文件默认配置基础上，覆盖命令行的配置，如果命令行未设置，不能强行覆盖一个False
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--nosortlabels",
        dest="sort_labels",
        action="store_false",
        help="stop sorting labels",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--flags",
        help="comma separated list of flags OR file containing flags",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--labelflags",
        dest="label_flags",
        help=r"yaml string of label specific flags OR file containing json "
             r"string of label specific flags (ex. {person-\d+: [male, tall], "
             r"dog-\d+: [black, brown, white], .*: [occluded]})",  # NOQA
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--labels",
        help="comma separated list of labels OR file containing labels",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--validatelabel",
        dest="validate_label",
        choices=["exact"],
        help="label validation types",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--keep-prev",
        action="store_true",
        help="keep annotation of previous frame",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        help="epsilon to find nearest vertex on canvas",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--lang",
        type=str,
        help="set language",
        default=QtCore.QLocale.system().name(),
    )
    return parser


def main(mainwin=XlMainWindow):
    """ 进行重封装，可以重新指定appname、version版本，以及主窗口程序mainwin """
    args = default_argument_parser().parse_args()

    if args.version:
        print("{0} {1}".format(__appname__, __version__))
        sys.exit(0)

    logger.setLevel(getattr(logging, args.logger_level.upper()))

    if hasattr(args, "flags"):
        if os.path.isfile(args.flags):
            with codecs.open(args.flags, "r", encoding="utf-8") as f:
                args.flags = [line.strip() for line in f if line.strip()]
        else:
            args.flags = [line for line in args.flags.split(",") if line]

    if hasattr(args, "labels"):
        if os.path.isfile(args.labels):
            with codecs.open(args.labels, "r", encoding="utf-8") as f:
                args.labels = [line.strip() for line in f if line.strip()]
        else:
            args.labels = [line for line in args.labels.split(",") if line]

    if hasattr(args, "label_flags"):
        if os.path.isfile(args.label_flags):
            with codecs.open(args.label_flags, "r", encoding="utf-8") as f:
                args.label_flags = yaml.safe_load(f)
        else:
            args.label_flags = yaml.safe_load(args.label_flags)

    config_from_args = args.__dict__
    config_from_args.pop("version")
    reset_config = config_from_args.pop("reset_config")
    filename = config_from_args.pop("filename")
    output = config_from_args.pop("output")
    config_file_or_yaml = config_from_args.pop("config")
    config = get_config(config_file_or_yaml, config_from_args)

    if not config["labels"] and config["validate_label"]:
        logger.error(
            "--labels must be specified with --validatelabel or "
            "validate_label: true in the config file "
            "(ex. ~/.labelmerc)."
        )
        sys.exit(1)

    output_file = None
    output_dir = None
    if output is not None:
        if output.endswith(".json"):
            output_file = output
        else:
            output_dir = output

    translator = QtCore.QTranslator()
    # 写不存在的值也没影响，默认就是变成英文
    # translator.load(osp.dirname(osp.abspath(__file__)) + "/translate/" + 'zh_CN.qm')
    translator.loadFromData(getattr(xllabelme.ts, args.lang))
    # app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(newIcon("icon.png"))
    app.installTranslator(translator)
    win = mainwin(
        config=config,
        filename=filename,
        output_file=output_file,
        output_dir=output_dir,
    )
    if reset_config:
        logger.info("Resetting Qt config: %s" % win.settings.fileName())
        win.settings.clear()
        sys.exit(0)

    win.show()
    win.raise_()
    sys.exit(app.exec_())


def handle_exception(exc_type, exc_value, exc_traceback):
    show_message_box(format_exception(exc_value), '程序跑路了，给管理员发这个截图让他来破案吧！')


# this main block is required to generate executable by pyinstaller
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sys.excepthook = handle_exception  # 全局异常捕获。既能获得错误，也能防止软件崩溃。
    main(XlMainWindow)
