# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 10:27:07 2022

@author: user
"""

from OfflineAlgorithmN import offline;
from OnlinePrediction import online;
from matplotlib import pyplot as plt;
import numpy as np;
import pandas as pd;
import random;


number_of_server = 10;
alpha = 1;
data = [];
with open("data/IBMObjectStore2.txt") as file:
    for item in file:
        item = item.strip('\n');
        a = item.split(sep=' ');
        if a[1] == 'REST.GET.OBJECT':      ##only pick the read requests from dataset
            data.append(a[0:3]);


prob_range = [];
temp = 0;
for i in range(1,number_of_server+1):
    temp+=1/i**alpha;
    prob_range.append(temp);
prob_range = [x/temp for x in prob_range];


local_server = [];
data = pd.DataFrame(data,columns=['Timestamp','RequestType','ObjectID']);   ##convert list into dataframe
frequency_list = data['ObjectID'].value_counts();                 ##frequency_list is a series
id_list=list(frequency_list.index);
for ID in id_list:
    #if frequency_list[ID]<12000 and frequency_list[ID]>10000:
    if ID=='652aaef228286e0a':      ##pick up the trace of object with id '652aaef228286e0a', and there are totally 11688 read requests over 7 days
        requests = data[data.ObjectID==ID];     ##request is a dataframe extracted from data, with objectID==ID
        requests = list(requests.Timestamp);
        requests = [(float(x)-float(requests[0]))/1000 for x in requests];    ##turns the time into unit 'second'----originally it is millisecond
    
        
        ##randomly distribute requests over 10 servers
        for i in range(len(requests)):
            randnum = random.uniform(0,1);
            for j in range(len(prob_range)):
                if randnum<prob_range[j]:
                    local_server.append(j);
                    break;
        local_server[0] = 0;
        
        #Discuss the cases when the transfer cost is 10, 100, 1000, or 10000.
        for transfer_cost in [10,100,1000,10000]:
            ## Try different combinations of hyperparameter and prediction accuracy
            hyperpara = np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]);
            accuracy = np.array([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]);
            A, H = np.meshgrid(hyperpara, accuracy);
            ratio = np.zeros((len(hyperpara),len(accuracy)));


            offline_cost = offline(requests,local_server, transfer_cost);
            consistency = True;
            robustness = True;
            for i in range(len(hyperpara)):                     #hyperpara---->Y axis (data in row is the same)
                for j in range(len(accuracy)):                  #accuracy---->X axis (data in column is the same)
                    ratio[i][j] = online(requests,local_server,hyperpara[i],accuracy[j],transfer_cost)/offline_cost;
        
                    if ratio[i][j] > 1+(1/hyperpara[i]):
                        robustness = False;
            
                    if accuracy[j] == 1:
                        if ratio[i][j] > (5+hyperpara[i])/3:
                            consistency = False;
        
        

            fig = plt.figure();
            ax = plt.axes(projection = '3d');
            ax.plot_surface(A,H,ratio,alpha=1,cmap='rainbow');
            ax.set_ylabel('hyperparameter');
            ax.set_xlabel('prediction accuracy');
            ax.set_zlabel('ratio');
            ax.set_title('Ratio of online and optimal offline cost for object '+ID);
            ax.view_init(25,30);
            plt.show();
            plt.savefig('./Figure/'+'TransferCost='+str(transfer_cost)+'.jpg')

            
            print('When the transfer cost is '+str(transfer_cost)+',');
            print('Always lower than consistency ratio when predictions are all correct? ',consistency);
            print('Always lower than robustness ratio? ',robustness);

