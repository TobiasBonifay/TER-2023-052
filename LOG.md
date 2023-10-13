# Abstract

## What was done by the last researches
Today, most data centers operate using virtual machines (VMs) that offer services tailored to client needs.
Virtualization provides data center managers with a means to optimize a server's physical resources. 
In this project, we focus on sharing memory between multiple VMs on a server. 
Typically, a memory region is allocated to a single VM upon its creation. 
This means that a VM's memory usage remains static throughout its lifecycle, 
making optimization techniques challenging to devise. 
However, existing techniques can reclaim memory used by VMs. 
One of these, studied in previous works, involves using kernel applications to force processes on which VMs run to release memory. 
Under Linux, these kernel applications are called 'cgroup'. 
However, these operations adversely impact the VM's performance. 
The project's objective is to offer a solution to free up memory space when a VM isn't operating at full capacity without significantly compromising its performance. 
Deciding how much memory to reclaim and when can be modeled using a machine learning algorithm. 
This model can predict the degradation of service in a VM when reducing allocated memory. 
This prediction aids in deciding whether to decrease the allocated memory amount.

## What is the goal of this research
The goal of this research is to optimize memory usage in VMs without compromising their performance. 
To achieve this, we will use the network bandwidth as a metric to measure VM performance instead of server web requests latency.
The network bandwidth may be a better metric to measure VM performance because it is more stable than the latency of web requests.
However, the network bandwidth may not be "exactly" correlated with the latency of web requests.

Building on this foundation, I will further investigate memory optimization techniques and enhance the machine learning algorithm's efficiency. 
By continuously analyzing VM performance data, the algorithm can be refined to make more accurate predictions. 
Additionally, exploring other kernel tools or newer virtualization techniques might present alternative solutions for memory optimization without compromising VM performance. 
The ultimate goal is to achieve a balance between optimal resource utilization and maintaining high VM performance.

## WEEK 1
Reading and understanding the previous work. 
Creating a new repository to store the new research.
Writing the first version of the README.md file.
Discovered the difference between swapping and ballooning.

## TO DO
Creating two VMs on a host machine that are connected by a virtual bridge network.
I will use the KVM hypervisor to create the VMs to stay consistent with the previous work.
The cgroup tool was used to restrict the memory of the VMs in the previous work, I will use it too.

## QUESTIONS TO ASKS
Should I use the iperf3 tool to measure the network bandwidth between the two VMs? is it the best option?

I guess I will use python script to automate the process of generating load on the VMs, measuring the network bandwidth, and measuring the performance of the VMs.
As discussed the (mm/dd/yyyy) 10/12/2023, the script will be executed on the second VM to generate load on the first VM. 