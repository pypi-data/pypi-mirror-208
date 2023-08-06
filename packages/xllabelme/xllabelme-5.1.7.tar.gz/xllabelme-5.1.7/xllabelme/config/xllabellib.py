import functools
import json
import os
import os.path as osp
import re
from statistics import mean
import time
import sys

import requests
import webbrowser

import numpy as np

from PyQt5.QtCore import QPointF, QTranslator, QLocale, QLibraryInfo
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox, QActionGroup, QApplication, QWidget
from qtpy import QtGui
from qtpy.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QColor

from pyxllib.file.specialist import XlPath
from pyxllib.algo.geo import rect_bounds
from pyxllib.algo.pupil import make_index_function
from pyxllib.prog.pupil import DictTool
from pyxlpr.ai.clientlib import XlAiClient
from pyxllib.algo.shapelylib import ShapelyPolygon
# from pyxllib.xlcv import xlcv
from pyxllib.cv.rgbfmt import RgbFormatter

from xllabelme import utils
from xllabelme.widgets import LabelListWidgetItem
from xllabelme.shape import Shape

_CONFIGS = {
    '原版labelme': {},
    'xllabelme': {},
    'm2302中科院题库':  # 这是比较旧的一套配置字段名
        {'_attrs':
             [['line_id', 1, 'int'],
              ['content_type', 1, 'str', ('印刷体', '手写体')],
              ["content_class", 1, "str", ("文本", "公式", "图片", "表格", "删除")],
              ['text', 1, 'str'],
              ],
         'label_shape_color': 'content_type,content_class'.split(','),
         'label_shape_color2': ['line_id'],
         'default_label': json.dumps({'line_id': 1,
                                      'content_type': '印刷体',
                                      'content_class': '文本',
                                      'text': ''}, ensure_ascii=False),
         },
    'm2303表格标注': {},
    'm2303表格标注二阶段': {
        '_attrs': [['text', 1, 'str', ('可见横线', '可见竖线', '不可见横线', '不可见竖线')]],
        'label_shape_color': ['text'],
    },
    'm2305公式符号标注': {
        'label_shape_color': ['loc'],
        'label_shape_color2': ['symbo'],
        'label_shape_color3': ['symbo', 'loc'],
    },
    # '渊亭OCR':  # 这是比较旧的一套配置字段名
    #     {'_attrs':
    #          [['content_type', 1, 'str', ('印刷体', '手写体', '印章', '其它')],
    #           ['content_kv', 1, 'str', ('key', 'value')],
    #           ["content_class", 1, "str", ("姓名", "身份证号", "联系方式", "采样时间", "检测时间", "核酸结果", "其它类")],
    #           ['text', 1, 'str'],
    #           ],
    #      'label_shape_color': 'content_class'.split(','),
    #      'label_vertex_fill_color': 'content_kv'.split(','),
    #      'default_label': json.dumps({'content_type': '印刷体', 'content_kv': 'value',
    #                                   'content_class': '其它类', 'text': ''}, ensure_ascii=False),
    #      },
    # '核酸检测':  # 这是比较旧的一套配置字段名
    #     {'_attrs':
    #          [['text', 1, 'str'],
    #           ["content_class", 1, "str", ("其它类", "姓名", "身份证号", "联系方式", "采样时间", "检测时间", "核酸结果")],
    #           ['content_kv', 1, 'str', ('key', 'value')],
    #           ],
    #      'label_shape_color': 'content_class'.split(','),
    #      'default_label': json.dumps({'text': '', 'content_class': '其它类', 'content_kv': 'value'}, ensure_ascii=False),
    #      },
    # '三码合一入学判定':
    #     {'_attrs':
    #          [['text', 1, 'str'],
    #           ["category", 1, "str", ("姓名", "身份证", "联系方式", "采样时间", "检测时间", "核酸结果",
    #                                   "14天经过或途经", "健康码颜色", "其他类")],
    #           ['text_kv', 1, 'str', ('key', 'value')],
    #           ],
    #      'label_shape_color': 'category'.split(','),
    #      'default_label': json.dumps({'text': '', 'category': '其他类', 'text_kv': 'value'}, ensure_ascii=False),
    #      },
    '文字通用':
        {'_attrs':
             [['text', 1, 'str'],
              ['category', 1, 'str'],
              ['text_kv', 1, 'str', ('other', 'key', 'value')],
              ['text_type', 1, 'str', ('印刷体', '手写体', '其它')],
              ],
         'label_line_color': ['category'],
         'label_vertex_fill_color': ['text_kv']
         },
    'XlCoco': {
        '_attrs':
            [['id', 1, 'int'],
             ['text', 1, 'str'],  # 这个本来叫label，但为了规范，统一成text
             ['category_id', 1, 'int'],
             ['content_type', 1, 'str', ('印刷体', '手写体', '印章', '身份证', '表格', '其它证件类', '其它')],
             ['content_class', 1, 'str'],
             ['content_kv', 1, 'str', ('key', 'value')],
             ['bbox', 0],
             ['area', 0],
             ['image_id', 0],
             ['segmentation', 0],
             ['iscrowd', 0],
             ['points', 0, 'list'],
             ['shape_color', 0, 'list'],
             ['line_color', 0, 'list'],
             ['vertex_color', 0, 'list'],
             ],
        'label_shape_color': 'category_id,content_class'.split(','),
        'label_line_color': 'gt_category_id,gt_category_name'.split(','),
        'label_vertex_fill_color': 'dt_category_id,dt_category_name,content_kv'.split(','),
    },
    # 'Sroie2019+':
    #     {'_attrs':
    #          [['text', 1, 'str'],  # 原来叫label的，改成text
    #           ['sroie_class', 1, 'str', ('other', 'company', 'address', 'date', 'total')],
    #           ['sroie_kv', 1, 'str', ('other', 'key', 'value')],
    #           ]
    #      },
}


def q_pixmap_to_np_array(qpixmap):
    qimage = qpixmap.toImage()
    width, height = qimage.width(), qimage.height()
    channel_count = qimage.pixelFormat().channelCount()
    buffer = qimage.constBits().asarray(width * height * channel_count)
    np_array = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, channel_count))
    return np_array


def np_array_to_q_pixmap(np_array):
    if len(np_array.shape) == 2:
        height, width = np_array.shape
        channel_count = 1
    else:
        height, width, channel_count = np_array.shape
    bytes_per_line = channel_count * width

    if channel_count == 1:
        format = QImage.Format_Grayscale8
    elif channel_count == 3:
        format = QImage.Format_RGB888
    elif channel_count == 4:
        format = QImage.Format_RGBA8888
    else:
        raise ValueError("Unsupported channel count: {}".format(channel_count))

    qimage = QImage(np_array.data, width, height, bytes_per_line, format)
    return QPixmap.fromImage(qimage)


def __1_自定义项目():
    pass


class 原版labelme:
    """ 不同项目任务可以继承这个类，进行一些功能的定制
    这里设计默认是labelme原版功能
    """

    def __init__(self, mainwin):
        self.mainwin = mainwin
        self.xllabel = mainwin.xllabel
        mainwin.showMaximized()  # 窗口最大化
        self.菜单新增动作 = []
        self.create()

    def __0_基础功能(self):
        pass

    def 查找控件(self, 名称, 类型=QWidget):
        return self.mainwin.findChild(类型, 名称)

    def set_label_color(self, label, color=None):
        """ 对普通文本值，做固定颜色映射 """
        from xllabelme.xlapp import _COLORS
        if isinstance(color, str):
            color = RgbFormatter.from_name(color).to_tuple()
        self.mainwin.labelDialog.addLabelHistory(label)  # 文本加入检索
        # 主要为了兼容xllabelme的一个tolist操作，所以要转np
        _COLORS[label] = np.array(color, 'uint8')  # 颜色做固定映射
        _COLORS[str({'text': label})] = np.array(color, 'uint8')  # 被转成字典的时候，也要带颜色映射规则

    def __1_菜单类通用工程功能(self):
        pass

    def 菜单添加动作(self, menu,
               text=None,  # 显示文本
               slot=None,  # 触发函数
               shortcut=None,  # 快捷键
               icon=None,  # 预设的图标
               tip=None,  # 详细提示内容
               checkable=False,  # 可勾选？
               enabled=True,  # 组件可使用？
               checked=False,  # 选中状态？
               name=None,  # 设一个全局名称，可以在其他地方需要的时候检索
               ):
        """ 通过这个函数添加的组会，切换project的时候，会自动进行检索销毁

        注意这里的menu不是QMenu对象，而是菜单功能清单，原理流程是
            1、提前用list存储到mainwin.actions里的动作列表，要展示的actions清单
            2、调用main.populateModeActions，可以把mainwin.acitons里的功能菜单都更新出来
            3、新建行为的时候，这个类里会做备份记录
            4、destroy自动销毁的时候，会用list.index进行检索把对应的action都移除
        """
        if text is None:
            self.菜单新增动作.append([menu, None])
            menu.append(None)
        else:
            action = utils.newAction(self.mainwin, self.mainwin.tr(text), slot,
                                     shortcut, icon, self.mainwin.tr(tip), checkable, enabled, checked)
            if name:
                action.setObjectName(name)
            self.菜单新增动作.append([menu, action])
            menu.append(action)
            return action

    def 菜单栏_编辑_添加动作(self, *args, **kwargs):
        return self.菜单添加动作(self.mainwin.actions.editMenu, *args, **kwargs)

    def 菜单栏_帮助_添加文档(self, 文档名称, 文档链接):
        return self.菜单添加动作(self.mainwin.actions.helpMenu, 文档名称, lambda: webbrowser.open(文档链接))

    def 左侧栏菜单添加动作(self, *args, **kwargs):
        return self.菜单添加动作(self.mainwin.actions.tool, *args, **kwargs)

    def 画布右键菜单添加动作(self, *args, **kwargs):
        return self.菜单添加动作(self.mainwin.actions.menu, *args, **kwargs)

    def 文件列表右键菜单添加动作(self, *args, **kwargs):
        return self.菜单添加动作(self.mainwin.actions.fileListMenu, *args, **kwargs)

    def __2_定制菜单(self):
        pass

    def config_settings_menu(self):
        """ 菜单栏_设置 """
        mainwin, xllabel = self.mainwin, self.xllabel

        def create_project_menu():
            # 1 关联选择任务后的回调函数
            def func(action):
                # 1 内置数据格式
                action.setCheckable(True)
                action.setChecked(True)
                xllabel.reset(action.text())
                # 一个时间，只能开启一个模式
                for a in task_menu.findChildren(QAction):
                    if a is not action:
                        a.setChecked(False)

                # 2 如果是自定义模式，弹出编辑窗
                pass

                # 3 保存配置
                xllabel.save_config()

            task_menu = QMenu(mainwin.tr('Project'), settings_menu)
            task_menu.triggered.connect(func)

            # 2 往Label菜单添加选项功能
            actions = []
            # 代码里配置的默认项目
            for x in _CONFIGS.keys():
                actions.append(QAction(x, task_menu))
            # 配置文件里也可以额外添加项目
            if xllabel.meta_cfg['custom_modes']:
                actions.append(None)
                for x in xllabel.meta_cfg['custom_modes'].keys():
                    actions.append(QAction(x, task_menu))
            # 激活初始mode模式的标记
            for a in actions:
                if a.text() == xllabel.meta_cfg['current_mode']:
                    a.setCheckable(True)
                    a.setChecked(True)
                    break
            utils.addActions(task_menu, actions)
            return task_menu

        def create_auto_rec_text_action():
            def func(x):
                xllabel.auto_rec_text = x

                if xllabel.auto_rec_text:
                    os.environ['XlAiAccounts'] = 'eyJwcml1IjogeyJ0b2tlbiI6ICJ4bGxhYmVsbWV5XipBOXlraiJ9fQ=='
                    try:
                        xllabel.xlapi = XlAiClient()
                    except requests.exceptions.ConnectionError:
                        # 没有网络
                        xllabel.xlapi = None
                        a.setChecked(False)
                        # 提示
                        msg_box = QMessageBox(QMessageBox.Information, "xllabelme标注工具：连接自动识别的API失败",
                                              "尝试连接xmutpriu.com的api失败，请检查网络问题，比如关闭梯子。\n"
                                              '如果仍然连接不上，可能是服务器的问题，请联系"管理员"。')
                        msg_box.setStandardButtons(QMessageBox.Ok)
                        msg_box.exec_()

                xllabel.save_config()

            a = QAction(mainwin.tr('Automatically recognize'), settings_menu)
            a.setCheckable(True)
            if xllabel.auto_rec_text:
                a.setChecked(True)
                func(True)
            else:
                a.setChecked(False)
            a.triggered.connect(func)
            return a

        def create_set_image_root_action():
            a = QAction(mainwin.tr('Set pictures directory'), settings_menu)

            def func():
                xllabel.image_root = XlPath(QFileDialog.getExistingDirectory(xllabel.image_root))
                self.mainwin.importDirImages(xllabel.mainwin.lastOpenDir)

            a.triggered.connect(func)
            return a

        def create_reset_config_action():
            a = QAction(mainwin.tr('Restore default labelme configuration'), settings_menu)

            def func():
                (XlPath.home() / '.labelmerc').delete()
                msg_box = QMessageBox(QMessageBox.Information, "恢复labelme的默认配置",
                                      "注意，需要重启软件才能生效。")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()

            a.triggered.connect(func)
            return a

        def create_savefile_without_dialog_action():
            a = utils.newAction(mainwin,
                                mainwin.tr("关闭保存标注文件的弹窗"),
                                lambda x: a.setChecked(x),
                                None,  # 快捷键
                                None,  # 图标
                                mainwin.tr("无json标注文件情况下，保存时不启用dialog而是自动生成标注文件"),  # 左下角的提示
                                checkable=True,
                                checked=True,
                                )
            mainwin.savefile_without_dialog_action = a
            return a

        settings_menu = self.mainwin.menus.settings
        settings_menu.addMenu(create_project_menu())
        settings_menu.addSeparator()
        settings_menu.addAction(create_auto_rec_text_action())
        settings_menu.addAction(create_savefile_without_dialog_action())
        # 关闭该功能，发现原本就有类似的功能，是我重复造轮子了
        # settings_menu.addAction(create_set_image_root_action())
        settings_menu.addSeparator()
        settings_menu.addAction(create_reset_config_action())

    def create(self, update=True):
        """ 子类也可能调用这个方法，此时populateModeActions不需要提前执行 """
        mainwin = self.mainwin

        # 1 设置菜单
        self.config_settings_menu()

        # 2 编辑菜单
        # 这个功能原labelme默认是开启的，导致兼职很容易经常误触增加多边形顶点，默认应该关闭
        self.菜单栏_编辑_添加动作()
        mainwin.add_point_to_edge_action = \
            self.菜单栏_编辑_添加动作('允许在多边形边上点击添加新顶点', checkable=True, tip='选中shape的edge时，增加分割点')
        mainwin.delete_selected_shape_with_warning_action = \
            self.菜单栏_编辑_添加动作('删除形状时会弹出提示框', checkable=True, checked=True, tip='选中shape的edge时，增加分割点')

        # 3 画布菜单
        self.画布右键菜单添加动作()
        mainwin.convert_to_rectangle_action = \
            self.画布右键菜单添加动作('将该多边形转为矩形', self.convert_to_rectangle, enabled=False)
        mainwin.split_shape_action = \
            self.画布右键菜单添加动作('切分该形状', self.xllabel.split_shape, enabled=False,
                            tip='在当前鼠标点击位置，将一个shape拆成两个shape（注意，该功能会强制拆出两个矩形框）')
        self.画布右键菜单添加动作()
        self.画布右键菜单添加动作('旋转图片', self.rotate_image,
                        tip='将图片和当前标注的形状，顺时针旋转90度，可以多次操作调整到合适方向。'
                            '注意1：软件中操作并未改变原始图片，需要保存标注文件后，外部图片文件才会更新。'
                            '注意2：图片操作目前是撤销不了的，不过可以不保存再重新打开文件恢复初始状态。')
        # self.画布右键菜单添加动作('歪斜图片矫正', self.deskew_image,
        #                 tip='歪斜比较严重的图片，可以尝试使用该功能矫正。'
        #                     '注意1：软件中操作并未改变原始图片，需要保存标注文件后，外部图片文件才会更新。'
        #                     '注意2：图片操作目前是撤销不了的，不过可以不保存再重新打开文件恢复初始状态。')

        # + 更新菜单的显示
        if update:
            mainwin.populateModeActions()

    def destroy(self):
        """ 销毁项目相关配置 """
        self.mainwin.menus.settings.clear()

        for menu, action in list(reversed(self.菜单新增动作)):
            if action is not None:  # 如果 action 不是 None，那么从 menu 中移除它
                action.deleteLater()  # 这个好像不用显式执行，其他官方原本的action都没有执行，但执行下应该问题也不大
            for i in range(len(menu) - 1, -1, -1):
                if menu[i] is action:
                    menu.pop(i)
                    break
        self.菜单新增动作 = []  # 清空 菜单新增动作 列表

    def __3_修改原版有的接口(self):
        """ 原版labelme有实现，但这里作了定制修改 """

    def shapeSelectionChanged(self, n_selected):
        """ 遍历所有跟选中shape时会激活有关的Action动作 """
        mainwin = self.mainwin
        mainwin.convert_to_rectangle_action.setEnabled(n_selected)
        mainwin.split_shape_action.setEnabled(n_selected)

    def updateShape(self, shape, label_list_item=None):
        """
        :param shape:
        :param label_list_item: item是shape的父级，挂在labelList下的项目
        """
        mainwin = self.mainwin
        label_list_item = LabelListWidgetItem(shape.label, shape)
        hashtext = shape.label

        def parse_htext(htext):
            if htext and not mainwin.uniqLabelList.findItemsByLabel(htext):
                item = mainwin.uniqLabelList.createItemFromLabel(htext)
                mainwin.uniqLabelList.addItem(item)
                rgb = mainwin._get_rgb_by_label(htext)
                mainwin.uniqLabelList.setItemLabel(item, htext, rgb)
                return rgb
            elif htext:
                return mainwin._get_rgb_by_label(htext)
            else:
                return None

        parse_htext(hashtext)
        mainwin.labelDialog.addLabelHistory(hashtext)

        mainwin._update_shape_color(shape)

        return label_list_item

    def get_default_label(self, shape=None):
        """ 这个是自己自己扩展的一个获得默认文本值的功能 """
        return ''

    def newShape(self, text=None):
        """ 新建标注框时的规则
        """
        mainwin = self.mainwin
        items = mainwin.uniqLabelList.selectedItems()
        if items:
            text = items[0].data(Qt.UserRole)
        flags = {}
        group_id = None
        if mainwin._config["display_label_popup"]:
            previous_text = mainwin.labelDialog.edit.text()
            text, flags, group_id = mainwin.labelDialog.popUp(text)
            if not text:
                mainwin.labelDialog.edit.setText(previous_text)

        if text is None:
            text = self.get_default_label(shape=mainwin.canvas.shapes[-1])

        if text and not mainwin.validateLabel(text):
            mainwin.errorMessage(
                mainwin.tr("Invalid label"),
                mainwin.tr("Invalid label '{}' with validation type '{}'").format(
                    text, mainwin._config["validate_label"]
                ),
            )
            text = ""
        if text:
            mainwin.labelList.clearSelection()
            shape = mainwin.canvas.setLastLabel(text, flags)
            shape.group_id = group_id
            # shape.description = description
            mainwin.addLabel(shape)
            mainwin.actions.editMode.setEnabled(True)
            mainwin.actions.undoLastPoint.setEnabled(False)
            mainwin.actions.undo.setEnabled(True)
            mainwin.setDirty()
        else:
            mainwin.canvas.undoLastLine()
            mainwin.canvas.shapesBackups.pop()

    def __4_自己扩展的功能(self):
        pass

    def open_last_workspace(self):
        """ 打开上一次退出软件的工作空间状态 """
        # 如果保存了目录和文件，打开上次工作状态
        if 'lastOpenDir' in self.xllabel.meta_cfg:
            d = XlPath(self.xllabel.meta_cfg['lastOpenDir'])
            if d.is_dir():
                if 'filename' in self.xllabel.meta_cfg:
                    p = d / self.xllabel.meta_cfg['filename']
                    if p.is_file():
                        self.mainwin.importDirImages(d, filename=str(p), offset=0)
                        return
                self.mainwin.importDirImages(d)

    def convert_to_rectangle(self):
        """ 将shape形状改为四边形 """
        item, shape = self.xllabel.get_current_select_shape()
        if shape:
            shape.shape_type = 'rectangle'
            pts = [(p.x(), p.y()) for p in shape.points]
            l, t, r, b = rect_bounds(pts)
            shape.points = [QPointF(l, t), QPointF(r, b)]
            self.mainwin.updateShape(shape, item)
            self.mainwin.setDirty()

    def rotate_image(self):
        """ 旋转图片，每次执行顺时针旋转90度 """

        def flip_points(sp, h):
            from pyxllib.algo.geo import resort_quad_points
            pts = sp.points
            if sp.shape_type == 'rectangle':
                # 矩形要特殊处理，仍然确保第1个点在左上角
                x1, y1 = pts[0].x(), pts[0].y()
                x2, y2 = pts[1].x(), pts[1].y()

                pts[0].setX(h - y2)
                pts[0].setY(x1)
                pts[1].setX(h - y1)
                pts[1].setY(x2)
            elif sp.shape_type == 'polygon' and len(pts) == 4:
                pts = [[h - p.y(), p.x()] for p in pts]
                pts = resort_quad_points(pts)
                for p1, p2 in zip(sp.points, pts):
                    p1.setX(p2[0])
                    p1.setY(p2[1])
            else:  # 其他形状暂不特殊处理
                for point in sp.points:
                    x = point.x()  # 要中转存储下，不然等下x会被新值覆盖
                    point.setX(h - point.y())
                    point.setY(x)

        from PyQt5.QtGui import QTransform

        # 1 旋转shapes坐标
        mainwin = self.mainwin
        canvas = mainwin.canvas
        h = canvas.pixmap.height()
        shapes = canvas.shapes
        for sp in shapes:
            flip_points(sp, h)

        # 2 旋转图片
        mainwin.updateShapes(shapes)
        transform = QTransform()
        transform.rotate(90)
        canvas.pixmap = canvas.pixmap.transformed(transform)
        mainwin.image = canvas.pixmap.toImage()

        # 3 end
        canvas.repaint()
        mainwin.setDirty(3)

    def deskew_image(self):
        """ 歪斜图片矫正 """
        from pyxllib.xlcv import xlcv
        mainwin = self.mainwin
        canvas = mainwin.canvas
        image = q_pixmap_to_np_array(canvas.pixmap)
        image = xlcv.deskew_image(image)
        canvas.pixmap = np_array_to_q_pixmap(image)
        canvas.repaint()
        mainwin.setDirty(2)

    def move_file(self, dst):
        """ 把指定的文件移到其他目录、子目录里，可以参考 'm2303表格标注' 里的运用 """
        # 0 准备
        m = self.mainwin
        fw = self.fileListWidget
        item = fw.currentItem()
        t = item.text()

        if t.startswith(dst + '/'):
            # 已经是分好类的，不处理
            return

        dst_path = XlPath.init(dst, m.lastOpenDir)
        dst_path.mkdir(exist_ok=True)

        # 1 移动文件
        p = m.get_image_path()
        p.move(dst_path / p.name)
        p2 = m.get_label_path()
        p2.move(dst_path / p2.name)

        # 2 更新标签
        item.setText(dst + '/' + p.name)


class 增强版xllabelme(原版labelme):
    """ xllabelme扩展功能 """

    def __2_定制菜单(self):
        pass

    def create(self, update=True):
        super().create(False)
        mainwin = self.mainwin

        self.左侧栏菜单添加动作()
        self.切换检查动作 = \
            self.左侧栏菜单添加动作('切换检查', self.switch_check_mode, 'F1',
                           tip='（快捷键：F1）切换不同的数据检查模式，有不同的高亮方案。')
        self.switch_check_mode(update=False)  # 把更精细的tip提示更新出来

        if update:
            mainwin.populateModeActions()

    def __3_修改原版有的接口(self):
        pass

    def updateShape(self, shape, label_list_item=None):
        """
        :param shape:
        :param label_list_item: item是shape的父级，挂在labelList下的项目
        """
        mainwin = self.mainwin
        # 1 确定显示的文本 text
        self.xllabel.update_other_data(shape)
        showtext, hashtext, labelattr = self.xllabel.parse_shape(shape)
        if label_list_item:
            label_list_item.setText(showtext)
        else:
            label_list_item = LabelListWidgetItem(showtext, shape)

        # 2 保存label处理历史
        def parse_htext(htext):
            if htext and not mainwin.uniqLabelList.findItemsByLabel(htext):
                item = mainwin.uniqLabelList.createItemFromLabel(htext)
                mainwin.uniqLabelList.addItem(item)
                rgb = mainwin._get_rgb_by_label(htext)
                mainwin.uniqLabelList.setItemLabel(item, htext, rgb)
                return rgb
            elif htext:
                return mainwin._get_rgb_by_label(htext)
            else:
                return None

        parse_htext(hashtext)
        mainwin.labelDialog.addLabelHistory(hashtext)
        for action in mainwin.actions.onShapesPresent:
            action.setEnabled(True)

        # 3 定制颜色
        # 如果有定制颜色，则取用户设置的r, g, b作为shape颜色
        # 否则按照官方原版labelme的方式，通过label哈希设置
        hash_colors = mainwin._get_rgb_by_label(hashtext)
        r, g, b = 0, 0, 0

        def seleter(key, default=None):
            if default is None:
                default = [r, g, b]

            if key in labelattr:
                v = labelattr[key]
            else:
                v = None

            if v:
                if len(v) == 3 and len(default) == 4:
                    # 如果默认值有透明通道，而设置的时候只写了rgb，没有写alpha通道，则增设默认的alpha透明度
                    v.append(default[-1])
                for i in range(len(v)):
                    if v[i] == -1:  # 用-1标记的位，表示用原始的hash映射值
                        v[i] = hash_colors[i]
                return v
            else:
                return default

        r, g, b = seleter('shape_color', hash_colors.tolist())[:3]
        label_list_item.setText(
            '{} <font color="#{:02x}{:02x}{:02x}">●</font>'.format(
                showtext, r, g, b
            )
        )

        # 注意，只有用shape_color才能全局调整颜色，下面六个属性是单独调的
        # 线的颜色
        rgb_ = parse_htext(mainwin.xllabel.get_hashtext(labelattr, 'label_line_color'))
        shape.line_color = QtGui.QColor(*seleter('line_color', rgb_))
        # 顶点颜色
        rgb_ = parse_htext(mainwin.xllabel.get_hashtext(labelattr, 'label_vertex_fill_color'))
        shape.vertex_fill_color = QtGui.QColor(*seleter('vertex_fill_color', rgb_))
        # 悬停时顶点颜色
        shape.hvertex_fill_color = QtGui.QColor(*seleter('hvertex_fill_color', (255, 255, 255)))
        # 填充颜色
        shape.fill_color = QtGui.QColor(*seleter('fill_color', (r, g, b, 128)))
        # 选中时的线、填充颜色
        shape.select_line_color = QtGui.QColor(*seleter('select_line_color', (255, 255, 255)))
        shape.select_fill_color = QtGui.QColor(*seleter('select_fill_color', (r, g, b, 155)))

        return label_list_item

    def get_default_label(self, shape=None):
        xllabel = self.mainwin.xllabel
        label = xllabel.cfg.get('default_label', '')
        if xllabel.auto_rec_text and xllabel.xlapi and shape:
            k = 'label' if 'label' in xllabel.keys else 'text'
            text, score = xllabel.rec_text(shape.points)
            label = xllabel.set_label_attr(label, k, text)
            label = xllabel.set_label_attr(label, 'score', score)
        return label

    def newShape(self, text=None):
        """ 新建标注框时的规则
        """
        mainwin = self.mainwin
        items = mainwin.uniqLabelList.selectedItems()
        if items:
            text = items[0].data(Qt.UserRole)
        flags = {}
        group_id = None
        if mainwin._config["display_label_popup"]:
            previous_text = mainwin.labelDialog.edit.text()

            shape = Shape()
            shape.label = self.get_default_label(shape=mainwin.canvas.shapes[-1])
            shape = mainwin.labelDialog.popUp2(shape, mainwin)
            if shape is not None:
                text, flags, group_id = shape.label, shape.flags, shape.group_id

            if not text:
                mainwin.labelDialog.edit.setText(previous_text)

        if text is None:
            text = self.get_default_label(shape=mainwin.canvas.shapes[-1])

        if text and not mainwin.validateLabel(text):
            mainwin.errorMessage(
                mainwin.tr("Invalid label"),
                mainwin.tr("Invalid label '{}' with validation type '{}'").format(
                    text, mainwin._config["validate_label"]
                ),
            )
            text = ""
        if text:
            mainwin.labelList.clearSelection()
            shape = mainwin.canvas.setLastLabel(text, flags)
            shape.group_id = group_id
            mainwin.addLabel(shape)
            mainwin.actions.editMode.setEnabled(True)
            mainwin.actions.undoLastPoint.setEnabled(False)
            mainwin.actions.undo.setEnabled(True)
            mainwin.setDirty()
        else:
            mainwin.canvas.undoLastLine()
            mainwin.canvas.shapesBackups.pop()

    def __4_自己扩展的功能(self):
        pass

    def switch_check_mode(self, *, update=True):
        """ 设置不同的高亮格式 """
        if update:
            self.xllabel.default_shape_color_mode += 1
            self.xllabel.reset()
            self.mainwin.updateLabelListItems()

        # 提示给出更具体的使用的范式配置
        act = self.切换检查动作
        tip = act.toolTip()
        tip = re.sub(r'当前配置.*$', '', tip)
        tip += '当前配置：' + ', '.join(self.xllabel.cfg['label_shape_color'])
        act.setStatusTip(tip)
        act.setToolTip(tip)


class 文字通用(增强版xllabelme):

    def __3_修改原版有的接口(self):
        """ 原版labelme有实现，但这里作了定制修改 """

    def get_default_label(self, shape=None):
        d = {'text': '', 'category': '', 'text_kv': 'value', 'text_type': '印刷体'}
        return json.dumps(d, ensure_ascii=False)


class m2302中科院题库(增强版xllabelme):

    def __2_定制菜单(self):
        pass

    def create(self, update=True):
        super().create(False)
        mainwin = self.mainwin

        self.左侧栏菜单添加动作('标注排序', self.resort_shapes, tip='重新对目前标注的框进行排序')
        self.左侧栏菜单添加动作('检查全文章', self.browser_paper, tip='将内容按照shapes的顺序拼接成完整的文章，并检查公式渲染效果')
        # todo 检查文本行
        # todo 检查小分块

        if update:
            mainwin.populateModeActions()

    def __3_修改原版有的接口(self):
        """ 原版labelme有实现，但这里作了定制修改 """

    def get_default_label(self, shape=None):
        from pyxllib.cv.xlcvlib import xlcv
        from pyxlpr.data.imtextline import TextlineShape

        # 1 获得基本内容。如果开了识别接口，要调api。
        mainwin = self.mainwin
        xllabel = mainwin.xllabel
        points = [(p.x(), p.y()) for p in shape.points]
        d = None
        if xllabel.auto_rec_text and xllabel.xlapi and shape:
            # 识别指定的points区域

            im = xlcv.get_sub(mainwin.arr_image, points, warp_quad=True)
            try:
                d = xllabel.xlapi.priu_api('content_ocr', im, filename=str(mainwin.filename))
            except requests.exceptions.ConnectionError:
                pass
        if d is None:  # 设默认值
            d = {'line_id': 1, 'content_type': '印刷体', 'content_class': '文本', 'text': ''}

        # 2 获得line_id
        line_id = 1
        shapes = mainwin.canvas.shapes  # 最后一个框
        if len(shapes) > 1:
            sp = shapes[-2]  # 当前框会变成shapes[-1]，所以要取shapes[-2]才是上一次建立的框
            line_id0 = json.loads(sp.label).get('line_id', 1)
            if TextlineShape(points).in_the_same_line(TextlineShape([(p.x(), p.y()) for p in sp.points])):
                line_id = line_id0
            else:
                line_id = line_id0 + 1
        d['line_id'] = line_id

        return json.dumps(d, ensure_ascii=False)

    def __4_自己扩展的功能(self):
        pass

    def resort_shapes(self):
        """ m2302中科院题库用，更新行号问题 """
        from pyxlpr.data.imtextline import TextlineShape

        mainwin = self.mainwin
        # 目前只用于一个项目
        if self.xllabel.meta_cfg['current_mode'] != 'm2302中科院题库':
            return

        # 0 数据预处理
        def parse(sp):
            points = [(p.x(), p.y()) for p in sp.points]
            return [sp, json.loads(sp.label), TextlineShape(points)]

        data = [parse(sp) for sp in mainwin.canvas.shapes]

        # 1 按照标记的line_id大小重排序
        # 先按行排序，然后行内按重心的x轴值排序（默认文本是从左往右读）。
        data.sort(key=lambda x: (x[1]['line_id'], x[2].centroid.x))

        # 2 编号重置，改成连续的自然数
        cur_line_id, last_tag = 0, ''
        for item in data:
            sp, label = item[0], item[1]
            if label['line_id'] != last_tag:
                cur_line_id += 1
                last_tag = label['line_id']
            label['line_id'] = cur_line_id
            sp.label = json.dumps(label, ensure_ascii=False)

        # 3 更新回数据
        mainwin.updateShapes([x[0] for x in data])

    def browser_paper(self):
        """ 将当前标注的text内容拼接并在公式文章渲染网页打开 """
        # 1 拼接内容
        shapes = self.mainwin.canvas.shapes
        last_line_id = 1
        paper_text = []
        line_text = []
        for sp in shapes:
            label = json.loads(sp.label)
            if label['line_id'] != last_line_id:
                last_line_id = label['line_id']
                paper_text.append(' '.join(line_text))
                line_text = []

            if label['content_class'] == '公式':
                t = '$' + label['text'] + '$'
            else:
                t = label['text']
            line_text.append(t)

        paper_text.append(' '.join(line_text))
        content = '\n\n'.join(paper_text)

        # 2 获取渲染网页
        title = self.mainwin.get_label_path().stem
        r = requests.post('https://xmutpriu.com/latex/paper', json={'title': title, 'content': content})
        p = XlPath.init(title + '.html', XlPath.tempdir())
        p.write_text(r.text)
        webbrowser.open(p)


class m2303表格标注(原版labelme):

    def __2_定制菜单(self):
        pass

    def create(self, update=True):
        super().create(False)
        mainwin = self.mainwin
        mainwin._config["display_label_popup"] = False  # 关闭这个参数可以在添加标注的时候不弹窗

        self.菜单栏_帮助_添加文档('表格标注文档', 'https://www.yuque.com/xlpr/data/zw58v08ay3rsy0hk?singleDoc#')

        self.文件列表右键菜单添加动作('移到"无表格"', lambda: self.move_file('无表格'))
        # self.文件列表右键菜单添加动作('移到"重复图"', lambda: self.move_file('重复图'))

        # 3 canvas右键可以添加一个全图方框的标注
        self.画布右键菜单添加动作()
        self.画布右键菜单添加动作('全图标记一个表格矩形框', self.add_full_image_table_label,
                        tip='整张图都是一个完整的表格，全部画一个框')

        if update:
            mainwin.populateModeActions()  # 要运行下这个才会更新菜单

    def destroy(self):
        self.mainwin._config["display_label_popup"] = True
        super().destroy()

    def __3_修改原版有的接口(self):
        """ 原版labelme有实现，但这里作了定制修改 """

    def get_default_label(self, shape=None):
        return 'table'

    def __4_自己扩展的功能(self):
        pass

    def add_full_image_table_label(self):
        """ 这里有些底层操作想封装的，但一封装又失去了灵活性。有时候批量添加的时候，也不用每次都刷新
        想着就还是暂时先不封装
        """
        mainwin = self.mainwin
        shape = Shape('table', shape_type='polygon', flags={})
        # labelme的形状，下标是0开始，并且是左闭右闭的区间值
        h, w = mainwin.image.height() - 1, mainwin.image.width() - 1
        shape.points = [QPointF(0, 0), QPointF(w, 0), QPointF(w, h), QPointF(0, h)]
        mainwin.canvas.shapes.append(shape)
        mainwin.canvas.storeShapes()
        mainwin.canvas.update()
        mainwin.addLabel(shape)
        mainwin.actions.editMode.setEnabled(True)
        mainwin.actions.undoLastPoint.setEnabled(False)
        mainwin.setDirty()


class m2303表格标注二阶段(增强版xllabelme):

    def __2_定制菜单(self):
        pass

    def create(self, update=True):
        super().create(False)

        mainwin = self.mainwin
        mainwin._config["display_label_popup"] = False  # 关闭这个参数可以在添加标注的时候不弹窗

        self.菜单栏_帮助_添加文档('表格二阶段标注说明', 'https://www.yuque.com/xlpr/data/kvq2g82zvk5x1lkb?singleDoc#')

        self.set_label_color('可见横线', (0, 123, 255))  # 蓝色
        self.set_label_color('可见竖线', (40, 167, 69))  # 绿色
        self.set_label_color('不可见横线', (174, 223, 247))  # 不可见是可见对应的浅色
        self.set_label_color('不可见竖线', (180, 244, 190))

        if update:
            mainwin.populateModeActions()

    def destroy(self):
        self.mainwin._config["display_label_popup"] = True
        super().destroy()

    def __3_修改原版有的接口(self):
        """ 原版labelme有实现，但这里作了定制修改 """

    def get_default_label(self, shape=None):
        """ 还有些细节要调，如果弹窗，应该给出默认的几种类别文本 """
        from pyxllib.cv.xlcvlib import xlcv

        # 0 注意：标注过程中，是可以修改框的位置的
        # shape.points = [QPointF(100, 100), QPointF(200, 200)]

        # 1 框的基本几何信息
        poly = ShapelyPolygon.gen([(p.x(), p.y()) for p in shape.points])
        bounds = poly.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        # 2 图片信息
        # 表格, 可见横线, 可见竖线, 不可见横线, 不可见竖线
        mainwin = self.mainwin
        points = [(p.x(), p.y()) for p in shape.points]
        im = xlcv.get_sub(mainwin.arr_image, points, warp_quad=True)
        im = xlcv.read(im, 0)  # 先转灰度图
        im = xlcv.replace_ground_color(im, 0, 255)  # 然后转白底黑字图
        color = im.mean()  # 计算平均颜色，越接近255，表示越是空白图。

        # 3 自动识别线类型
        visible_tag = '可见' if color < 250 else '不可见'
        line_tag = '竖线' if height > width else '横线'
        return json.dumps({'text': visible_tag + line_tag}, ensure_ascii=False)


class m2305公式符号标注(增强版xllabelme):

    def __2_定制菜单(self):
        pass

    def create(self, update=True):
        super().create(False)

        mainwin = self.mainwin
        self.菜单栏_帮助_添加文档('公式符号标注说明', 'https://www.yuque.com/xlpr/data/sn3uglc7g6l49akv?singleDoc#')

        if update:
            mainwin.populateModeActions()

    def __3_修改原版有的接口(self):
        """ 原版labelme有实现，但这里作了定制修改 """

    def newShape(self):
        """ 这个项目的newShape比较特别，并不实际添加shape，而是把无效的矩形框重新替换标注

        这个功能是有一定通用性的，以后可以考虑怎么加到一般功能性框架。
        """
        # 1 找到第一个未显示的shape
        mainwin = self.mainwin
        model = mainwin.labelList.model()
        for index in range(model.rowCount()):
            item = model.item(index, 0)
            if not item.checkState():
                break
        else:  # 如果已经全部修复，则创建不了新矩形
            return

        # 2 更新shapes位置
        shapes = mainwin.canvas.shapes

        mainwin.labelList.clearSelection()

        item.shape().points = shapes[-1].points
        item.shape().shape_type = shapes[-1].shape_type
        item.setCheckState(Qt.Checked)
        mainwin.canvas.shapes = shapes[:-1]

        mainwin.actions.editMode.setEnabled(True)
        mainwin.actions.undoLastPoint.setEnabled(False)
        mainwin.actions.undo.setEnabled(True)
        mainwin.setDirty()


def __2_xllabel中介组件():
    pass


class XlLabel:
    """
    开发指南：尽量把对xllabelme的扩展，都写到这个类里，好集中统一管理
    """

    def __init__(self, parent):
        self.mainwin = parent

        self.read_config()
        self.default_shape_color_mode = 0  # 用来设置不同的高亮检查格式，会从0不断自增。然后对已有配色方案轮循获取。

        self.cur_img = {}  # 存储当前图片的ndarray数据。只有一条数据，k=图片路径，v=图片数据
        self.image_root = None  # 图片所在目录。有特殊功能用途，用在json和图片没有放在同一个目录的情况。
        # 这里可以配置显示哪些可用项目标注，有时候可能会需要定制化
        self.reset()
        # self.config_settings_menu()  # 配置界面
        self.xlapi = None

    def reset(self, mode=None):
        """ 更新配置 """
        # 0 旧项目相关配置要回退
        project = getattr(self.mainwin, 'project', None)
        if project:
            project.destroy()

        # 1 确定mode
        if mode:
            self.meta_cfg['current_mode'] = mode
        if self.meta_cfg['current_mode'] not in _CONFIGS:
            self.meta_cfg['current_mode'] = '文字通用'
        mode = self.meta_cfg['current_mode']

        # 2 预设mode或自定义mode的详细配置
        default_cfg = {
            'attrs': [],
            'editable': False,
            'label_shape_color': [],
            'label_line_color': [],
            'label_vertex_fill_color': [],
        }

        if mode in _CONFIGS:
            cfg = _CONFIGS[mode]
        else:
            cfg = self.meta_cfg['custom_modes'][mode]

        # 3 _attrs的处理
        def _attrs2attrs(_attrs):
            """ 简化版的属性配置，转为标准版的属性配置 """
            res = []
            for x in _attrs:
                # 1 补长对齐
                if len(x) < 4:
                    x += [None] * (4 - len(x))
                # 2 设置属性值
                d = {'key': x[0], 'show': x[1], 'type': x[2], 'items': x[3]}
                if isinstance(x[3], list):
                    d['editable'] = 1
                res.append(d)
            return res

        if '_attrs' in cfg:
            cfg['attrs'] = _attrs2attrs(cfg['_attrs'])
            del cfg['_attrs']

        # 4 设置该模式的详细配置
        default_cfg.update(cfg)
        cfg = default_cfg
        self.keyidx = {x['key']: i for i, x in enumerate(cfg['attrs'])}
        for x in cfg['attrs']:
            if isinstance(x['items'], (list, tuple)):
                if x.get('editable', 0):
                    x['items'] = list(x['items'])
                else:
                    x['items'] = tuple(x['items'])
        self.keys = [x['key'] for x in cfg['attrs']]
        self.hide_attrs = [x['key'] for x in cfg['attrs'] if x['show'] == 0]
        self.cfg = cfg

        # 5 确定当前配色方案
        ms = re.findall(r'(label_shape_color(?:\d+)?)(?:,|$)', ','.join(self.cfg.keys()))
        if ms:
            idx = self.default_shape_color_mode % len(ms)
            self.cfg['label_shape_color'] = self.cfg[ms[idx]]

        # 6 设置项目
        if project:
            self.mainwin.project = self.open_project()

    def config_label_menu(self):
        """ Label菜单栏
        """

        def get_task_menu():
            # 1 关联选择任务后的回调函数
            def func(action):
                # 1 内置数据格式
                action.setCheckable(True)
                action.setChecked(True)
                self.reset(action.text())
                # 一个时间，只能开启一个模式
                for a in task_menu.findChildren(QAction):
                    if a is not action:
                        a.setChecked(False)

                # 2 如果是自定义模式，弹出编辑窗
                pass

                # 3 保存配置
                self.save_config()

            task_menu = QMenu('任务', label_menu)
            task_menu.triggered.connect(func)

            # 2 往Label菜单添加选项功能
            actions = []
            for x in _CONFIGS.keys():
                actions.append(QAction(x, task_menu))
            if self.meta_cfg['custom_modes']:
                actions.append(None)
                for x in self.meta_cfg['custom_modes'].keys():
                    actions.append(QAction(x, task_menu))
            # 激活初始mode模式的标记
            for a in actions:
                if a.text() == self.meta_cfg['current_mode']:
                    a.setCheckable(True)
                    a.setChecked(True)
            utils.addActions(task_menu, actions)
            return task_menu

        def get_auto_rec_text_action():
            def func(x):
                self.auto_rec_text = x

                if self.auto_rec_text:
                    os.environ['XlAiAccounts'] = 'eyJwcml1IjogeyJ0b2tlbiI6ICJ4bGxhYmVsbWV5XipBOXlraiJ9fQ=='
                    try:
                        self.xlapi = XlAiClient()
                    except requests.exceptions.ConnectionError:
                        # 没有网络
                        self.xlapi = None
                        a.setChecked(False)
                        # 提示
                        msg_box = QMessageBox(QMessageBox.Information, "xllabelme标注工具：连接自动识别的API失败",
                                              "尝试连接xmutpriu.com的api失败，请检查网络问题，比如关闭梯子。\n"
                                              '如果仍然连接不上，可能是服务器的问题，请联系"管理员"。')
                        msg_box.setStandardButtons(QMessageBox.Ok)
                        msg_box.exec_()

                self.save_config()

            a = QAction('自动识别文本内容', label_menu)
            a.setCheckable(True)
            if self.auto_rec_text:
                a.setChecked(True)
                func(True)
            else:
                a.setChecked(False)
            a.triggered.connect(func)
            return a

        def get_set_image_root_action():
            a = QAction('设置图片所在目录', label_menu)

            def func():
                self.image_root = XlPath(QFileDialog.getExistingDirectory(self.image_root))
                self.mainwin.importDirImages(self.mainwin.lastOpenDir)

            a.triggered.connect(func)
            return a

        label_menu = self.mainwin.menus.label
        label_menu.addMenu(get_task_menu())
        label_menu.addSeparator()
        label_menu.addAction(get_auto_rec_text_action())
        label_menu.addAction(get_set_image_root_action())

    def parse_shape(self, shape):
        """ xllabelme相关扩展功能，常用的shape解析

        :return:
            showtext，需要重定制展示内容
            hashtext，用于哈希颜色计算的label
            labelattr，解析成字典的数据，如果其本身标注并不是字典，则该参数为空值
        """
        # 1 默认值，后面根据参数情况会自动调整
        showtext = shape.label
        labelattr = self.get_labelattr(shape.label)

        # 2 hashtext
        # self.hashtext成员函数只简单分析labelattr，作为shape_color需要扩展考虑更多特殊情况
        hashtext = self.get_hashtext(labelattr)
        # dprint(labelattr, hashtext)
        if not hashtext:
            if 'label' in labelattr:
                hashtext = labelattr['label']
            elif 'id' in labelattr:
                hashtext = labelattr['id']
            elif labelattr:
                hashtext = next(iter(labelattr.values()))
            else:
                hashtext = showtext
        hashtext = str(hashtext) or ' '  # 如果是空字符串，就映射到一个空格

        # 3 showtext
        if labelattr:
            # 3.1 隐藏部分属性
            hide_attrs = self.hide_attrs
            showdict = {k: v for k, v in labelattr.items() if k not in hide_attrs}
            # 3.2 排序
            keys = sorted(showdict.keys(), key=make_index_function(self.keys))
            showdict = {k: showdict[k] for k in keys}
            showtext = json.dumps(showdict, ensure_ascii=False)
        # 3.3 转成文本，并判断是否有 group_id 待展示
        if shape.group_id not in (None, ''):  # 这里扩展支持空字符串
            showtext = "{} ({})".format(showtext, shape.group_id)

        # + return
        return showtext, hashtext, labelattr

    def get(self, k, default=None):
        idx = self.keyidx.get(k, None)
        if idx is not None:
            return self.cfg['attrs'][idx]
        else:
            return default

    def read_config(self):
        self.configpath = XlPath.userdir() / ".xllabelme"
        if self.configpath.is_file():
            self.meta_cfg = self.configpath.read_json()
        else:
            self.meta_cfg = {'current_mode': '文字通用',
                             'custom_modes': {},
                             'auto_rec_text': False,
                             'language': 'zh_CN',
                             }
        self.auto_rec_text = self.meta_cfg.get('auto_rec_text', False)  # 新建框的时候，是否自动识别文本内容
        # auto_rec_text和xlapi两个参数不是冗余，是分别有不同含义的，最好不要去尝试精简掉！
        # auto_rec_text是设置上是否需要每次自动识别，xlapi是网络、api是否确实可用

        if self.meta_cfg['current_mode'] == 'm2302阅深题库':
            self.meta_cfg['current_mode'] = 'm2302中科院题库'

    def save_config(self):
        if self.mainwin.lastOpenDir:
            self.meta_cfg['lastOpenDir'] = XlPath(self.mainwin.lastOpenDir).as_posix()
        self.meta_cfg['auto_rec_text'] = self.auto_rec_text
        self.configpath.write_json(self.meta_cfg, encoding='utf8', indent=2, ensure_ascii=False)

    def __labelattr(self):
        """ label相关的操作

        labelme原始的格式，每个shape里的label字段存储的是一个str类型
        我为了扩展灵活性，在保留其str类型的前提下，存储的是一串可以解析为json字典的数据
        前者称为labelstr类型，后者称为labelattr格式

        下面封装了一些对label、labelattr进行操作的功能
        """

    @classmethod
    def json_dumps(cls, label):
        return json.dumps(label, ensure_ascii=False)

    def get_hashtext(self, labelattr, mode='label_shape_color'):
        """
        :param labelattr:
        :param mode:
            label_shape_color
            label_line_color
            label_vertex_fill_colorS
        :return:
            如果 labelattr 有对应key，action也有开，则返回拼凑的哈希字符串值
            否则返回 ''
        """
        ls = []
        attrs = self.cfg.get(mode, [])
        for k in attrs:
            if k in labelattr:
                ls.append(str(labelattr[k]) or ' ')
        if ls:
            return ', '.join(ls)
        else:
            return ''

    @classmethod
    def update_other_data(cls, shape):
        labelattr = cls.get_labelattr(shape.label, shape.other_data)
        if labelattr:
            shape.label = cls.json_dumps(labelattr)
            shape.other_data = {}

    @classmethod
    def get_labelattr(cls, label, other_data=None):
        """ 如果不是字典，也自动升级为字典格式 """
        labelattr = DictTool.json_loads(label, 'text')
        if other_data:
            # 如果有扩展字段，则也将数据强制取入 labelattr
            labelattr.update(other_data)
        return labelattr

    @classmethod
    def set_label_attr(cls, label, k, v):
        """ 修改labelattr某项字典值 """
        labelattr = cls.get_labelattr(label)
        labelattr[k] = v
        return cls.json_dumps(labelattr)

    def update_shape_text(self, x, text=None):
        """ 更新text内容

        :param x: 可以是shape结构，也可以是label字符串
            如果是shape结构，text又设为None，则会尝试用ocr模型识别文本
        """
        if isinstance(x, dict):
            if text is not None:
                x['text'] = text
        elif isinstance(x, str):
            if text is not None:
                x = self.set_label_attr(x, 'text', text)
        else:  # Shape结构
            if text is None:
                if self.auto_rec_text and self.xlapi:
                    labelattr = self.get_labelattr(x.label)
                    labelattr['text'], labelattr['score'] = self.rec_text(x.points)
                    x.label = self.json_dumps(labelattr)
            else:
                x.label = self.set_label_attr(x.label, 'text', text)

        return x

    def __smart_label(self):
        """ 智能标注相关 """

    def rec_text(self, points):
        """ 文字识别或者一些特殊的api接口 """
        from pyxllib.cv.xlcvlib import xlcv
        # 识别指定的points区域
        if isinstance(points[0], QPointF):
            points = [(p.x(), p.y()) for p in points]
        im = xlcv.get_sub(self.mainwin.arr_image, points, warp_quad=True)

        texts, scores = [], []  # 因图片太小等各种原因，没有识别到结果，默认就设空值
        try:
            d = self.xlapi.priu_api('basicGeneral', im)
            if 'shapes' in d:
                texts = [sp['label']['text'] for sp in d['shapes']]
                scores = [sp['label']['score'] for sp in d['shapes']]
        except requests.exceptions.ConnectionError:
            pass

        text = ' '.join(texts)
        if scores:
            score = round(mean(scores), 4)
        else:
            score = -1

        # if score == -1:
        #     dprint(points, text, score, im.shape)

        return text, score

    def content_ocr(self, shape):
        """ 主要给"m2302中科院题库"用的 """
        from pyxllib.cv.xlcvlib import xlcv
        from pyxlpr.data.imtextline import TextlineShape

        # 1 获得基本内容。如果开了识别接口，要调api。
        points = shape.points
        d = None
        if self.auto_rec_text and self.xlapi and shape:
            # 识别指定的points区域
            if isinstance(points[0], QPointF):
                points = [(p.x(), p.y()) for p in points]
            im = xlcv.get_sub(self.mainwin.arr_image, points, warp_quad=True)
            try:
                d = self.xlapi.priu_api('content_ocr', im, filename=self.mainwin.filename)
            except requests.exceptions.ConnectionError:
                pass
        if d is None:
            d = json.loads(_CONFIGS['m2302中科院题库']['default_label'])

        # 2 获得line_id
        line_id = 1
        shapes = self.mainwin.canvas.shapes  # 最后一个框
        if len(shapes) > 2:
            sp = shapes[-2]  # 当前框会变成shapes[-1]，所以要取shapes[-2]才是上一次建立的框
            line_id0 = json.loads(sp.label)['line_id']
            if TextlineShape(points).in_the_same_line(TextlineShape([(p.x(), p.y()) for p in sp.points])):
                line_id = line_id0
            else:
                line_id = line_id0 + 1
        d['line_id'] = line_id

        return json.dumps(d, ensure_ascii=False)

    def __right_click_shape(self):
        """ 扩展shape右键操作菜单功能
        """

    def get_current_select_shape(self):
        """ 如果当前没有选中item（shape），会返回None """
        mainwin = self.mainwin
        if not mainwin.canvas.editing():
            return None, None
        item = mainwin.currentItem()
        if item is None:
            return None, None
        shape = item.shape()
        return item, shape

    def split_shape(self):
        """ 将一个框拆成两个框

        TODO 支持对任意四边形的拆分
        策略1：现有交互机制上，选择参考点后，拆分出多边形
        策略2：出来一把剪刀，通过画线指定切分的详细形式
        """
        mainwin = self.mainwin
        item, shape = self.get_current_select_shape()
        if shape:
            # 1 获取两个shape
            # 第1个形状
            pts = [(p.x(), p.y()) for p in shape.points]
            l, t, r, b = rect_bounds(pts)
            p = mainwin.canvas.prevPoint.x()  # 光标点击的位置
            shape.shape_type = 'rectangle'
            shape.points = [QPointF(l, t), QPointF(p, b)]

            # 第2个形状
            shape2 = shape.copy()
            shape2.points = [QPointF(p, t), QPointF(r, b)]

            # 2 调整label
            # 如果开了识别模型，更新识别结果
            if self.auto_rec_text and self.xlapi:
                self.update_shape_text(shape)
                self.update_shape_text(shape2)
            else:  # 否则按几何比例重分配文本
                from pyxlpr.data.imtextline import merge_labels_by_widths
                text = self.get_labelattr(shape.label).get('text', '')
                text1, text2 = merge_labels_by_widths(list(text), [p - l, r - p], '')
                self.update_shape_text(shape, text1)
                self.update_shape_text(shape2, text2)

            # 3 更新到shapes里
            mainwin.canvas.selectedShapes.append(shape2)
            mainwin.addLabel(shape2)
            shapes = mainwin.canvas.shapes
            idx = shapes.index(shape)
            shapes = shapes[:idx + 1] + [shape2] + shapes[idx + 1:]  # 在相邻位置插入新的shape
            mainwin.updateShapes(shapes)
            mainwin.setDirty()

    def switch_check_mode(self, update=True):
        """ 设置不同的高亮格式 """
        if update:
            self.default_shape_color_mode += 1
            self.reset()
            self.mainwin.updateLabelListItems()

        # 提示给出更具体的使用的范式配置
        act = self.mainwin.changeCheckAction
        tip = act.toolTip()
        tip = re.sub(r'当前配置.*$', '', tip)
        tip += '当前配置：' + ', '.join(self.cfg['label_shape_color'])
        act.setStatusTip(tip)
        act.setToolTip(tip)

    def open_project(self):
        try:
            project = eval(self.mainwin.xllabel.meta_cfg['current_mode'])(self.mainwin)
        except NameError:
            project = 原版labelme(self.mainwin)
        return project
