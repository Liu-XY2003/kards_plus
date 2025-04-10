from typing import Optional, Tuple, List
import numpy as np
import pyautogui
import cv2
import time
import random
from dataclasses import dataclass,field
from scipy.interpolate import interp1d
#学习进度：练习1已完成 练习2已完成 练习3
#获取屏幕分辨率 最高亮度
screen_width,screen_height=pyautogui.size()
#练习1.通过图像识别技术寻找按钮并自动移动鼠标，然后点击
#截图函数，返回截取的全屏（区域屏）灰度图
def lianxi_00(select_region=None):
    image=pyautogui.screenshot(region=select_region)
    gray_image=cv2.cvtColor(np.array(image),cv2.COLOR_BGR2GRAY)
    return gray_image
def lianxi_01(path="play.png"):
    #文件取图
    image=cv2.imread(path)
    #加工成模板灰度图
    template_image_gray=cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    #截图获取全屏灰度图
    screen_shot_gray=lianxi_00()
    #图像匹配,寻找模板位置
    result = cv2.matchTemplate(screen_shot_gray, template_image_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #匹配度为0.8
    thread=0.8
    if max_val>thread:
        pyautogui.moveTo(max_loc)
        pyautogui.click()
#练习2.欺骗反作弊程序，实现鼠标移动自然化
class MouseTransition:
    def __init__(self):
        # 高斯噪声参数
        self.noise_scale = random.uniform(1, 3)  # 噪声强度
        # 速度曲线参数
        self.acceleration = random.uniform(0.3, 0.7)  # 加速度因子
        # 屏幕尺寸
        self.screen_width, self.screen_height = pyautogui.size()

    def _add_gaussian_noise(self, points, scale=1.0):
        """为路径添加高斯噪声"""
        noise = np.random.normal(0, scale, (len(points), 2))
        return points + noise

    def _generate_bezier_curve(self, start, end, control_points=None, num_points=100):
        """生成贝塞尔曲线路径"""
        if control_points is None:
            # 自动生成1个随机控制点
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            control_points = [
                (mid_x + random.uniform(-100, 100),
                 mid_y + random.uniform(-100, 100))
            ]
        #核心素养
        t = np.linspace(0, 1, num_points)
        t = t[:, np.newaxis]
        curve = (1 - t) ** 2 * start + 2 * (1 - t) * t * control_points[0] + t ** 2 * end
        return curve

    def _generate_speed_profile(self, num_points):
        """生成变速曲线（先快后慢）"""
        x = np.linspace(0, 1, num_points)
        y = np.sin(x * np.pi * self.acceleration)  # 正弦曲线模拟速度变化
        return y / y.max()  # 归一化到[0,1]

    def _clamp_position(self, pos):
        """确保坐标在屏幕范围内"""
        x = max(0, min(pos[0], self.screen_width - 1))
        y = max(0, min(pos[1], self.screen_height - 1))
        return (x, y)

    def move(self, start_pos, end_pos, duration=1.0):
        """带随机轨迹的鼠标移动"""
        try:
            # 生成贝塞尔曲线路径
            control_point = (
                (start_pos[0] + end_pos[0]) / 2 + random.randint(-50, 50),
                (start_pos[1] + end_pos[1]) / 2 + random.randint(-50, 50)
            )
            curve = self._generate_bezier_curve(
                np.array(start_pos),
                np.array(end_pos),
                [control_point]  # 作为列表传递
            )

            # 添加高斯噪声
            noisy_curve = self._add_gaussian_noise(curve, scale=self.noise_scale)

            # 生成变速参数
            speed = self._generate_speed_profile(len(noisy_curve))

            # 执行移动
            start_time = time.time()
            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                progress = min(elapsed / duration, 1.0)  # 当前进度[0,1]

                # 根据速度曲线计算当前应到达的路径点
                idx = int(progress * (len(noisy_curve) - 1))
                target_pos = noisy_curve[idx]

                # 随机微调（模拟手抖）并确保在屏幕内
                jitter_x = random.uniform(-1, 1)
                jitter_y = random.uniform(-1, 1)
                current_pos = self._clamp_position((
                    target_pos[0] + jitter_x,
                    target_pos[1] + jitter_y
                ))

                pyautogui.moveTo(*current_pos, _pause=False)
                time.sleep(0.01)  # 控制刷新率

        except Exception as e:
            print(f"移动过程中出错: {e}")
            # 出错时直接移动到终点
            pyautogui.moveTo(*end_pos)
#练习3：实战过渡，设计按钮类
@dataclass
class Button:
    """按钮抽象类（Python 3.9兼容版）"""
    name: str
    image_path: str
    confidence: float = 0.8
    _template: Optional[np.ndarray] = field(default=None, init=False, repr=False)

    @property
    def template(self) -> np.ndarray:
        """延迟加载模板图像"""
        if self._template is None:
            self._template = cv2.imread(self.image_path)
            if self._template is None:
                raise FileNotFoundError(f"无法加载按钮图片: {self.image_path}")
        return self._template

    def find(self) -> Optional[Tuple[int, int]]:
        """定位按钮中心坐标"""
        screenshot = np.array(pyautogui.screenshot())
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screenshot, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= self.confidence:
            h, w = self.template.shape[:2]
            return (max_loc[0] + w//2, max_loc[1] + h//2)
        return None

    def click(self, timeout: float = 5) -> bool:
        """尝试点击按钮"""
        for _ in range(int(timeout * 2)):  # 每0.5秒尝试一次
            if pos := self.find():
                pyautogui.click(pos)
                print(f"[{self.name}] 点击成功")
                return True
            time.sleep(0.5)
        print(f"[{self.name}] 未找到按钮 (超时: {timeout}s)")
        return False
def main():
    return 0
# 使用示例

main()



