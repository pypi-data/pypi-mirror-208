import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Union, Any
import requests
from loguru import logger
import re
from pathlib import Path
import base64


@dataclass
class ImgArea:
    start_x: float = 0
    end_x: float = 1
    start_y: float = 0
    end_y: float = 1


class ImgLocation(Enum):
    FULL = ImgArea(0, 1, 0, 1)
    LEFT = ImgArea(0, 0.5, 0, 1)
    RIGHT = ImgArea(0.5, 1, 0, 1)
    TOP = ImgArea(0, 1, 0, 0.5)
    BOTTOM = ImgArea(0, 1, 0.5, 1)
    MIDDLE = ImgArea(0, 1, 0.25, 0.75)
    HEAD = ImgArea(0, 1, 0, 0.25)
    HEADLINE = ImgArea(0, 1, 0, 0.1)
    TAIL = ImgArea(0, 1, 0.75, 1)
    FOOT = ImgArea(0, 1, 0.9, 1)


@dataclass
class TemplateLocation:
    points: list[Union[tuple[int, int], list[int]]]
    center: tuple[Union[int, float], Union[int, float]] = (-1, -1)
    found: bool = False
    size: int = 0


class TextAction(Enum):
    KEYCODE_NEXT = 'KEYCODE_NEXT'
    KEYCODE_PREVIOUS = 'KEYCODE_PREVIOUS'
    KEYCODE_DONE = 'KEYCODE_DONE'
    KEYCODE_SEARCH = 'KEYCODE_SEARCH'
    KEYCODE_SEND = 'KEYCODE_SEND'
    KEYCODE_GO = 'KEYCODE_GO'
    KEYCODE_DELETE = 'KEYCODE_DELETE'
    KEYCODE_DELETE_ALL = 'KEYCODE_DELETE_ALL'
    KEYCODE_MAIN_KEYBOARD = 'KEYCODE_MAIN_KEYBOARD'
    KEYCODE_CLOSE = 'KEYCODE_CLOSE'


def location_serialize(location: Union[
    ImgLocation, list[ImgLocation],
    ImgArea, list[ImgArea]] = ImgLocation.FULL):
    try:
        if not isinstance(location, list) and not isinstance(location, tuple):
            location = [location]
        result = []
        for loc in location:
            if isinstance(loc, ImgLocation):
                result.append(loc.name)
            else:
                result.append(asdict(loc))
        return result
    except Exception as e:
        logger.exception(e)
        return location

class Robot:
    def __init__(self, ip: str):
        self.ip = ip
        self._phones: dict[int, Phone] = {}
        self.__load()

    def __load(self):
        """
        load phones from robot
        :return:
        """
        phones = self.call_api('phones/get')
        try:
            phones = phones.json()
            for phone in phones:
                pos = phone['position']
                self._phones[pos] = Phone(
                    pos,
                    self,
                    data=phone
                )
        except Exception as e:
            logger.exception(e)
            logger.debug(phones.content)

    def phone(self, position: int) -> 'Phone':
        return self._phones.get(position)

    @property
    def phones(self) -> dict[int, 'Phone']:
        return self._phones

    def call_func(self, position, path, **kwargs) -> Any:
        phone = self.phone(position)

        if 'location' in kwargs:
            kwargs['location'] = location_serialize(kwargs['location'])

        if phone:
            headers = {
                'PhonePosition': str(phone.position)
            }
        else:
            headers = {}
        result = requests.post(
            f'http://{self.ip}/api/{path}/',
            json=json.dumps(kwargs),
            headers=headers
        )
        try:
            return result.json()
        except Exception:
            try:
                return result.content.decode()
            except:
                return result.content

    def call_api(self, path, **kwargs):
        return requests.get(
            f'http://{self.ip}/api/{path}/',
            json=json.dumps(kwargs),
        )

    def home(self):
        """
        机器人回零复位
        :return:
        """
        return self.call_api('home-robot')


class ScreenInfo:
    def __init__(self, phone: 'Phone'):
        self.phone = phone
        self.model = None

    @property
    def phone_model(self):
        if not self.model:
            model = self.phone.robot.call_func(
                self.phone.position, 'screen/phone_model'
            )
            self.model = model
        return self.model

    def current_app(self):
        """
        当前APP
        :return:
        """
        key = 'screen/current_app'
        return self.phone.robot.call_func(self.phone.position, key)

    def is_front(self):
        """
        agent是否在前台
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/is_front')

    def launch_app(self, app=None):
        """
        启动app
        :param app:
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/launch_app', app=app)

    def to_front(self):
        """
        打开agent
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/to_front')

    def set_volume(self, value=20):
        """
        设置音量
        :param value: 0-100
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/set_volume', value=value)

    def set_brightness(self, value=20):
        """
        设置亮度
        :param value: 0-100
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/set_brightness', value=value)

    def uninstall(self, app):
        """
        卸载app
        :param app:
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/uninstall', app=app)

    def generate_password(self, app):
        """
        为指定app生成一个密码, UI界面可以直接输入
        :param app:
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/generate_password', app=app)

    def apps(self, update=False):
        """
        列出所有app
        :param update:
        :return:
        """
        key = 'screen/apps'
        return self.phone.robot.call_func(self.phone.position, key)

    def recent_apps(self):
        """
        列出最近app
        :return:
        """
        key = 'screen/recent_apps'
        return self.phone.robot.call_func(self.phone.position, key)

    def wait_app(self, app, timeout=120):
        """
        等待app启动成功
        :param app:
        :param timeout:
        :return:
        """
        key = 'screen/wait_app'
        self.phone.robot.call_func(self.phone.position, key, app=app, timeout=timeout)

    def read_sms(self):
        """
        读取最近短信. MIUI可以读取验证码短信 但是需要给agent授权
        :return:
        """
        key = 'screen/read_sms'
        return self.phone.robot.call_func(self.phone.position, key)

    def phone_info(self):
        """
        手机信息
        :return:
        """
        key = 'self/to-json'
        return self.phone.robot.call_func(self.phone.position, key)

    def copy_clipboard(self):
        info = self.phone_info()
        return info['clipboard']

    def get_phone_text(self, local_only=False):
        """
        获取手机屏幕上的文字
        格式: [[[start_x, start_y, end_x, end_y], 文字, 可信度]]
        :param local_only: 是否使用缓存
        :return:
        """
        key = 'screen/get_phone_text'
        return self.phone.robot.call_func(self.phone.position, key, local_only=local_only)

    def has_texts(self, texts: list[str, re.Pattern], prev=False, ignore_case=True,
                  location: Union[ImgLocation, list[ImgLocation], ImgArea, list[ImgArea]] = ImgLocation.FULL,
                  contain=True):
        """
        屏幕里是否有这些词
        :param texts: str或者regex
        :param prev: update前的text还是现在的
        :param ignore_case: 忽略大小写
        :param location: ImgLocation 或者 ImgArea, 可以多个组合
        :param contain: 包含还是完全匹配
        :return:
        """
        if not isinstance(texts, list):
            texts = [texts]
        return self.phone.robot.call_func(
            self.phone.position, 'screen/has_texts', texts=list(map(str, texts)),
            location=location,
            contain=contain,
            prev=prev,
            ignore_case=ignore_case
        )

    def has_any_texts(self, texts: list[str, re.Pattern], prev=False, ignore_case=True,
                      location: Union[ImgLocation, list[ImgLocation], ImgArea, list[ImgArea]] = ImgLocation.FULL,
                      contain=True, k=1):
        """
        屏幕里是否至少有这些词中的一部分
        :param texts: str或者regex
        :param prev: update前的text还是现在的
        :param ignore_case: 忽略大小写
        :param location: ImgLocation 或者 ImgArea, 可以多个组合
        :param contain: 包含还是完全匹配
        :param k: 至少需要几个
        :return:
        """
        return self.phone.robot.call_func(
            self.phone.position, 'screen/has_any_texts',
            texts=list(map(str, texts)),
            location=location,
            contain=contain,
            prev=prev,
            ignore_case=ignore_case,
            k=k,
        )

    def count_texts(self, texts: Union[list[str, re.Pattern], Union[str, re.Pattern]], prev=False, ignore_case=True,
                    location: Union[ImgLocation, list[ImgLocation], ImgArea, list[ImgArea]] = ImgLocation.FULL,
                    contain=True):
        """
        文字计数
        :param texts: str或者regex
        :param prev: update前的text还是现在的
        :param ignore_case: 忽略大小写
        :param location: ImgLocation 或者 ImgArea, 可以多个组合
        :param contain: 包含还是完全匹配
        :return:
        """
        if not isinstance(texts, list):
            texts = [texts]
        return self.phone.robot.call_func(
            self.phone.position, 'screen/count_texts',
            texts=list(map(str, texts)),
            location=location,
            contain=contain,
            prev=prev,
            ignore_case=ignore_case
        )

    def update(self, text=True):
        """
        更新屏幕图像和文字
        :param text: 是否更新文字
        :return:
        """
        key = 'screen/update'
        return self.phone.robot.call_func(self.phone.position, key, text=text)

    def home(self):
        """
        机器人回零复位
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/home')

    @property
    def image_raw(self):
        """
        当前屏幕图片的bytes
        :return:
        """
        return self.phone.robot.call_func(self.phone.position, 'screen/image_raw')

    def app_stick(self, app_str: str):
        """
        UI中置顶或者取消置顶app
        :param app_str: app package name
        :return:
        """
        return self.phone.robot.call_func(
            self.phone.position, 'screen/app_stick', app_str=app_str)

    def enter_text(self, text: Union[TextAction, str]):
        """
        输入文字
        :param text: 文字或者TextAction
        :return:
        """
        if isinstance(text, TextAction):
            text = text.name
        return self.phone.robot.call_func(self.phone.position,
                                          'screen/enter_text', text=text
                                          )

    def get_chinese(self, k=8, prev=False, start: int = None):
        """
        :param k: 总计对比多少组词
        :param prev: call update前的文字
        :param start: 竖屏默认值是3, 忽略前三个词， 因为时间一直在变
        :return:
        """
        return self.phone.robot.call_func(
            self.phone.position,
            'screen/get_chinese', k=k, prev=prev, start=start
        )

    def chinese_changed(self, update=True, k=8, start: int = None):
        """
        对比call update 前后是否中文有改变
        :param update: 是否先update再对比, 如果已经call了update这里可以用False
        :param k: 总计对比多少组词
        :param start: 竖屏默认值是3, 忽略前三个词， 因为时间一直在变
        :return:
        """
        return self.phone.robot.call_func(
            self.phone.position,
            'screen/chinese_changed', update=update, k=k, start=start
        )

    def clear_folder(self, folder: str = "DCIM"):
        """
        清空指定文件夹 默认清空DCIM
        :param folder: default DCIM
        :return:
        """
        return self.phone.robot.call_func(
            self.phone.position,
            'screen/clear_folder', folder=folder
        )

    def clear_midea(self):
        for folder in ['DCIM', 'Pictures']:
            self.clear_folder(folder)

    def locate_image(
            self, template: Union[Path, bytes],
            image: Union[Path, bytes] = None,
            location: Union[ImgLocation, list[ImgLocation], ImgArea, list[ImgArea]] = ImgLocation.FULL,
            threshold=0.8
    ) -> list[TemplateLocation]:
        """
        图查图. 仅作为实验用途. 如果效果可能不完美, 可以自行使用其它库去实现.

        :param template: 被查找的模版路径或者bytes
        :param image: 默认查找当前手机画面, 也可以提供被查图的路径或bytes
        :param location: 只查找指定位置
        :param threshold: 特征点集合阈值 , 0-∞, 越小越严格, 越大越宽松
        :return:
        """

        def read_img(path):
            if not path:
                return path
            if isinstance(path, bytes):
                content = path
            else:
                with open(path, 'rb') as fin:
                    content = fin.read()
            return base64.b64encode(content).decode()

        template_content = read_img(template)
        img_content = read_img(image)

        res = self.phone.robot.call_func(
            self.phone.position,
            'screen/locate-image',
            template=template_content,
            image=img_content,
            location=location,
            threshold=threshold,
        )
        result = []
        for loc in res:
            result.append(TemplateLocation(**loc))
        return result

    def show_keyboard(self):
        """
        显示输入法键盘
        可以自行调用 enter_text(TextAction) 去实现其它功能
        :return:
        """
        return self.enter_text(TextAction.KEYCODE_MAIN_KEYBOARD)

    def hide_keyboard(self):
        """
        隐藏输入法键盘
        :return:
        """
        return self.enter_text(TextAction.KEYCODE_CLOSE)


class Phone:
    def __init__(
            self,
            position: int,
            robot: Robot,
            data: dict
    ):
        self.position = position
        self.robot = robot
        self.data = data
        self.screen = ScreenInfo(self)

    @property
    def image(self):
        """
        当前屏幕图片的bytes
        :return:
        """
        return self.robot.call_api(f'{self.position}.jpeg').content

    @property
    def calibrated(self) -> bool:
        """
        是否已经校准
        :return:
        """
        return self.robot.call_func(self.position, 'self/is-calibrated')

    def upload(self, file, name=None):
        """
        上传文件到手机
        :param file: 文件路径
        :param name: 自定义文件名, 需要包含扩展名!!
        :return:
        """
        with open(file, 'rb') as f:
            files = {'file': f if not name else (name, f)}
            url = f'http://{self.robot.ip}/api/upload/{self.position}/'
            requests.post(
                url, files=files,
                timeout=(100, 100)
            )

    def touch(self, x: Union[int, float] = None, y: Union[int, float] = None, z: Union[int, float] = None,
              speed: Union[int, float] = None, raw=False, lift=True, delay=0,
              **kwargs):
        """

        :param x: (0-1) 百分比, > 1 实际像素
        :param y: (0-1) 百分比, > 1 实际像素
        :param z: z高度. 除非知道如何使用 否则不建议使用
        :param speed: 移动速度
        :param raw: 用mm尺寸. 除非知道如何使用 否则不建议使用
        :param lift: 是否抬起
        :param delay: 抬起延迟
        :param kwargs:
        :return:
        """
        return self.robot.call_func(self.position, 'self/touch', x=x, y=y, z=z, speed=speed, raw=raw, lift=lift,
                                    delay=delay, **kwargs)

    def drag(self, x1: Union[int, float] = None, y1: Union[int, float] = None, x2: Union[int, float] = None,
             y2: Union[int, float] = None, speed=55000, lift=True, raw=False, precise=False, delay=0.1):
        """

        :param x1: 起始X (0-1) 百分比, > 1 实际像素
        :param y1: 起始Y (0-1) 百分比, > 1 实际像素
        :param x2: 结束X (0-1) 百分比, > 1 实际像素
        :param y2: 结束Y (0-1) 百分比, > 1 实际像素
        :param speed: 移动速度
        :param lift: 是否抬起
        :param raw: 用mm尺寸. 除非知道如何使用 否则不建议使用
        :param precise: 精确还是不精确. 不精确: 会模拟真实滑屏时的加速抬起
        :param delay: 抬起延迟
        :return:
        """
        return self.robot.call_func(self.position, 'self/drag', x1=x1, y1=y1, x2=x2, y2=y2, speed=speed, lift=lift,
                                    raw=raw, precise=precise, delay=delay)

    def swipe_up(self):
        """
        模拟人手随机向上滑屏
        :return:
        """
        return self.robot.call_func(self.position, 'self/swipe-up')

    def swipe_down(self):
        """
        模拟人手随机向下滑屏
        :return:
        """
        return self.robot.call_func(self.position, 'self/swipe-down')

    def swipe_right(self):
        """
        模拟人手随机向右滑屏
        :return:
        """
        return self.robot.call_func(self.position, 'self/swipe-right')

    def hold(self, x, y, seconds: Union[int, float] = 2):
        """
        长按
        :param x: (0-1) 百分比, > 1 实际像素
        :param y: (0-1) 百分比, > 1 实际像素
        :param seconds: 延迟时间
        :return:
        """
        return self.robot.call_func(self.position, 'self/hold', x=x, y=y, seconds=seconds)

    def swipe_left(self):
        """
        模拟人手随机向左滑屏
        :return:
        """
        return self.robot.call_func(self.position, 'self/swipe-left')

    def enter_tasks(self, clear=False):
        """
        打开任务列表
        :param clear: 是否清除所有任务
        :return:
        """
        return self.robot.call_func(self.position, 'self/enter_tasks', clear=clear)

    def back(self):
        """
        机器人回零复位
        :return:
        """
        return self.robot.call_func(self.position, 'self/back')

    def calibrate(self):
        """
        校准单个手机
        :return:
        """
        return self.robot.call_func(self.position, 'self/calibrate')

    def take_picture(self, move=True):
        """
        用相机拍照
        :param move: 是否移动的对应的拍照点
        :return:
        """
        return self.robot.call_func(self.position, 'self/take_picture', move=move)

    def touch_text(self, text: Union[str, re.Pattern],
                   index=0,
                   location: Union[
                       ImgLocation, list[ImgLocation],
                       ImgArea, list[ImgArea]] = ImgLocation.FULL,
                   contain=True,
                   offset: tuple[float, float] = (0.0, 0.0), jitter_x=True):
        """
        点击屏幕里的文字
        :param text: 需要点击的文字或者regex
        :param index: 点击第几个匹配的文字 默认第一个
        :param location: ImgLocation 或者 ImgArea, 可以多个组合去匹配想要匹配的区域
        :param contain: 包含还是完全匹配
        :param offset: 偏移, 比如想点击文字左边的按钮可以用 (-0.05, 0) UI界面鼠标放在手机屏幕上可以看比例. 原点是左上角, 向下Y+, 向右x+
        :param jitter_x: 是否左右随机一点
        :return:
        """
        return self.robot.call_func(
            self.position,
            'self/touch_text',
            text=str(text),
            index=index,
            location=location,
            contain=contain,
            offset=list(offset),
            jitter_x=jitter_x
        )

    def move(self, x: Union[int, float] = None, y: Union[int, float] = None, z: Union[int, float] = None,
             speed: Union[int, float] = None, raw=False):
        """

        :param x: X (0-1) 百分比, > 1 实际像素
        :param y: Y (0-1) 百分比, > 1 实际像素
        :param speed: 移动速度
        :param raw: 用mm尺寸. 除非知道如何使用 否则不建议使用
        :return:
        """
        return self.robot.call_func(
            self.position, 'self/move', x=x, y=y, z=z, speed=speed, raw=raw,
        )
