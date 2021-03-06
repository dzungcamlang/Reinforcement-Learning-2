import numpy as np

from Algorithms import Algorithms


class TDLearning(Algorithms):

    def __init__(self, landa, N0, gamma, score_upper_bound):
        super().__init__(N0=N0, gamma=gamma, score_upper_bound=score_upper_bound)
        self.landa = landa

    def sarsa_initialize(self):
        self.state_action_value_estimation = np.zeros((self.score_upper_bound, 10, 2))
        self.state_action_visit_count = np.zeros(self.state_action_value_shape)
        self.state_visit_count = np.zeros(self.state_value_shape)

    #     TODO zero terminal state

    def sarsa_lambda_initialize(self):
        self.state_action_value_estimation = np.zeros((self.score_upper_bound, 10, 2))
        self.state_action_visit_count = np.zeros(self.state_action_value_shape)
        self.state_visit_count = np.zeros(self.state_value_shape)
    #     TODO zero terminal state

    def sarsa(self, episodes):
        self.sarsa_initialize()

        for i in range(episodes):
            current_state = self.Environment.first_step()
            epsilon = self.epsilon_t(count=self.state_visit_count[self.coord(current_state)])
            current_action = self.epsilon_greedy(state=current_state, epsilon=epsilon)
            current_state_action = self.to_state_action(state=current_state, action=current_action)

            self.state_action_visit_count[self.coord_3d(current_state_action)] += 1
            self.state_visit_count[self.coord(current_state)] += 1

            new_state, reward, is_terminal = self.Environment.step(do_hit=current_action,
                                                                   scores=current_state)

            while is_terminal == 0:

                epsilon = self.epsilon_t(count=self.state_visit_count[self.coord(new_state)])
                new_action = self.epsilon_greedy(state=new_state, epsilon=epsilon)

                alpha = self.alpha_t(current_state_action=current_state_action)

                self.state_action_value_estimation[self.coord_3d_2(current_state, current_action)] += alpha * (reward +
                    self.gamma * self.state_action_value_estimation[self.coord_3d_2(new_state, new_action)] * (1 -
                        is_terminal) - self.state_action_value_estimation[self.coord_3d_2(current_state, current_action)])

                current_state = new_state
                current_action = new_action
                current_state_action = self.to_state_action(action=current_action, state=current_state)

                self.state_action_visit_count[self.coord_3d(current_state_action)] += 1
                self.state_visit_count[self.coord(current_state)] += 1

                new_state, reward, is_terminal = self.Environment.step(do_hit=current_action,
                                                                       scores=current_state)

            # For the terminal state
            alpha = self.alpha_t(current_state_action=current_state_action)

            self.state_action_value_estimation[self.coord_3d_2(current_state, current_action)] += alpha * (reward
                        - self.state_action_value_estimation[self.coord_3d_2(current_state, current_action)])

    def sarsa_lambda(self, episodes, landa):
        for i in range(episodes):

            self.eligibility_trace = np.zeros(self.state_action_value_shape)

            current_state = self.Environment.first_step()
            epsilon = self.epsilon_t(count=self.state_visit_count[self.coord(current_state)])
            current_action = self.epsilon_greedy(state=current_state, epsilon=epsilon)
            current_state_action = self.to_state_action(action=current_action, state=current_state)

            self.state_action_visit_count[self.coord_3d(current_state_action)] += 1
            self.state_visit_count[self.coord(current_state)] += 1

            new_state, reward, is_terminal = self.Environment.step(do_hit=current_action,
                                                                   scores=current_state)

            while is_terminal == 0:
                epsilon = self.epsilon_t(count=self.state_visit_count[self.coord(new_state)])
                new_action = self.epsilon_greedy(state=new_state, epsilon=epsilon)
                new_state_action = self.to_state_action(state=new_state, action=new_action)

                delta = reward + self.gamma * self.state_action_value_estimation[self.coord_3d(new_state_action)]\
                        - self.state_action_value_estimation[self.coord_3d(current_state_action)]
                self.eligibility_trace[self.coord_3d(current_state_action)] += 1

                alpha = self.alpha_t(current_state_action=current_state_action)
                self.state_action_value_estimation += delta * np.multiply(alpha, self.eligibility_trace)
                self.eligibility_trace = self.gamma * landa * self.eligibility_trace

                current_state = new_state.copy()
                current_action = new_action
                current_state_action = self.to_state_action(action=current_action, state=current_state)

                self.state_action_visit_count[self.coord_3d(current_state_action)] += 1
                self.state_visit_count[self.coord(current_state)] += 1
                new_state, reward, is_terminal = self.Environment.step(do_hit=current_action,
                                                                       scores=current_state)

            alpha = self.alpha_t(current_state_action=current_state_action)

            self.state_action_value_estimation[self.coord_3d(current_state_action)] += \
                alpha * (reward - self.state_action_value_estimation[self.coord_3d(current_state_action)])

    def learn_sarsa(self, episodes):
        self.sarsa(episodes=episodes)
        state_value_estimation = self.to_value_function(state_value_function=self.state_action_value_estimation)
        output = {'state_value': state_value_estimation,
                  'decision': self.state_action_value_estimation.argmax(axis=2),
                  'state_action_value': self.state_action_value_estimation
                  }
        return output

    def learn_sarsa_landa(self, episodes, landa):
        self.sarsa_lambda_initialize()
        self.sarsa_lambda(episodes=episodes, landa=landa)
        state_value_estimation = self.to_value_function(state_value_function=self.state_action_value_estimation)
        output = {'state_value': state_value_estimation,
                  'decision': self.state_action_value_estimation.argmax(axis=2),
                  'state_action_value': self.state_action_value_estimation
                  }
        return output

    def rmse_sarsa_landa(self, landa, measure_step, episodes, state_action_value_mc):
        self.sarsa_lambda_initialize()
        steps_number = episodes / measure_step
        rmse_array = []

        for i in range(int(steps_number)):
            rmse = self.rmse(self.state_action_value_estimation, state_action_value_mc)
            rmse_array.append(rmse)
            self.sarsa_lambda(episodes=measure_step, landa=landa)
        return rmse_array

    def rmse_sarsa(self, measure_step, episodes, state_action_value_mc):
        self.sarsa_initialize()
        steps_number = episodes / measure_step
        rmse_array = []

        for i in range(int(steps_number)):
            rmse = self.rmse(self.state_action_value_estimation, state_action_value_mc)
            rmse_array.append(rmse)
            self.sarsa(episodes=measure_step)

        return rmse_array