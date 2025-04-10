from typing import Optional, Tuple, List
import numpy as np
import pyautogui
import cv2
import time
import random
from dataclasses import dataclass,field
from scipy.interpolate import interp1d
# 按键类，核心功能承担者
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
        print(f"正在寻找按钮{self.name}中心坐标")
        screenshot = np.array(pyautogui.screenshot())
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screenshot, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= self.confidence:
            h, w = self.template.shape[:2]
            print(f"已经找到按钮{self.name}中心坐标，{(max_loc[0] + w // 2, max_loc[1] + h // 2)}")
            return (max_loc[0] + w // 2, max_loc[1] + h // 2)
        else:
            print(f"没有找到按钮{self.name}")
        return None
#标记
    def click(self, timeout: float = 5) -> bool:
        """尝试点击按钮"""
        start_pos = pyautogui.position()  # 获取当前鼠标位置作为起点
        for _ in range(int(timeout * 2)):  # 每0.5秒尝试一次
            if pos := self.find():
                MouseTransition.MoveTo_with_Transiton(start_pos, pos)
                pyautogui.click()
                print(f"[{self.name}] 点击成功")
                return True
            time.sleep(0.5)
        print(f"[{self.name}] 未找到按钮 (超时: {timeout}s)")
        return False


# 欺骗反作弊程序，实现鼠标移动自然化
class MouseTransition:
    @staticmethod
    def _add_gaussian_noise(points, scale=1.0):
        """为路径添加高斯噪声"""
        noise = np.random.normal(0, scale, (len(points), 2))
        return points + noise

    @staticmethod
    def _generate_bezier_curve(start, end, control_points=None, num_points=100):
        """生成贝塞尔曲线路径"""
        if control_points is None:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            control_points = [(mid_x + random.uniform(-100, 100), mid_y + random.uniform(-100, 100))]
        t = np.linspace(0, 1, num_points)
        t = t[:, np.newaxis]
        curve = (1 - t) ** 2 * start + 2 * (1 - t) * t * control_points[0] + t ** 2 * end
        return curve

    @staticmethod
    def _clamp_position(pos, screen_width, screen_height):
        """确保坐标在屏幕范围内"""
        x = max(0, min(pos[0], screen_width - 1))
        y = max(0, min(pos[1], screen_height - 1))
        return (x, y)

    @staticmethod
    def MoveTo_with_Transiton(start_pos, end_pos, duration=1.0):
        """带随机轨迹的鼠标移动"""
        screen_width, screen_height = pyautogui.size()
        control_point = (
            (start_pos[0] + end_pos[0]) / 2 + random.randint(-50, 50),
            (start_pos[1] + end_pos[1]) / 2 + random.randint(-50, 50)
        )
        curve = MouseTransition._generate_bezier_curve(
            np.array(start_pos), np.array(end_pos), [control_point]
        )
        noisy_curve = MouseTransition._add_gaussian_noise(curve, scale=1.5)
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            idx = int(progress * (len(noisy_curve) - 1))
            target_pos = noisy_curve[idx]
            current_pos = MouseTransition._clamp_position(target_pos, screen_width, screen_height)
            pyautogui.moveTo(*current_pos, _pause=False)
            time.sleep(0.01)

# def test():
#     play_button = Button(name="play", image_path="play.png", confidence=0.8)
#     play_button.click()

def main():
    begin01_buttun=Button(name="begin01.png",image_path="begin01.png",confidence=0.8)
    begin02_buttun = Button(name="begin02.png", image_path="begin02.png", confidence=0.8)
    cards_back_German_button=Button(name="cards_back_German.png",image_path="cards_back_German.png",confidence=0.8)
    defeat_play_button = Button(name="defeat_play.png", image_path="defeat_play.png", confidence=0.8)
    error01_button = Button(name="error01.png", image_path="error01.png", confidence=0.8)
    find_competitor_button = Button(name="find_competitor.png", image_path="find_competitor.png", confidence=0.8)
    paiwei_match_button = Button(name="paiwei_match.png", image_path="paiwei_match.png", confidence=0.8)
    permit_to_compete_button = Button(name="permit_to_compete.png", image_path="permit_to_compete.png", confidence=0.8)
    play_button = Button(name="play.png", image_path="play.png", confidence=0.8)
    play_end_button = Button(name="play_end.png", image_path="play_end.png", confidence=0.8)
    round_end_button = Button(name="round_end.png", image_path="round_end.png", confidence=0.8)
    set_button = Button(name="set.png", image_path="set.png", confidence=0.8)
    xiuxian_match_button = Button(name="xiuxian_match.png", image_path="xiuxian_match.png", confidence=0.8)
    out_button=Button(name="out_.png",image_path="out.png",confidence=0.8)
    puton_max_time_for_one_play = input("输入是否设置一局游戏的最长时间，如设置，请输入0，否则输入1")
    print("准备执行脚本，请打开官方启动器，语言设置为英文，倒计时10秒")
    time.sleep(10)
    print("脚本启动，请勿移动鼠标")
    # 第一步：点击play，从官方启动器窗口进入游戏
    if play_button.find():
        play_button.click()
    else:
        print("未找到按钮0，程序中止")
        return 0
    time.sleep(20 + random.uniform(-5, 5))
    #单击进入开始界面
    pyautogui.doubleClick(1300+random.uniform(-50,50),1300+random.uniform(-50,50))
    time.sleep(5)
    pyautogui.doubleClick(2220+random.uniform(-50,50),100+random.uniform(-20,20))
    work=True
    wait=3 + random.uniform(-1, 1)
    wait_max=300
    work_time=4*3600
    while(work):
        if out_button.find():
            out_button.click()
            pyautogui.doubleClick(150+random.uniform(-10,10),600+random.uniform(-100,100))
        if puton_max_time_for_one_play==0:
            wait_for_one_play=random.uniform(150,300)
        else:
            wait_for_one_play = 0
        start_time=time.time()
        # 第二步：进入游戏，点击开始按钮，卡背按钮，开始（02）按钮，准备对局
        if begin01_buttun.find():
            begin01_buttun.click()
        else:
            print("未找到按钮1，程序中止")
            break
        time.sleep(wait)
        if cards_back_German_button.find():
            cards_back_German_button.click()
        else:
            print("未找到按钮2，程序中止")
            break
        time.sleep(wait)
        if begin02_buttun.find():
            begin02_buttun.click()
        else:
            print("未找到按钮3，程序中止")
            break
        time.sleep(3)
        #检测是否进入匹配界面
        if find_competitor_button.find():
            print("检测到已顺利进入匹配界面")
        else:
            print("未找到按钮4，检测失败，程序中止")
            break
        #每隔十五秒判断一次是否进入游戏
        time_begin_play=time.time()
        while(True):
            if time.time()-time_begin_play>wait_max:
                print("匹配超时，程序中断")
                return
            if permit_to_compete_button.find():
                print("已经进入游戏")
                time.sleep(wait)
                permit_to_compete_button.click()
                break
            else:
                time.sleep(15)
        time_begin_play_02=time.time()
        while(time.time()-time_begin_play_02<=wait_for_one_play or puton_max_time_for_one_play):
            if round_end_button.find():
                print("找到结束回合按键，即将结束本回合")
                time.sleep(12+random.uniform(-3,3))
                round_end_button.click()
            elif play_end_button.find():
                print("已经被对手击败，提前结束本局游戏循环体")
                break
            else:
                print("对手回合,等待十秒再检测")
                time.sleep(8)
        print(f"游戏主循环执行完毕，执行时间{time.time()-time_begin_play_02}秒，即将结束游戏")
        time.sleep(wait)
        if play_end_button.find():
            print("已经被对手击败，跳转到结算界面代码")
            pass
        elif set_button.find():
            print("找到右上角设置按钮")
            set_button.click()
            sleep(1+uniform(-0.5,0.5))
            if defeat_play_button.find():
                print("找到投降按钮")
                defeat_play_button.click()
            else:
                print("故障原因：未找到投降按钮，程序中止")
                break
        else:
            print("故障原因：未找到右上角设置键，也没有找到继续按钮，程序中止")
            break
        time.sleep(5+wait)
        #检测是否进入结算界面
        if play_end_button.find():
            print("第一次找到继续按钮，本场对局已经结束")
            play_end_button.click()
            pyautogui.click()
        else:
            print("故障原因：未找到游戏结束的标志，继续按钮，不能判定游戏是否结束，程序中止")
            break
        time.sleep(wait)
        if play_end_button.find():
            print("第二次找到继续按钮，准备结束本场对局")
            play_end_button.click()
            pyautogui.click()
        else:
            print("本次寻找未找到继续按钮，继续执行程序")
            pyautogui.click()
        time.sleep(2+wait)
        if play_end_button.find():
            print("第三次找到继续按钮，结束本场对局")
            play_end_button.click()
            pyautogui.click()
        else:
            print("第三次寻找未找到继续按钮，继续执行程序")
            pyautogui.click()
        time.sleep(wait)
        if time.time()-start_time>work_time:
            print("程序执行时间已经达到您的要求（默认4小时），程序结束")
            work=0
        else:
            print("一局游戏结束，程序将继续执行")
    return 0
if __name__ == "__main__":
    main()
#改进方向：反检测手段应该使得鼠标轨迹更加随机，且类似于平滑曲线，落点位置不确定性应该增加。此外，各处等待时间都应该设置成变量，方便调整