import os
import time
import shutil
import sys
import numpy as np


class ScenarioOrganizer():
    def __init__(self, use_socket=False):
        self.socket_mode = use_socket
        self.test_mode = ""
        self.scenario_list = []
        self.test_matrix = np.array([])
        self.test_num = 0
        self.scaler = None
        self.adaptive_method = None

    def load(self, input_dir: str, output_dir: str) -> None:
        """读取配置文件，按照配置文件（py格式）准备场景内容

        """
        self._check_output_dir(output_dir)
        # 清空场景列表
        self.scenario_list = []
        # 将目标目录加入检索目录
        sys.path.append(input_dir)
        # 读取配置文件
        from test_conf import config  # conf.py可能出现与第三方库conf冲突的情况，故改名为test_conf
        self.config = config
        self.test_mode = config['test_settings']['mode']

        self.config['file_info'] = {
            'input': input_dir,
            'output': output_dir
        }

        self.config['test_settings'].setdefault('visualize', False)

        # 如果测试模式 == 'replay'，读取文件夹下所有待测场景，存在列表中
        if self.test_mode == 'replay':  # 判断测试模式是否为replay
            self.config['test_settings'].setdefault('skip_exist_scene', False)
            for item in os.listdir(input_dir):
                if item.split(".")[-1] != 'py':
                    if item != "__pycache__" and item[0] != '.':
                        if self.config['test_settings']['skip_exist_scene'] and os.path.exists(os.path.join(output_dir, item+'_result.csv')):
                            continue
                        sce_path = input_dir + "/" + item
                        sce = self.config.copy()
                        sce['data'] = {
                            'scene_name': item,
                            'params': sce_path
                        }
                        # 将场景加入列表中
                        self.scenario_list += [sce]
            self.test_num = len(self.scenario_list)

    def next(self):
        """给出下一个待测场景与测试模式，如果没有场景了，则待测场景名称为None

        """
        # 首先判断测试的模式，replay模式和adaptive模式不一样
        if self.test_mode == 'replay':  # 如果是回放测试
            if self.scenario_list:  # 首先判断列表是否为空，如果列表不为空，则取场景；否则，输出None
                # 列表不为空，输出0号场景，且将其从列表中删除（通过pop函数实现）
                scenario_to_test = self.scenario_list.pop(0)
            else:
                # 列表为空，输出None
                scenario_to_test = None
        return scenario_to_test

    def add_result(self, concrete_scenario: dict, res: float) -> None:
        # 判断测试模式，如果是replay，则忽略测试结果
        if self.test_mode == 'replay':
            return

    def _check_output_dir(self, output_dir: str) -> None:
        """检查输出文件夹是否存在，如果不存在，则创建

        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)


if __name__ == "__main__":
    demo_replay = r"demo/demo_inputs_adaptive"
    demo_ouput_dir = r"demo/demo_outputs"
    so = ScenarioOrganizer()
    so.load(demo_replay, demo_ouput_dir)
    while True:
        scenario_to_test = so.next()
        if scenario_to_test is None:
            break  # 如果场景管理模块给出None，意味着所有场景已测试完毕。
        if scenario_to_test['test_settings']['mode'] == 'adaptive':
            res = scenario_to_test['data']['params'][0]**2 - \
                scenario_to_test['data']['params'][1]**2
        else:
            res = 1
        print(scenario_to_test, res)
        so.add_result(scenario_to_test, res)
