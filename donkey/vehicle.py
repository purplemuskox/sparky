#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 10:44:24 2017

@author: wroscoe
"""

import time
from threading import Thread


class Vehicle():
    def __init__(self, mem):
        
        self.mem = mem
        self.parts = [] 
        self.on = True
        self.threads = []
        
        
    def add(self, part, inputs=[], outputs=[], threaded=False):
        """ 
        Method to add a part to the vehicle drive loop.
        
        Parameters
        ----------
            inputs : list 
                Channel names to get from memory.
            ouputs : list
                Channel names to save to memory.
            threaded : boolean 
                If a part should be run in a separate thread.
        """
        
        p = part
        print('Adding part {}.'.format(p.__class__.__name__))
        entry={}
        entry['part'] = p
        entry['inputs'] = inputs
        entry['outputs'] = outputs
        
        if threaded:
            t = Thread(target=part.update, args=())
            t.daemon = True
            entry['thread'] = t
            
        self.parts.append(entry)
    
    
    def start(self, rate_hz=10, max_loop_count=None):
        """ 
        Start vehicle's main drive loop.  
        
        This is the main thread of the vehicle. It starts all the new
        threads for the threaded parts then starts an infinit loop
        that runs each part and updates the memory.
        
        Parameters
        ----------
        
        rate_hz : int
            The max frequency that the drive loop should run. The actual 
            frequency may be less than this if there are many blocking parts.
        max_loop_count : int
            Maxiumum number of loops the drive loop should execute. This is 
            used for testing the all the parts of the vehicle work.
        """
        
        
        for entry in self.parts:
            if entry.get('thread'):
                #start the update thread
                entry.get('thread').start()
        
        #wait until the parts warm up.
        print('Starting vehicle...')
        time.sleep(1)
        
        loop_count = 0
        while self.on:
            loop_count += 1
            
            for entry in self.parts:
                p = entry['part']
                #get inputs from memory
                inputs = self.mem.get(entry['inputs'])
                
                #run the part
                if entry.get('thread'):
                    outputs = p.run_threaded(*inputs)
                else:
                    outputs = p.run(*inputs)
                
                #save the output to memory
                self.mem.put(entry['outputs'], outputs)

            #TODO: This should only add the needed time to match the frequency                 
            time.sleep(1/rate_hz)
                
            #stop drive loop if loop_count exceeds max_loopcount
            if max_loop_count and loop_count > max_loop_count:
                self.on = False