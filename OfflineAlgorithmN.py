# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 15:27:06 2022

@author: user
"""

cache_cost = 1;


##Find the candidate request r_k s.t. the storage period [r_{p(k)},r_k] crosses r_{p(i)}
def FindHighestCross(start, end, requests, previous, transfer_cost):
    highestCross = start;           ##highestCross is the highest index of request r_h between r_{p(i)} and r_{i} s.t. t_{h}-t_{p(h)} < transfer_cost
    candidate = [];
    first_request = [];             ##this list is used to store the indexes of candidate requests
    
    
    ##use this for-loop to find the set of candidate requests
    for i in range(start+1, end):
        if previous[i] < start and previous[i]>-1:
            candidate.append(i);
            if requests[i]-requests[previous[i]] <= transfer_cost and i > highestCross:
                highestCross = i; 
    
    ##rule out some of the candidate requests if they are before the request with index highestCross 
    #for request in first_request:
        #if request < highestCross:
        #    first_request.remove(request);
    first_request = [x for x in candidate if x>=highestCross];
            
    return first_request;


##calcuate the marginal cost of request from index start to index end
def MarginalBound(start, end, requests, previous, transfer_cost):
    cost = 0;
    cache = 0;
    for i in range(start, end+1):
        if previous[i] > -1:
            cache = requests[i]-requests[previous[i]];
        else:
            cache = float('inf');
            
        cost += min(transfer_cost, cache);
    
    return cost;




def offline(requests, local_server, transfer_cost):
    #requests = [0,1,4,5,8];          ##The request sequence should contain dummy request.
    #local_server =  [0,1,1,2,0];      ##the local servers of requests (indexed from 0)
    servers = max(local_server);     ##number of servers-1

    optimal = [0]*len(requests);   ##The optimal offline cost up to each request
    D = [0]*len(requests);         ##Type-D optimal offline cost
    F = [0]*len(requests);         ##Type-F optimal offline cost
    pivot = 0;



    previous = [0]*(len(requests));    ##the index of previous local request in the same server
    current_local = [0]+[-1]*(servers)    ##use this list to record the current local requests that are processing in the for loop
    ##calculate the index of previous local request (previous), 
    ##and the arrival time of the next local request(nextIAT)
    for i in range(len(requests)):
        if current_local[local_server[i]] == -1:
            previous[i] = -1;     ##the first request in the local server, with no previous local request
        else:
            previous[i] = current_local[local_server[i]];  ##otherwise record the previous local request
        
        current_local[local_server[i]] = i;      ##update the request we are processing


    ##calculate the optimal cost of each request r_i    
    for i in range(1,len(requests)):
        ##calculate the optimal cost when r_i is served by transfer    
        if local_server[i]==local_server[i-1]:    ##if r_{i-1} and r_i is in the same server, Type-F cannot be the optimal cost 
            F[i] = float('inf');
        else:                                 
            F[i] = optimal[i-1] + (requests[i] - requests[i-1]) + transfer_cost;
        
        
        ##calculate the optimal cost when r_i is served by local cache
        ##case 1: For r_i, there is a previous local request in the same server. 
        if previous[i] > -1:
            pivots = FindHighestCross(previous[i], i, requests, previous, transfer_cost);
            mincost = optimal[previous[i]] + (requests[i]-requests[previous[i]]) + MarginalBound(previous[i]+1, i-1, requests, previous, transfer_cost);    
            candidate = mincost;
            for pivot in pivots:   ##use this for-loop to find the optimal cost when r_i is served by local cache
                candidate = D[pivot] + (requests[i]-requests[previous[i]]) + MarginalBound(pivot+1, i-1, requests, previous, transfer_cost);
            
                if candidate < mincost:    ##find the minimal value of Type-D
                    mincost = candidate;
            
            D[i] = mincost;
        
        ##case 2: For r_i, there is no previous local request in the same server-----r_i should be served by transfer! 
        else:
            D[i] = float('inf');
        
        ##Take the minimum value of D[i] and F[i] to find the optimal cost of serving requests up to r_i
        optimal[i] = min(D[i],F[i]);
        
    return(optimal[len(requests)-1]);
