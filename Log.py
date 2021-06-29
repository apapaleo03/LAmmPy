
import glob
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
from types import SimpleNamespace
import pandas as pd


class Log:

    def __init__(self,file,specified_run = 'all'):
        self.data = [] # Contains an array of runs, each of which hold a 2-D array of thermo data
        self.run_indices = []
        self.start_indices = []
        self.end_indices = []
        self.txt = self.__importFile(file)


        
        # Get the number of runs and populate the data and values
        self.__get_all_indices()
        self.__populateData(specified_run)
        
        
        
    def __populateData(self,run):

        if isinstance(run,int):
            if run > 0 and run < self.num_runs:
                self.data.append(self.__find_data(self.run_indices[run]),
                                                self.__find_data[run+1])
        elif isinstance(run, str):
            if run == 'all':
                for i in range(len(self.run_indices)):
                    if i + 1 < len(self.run_indices):
                        self.data.append(self.__find_data(self.run_indices[i],self.run_indices[i+1]))
                    else:
                        self.data.append(self.__find_data(self.run_indices[i]))
            elif run == 'first':
                if len(self.run_indices) == 1:
                    self.data.append(self.__find_data(self.run_indices[0]))
                else:
                    self.data.append(self.__find_data(self.run_indices[0],self.run_indices[1]))
            elif run == 'last':
                self.data.append(self.__find_data(self.run_indices[-1]))
            else:
                print('Invalid run selection.')
        print(f"Log file has {len(self.run_indices)} runs")

    def __importFile(self,file):
        # self.txt holds the contents of the log file
        try:
            with open(file,'r') as f:
                return [line.split() for line in f.readlines() if line != '\n']
        except:
            print(f"No file called {file}.")
            quit()
            


    def __get_all_indices(self):
        index = 0
        for line in self.txt:
            if line[0] == "Step":
                self.start_indices.append(index)
            elif line[0] == "Loop":
                self.end_indices.append(index)
            elif line[0] == "run":
                self.run_indices.append(index)
            index += 1
        if len(self.end_indices) == 0:
            self.end_indices.append(index)
        assert len(self.run_indices) != 0 , "No keywords (Step, Loop, run) in file"
        
        

    def __find_data(self,current_run, next_run=0):
        if not next_run:
            current_start = [x for x in self.start_indices if (x > current_run)]
            current_end = [x for x in self.end_indices if (x > current_run)]
        else:
            current_start = [x for x in self.start_indices if (x > current_run) and (x < next_run)]
            current_end = [x for x in self.end_indices if (x > current_run) and (x < next_run)]
        header = self.txt[current_start[0]]
        data = []
        for start,end in zip(current_start,current_end):
            data.append(self.txt[start+1:end])
            
        if len(data) == 1:
            data = np.array(data[0])
        else:
            stacked = []
            for chunk in data:
                if len(stacked) == 0:
                    stacked = np.asarray(chunk)
                else:
                    stacked = np.vstack((stacked,np.asarray(chunk)))

            data = stacked
            
        assert len(set([len(line) for line in data])) == 1, "Thermo data incomplete, check lines for equal number of values"
        
        data = data.astype(float)
        
        return pd.DataFrame(data,columns=header)





################################################################
################################################################
################################################################

class Logs:

    def __init__(self,files,specified_run = 'all'):
        # Separate filename and directory
        self.filename = files.split('/')[-1]
        self.dir = '/'.join(files.split('/')[:-1])

        self.log_list = {}
        self.start_wldcd = files.index('*')
        self.char_after_wldcd = files[self.start_wldcd+1]
        self.file_list = glob.glob(files)
        for file in self.file_list:
            end_wldcd = file.find(self.char_after_wldcd,self.start_wldcd)
            diff = file[self.start_wldcd:end_wldcd]
            self.log_list[diff] = Log(file,specified_run)


    def keys(self):
        return self.log_list.keys()

    def get_dict(self):
        return self.log_list

    def get(self,*args):
        if len(args) == 0:
            raise TypeError("get expected 1 or more arguments, got 0")
        values = {}
        for key in self.log_list:
            values[key] = self.log_list[key].get(*args)

        return values

    def get_aves(self,*args):
        vals = self.get(*args)

        ave_vals = {}
        for key in vals:
            if len(args) > 1:
                ave_vals[key] = [np.average(data) for data in vals[key]]
            else:
                ave_vals[key] = np.average(vals[key])

        return ave_vals


if __name__ == '__main__' :
    d = Log('../../../../../../Users/apapaleo/Research/Simulations/Fe/SpringConstant/data/lammps_rampedTemp.log')
    print(type(d.data[0]))
    




