from onsite.observation import Observation
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np


class Visualizer():
    def __init__(self):
        self.visilize = False
        self.road_exist = False

    def init(self, observation: Observation, visilize: bool = False):
        # 测试信息
        self.scenario_name = observation.test_setting['scenario_name']
        self.scenario_type = observation.test_setting['scenario_type']
        # 可视化设置
        self.visilize = visilize
        # 初始化画布
        if visilize:
            plt.ion()
            self.fig = plt.figure(figsize=[6.4, 4.8])
            self.axbg = self.fig.add_subplot()
            self.axveh = self.axbg.twiny()
            self.road_exist = False
        else:
            plt.ioff()
            return
        if observation.road_info:  # 对于有地图文件的测试场景，如回放测试
            # 获得目标区域
            self.x_target = list(observation.test_setting['goal']['x'])
            self.y_target = list(observation.test_setting['goal']['y'])
            # 获得该场景车辆行驶的边界
            self.x_max = max(observation.test_setting['goal']['x'][-1], observation.vehicle_info['ego']['x']) + 50
            self.x_min = min(observation.test_setting['goal']['x'][-1], observation.vehicle_info['ego']['x']) - 50
            # 固定GIF图中路网范围
            self.axbg.set_xlim(self.x_min, self.x_max)
        # 更新观测值
        self.update(observation)

    def update(self, observation: Observation) -> None:
        # 结束条件
        # ---------------------------------------------
        # 如果不画图，直接退出
        if not self.visilize:
            return
        # 如果测试结束，则结束绘图，关闭绘图模块
        if observation.test_setting['end'] != -1:
            plt.ioff()
            plt.close()
            return
        self.axveh.cla()

        # 绘制车辆及道路
        # ---------------------------------------------
        self._plot_vehicles(observation)
        # 若发生碰撞，则绘制碰撞警告标志
        if observation.test_setting['end'] == 2 or observation.test_setting['end'] == 3:
            self._plot_warning_signal(observation)
        if not self.road_exist:
            self._plot_roads(observation)
            self.road_exist = True

        # 画布属性设置
        # ---------------------------------------------
        # plt.rcParams['font.family'] = 'Times New Roman'  # 若需显示汉字 SimHei黑体，STsong 华文宋体还有font.style  font.size等
        plt.rcParams['axes.unicode_minus'] = False
        if observation.road_info:   # 拥有地图文件的，默认采用上帝视角
            # 指定y坐标的显示范围
            plt.ylim(-1 * (self.x_max - self.x_min) / 2, (self.x_max - self.x_min) / 2)  # 防止车辆畸变，y轴范围与x轴一致
            # GIF视角以主车行驶范围路段固定
            self.axveh.set_xlim(self.x_min, self.x_max)
        else:  # 无地图文件的（如加速测试），采用主车中心视角
            # 设置x,y坐标的比例为相同
            plt.gca().set_aspect('equal')
            # GIF视角以主车为中心固定
            x_center = observation.vehicle_info['ego']['x']
            plt.xlim(x_center - 20, x_center + 200)
            plt.ylim(-80, 80)

        # GIF显示各类信息
        # ---------------------------------------------
        # 显示测试相关信息
        ts_text = "Time_stamp: " + str(round(observation.test_setting['t'], 4))
        name_text = 'Test_scenario: ' + str(self.scenario_name)
        type_text = 'Test_type: ' + str(self.scenario_type)
        self.axveh.text(0.02, 0.95, name_text, transform=self.axveh.transAxes, fontdict={'size': '10', 'color': 'black'})
        self.axveh.text(0.02, 0.90, type_text, transform=self.axveh.transAxes, fontdict={'size': '10', 'color': 'black'})
        self.axveh.text(0.75, 0.95, ts_text, transform=self.axveh.transAxes, fontdict={'size': '10', 'color': 'black'})
        # 碰撞信息显示
        if observation.test_setting['end'] == 2 or observation.test_setting['end'] == 3:
            collision_text = 'A collision has occurred'
            self.axveh.text(0.02, 0.85, collision_text, transform=self.axveh.transAxes, fontdict={'size': '10', 'color': 'red'})
        # 显示所有车辆运行信息
        colLabels = list(observation.vehicle_info.keys())
        rowLabels = ['v (m/s)', 'a (m/s2)']
        v = np.array([round(observation.vehicle_info[key]['v'], 4) for key in colLabels]).reshape(1, -1)
        a = np.array([round(observation.vehicle_info[key]['a'], 4) for key in colLabels]).reshape(1, -1)
        cellTexts = np.vstack((v, a))
        info_table = self.axveh.table(cellText=cellTexts, colLabels=colLabels, rowLabels=rowLabels,
                                      rowLoc='center', colLoc='center', cellLoc='center', loc='bottom')
        info_table.auto_set_font_size(False)
        info_table.set_fontsize(10)

        # 刷新当前帧画布
        # ---------------------------------------------
        plt.subplots_adjust()
        plt.pause(1e-7)
        # plt.show()

    def _plot_vehicles(self, observation: Observation) -> None:
        for key, values in observation.vehicle_info.items():
            if key == 'ego':
                self._plot_single_vehicle(key, values, c='green')
            else:
                self._plot_single_vehicle(key, values, c='cornflowerblue')

    def _plot_single_vehicle(self, key: str, vehi: dict, c='cornflowerblue'):
        """利用 matplotlib 和 patches 绘制小汽车，以 x 轴为行驶方向

        """
        x, y, yaw, width, length = [float(vehi[i])
                                    for i in ['x', 'y', 'yaw', 'width', 'length']]

        angle = np.arctan(width / length) + yaw
        diagonal = np.sqrt(length ** 2 + width ** 2)
        self.axveh.add_patch(
            patches.Rectangle(
                xy=(x - diagonal / 2 * np.cos(angle),
                    y - diagonal / 2 * np.sin(angle)),
                width=length,
                height=width,
                angle=yaw / np.pi * 180,
                color=c,
                fill=True,
                zorder=3
            ))
        if key != 'ego':
            self.axveh.annotate(key, (x, y))

    def _plot_warning_signal(self, observation: Observation, c='red'):
        '''绘制主车碰撞时的提醒标志

        '''
        for key, values in observation.vehicle_info.items():
            if key == 'ego':
                x, y = [float(values[i]) for i in ['x', 'y']]
                self.axveh.scatter(x, y, s=60, c=c, alpha=1.0, marker=(8, 1, 30), zorder=4)

    def _plot_roads(self, observation: Observation) -> None:
        '''根据observation绘制道路，只要完成绘制工作即可。plt.plot()。其他plt.show()之类的不需要添加

        Parameters
        ----------
        observation:当前时刻的观察值
        '''
        road_data_for_plot = observation.road_info
        # plotting roads
        if not road_data_for_plot:
            return

        xlim1 = float("Inf")
        xlim2 = -float("Inf")
        ylim1 = float("Inf")
        ylim2 = -float("Inf")
        color = "gray"
        label = None
        draw_arrow = True

        for discrete_lane in road_data_for_plot.discretelanes:
            verts = []
            codes = [Path.MOVETO]

            for x, y in np.vstack(
                [discrete_lane.left_vertices, discrete_lane.right_vertices[::-1]]
            ):
                verts.append([x, y])
                codes.append(Path.LINETO)

                # if color != 'gray':
                xlim1 = min(xlim1, x)
                xlim2 = max(xlim2, x)

                ylim1 = min(ylim1, y)
                ylim2 = max(ylim2, y)

            verts.append(verts[0])
            codes[-1] = Path.CLOSEPOLY

            path = Path(verts, codes)

            self.axbg.add_patch(
                patches.PathPatch(
                    path,
                    facecolor=color,
                    edgecolor="black",
                    lw=0.0,
                    alpha=0.5,
                    zorder=0,
                    label=label,
                )
            )

            self.axbg.plot(
                [x for x, _ in discrete_lane.left_vertices],
                [y for _, y in discrete_lane.left_vertices],
                color="black",
                lw=0.3,
                zorder=1,
            )
            self.axbg.plot(
                [x for x, _ in discrete_lane.right_vertices],
                [y for _, y in discrete_lane.right_vertices],
                color="black",
                lw=0.3,
                zorder=1,
            )

            self.axbg.plot(
                [x for x, _ in discrete_lane.center_vertices],
                [y for _, y in discrete_lane.center_vertices],
                color="white",
                alpha=0.5,
                lw=0.8,
                zorder=1,
            )

            if draw_arrow:
                mc = discrete_lane.center_vertices
                total_len = ((mc[0][0] - mc[-1][0]) ** 2 + (mc[0][1] - mc[-1][1]) ** 2) ** 0.5
                if total_len > 30:
                    index_ = list(map(int, np.linspace(start=10, stop=mc.shape[0] - 10, num=4)))
                else:
                    index_ = []
                for i in range(len(index_)):
                    start_c, end_c = mc[index_[i]], mc[index_[i] + 1]
                    self.axbg.arrow(
                        start_c[0], start_c[1], end_c[0] - start_c[0], end_c[1] - start_c[1],
                        shape='full',
                        color='white',
                        alpha=0.5,
                        head_width=1,
                        head_length=2,
                        length_includes_head=True,
                        zorder=1,
                    )
                    '''
                    start_l, end_l = ml[index_[i]], ml[index_[i] + 1]
                    start_r, end_r = mr[index_[i]], mr[index_[i] + 1]
                    self.axbg.arrow(
                        start_l[0], start_l[1], end_l[0] - start_l[0], end_l[1] - start_l[1],
                        shape='full',
                        color='black',
                        head_width=0.5,
                        head_length=2,
                        length_includes_head=True,
                        zorder=1,
                    )
                    self.axbg.arrow(
                        start_r[0], start_r[1], end_r[0] - start_r[0], end_r[1] - start_r[1],
                        shape='full',
                        color='black',
                        head_width=0.5,
                        head_length=2,
                        length_includes_head=True,
                        zorder=1
                    )
                    '''
        # 绘制目标区域
        if self.x_target and self.y_target:
            x, y = self.x_target, self.y_target
            codes_box = [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]  # 路径连接方式
            vertices_box = [(x[0], y[0]), (x[1], y[0]), (x[1], y[1]), (x[0], y[1]), (0, 0)]  # 路径连接点
            path_box = Path(vertices_box, codes_box)  # 定义对应Path
            pathpatch_box = patches.PathPatch(path_box, facecolor='tomato', edgecolor='orangered', zorder=2)
            self.axbg.add_patch(pathpatch_box)
        return
