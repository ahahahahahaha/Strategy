# action只有345678有效，前3个是用来初始化之类的东西不用管
import numpy as np
import socket
import struct
CMD = {'Run':0, 'Reset':1, 'Sensor':2, 'Takeoff':3, 'Move':4, 'Land':5, 'Intercept':6, 'Touch':7, 'Follow':8}
# action = (cmd, x, y, n)
class env:
    def __init__(self, num_target, num_obs):
        # ground bot
        self.target_number = num_target
        self.target_loc = 999*np.ones(shape=(2,self.target_number))
        self.target_vel = np.zeros(shape=(2,self.target_number))
        # obstacle bot
        self.obs_number = num_obs
        self.obs_loc = 999*np.ones(shape=(2,self.obs_number))
        self.obs_vel = np.zeros(shape=(2,self.obs_number))
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

    def sendudp(self, cmd):
        c = struct.pack('iidd',cmd(0), cmd(1), cmd(2), cmd(3))
        self.sck_send.sendto(c, ('127.0.0.1', 4012))
        # send sensor
    def recvudp(self):
        c = struct.pack('iidd', 2, 0, 0, 0)
        self.sck_send.sendto(c, ('127.0.0.1', 4012))
        # udp send
        time = 0
        for i in range(self.target_number):
            message, clientAddress = self.sck_recv.recvfrom(2048)
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
            message, clientAddress = self.sck_recv.recvfrom(2048)
            msg = struct.unpack('didddd', message)
            idx = msg[1]
            self.obs_loc[0][idx] = msg[2]
            self.obs_loc[1][idx] = msg[3]
            self.obs_vel[0][idx] = msg[4]
            self.obs_vel[1][idx] = msg[5]
        self.last_time = self.cur_time
        self.cur_time = time
        print('current time: ', time)
        # todo 还没有加入obs
        return np.concatenate((self.target_loc, self.target_vel))

    def reset(self):
        # reset
        cmd = struct.pack('iidd',1, 0, 0, 0)
        self.sck_send.sendto(cmd, ('127.0.0.1', 4012))
        # get sensor
        cmd = struct.pack('iidd', 2, 0, 0, 0)
        self.sck_send.sendto(cmd, ('127.0.0.1', 4012))
    def step(self, action):
        if action(0) > 0 and action(0) < 9:
            self.sendudp(action)
            self.observation = self.recvudp()
            self.done = False # 包里没有这个东西
            self.log = ""
            self.reward = 0
            return (self.observation, self.reward, self.done, self.log)


