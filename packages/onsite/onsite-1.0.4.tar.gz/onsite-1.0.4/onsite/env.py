from onsite.observation import Observation
from onsite.controller import Controller
from onsite.recorder import Recorder
from onsite.visualizer import Visualizer


class Env():
    def __init__(self):
        self.controller = Controller()
        self.recorder = Recorder()
        self.visualizer = Visualizer()

    def make(self, scenario: dict, read_only=False) -> Observation:
        observation, traj = self.controller.init(scenario)
        self.recorder.init(observation, scenario['file_info']['output'], read_only)
        self.visualizer.init(observation, scenario['test_settings']['visualize'])
        
        return observation.format(), traj

    def step(self, action) -> Observation:
        observation = self.controller.step(action)
        self.recorder.record(observation)
        self.visualizer.update(observation)
        return observation.format()


if __name__ == "__main__":
    import time
    demo_input_dir = r"demo/demo_inputs"
    demo_ouput_dir = r"demo/demo_outputs"
    tic = time.time()
    env = Env()

    from onsite.scenarioOrganizer import ScenarioOrganizer
    # 实例化场景管理模块（ScenairoOrganizer）和场景测试模块（Env）
    so = ScenarioOrganizer()
    # 根据配置文件config.py装载场景，指定输入文件夹即可，会自动检索配置文件
    so.load(demo_input_dir, demo_ouput_dir)
    num_scenario = len(so.scenario_list)
    for i in range(num_scenario):
        scenario_to_test = so.next()
        print(scenario_to_test)
        observation = env.make(scenario_to_test, demo_ouput_dir, visilize=True)
        while observation.test_setting['end'] == -1:
            observation = env.step([-1, 0])
            # print(observation.vehicle_info['ego'])
    toc = time.time()
    print(toc - tic)
