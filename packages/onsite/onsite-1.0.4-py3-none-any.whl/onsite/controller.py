import math

from unicodedata import category

from onsite.observation import Observation
from onsite.opendrive2discretenet.opendriveparser.parser import parse_opendrive
from onsite.opendrive2discretenet.network import Network

import os
import xml.dom.minidom
from lxml import etree
import json
import re
import numpy as np
import copy
from shapely.geometry import Polygon
from itertools import combinations


class ReplayInfo():
    """用于存储回放测试中用以控制背景车辆的所有数据
        背景车轨迹信息 vehicle_traj
        vehicle_traj = {
            "vehicle_id_0":{
                "shape":{
                    "wid":4,
                    "len":5
                },
                "t_0":{
                    "x":10,
                    "y":10,
                    "v":10,
                    "a":0,
                    "yaw":0
                },
                "t_1":{...},
                ...
            },
            "vehicle_id_1":{...},
            ...
        }
        主车轨迹信息，只包含当前帧信息
        ego_info = {
            "x":,
            "y":,
            "v":,
            "a":,
            "yaw":,
            "length":,
            "width":,
        }
        信号信息
        light_info = {}
        地图相关信息，具体介绍参考网站上入门中地图解析工作的教程
        road_info = {}
        测试环境相关信息 test_setting
        test_setting = {
            "t":,
            "dt":,
            "max_t",
            "goal":{
                    "x":[],
                    "y":[]
                }
            "end":,
            "scenario_type":,
            "scenario_name":,
            "map_type":
        }

    """

    def __init__(self):
        self.vehicle_traj = {}
        self.ego_info = {
            "length": 4.924,
            "width": 1.872,
            "x": 0,
            "y": 0,
            "v": 0,
            "a": 0,
            "yaw": 0
        }
        self.light_info = {}
        self.road_info = {}
        self.test_setting = {
            "t": 0,
            "dt": 0.01,
            "max_t": 10,
            "goal": {
                "x": [-10, 10],
                "y": [-10, 10]
            },
            "end": -1,
            "scenario_name":None,
            "scenario_type":None,
            "map_type":None
        }

    def add_vehicle(self, id, t, x=None, y=None, v=None, a=None, yaw=None, length=None, width=None):
        """
        该函数实现向vehicle_trajectiry中添加背景车轨迹信息的功能
        """
        if id == "ego":
            self._add_vehicle_ego(x, y, v, a, yaw, length, width)
        else:
            if id not in self.vehicle_traj.keys():
                self.vehicle_traj[id] = {}
                self.vehicle_traj[id]['shape'] = {}
            if t not in self.vehicle_traj[id].keys():
                self.vehicle_traj[id][t] = {}
            for key, value in zip(['x', 'y', 'v', 'a', 'yaw'], [x, y, v, a, yaw]):
                if value is not None:
                    self.vehicle_traj[id][t][key] = value
            for key, value in zip(['length', 'width'], [length, width]):
                if value is not None:
                    self.vehicle_traj[id]['shape'][key] = value

    def add_settings(self, scenario_name=None, scenario_type=None, dt=None, max_t=None, goal_x=None, goal_y=None):
        """
        该函数实现向test_setting中添加测试环境相关信息
        """
        for key, value in zip(['scenario_name', 'scenario_type', 'dt', 'max_t'],
                              [scenario_name, scenario_type, dt, max_t]):
            if value is not None:
                self.test_setting[key] = value
        for key, value in zip(['x', 'y'], [goal_x, goal_y]):
            if value is not None:
                self.test_setting['goal'][key] = value

    def _add_vehicle_ego(self, x=None, y=None, v=None, a=None, yaw=None, length=None, width=None):
        """
        该函数实现向ego_info中增加主车信息的功能
        注意：ego_info中只含有主车当前帧的信息
        """
        for key, value in zip(['x', 'y', 'v', 'a', 'yaw', 'length', 'width'], [x, y, v, a, yaw, length, width]):
            if value is not None:
                self.ego_info[key] = value

    def _get_dt_maxt(self):
        """
        该函数实现得到最大仿真时长阈值以及采样率的功能
        """
        max_t = 0
        for i in self.vehicle_traj.keys():
            t_i = list(self.vehicle_traj[i].keys())
            max_t_i = float(t_i[-1])
            if max_t_i > max_t:
                max_t = max_t_i
        dt = np.around(float(t_i[-1]) - float(t_i[-2]), 3)
        self.add_settings(dt=dt, max_t=max_t)


class ReplayParser():
    """
    解析场景文件
    """
    def __init__(self):
        self.replay_info = ReplayInfo()

    def parse(self, senario_data: str) -> ReplayInfo:
        # 在目录中寻找.xosc文件、.xodr文件和.json文件
        path_json = ''
        input_dir = senario_data['params']
        for item in os.listdir(input_dir):
            if item.split(".")[-1] == 'xosc':
                path_openscenario = input_dir + "/" + item
            if item.split(".")[-1] == 'xodr':
                path_opendrive = input_dir + "/" + item
            if item.split(".")[-1] == 'json':
                path_json = input_dir + "/" + item

        # 获取其他信息
        # 场景名称与测试类型
        self.replay_info.add_settings(scenario_name=senario_data['scene_name'], scenario_type='replay')

        self._parse_openscenario(path_openscenario)
        self._parse_opendrive(path_opendrive)
        if path_json:
            self._parse_light_json(path_json)
        return self.replay_info

    def _parse_light_json(self, file_dir: str) -> None:
        with open(file_dir, 'r') as read_f:
            self.replay_info.light_info = json.load(read_f)
        return

    def _parse_openscenario(self, file_dir: str):
        # 读取OpenScenario文件
        opens = xml.dom.minidom.parse(file_dir).documentElement

        # 读取车辆长度与宽度信息，录入replay_info。背景车id从1号开始
        wl_node = opens.getElementsByTagName('Dimensions')
        for num, wl in zip(range(len(wl_node)), wl_node):
            if num == 0:
                self.replay_info.add_vehicle(
                    id="ego",
                    t=-1,
                    width=float(wl.getAttribute('width')),
                    length=float(wl.getAttribute('length'))
                )
            else:
                self.replay_info.add_vehicle(
                    id=num,
                    t=-1,
                    width=float(wl.getAttribute('width')),
                    length=float(wl.getAttribute('length'))
                )

        # 读取本车信息, 记录为ego_v,ego_x,ego_y,ego_head
        ego_node = opens.getElementsByTagName('Private')[0]
        ego_init = ego_node.childNodes[3].data
        ego_v, ego_x, ego_y, ego_head = [
            float(i.split('=')[1]) for i in ego_init.split(',')]
        ego_v = abs(ego_v)
        ego_head = (ego_head + 2 * math.pi) if -math.pi <= ego_head < 0 else ego_head
        self.replay_info.add_vehicle(
            id="ego",
            t=-1,
            x=ego_x,
            y=ego_y,
            v=ego_v,
            a=0,
            yaw=ego_head
        )

        """以下读取背景车相关信息，车辆编号从1号开始，轨迹信息记录在vehicle_traj中"""
        """新版场景中采用更general的定义方式，在初始时仅初始化主车，背景车的采用Event中的AddEntityAction和DeleteEntityAction"""
        act_list = opens.getElementsByTagName('Act')
        for id, act in zip(np.arange(1, len(act_list) + 1), act_list):
            # 记录OpenScenario中存在的位置、航向角、时间信息
            t_list, x_list, y_list, yaw_list = [[] for i in range(4)]
            for point in act.getElementsByTagName('Vertex'):
                t_list.append(round(float(point.getAttribute('time')), 3))  # 记录时间，保留三位小数
                loc = point.getElementsByTagName('WorldPosition')[0]
                x_list.append(float(loc.getAttribute('x')))  # 记录横向位置
                y_list.append(float(loc.getAttribute('y')))  # 记录纵向位置
                yaw = float(loc.getAttribute('h'))  # 记录航向角
                yaw = (yaw + 2 * math.pi) if -math.pi <= yaw < 0 else yaw  # 航向角范围调整到(0, 2pi)
                yaw_list.append(yaw)
            # 计算速度信息
            x_diff = np.diff(x_list)  # 横向距离差
            y_diff = np.diff(y_list)  # 纵向距离差
            t_diff = np.diff(t_list)
            v_list = np.sqrt(x_diff**2+y_diff**2)/t_diff  # 此时v维度比其他参数低
            v_list = list(np.around(v_list, 2))  # 保留2位小数
            v_list.append(v_list[-1])  # 补全维度
            # 计算加速度信息
            v_diff = np.diff(v_list)
            a_list = v_diff/t_diff
            a_list = list(np.around(a_list, 2))  # 保留2位小数
            a_list.append(0.00)  # 补全维度
            # 把时间t_list的内容以字符串形式保存，作为key
            t_list = [str(t) for t in t_list]
            for t, x, y, v, a, yaw in zip(t_list, x_list, y_list, v_list, a_list, yaw_list):
                self.replay_info.add_vehicle(
                    id=id,
                    t=t,
                    x=round(x, 2),
                    y=round(y, 2),
                    v=round(v, 2),
                    a=round(a, 2),
                    yaw=round(yaw, 3)
                )

        # 获取行驶目标, goal
        goal_init = ego_node.childNodes[5].data
        goal = [float(i) for i in re.findall('-*\d+\.\d+', goal_init)]
        self.replay_info.add_settings(
            goal_x=goal[:2],
            goal_y=goal[2:]
        )
        # 步长与最大时间
        self.replay_info._get_dt_maxt()

        return self.replay_info

    def _parse_opendrive(self, path_opendrive: str) -> None:
        """
        解析opendrive路网的信息，存储到self.replay_info.road_info。
        """
        fh = open(path_opendrive, "r")
        # 返回OpenDrive类的实例对象（经过parser.py解析）
        root = etree.parse(fh).getroot()
        openDriveXml = parse_opendrive(root)
        fh.close()

        # 将OpenDrive类对象进一步解析为参数化的Network类对象，以备后续转化为DiscreteNetwork路网并可视化
        self.loadedRoadNetwork = Network()
        self.loadedRoadNetwork.load_opendrive(openDriveXml)

        """将解析完成的Network类对象转换为DiscreteNetwork路网，其中使用的只有路网中各车道两侧边界的散点坐标
            车道边界点通过线性插值的方式得到，坐标点储存在<DiscreteNetwork.discretelanes.left_vertices/right_vertices> -> List"""

        open_drive_info = self.loadedRoadNetwork.export_discrete_network(
            filter_types=["driving", "onRamp", "offRamp", "exit", "entry"])  # -> <class> DiscreteNetwork
        self.replay_info.road_info = open_drive_info
        # 记录地图类型
        name = root.find('header').attrib['name']
        if name in ['highway','highD']:
            self.replay_info.test_setting['map_type'] = "highway"
        elif name in ['','SinD']:
            self.replay_info.test_setting['map_type'] = "intersection"
        elif name in ['NDS_ramp']:
            self.replay_info.test_setting['map_type'] = 'ramp'


class ReplayController():
    def __init__(self):
        self.control_info = ReplayInfo()

    def init(self, control_info: ReplayInfo) -> Observation:
        self.control_info = control_info
        return self._get_initial_observation()

    def step(self, action, old_observation: Observation) -> Observation:
        action = self._action_cheaker(action)
        new_observation = self._update_ego_and_t(action, old_observation)
        new_observation = self._update_other_vehicles_to_t(new_observation)
        new_observation = self._update_end_status(new_observation)
        if self.control_info.light_info:
            new_observation = self._update_light_info_to_t(new_observation)
        return new_observation

    def _action_cheaker(self, action):
        a = np.clip(action[0], -15, 15)
        rad = np.clip(action[1], -1, 1)
        return (a, rad)

    def _get_initial_observation(self) -> Observation:
        observation = Observation()
        # vehicle_info
        observation.vehicle_info["ego"] = self.control_info.ego_info
        observation = self._update_other_vehicles_to_t(observation)
        # road_info
        observation.road_info = self.control_info.road_info
        # test_setting
        observation.test_setting = self.control_info.test_setting
        # 求出一个包含所有地图的矩形
        points = np.empty(shape=[0, 2])
        for discrete_lane in observation.road_info.discretelanes:
            points = np.concatenate(
                [discrete_lane.left_vertices, discrete_lane.right_vertices, discrete_lane.center_vertices, points],
                axis=0)
        points_x = points[:, 0]
        points_y = points[:, 1]
        observation.test_setting['x_max'] = np.max(points_x)
        observation.test_setting['x_min'] = np.min(points_x)
        observation.test_setting['y_max'] = np.max(points_y)
        observation.test_setting['y_min'] = np.min(points_y)
        observation = self._update_end_status(observation)
        # light_info
        if self.control_info.light_info:
            observation.test_setting['t'] = float(('%.2f'% observation.test_setting['t']))
            observation.light_info = self.control_info.light_info[str(np.around(observation.test_setting['t'], 3))]
        return observation

    def _update_light_info_to_t(self, old_observation: Observation) -> Observation:
        new_observation = copy.copy(old_observation)
        new_observation.light_info = self.control_info.light_info[str(np.around(old_observation.test_setting['t'], 3))]
        return new_observation

    def _update_ego_and_t(self, action: tuple, old_observation: Observation) -> Observation:
        # 拷贝一份旧观察值
        new_observation = copy.copy(old_observation)
        # 小数点位数，避免浮点数精度问题
        decimal_places = len(str(old_observation.test_setting['dt']).split('.')[-1])
        # 首先修改时间，新时间=t+dt
        new_observation.test_setting['t'] = round(float(
            old_observation.test_setting['t'] +
            old_observation.test_setting['dt']
        ), decimal_places)
        # 修改本车的位置，方式是前向欧拉更新，1.根据旧速度更新位置；2.然后更新速度。
        # 速度和位置的更新基于自行车模型。
        # 首先分别取出加速度和方向盘转角
        a, rot = action
        # 取出步长
        dt = old_observation.test_setting['dt']
        # 取出本车的各类信息
        x, y, v, yaw, width, length = [float(old_observation.vehicle_info['ego'][key]) for key in [
            'x', 'y', 'v', 'yaw', 'width', 'length']]

        # 首先根据旧速度更新本车位置
        new_observation.vehicle_info['ego']['x'] = x + \
                                                   v * np.cos(yaw) * dt  # 更新X坐标

        new_observation.vehicle_info['ego']['y'] = y + \
                                                   v * np.sin(yaw) * dt  # 更新y坐标

        new_observation.vehicle_info['ego']['yaw'] = yaw + \
                                                     v / length * 1.7 * np.tan(rot) * dt  # 更新偏航角

        new_observation.vehicle_info['ego']['v'] = v + a * dt  # 更新速度
        if new_observation.vehicle_info['ego']['v'] < 0:
            new_observation.vehicle_info['ego']['v'] = 0

        new_observation.vehicle_info['ego']['a'] = a  # 更新加速度
        return new_observation

    def _update_other_vehicles_to_t(self, old_observation: Observation) -> Observation:
        # 删除除了ego之外的车辆观察值
        new_observation = copy.copy(old_observation)  # 复制一份旧观察值
        new_observation.vehicle_info = {}
        # 将本车信息添加回来
        new_observation.vehicle_info['ego'] = old_observation.vehicle_info['ego']
        # 根据时间t，查询control_info,赋予新值
        t = old_observation.test_setting['t']
        t = str(np.around(t, 3))  # t保留3位小数，与生成control_info时相吻合
        for vehi in self.control_info.vehicle_traj.items():
            id = vehi[0]  # 车辆id
            info = vehi[1]  # 车辆的轨迹信息
            if t in info.keys():
                new_observation.vehicle_info[id] = {}
                for key in ['x', 'y', 'v', 'a', 'yaw']:
                    new_observation.vehicle_info[id][key] = info[t][key]
                for key in ['width', 'length']:
                    new_observation.vehicle_info[id][key] = info['shape'][key]
        return new_observation

    def _update_end_status(self, observation: Observation) -> Observation:
        """计算T时刻, 测试是否终止, 更新observation.test_setting中的end值
            end=
                1:回放测试运行完毕;
                2:发生碰撞;
        """
        status_list = [-1]

        # 检查主车与背景车是否发生碰撞
        if self._collision_detect(observation):
            status_list += [2]

        # 检查是否已到达场景终止时间max_t
        if observation.test_setting['t'] >= self.control_info.test_setting['max_t']:
            status_list += [1]
        # 检查是否已经驶出地图范围
        if self.control_info.test_setting['map_type'] in ['highway', 'ramp']:
            if observation.vehicle_info['ego']['x'] > observation.test_setting['x_max'] or \
                    observation.vehicle_info['ego']['x'] < observation.test_setting['x_min']:
                status_list += [1.5]
        elif self.control_info.test_setting['map_type'] in ["intersection"]:
            if observation.vehicle_info['ego']['x'] > observation.test_setting['x_max'] or \
                    observation.vehicle_info['ego']['x'] < observation.test_setting['x_min'] or \
                    observation.vehicle_info['ego']['y'] > observation.test_setting['y_max'] or \
                    observation.vehicle_info['ego']['y'] < observation.test_setting['y_min']:
                status_list += [1.5]

        # 从所有status中取最大的那个作为end。
        observation.test_setting['end'] = max(status_list)
        return observation

    def _collision_detect(self, observation: Observation) -> bool:
        poly_zip = []
        self.vehicle_index = []  # 这里为了判断哪两辆车发生了碰撞，定义了列表用来存放车辆名称，其index与poly_zip中车辆的图形索引相对应
        # 当测试时间大于0.5秒时，遍历所有车辆，绘制对应的多边形。这是因为数据问题，有些车辆在初始位置有重叠。也就是说0.5s以内不会判断是否碰撞。
        if observation.test_setting['t'] > 0.5:
            for index, vehi in observation.vehicle_info.items():
                self.vehicle_index += [index]
                poly_zip += [self._get_poly(vehi)]

        # 检测主车是否与背景车碰撞
        for a, b in combinations(poly_zip, 2):
            if self.vehicle_index[poly_zip.index(a)] == 'ego' or self.vehicle_index[poly_zip.index(b)] == 'ego':
                if a.intersects(b):
                    return True
                else:
                    continue
        return False

    def _get_poly(self, vehicle: dict) -> Polygon:
        """根据车辆信息,通过shapely库绘制矩形。

        这是为了方便地使用shapely库判断场景中的车辆是否发生碰撞
        """
        # 从字典中取出数据，方便后续处理
        x, y, yaw, width, length = [float(vehicle[i])
                                    for i in ['x', 'y', 'yaw', 'width', 'length']]

        # 以下代码，是通过x，y，车辆转角，车长，车宽信息，计算出车辆矩形的4个顶点。
        alpha = np.arctan(width / length)
        diagonal = np.sqrt(width ** 2 + length ** 2)
        # poly_list = []
        x0 = x + diagonal / 2 * np.cos(yaw + alpha)
        y0 = y + diagonal / 2 * np.sin(yaw + alpha)
        x2 = x - diagonal / 2 * np.cos(yaw + alpha)
        y2 = y - diagonal / 2 * np.sin(yaw + alpha)
        x1 = x + diagonal / 2 * np.cos(yaw - alpha)
        y1 = y + diagonal / 2 * np.sin(yaw - alpha)
        x3 = x - diagonal / 2 * np.cos(yaw - alpha)
        y3 = y - diagonal / 2 * np.sin(yaw - alpha)

        # 通过车辆矩形的4个顶点，可以绘制出对应的长方形
        poly = Polygon(((x0, y0), (x1, y1),
                        (x2, y2), (x3, y3),
                        (x0, y0))).convex_hull
        return poly


def _add_vehicle_to_observation(env, old_observation: Observation) -> Observation:
    # print(env.vehicle_list,env.vehicle_array)
    new_observation = old_observation
    for i in range(len(env.vehicle_list)):
        name = env.vehicle_list[i]
        data = env.vehicle_array[0, i, :]
        for key, value in zip(
                ['x', 'y', 'v', 'yaw', 'length', 'width'],
                data
        ):
            if name not in new_observation.vehicle_info.keys():
                new_observation.vehicle_info[name] = {'x': -1, 'y': -1, 'v': -1,
                                                      'a': 0, 'yaw': -1, 'length': -1, 'width': -1}
            new_observation.vehicle_info[name][key] = value
    return new_observation

class Controller():
    """控制车辆运行

    """

    def __init__(self) -> None:
        self.observation = Observation()
        self.parser = None
        self.control_info = None
        self.controller = None
        self.mode = 'replay'

    def init(self, scenario: dict) -> Observation:
        """初始化运行场景，给定初始时刻的观察值

        Parameters
        ----------
        input_dir : str
            测试输入文件所在位置
                回放测试：包含.xodr、.xosc文件
                交互测试：
        mode : str
            指定测试模式
                回放测试：replay
                交互测试：interact
        Returns
        -------
        observation : Observation
            初始时刻的观察值信息，以Observation类的对象返回。
        """
        self.mode = scenario['test_settings']['mode']
        if self.mode == 'replay':
            self.parser = ReplayParser()
            self.controller = ReplayController()
            self.control_info = self.parser.parse(scenario['data'])
            self.observation = self.controller.init(self.control_info)
            self.traj = self.control_info.vehicle_traj
        return self.observation, self.traj

    def step(self, action):
        self.observation = self.controller.step(action, self.observation)
        return self.observation


if __name__ == "__main__":
    # 指定输入输出文件夹位置
    demo_input_dir = r"demo/demo_inputs"
    demo_output_dir = r"demo/demo_outputs"
    from onsite.scenarioOrganizer import ScenarioOrganizer

    # 实例化场景管理模块（ScenairoOrganizer）和场景测试模块（Env）
    so = ScenarioOrganizer()
    # 根据配置文件config.py装载场景，指定输入文件夹即可，会自动检索配置文件
    so.load(demo_input_dir, demo_output_dir)
    scenario_to_test = so.next()
    print(scenario_to_test)
    controller = Controller()
    controller.init(scenario_to_test)

    # self.l = len_list[0]/self.l_l # 计算本车轴距
