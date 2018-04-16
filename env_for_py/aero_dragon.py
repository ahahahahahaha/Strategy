from tensorforce.environments import Environment
# action只有345678有效，前3个是用来初始化之类的东西不用管
import numpy as np
import socket
import struct
CMD = {'Run': 0, 'Reset': 1, 'Sensor': 2, 'Takeoff': 3, 'Move': 4, 'Land': 5, 'Intercept': 6, 'Touch': 7, 'Follow': 8}
ACTION_NAMES = ['cmd', 'x', 'y', 'n']


class AeroDragon(Environment):
    def __init__(self, num_target, num_obs):
        # ground bot
        self.target_number = num_target
        self.target_loc = 999*np.ones(shape=(2, self.target_number))
        self.target_vel = np.zeros(shape=(2, self.target_number))
        # obstacle bot
        self.obs_number = num_obs
        self.obs_loc = 999*np.ones(shape=(2, self.obs_number))
        self.obs_vel = np.zeros(shape=(2, self.obs_number))
        # aero bot
        # 还没有传过来
        self.cur_time = 0
        self.last_time = 0
        self.action_space = 6
        # self.observation_space
        self.sck_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sck_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sck_recv.bind(('', 4011))
        # sendto localhost:4012
        # recvat localhost:4011
        self._state = np.zeros((4, self.target_number+self.obs_number+1))
        self.log = ""
        self.done = False
        self.reward = 0

    def sendudp(self, cmd):
        c = struct.pack('iidd', cmd(0), cmd(1), cmd(2), cmd(3))
        self.sck_send.sendto(c, ('127.0.0.1', 4012))
        # send sensor

    def recvudp(self):
        c = struct.pack('iidd', 2, 0, 0, 0)
        self.sck_send.sendto(c, ('127.0.0.1', 4012))
        # udp send
        time = 0
        for i in range(self.target_number):
            message, clientaddress = self.sck_recv.recvfrom(2048)
            msg = struct.unpack('didddd', message)
            time = msg[0]
            idx = msg[1]
            self.target_loc[0][idx] = msg[2]
            self.target_loc[1][idx] = msg[3]
            self.target_vel[0][idx] = msg[4]
            self.target_vel[1][idx] = msg[5]
            print('target location: ', self.target_loc)
            print('target velocity: ', self.target_vel)
        for i in range(self.obs_number):
            message, clientaddress = self.sck_recv.recvfrom(2048)
            msg = struct.unpack('didddd', message)
            idx = msg[1]
            self.obs_loc[0][idx] = msg[2]
            self.obs_loc[1][idx] = msg[3]
            self.obs_vel[0][idx] = msg[4]
            self.obs_vel[1][idx] = msg[5]

        self.last_time = self.cur_time
        self.cur_time = time
        print('current time: ', time)
        # return 2*(num_tar+num_obs+1)
        t1 = np.concatenate((self.target_loc, self.target_vel))
        t2 = np.concatenate((self.obs_loc, self.obs_vel))
        # todo
        # aero loc & vel
        t3 = np.zeros(shape=(4, 1))
        return np.concatenate((t1, t2, t3), axis=1)

    # def step(self, action):
    #     if action(0) > 0 and action(0) < 9:
    #         self.sendudp(action)
    #         self.observation = self.recvudp()
    #         self.done = False  # 包里没有这个东西
    #         self.log = ""
    #         self.reward = 0
    #         return (self.observation, self.reward, self.done, self.log)

    def reset(self):
        cmd = struct.pack('iidd', 1, 0, 0, 0)
        self.sck_send.sendto(cmd, ('127.0.0.1', 4012))
        # get sensor
        cmd = struct.pack('iidd', 2, 0, 0, 0)
        self.sck_send.sendto(cmd, ('127.0.0.1', 4012))
        self._state = self.recvudp()
        return self._state

    def execute(self, action):
        if action(0) > 0 and action(0) < 9:
            self.sendudp(action)
            self._state = self.recvudp()
            self.done = False  # 包里没有这个东西
            self.log = ""
            self.reward = 0
            return self._state, self.reward, self.done, self.log

    @property
    def states(self):
        return dict(shape=self._state.shape, type='float32')

    @property
    def actions(self):
        return dict(num_actions=len(ACTION_NAMES), type='int')

    def print_state(self):
        separator_line = '-' * 25
        print(separator_line)
        print(self._state)

    def __str__(self):
        self.print_state()