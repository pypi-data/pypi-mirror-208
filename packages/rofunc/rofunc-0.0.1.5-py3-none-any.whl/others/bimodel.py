import numpy as np
import matplotlib.pyplot as plt
import rofunc as rf
from rofunc.utils.data_generator.bezier import multi_bezier_demos
from rofunc.utils.data_generator.circle import draw_arc

np.set_printoptions(precision=2)
demo_idx = 2

save_params = {'save_dir': '/home/ubuntu/Pictures/BIRP5', 'format': ['eps', 'png']}


def bi_spatial_data():
    # Create demos for dual arms via bezier
    left_demo_points = np.array([[[0, 0], [-1, 8], [4, 3], [2, 1], [4, 3]],
                                 [[0, -2], [-1, 7], [3, 2.5], [2, 1.6], [4, 3]],
                                 [[0, -1], [-1, 8], [4, 5.2], [2, 1.1], [4, 3.5]]])
    right_demo_points = np.array([[[8, 8], [7, 1], [4, 3], [6, 8], [4, 3.5]],
                                  [[8, 7], [7, 1], [3, 3], [6, 6], [4, 3]],
                                  [[8, 8], [7, 1], [4, 5], [6, 8], [4, 3.5]]])

    fig = plt.figure()
    demos_left_x = multi_bezier_demos(left_demo_points)  # (3, 50, 2): 3 demos, each has 50 points
    demos_right_x = multi_bezier_demos(right_demo_points)
    plt.plot([4, 4], [3.5, 3], 'kx', label='meeting points')
    plt.plot(left_demo_points[:, 0, 0], left_demo_points[:, 0, 1], 'go', label='left starting points')
    plt.plot(right_demo_points[:, 0, 0], right_demo_points[:, 0, 1], 'bo', label='right starting points')
    plt.legend()
    rf.visualab.save_img(fig, save_params['save_dir'])
    plt.show()
    return demos_left_x, demos_right_x


def data2():
    # Create demos for dual arms via bezier
    left_demo_points = np.array([[[0, 0], [-1, 8], [4, 3], [2, 1], [3.5, 3]],
                                 [[0, -2], [-1, 7], [3, 2.5], [2, 1.6], [3.5, 3]],
                                 [[0, -1], [-1, 8], [4, 5.2], [2, 1.1], [3.5, 3.5]]])
    right_demo_points = np.array([[[8, 8], [7, 1], [4, 3], [6, 8], [4.5, 3]],
                                  [[8, 7], [7, 1], [3, 3], [6, 6], [4.5, 3]],
                                  [[8, 8], [7, 1], [4, 5], [6, 8], [4.5, 3.5]]])

    plt.figure()
    demos_left_x = multi_bezier_demos(left_demo_points)  # (3, 50, 2): 3 demos, each has 50 points
    demos_right_x = multi_bezier_demos(right_demo_points)

    left_line = multi_bezier_demos(np.array([[[3.5, 3], [4, 4], [3, 5]],
                                             [[3.5, 3], [4, 4], [3, 5]],
                                             [[3.5, 3.5], [4, 4.5], [3, 5.5]]]))
    right_line = multi_bezier_demos(np.array([[[4.5, 3], [5, 4], [4, 5]],
                                              [[4.5, 3], [5, 4], [4, 5]],
                                              [[4.5, 3.5], [5, 4.5], [4, 5.5]]]))

    plt.plot([4, 4], [3.5, 3], 'kx', label='meeting points')
    plt.plot(left_demo_points[:, 0, 0], left_demo_points[:, 0, 1], 'go', label='left starting points')
    plt.plot(right_demo_points[:, 0, 0], right_demo_points[:, 0, 1], 'bo', label='right starting points')
    plt.legend()
    plt.show()

    demos_left_x = np.hstack((demos_left_x, left_line))
    demos_right_x = np.hstack((demos_right_x, right_line))
    return demos_left_x, demos_right_x


def data3d():
    # Create demos for dual arms via bezier
    left_demo_points = np.array([[[0, 0, 0], [-1, 8, 1], [4, 3, 2], [2, 1, 2.5], [3.5, 3, 4]],
                                 [[0, -2, 0], [-1, 7, 2], [3, 2.5, 2.5], [2, 1.6, 3], [3.5, 3, 5]],
                                 [[0, -1, 0], [-1, 8, 2], [4, 5.2, 2.5], [2, 1.1, 2.5], [3.5, 3.5, 4]]])
    right_demo_points = np.array([[[8, 8, 10], [7, 1, 9], [4, 3, 7], [6, 8, 6.5], [3.5, 3, 4]],
                                  [[8, 7, 10], [7, 1, 9], [3, 3, 7.5], [6, 6, 6.5], [3.5, 3, 5]],
                                  [[8, 8, 9], [7, 1, 8], [4, 5, 7.5], [6, 8, 6], [3.5, 3.5, 4]]])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', fc='white')
    demos_left_x = multi_bezier_demos(left_demo_points, ax)  # (3, 50, 2): 3 demos, each has 50 points
    demos_right_x = multi_bezier_demos(right_demo_points, ax)

    # left_line = multi_bezier_demos(np.array([[[3.5, 3], [3.5, 4], [3.5, 5]],
    #                                          [[3.5, 3], [3.5, 4], [3.5, 5]],
    #                                          [[3.5, 3.5], [3.5, 4.5], [3.5, 5.5]]]))
    # right_line = multi_bezier_demos(np.array([[[4.5, 3], [4.5, 4], [4.5, 5]],
    #                                           [[4.5, 3], [4.5, 4], [4.5, 5]],
    #                                           [[4.5, 3.5], [4.5, 4.5], [4.5, 5.5]]]))

    # plt.plot([4, 4], [3.5, 3], 'kx', label='meeting points')
    # plt.plot(left_demo_points[:, 0, 0], left_demo_points[:, 0, 1], 'go', label='left starting points')
    # plt.plot(right_demo_points[:, 0, 0], right_demo_points[:, 0, 1], 'bo', label='right starting points')
    plt.legend()
    rf.visualab.set_axis(ax, azim=135)
    rf.visualab.save_img(fig, save_params['save_dir'])
    plt.show()

    # demos_left_x = np.hstack((demos_left_x, left_line))
    # demos_right_x = np.hstack((demos_right_x, right_line))
    return demos_left_x, demos_right_x


def bi_temporal_data():
    # Create demos for dual arms via bezier
    theta_right = np.array([[-1 * np.pi / 4, 1 * np.pi / 5],
                            [-2 * np.pi / 4, 1 * np.pi / 6],
                            [-1 * np.pi / 4, 2 * np.pi / 7],
                            [-1 * np.pi / 4, 1 * np.pi / 7]])
    theta_left = np.pi + theta_right
    # theta_right[:, 1] = theta_right[:, 1] + 1 * np.pi / 3

    plt.figure()
    demos_left_x = np.vstack((draw_arc([-1, 0], 1, theta_left[0, 0], theta_left[0, 1], 'orange'),
                              draw_arc([2, -3], 2, theta_left[1, 0], theta_left[1, 1], 'purple'),
                              draw_arc([1, -2], 3, theta_left[2, 0], theta_left[2, 1], 'grey'),
                              draw_arc([1, -2], 2.5, theta_left[3, 0], theta_left[3, 1],
                                       'blue')))  # (3, 100, 2): 3 demos, each has 100 points
    demos_right_x = np.vstack((draw_arc([-1, 0], 2, theta_right[0, 0], theta_right[0, 1], 'orange'),
                               draw_arc([2, -3], 3, theta_right[1, 0], theta_right[1, 1], 'purple'),
                               draw_arc([1, -2], 4, theta_right[2, 0], theta_right[2, 1], 'grey'),
                               draw_arc([1, -2], 1, theta_right[3, 0], theta_right[3, 1], 'blue')))
    # plt.plot([4, 4], [3.5, 3], 'kx', label='meeting points')
    # plt.plot(left_demo_points[:, 0, 0], left_demo_points[:, 0, 1], 'go', label='left starting points')
    # plt.plot(right_demo_points[:, -1, 0], right_demo_points[:, -1, 1], 'bo', label='right starting points')
    plt.plot(demos_left_x[:, 0, 0], demos_left_x[:, 0, 1], 'go', label='left starting points')
    plt.plot(demos_left_x[:, -1, 0], demos_left_x[:, -1, 1], 'gx', label='left ending points')
    plt.plot(demos_right_x[:, 0, 0], demos_right_x[:, 0, 1], 'bo', label='right starting points')
    plt.plot(demos_right_x[:, -1, 0], demos_right_x[:, -1, 1], 'bx', label='right ending points')
    plt.axis('equal')
    plt.legend()
    plt.show()
    return demos_left_x, demos_right_x


def learn(demos_left_x, demos_right_x):
    representation = rf.tpgmm.TPGMM_RPAll(demos_left_x, demos_right_x, nb_states=4, plot=False, save=True,
                                          save_params=save_params)

    nb_dim = len(demos_left_x[0][0])

    start_xdx_l = representation.repr_l.demos_xdx[demo_idx][0]
    end_xdx_l = np.array(
        [5, 5, 5, representation.repr_l.demos_xdx[demo_idx][-1][2], representation.repr_l.demos_xdx[demo_idx][-1][3],representation.repr_l.demos_xdx[demo_idx][-1][4]
         ])
    # end_xdx_l = representation.repr_l.demos_xdx[demo_idx][-1]
    start_xdx_r = representation.repr_r.demos_xdx[demo_idx][0]
    end_xdx_r = np.array(
        [5, 5, 5, representation.repr_r.demos_xdx[demo_idx][-1][2], representation.repr_r.demos_xdx[demo_idx][-1][3],representation.repr_r.demos_xdx[demo_idx][-1][4]
         ])
    # end_xdx_r = representation.repr_r.demos_xdx[demo_idx][-1]

    task_params = {'left': {'start_xdx': start_xdx_l, 'end_xdx': end_xdx_l},
                   'right': {'start_xdx': start_xdx_r, 'end_xdx': end_xdx_r,
                             'traj': representation.repr_r.demos_x[demo_idx]}}
    if isinstance(representation, rf.tpgmm.TPGMM_RPCtrl) or isinstance(representation, rf.tpgmm.TPGMM_RPAll):
        model_l, model_r, model_c = representation.fit()
        representation.reproduce(model_l, model_r, model_c, show_demo_idx=demo_idx)
        traj_l, traj_r, _, _ = representation.generate(model_l, model_r, model_c, ref_demo_idx=demo_idx,
                                                       task_params=task_params)
    else:
        model_l, model_r = representation.fit()
        representation.reproduce(model_l, model_r, show_demo_idx=demo_idx)
        leader = None
        traj_leader, traj_follower, _, _ = representation.generate(model_l, model_r, ref_demo_idx=demo_idx,
                                                                   task_params=task_params, leader=leader)

        traj_l, traj_r = (traj_leader, traj_follower) if leader in ['left', None] else (traj_follower, traj_leader)

    data_lst = [traj_l[:, :nb_dim], traj_r[:, :nb_dim]]
    fig = rf.visualab.traj_plot(data_lst, title='Generated Trajectories', ori=True)
    rf.visualab.save_img(fig, save_params['save_dir'])
    # plt.show()


def pour():
    import os
    import pandas as pd
    import copy
    # path = '/home/ubuntu/Downloads/OneDrive_2023-03-31/Donas Code'
    #
    # data_lst = []
    # for i in os.listdir(path):
    #     # if i.endswith('.csv') and i in ['demo_exp_12.csv', 'demo_exp_15.csv', 'demo_exp_16.csv']:
    #     if i.endswith('.csv') and i in ['demo_exp_7.csv', 'demo_exp_2.csv', 'demo_exp_3.csv']:
    #         data_lst.append(np.array(pd.read_csv(os.path.join(path, i), skiprows=1)))

    # demos_left_x = [data[::5, 3:10] / 100. for data in data_lst]
    # demos_right_x = [data[::5, 10:17] / 100. for data in data_lst]

    # demos_left_x = [data[: 200] for data in demos_left_x]
    # demos_right_x = [data[: 200] for data in demos_right_x]

    path = '/home/ubuntu/Downloads/LQT'

    data_lst = []
    for i in os.listdir(path):
        if i.endswith('.csv') and i in ['lqt1.csv']:
            data_lst.append(np.array(pd.read_csv(os.path.join(path, i), skiprows=1)))

    demos_left_x = [data[:, :7] for data in data_lst]
    demos_right_x = [data[:, 14:21] for data in data_lst]

    # for i in range(len(demos_left_x)):
    #     tmp = copy.copy(demos_left_x[i][:, 1])
    #     demos_left_x[i][:, 1] = demos_left_x[i][:, 2]
    #     demos_left_x[i][:, 2] = tmp
    #
    #     tmp = copy.copy(demos_right_x[i][:, 1])
    #     demos_right_x[i][:, 1] = demos_right_x[i][:, 2]
    #     demos_right_x[i][:, 2] = tmp

    for i in range(len(demos_left_x)):
        tmp = copy.copy(demos_left_x[i][:, 4])
        demos_left_x[i][:, 4] = demos_left_x[i][:, 5]
        demos_left_x[i][:, 5] = tmp

        tmp = copy.copy(demos_right_x[i][:, 4])
        demos_right_x[i][:, 4] = demos_right_x[i][:, 5]
        demos_right_x[i][:, 5] = tmp

    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_subplot(111, projection='3d', fc='white')
    rf.visualab.traj_plot(demos_left_x, legend='left', g_ax=ax, ori=False)
    rf.visualab.traj_plot(demos_right_x, legend='right', g_ax=ax, ori=False)
    # rf.visualab.traj_plot([demos_left_cup[0]], legend='left_cup', g_ax=ax)
    # rf.visualab.traj_plot([demos_right_cup[0]], legend='right_cup', g_ax=ax)

    rf.visualab.save_img(fig, save_params['save_dir'])
    plt.show()
    return demos_left_x, demos_right_x


if __name__ == '__main__':
    # demos_left_x, demos_right_x = data3d()
    # learn(demos_left_x, demos_right_x)
    demos_left_x, demos_right_x = pour()
    learn(demos_left_x, demos_right_x)
