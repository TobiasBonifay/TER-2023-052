# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 13:39:15 2022

@author: alexis merienne
"""




import numpy as np
import matplotlib.pyplot as plt


FILE = "host/output_memuse_swapuse_memproc/out3.txt"


def readfile(file):
    arr = np.loadtxt(file)
    return arr[:,0],arr[:,1],arr[:,2],arr[:,3],arr



def analyse(data):
    sub1 = data[0:100]
    sub2 = data[200:300]
    
    mean1 = np.mean(sub1[:,1])
    mean2 = np.mean(sub2[:,1])
    
    
    return mean1,mean2
    
def get_delta(data):
    max_memory = data[0,1]
    min_memory = data[len(data[:,1])-1][1]
    
    return max_memory - min_memory
        
    

if __name__ == "__main__":
    
    
    
    time,mem,swap,procmem,data = readfile(FILE)
    meanp1_mem,meanp1_swap,meanp1_procmem = np.mean(np.array(mem[0:28])),np.mean(np.array(swap[0:28])),np.mean(np.array(procmem[0:28]))
    meanp2_mem,meanp2_swap,meanp2_procmem = np.mean(np.array(mem[32:2399])),np.mean(np.array(swap[32:2399])),np.mean(np.array(procmem[32:2399]))
    #time,mem,swap,procmem = time[290:330],mem[290:330],swap[290:330],procmem[290:330] 
    procmem = [p/1e3 for p in procmem]
    #a,b = get_a_b_fin(data)
    diff_memory = get_delta(data)
    mean_proc = np.mean(np.array(procmem))
    #mean1,mean2 = analyse(data)
    
    fig, ax_mem = plt.subplots()
    

    
    ax_swap = ax_mem.twinx()
    
    desc = "mean(mem_use) = " + format(np.mean(np.array(mem)),".2E") + " kB\nmean(swap_use)=" + format(np.mean(np.array(swap)),".2E") + " kB"
    
    desc_t_inf = "mean(mem_use,t<30) =  " + format(meanp1_mem,'.2E') + " kB\nmean(swap_use,t<30) = " + format(meanp1_swap,".2E") + " kB"
    
    desc_t_sup = "mean(mem_use,t>65) =  " + format(meanp2_mem,'.2E') + " kB\nmean(swap_use,t>65) = " + format(meanp2_swap,".2E") + " kB"
    
    desc_diff = "mean(mem_use,t<30) - mean(mem_use,t>65) = " + format(meanp1_mem-meanp2_mem,'.2E') + "kB\nmean(mem_use,t<30) - mean(mem_use,t>30) = " + format(meanp1_swap-meanp2_swap,'.2E') + "kB"
    
    '''
   
    fig.text(0.4, 0.5, 
         desc_t_inf,
         fontsize = 10,
         color = "black")

     
    fig.text(0.4, 0.4, 
         desc_t_sup,
         fontsize = 10,
         color = "black")
    
    fig.text(0, -0.1, 
         desc_diff,
         fontsize = 10,
         color = "black")
    '''
    
    ax_mem.plot(time,mem)   
    ax_mem.set_ylabel("RAM memory consumption (kB)",color="blue")
    
    ax_swap.plot(time,swap, color='orange',label="swap use")
    ax_swap.set_ylabel("swap memory consumption (kB)",color="orange")
    
    
    ax_mem.set_xlabel("Time (s)")
    ax_mem.set_title("RAM and swap memory consumption")
    
    plt.show()
    
    
   
    plt.plot(time,procmem)
    plt.title("memory the VM use throught time ")
    plt.xlabel("time (s)")
    plt.ylabel("memory use by the VM process (Mb)")
    plt.xlim(time[0], time[len(time)-1])
    plt.ylim(0, mean_proc+(mean_proc*0.7))
    #plt.text(-10,mean_proc-(mean_proc*0.5),"mean(mem_proc_use,t<30) = "+format(meanp1_procmem,".2E")+" Mb\nmean(mem_proc_use,t>65) = "+format(meanp2_procmem,".2E")+" Mb",bbox=dict(facecolor='white', alpha=0.5))
    #plt.text(-10,mean_proc-(mean_proc*0.6),"mean(mem_proc_use,t<30) - mean(mem_proc_use,t>65) = "+format(meanp1_procmem-meanp2_procmem,".2E")+" kB",bbox=dict(facecolor='white', alpha=0.5))
    #plt.text(int(a),mem[1]/5,"decrease time = "+format(-a,".1E")+" kB/s",bbox=dict(facecolor='green', alpha=0.5))
    plt.autoscale(False)
    plt.show()
   
    