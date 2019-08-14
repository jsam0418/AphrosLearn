# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 17:17:40 2019

@author: josia
"""

from state import State
import random
import csv
import yaml
import matplotlib.pyplot as plt
from envs.simulation import gridSimulation as sim
from agents.randomAgent import randomAgent
from agents.OptimalPolicyAgent import optimalAgent
from agents.QLearnAgent import qLearnAgent


class framework:
    
    def __init__(self, fileName='params', debug = False):
        success = self.loadParams(fileName)
        self.debug = debug
        if success:
            self.train()
        else:
            return None
    
    def train(self):
        dungeon = sim(self.goalReward, self.stepReward, self.stepPunishment, self.xLength, self.yLength)
        # select agent
        if self.agent == 'RANDOM':
            agent = randomAgent(learningRate=self.learning_rate, discount=self.discount, xLength=self.xLength, yLength=self.yLength)
        elif self.agent == 'OPTIMALPOLICY':
            agent = optimalAgent(learningRate=self.learning_rate, discount=self.discount, xLength=self.xLength, yLength=self.yLength)
        elif self.agent == 'QLEARN':
            agent = qLearnAgent(self.learning_rate, self.discount, self.xLength, self.yLength, self.iterations, self.explorationRate)
        else:
            print("Invalid selection. Please try again.")
            return
    
        # setup simulation
        
        # main loop for episodes
        for z in range(self.trainingRuns):
            total_global_reward = 0
            
            x_session = []
            y_total_reward = []
            for i in range(self.iterations):
                # main loop for sessions in each episode
                dungeon.reset()
                
                total_reward = 0 # Score keeping
                
                for j in range(self.sessionLength):
                    old_state = dungeon.getState() # Store current state
                    action = agent.get_next_action(old_state) # Query agent for the next action
                    reward, new_state = dungeon.update(action, old_state) # Take action, get new state and reward
                    if reward == None or new_state == None:
                        print("There was an error with one of the actions chosen.")
                        return
                    agent.update(old_state, new_state, action, reward) # Let the agent update internals
                    if self.debug:
                        print(agent.qTable)
                        test = input()
                    total_reward += reward # Keep score
                    
                    if reward == self.goalReward:
                        print("\nWe made it to the goal on episode "+str(i)+" and session "+str(j))
                        break
                print("The total reward for episode "+str(i)+" session "+str(j)+" is "+str(total_reward)+'\n')
                total_global_reward += total_reward
                x_session.append(i)
                y_total_reward.append(total_global_reward)
            print("The training is over! The total global reward is "+str(total_global_reward))
            plt.plot(x_session, y_total_reward, Label = 'Training'+str(z+1))
            
        plt.xlabel('Session Number')
        plt.ylabel('Total Reward Earned')
        plt.ylim(bottom=-5000, top=2500000)
        plt.title('Total Reward Earned Over Time - '+str(self.agent.lower())+'\n'+str(self.xLength)+'x'+str(self.yLength))
        plt.legend()
        plt.savefig(str("results/"+self.agent.lower())+'AgentTrainingResults'+str(self.xLength)+'x'+str(self.yLength)+'.png', bbox_inches = 'tight')
        plt.show()
        
    def loadParams(self, fileName):
        try:
            print("Loading the values from "+fileName+".yaml...")
            with open(fileName+'.yaml', 'r') as params:
                file = yaml.safe_load_all(params)
                for data in file:
                    paramsMap = data['params']
                    self.agent = paramsMap['agent']
                    self.xLength = paramsMap['xLength']
                    self.yLength = paramsMap['yLength']
                    self.learning_rate = paramsMap['learning_rate']
                    self.discount = paramsMap['discount']
                    self.iterations = paramsMap['iterations']
                    self.sessionLength = paramsMap['sessionLength']
                    self.goalReward = paramsMap['goalReward']
                    self.stepReward = paramsMap['stepReward']
                    self.stepPunishment = paramsMap['stepPunishment']
                    self.trainingRuns = paramsMap['training_runs']
                    self.explorationRate = paramsMap['exploration_rate']
            params.close()
            return True
                    
        except Exception as ex:
            print(ex)
            print("There was an error loading the values.")
            return False
            
