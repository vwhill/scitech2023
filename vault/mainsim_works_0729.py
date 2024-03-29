# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 2021

@author: Vincent W. Hill
Main simulation script for IEEE Aerospace 2022 paper "Multi-Sensor Fusion for
Decentralized Cooperative Navigation using Random Finite Sets"

THIS WORKS BEFORE SWITCHING TO EKF-CPHD
"""

#%% Imports

import numpy as np
import utilities_works0729 as util
import important_works0729 as imp
from datetime import datetime

rng = np.random.default_rng(69)
# rng = np.random.default_rng()

now = datetime.now()
start_time = now.strftime("%H:%M:%S")
print('Start Time = ', start_time)

#%% Initialize

agent_list, target_list, env, kf, rfs, control = util.init_sim()

#%% Main Loop

simlen = 300 # seconds
maxiter = int(simlen/control.dt)
count = 0

for i in range(0, 5000):
    y = []
    for ii in range(0, len(agent_list)):
        a = agent_list[ii][0]
        num = agent_list[ii][1]
        a.prop_state()
        a.save_state()
        a.prop_position()
        imp.dead_reckon(a)
        a.save_position()
        a.get_object_positions(agent_list, num, env)
        a.get_meas()
        # y.append(a.meas)  # 2DR&B
        y.append(a.dr_pos_est)  # linear position
        a.check_waypoint()
    
    y = util.miss_detect(rfs, y)
    util.gen_clutter(rfs, env, y)
    
    if i % 100 == 0:
        rfs.predict()  # CPHD
        rfs.correct(meas=y)
        rfs.prune()
        rfs.merge()
        rfs.cap()
        rfs.extract_states()

        count = count + 1
        if count % 10 == 0:
            print(count, 'CPHD runs have been performed')

#%% Plots

util.plot_results(agent_list, target_list, rfs, env)

print('Start Time = ', start_time)
now = datetime.now()
end_time = now.strftime("%H:%M:%S")
print('End Time = ', end_time)
