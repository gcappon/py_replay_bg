import numpy as np

class ReplayBGData:

    def __init__(self, data, BW, rbg):

        #From the time retain only the hour since is the only thing actually needed during the simulation
        self.t = np.array(data.t.dt.hour.values).astype(int)

        #Save idxs 
        self.idx = np.arange(0, len(self.t))
        
        #Unpack glucose only if exists
        if 'glucose' in data:
            self.glucose = data.glucose.values.astype(float)

        #Unpack insulin
        self.bolus, self.basal = self.__insulin_setup(data, rbg)
        self.meal, self.meal_announcement, self.meal_type = self.__meal_setup(data, rbg)

        #TODO: manage the multimeal and exercise
        self.bolus_label = []
        self.cho_label = []
        self.exercise = []



    def __insulin_setup(self, data, rbg):

        basal = np.zeros([rbg.model.tsteps,])
        bolus = np.zeros([rbg.model.tsteps,])

        if rbg.environment.bolus_source == 'data':
        
            #Find the boluses
            b_idx = np.where(data.bolus)[0]

            #Set the bolus vector
            for i in range(np.size(b_idx)):
                bolus[int( b_idx[i] * rbg.model.yts / rbg.model.ts ) : int( (b_idx[i] + 1) * rbg.model.yts / rbg.model.ts )] = data['bolus'][b_idx[i]] * 1000 / rbg.model.model_parameters['BW'] #mU/(kg*min)

        if rbg.environment.basal_source == 'data':
        
            #Set the basal vector
            for time in range(0, np.size(np.arange(0,rbg.model.tsteps, rbg.model.yts))):
                basal[int( time * rbg.model.yts / rbg.model.ts ) : int( (time + 1) * rbg.model.yts / rbg.model.ts )] = data['basal'][time] * 1000 / rbg.model.model_parameters['BW'] #mU/(kg*min)
        
        if rbg.environment.basal_source == 'u2ss':
        
            basal[:] = rbg.model.model_parameters['u2ss']
    
        #Convert to lookup dictionaries
        keys = np.arange(0, rbg.model.tsteps)
        bolus = dict(zip(keys, bolus))
        basal = dict(zip(keys, basal))

        return bolus, basal
    
    def __meal_setup(self, data, rbg):

        if rbg.environment.scenario == 'single-meal':

            #Initialize the meal vector
            meal = np.zeros([rbg.model.tsteps,])
            
            #Initialize the mealAnnouncements vector
            meal_announcement = np.zeros([rbg.model.tsteps,])
            
            #Initialize the meal type vector
            meal_type = np.empty([rbg.model.tsteps,], dtype = str)

            if rbg.environment.cho_source == 'data':
                
                #Find the meals
                m_idx = np.where(data.cho)[0]

                #Set the meal vector
                for i in range(np.size(m_idx)):
                    meal[int( m_idx[i] * rbg.model.yts / rbg.model.ts ) : int( (m_idx[i] + 1) * rbg.model.yts / rbg.model.ts )] = data['cho'][m_idx[i]] * 1000 / rbg.model.model_parameters['BW'] #mg/(kg*min)
                    meal_announcement[ int( m_idx[i] * rbg.model.yts / rbg.model.ts )] = data['cho'][m_idx[i]] * rbg.model.yts / rbg.model.ts #mg/(kg*min)

                    #Set the first meal to the MAIN meal (the one that can be delayed by beta) using the label 'M', set the other meal inputs to others using the label 'O'
                    if i == 0:
                        meal_type[ int( m_idx[i] * rbg.model.yts / rbg.model.ts )] = 'M'
                    else:
                        meal_type[ int( m_idx[i] * rbg.model.yts / rbg.model.ts )] = 'O'

            #Convert to lookup dictionaries
            keys = np.arange(0, rbg.model.tsteps)
            meal = dict(zip(keys, meal))
            meal_announcement = dict(zip(keys, meal_announcement))
            meal_type = dict(zip(keys, meal_type))

        if rbg.environment.scenario == 'multi-meal':
            #TODO: implement multi-meal
            pass
        
        return meal, meal_announcement, meal_type