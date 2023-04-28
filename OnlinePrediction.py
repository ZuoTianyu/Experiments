# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 16:45:12 2022

@author: user
"""
import random


def online(requests, local_server, hyper_para, prediction_accuracy, transfer_cost):
    total_cost = 0;         ##We use it to record the total online cost
    cache_cost = 1;
    
    cache_time = [transfer_cost/hyper_para, hyper_para*transfer_cost];   ##two possible storage periods in the online algorithm with prediction
    servers = max(local_server);     ##number of servers-1
    
    nextIAT = [0]*(len(requests));     ##the arrival time of the next local request
    previous = [0]*(len(requests));    ##the index of previous request in the same server
    expiration_time = [transfer_cost]+[float('-inf')]*(len(requests)-1);  ##the expiration of regular copy in the online algorithm

    prediction = [-1]*(len(requests));   ##the binary prediction of whether the next arrival time is larger than transfer cost
                                     ##0---smaller than transfer cost, 1---larger than transfer cost
    
    current_local = [0]+[-1]*(servers)    ##use this list to record the current local requests that are processing in the for loop
    ##calculate the index of previous local request (previous), 
    ##and the arrival time of the next local request(nextIAT)
    for i in range(len(requests)):
        if current_local[local_server[i]] == -1:
            previous[i] = -1;     ##the first request in the local server, with no previous local request
        else:
            previous[i] = current_local[local_server[i]];  ##otherwise record the previous local request
            nextIAT[current_local[local_server[i]]] = requests[i] - requests[current_local[local_server[i]]];
        current_local[local_server[i]] = i;      ##update the request we are processing

    ##set the next arrival time of the last local request to be infinity 
    for index in current_local:
        nextIAT[index] = float('inf');
    

    ##simulate the prediction of the arrival time of next local requests, with prediction_accuracy \leq 1.
    for i in range(len(requests)):
        randnum = random.uniform(0,1);
        if randnum <= prediction_accuracy:    ##prediction is correct
            prediction[i] = int(nextIAT[i]>transfer_cost);
        else:                                 ##prediction is incorrect
            prediction[i] = 1-int(nextIAT[i]>transfer_cost);


    i = 0;
    special_cost = 0;    ##cost of sepcial copy
    preceded_regular = 0;
    while i<=len(requests)-1:
        if requests[i]<=expiration_time[local_server[i]]: ##The Type-3 request should be served by cache.
            total_cost += requests[i]-requests[previous[i]];    #last_local[local_server[i]];
        
        else:   ##The request should be served by transfer.
            if previous[i] == -1:
                preceded_regular = 0;
            else:
                preceded_regular = expiration_time[local_server[i]]-requests[previous[i]];
        
            if requests[i]>max(expiration_time):   ##transfer is from special copy
                special_cost = requests[i] - max(expiration_time);  ##calculate cost of special copy
                ##The request is a Type-4 request.
                if local_server[i] == expiration_time.index(max(expiration_time)):
                    total_cost += (preceded_regular + special_cost);

                ##The request is a Type-2 request.
                else:
                    #expiration_time[expiration_time.index(max(expiration_time))] = requests[i];
                    total_cost += (transfer_cost + preceded_regular + special_cost);
                
            
            else:                  ##transfer is from regular copy (Type-1 request)
                total_cost += (transfer_cost + preceded_regular);  ##first request problem, previous==-1
            
            
        #last_local[local_server[i]] = requests[i];     ##record the last local request
        expiration_time[local_server[i]] = requests[i] + cache_time[prediction[i]]; ##update expiration time
    
        ##add up the cost of the last regular copy if the current request is the last local request
        if nextIAT[i] == float('inf') and i != len(requests)-1:
            total_cost += cache_time[prediction[i]];
    
        i += 1;
    
    return total_cost;
    
#print(total_cost);