import sys
import os 
import socket
import time
import threading



#TCP SERVER VARIABLE
HOST = '192.168.122.49'
PORT = 8080

#EXPERIEMNT VARIABLE
DOM_NAME = "ubuntu20.04"
DURATION = 120.0
FINESSE = 1.0
BENCHMARK = True
COEFF_BYTES_TO_MB = 9.765625e-4
COEFF_KB_TO_BYTE = 1024



##############################################
#
# Overview : 
# 
##############################################

# This script is used to run data generation experiments 
#
#  - it generate data for 8 different reduction values (0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2)
# (a reduction value is the coefficient to multiply the VM's memory to get the cgroup limitation)
#
#  - for each of these 8 reduction values, it run 5 measurements
#



##############################################
#
# Script's architecture :
#
##############################################
#
#  - it run on 4 different threads :
#       - one to run the benchmark
#       - one to run the host
#       - one to run the client
#       - one to run the cgroup limitation
#
#  - it takes 2 arguments :
#       - the duration of the experiment
#       - the sampling frequency of the experiment
#




##############################################
#
# Host's thread :
#
##############################################

'''
 run the host's thread
 it run C executable that get memory's indicators
 it store the indicators in a file at /outputs/<reduction_value>/<measurement_nbr>/out.txt
'''
def run_exec_host(reduction_value,measurement,start_time):
    print_log("host is running")
    dir_output = 'outputs/0_'+str(reduction_value).split(".")[1] +"/"+ str(measurement)
    os.system("./memoryexe "+str(DURATION) + " " + str(FINESSE)+ "> "+dir_output+"/out.txt")
    

        
##############################################
#
# Client's thread :
#
##############################################

'''
write name of benchmark file to have them sort by time of creation
'''
def format_bench_name(name,t,n):
    if int(t/n)<1:
        return format_bench_name("0"+name,t,n/10)
    else :
        return name

    
'''
 it run apache benchmark to get the number of request per second
 start a benchmark every 45s
 it store the benchmarks result in a file at /benchmarks/<reduction_value>/<measurement_nbr>/<time>.csv
'''
def run_benchmark(start_time,reduction_value,measurement):
    print_log("benchmark is running")
    n = 30.0
    b= 0


    while(True):
        t = round(time.process_time() - start_time)
        #every 45s we start a new benchmark
        if t==n:
            t = round(t)
            print_log("benchmark : "+str(t))
            dir_bench = 'benchmarks/0_'+str(reduction_value).split(".")[1] +"/"+ str(measurement)
            #100000 request, 500 concurrents, ask apache http server that is running on the VM
            os.system("ab -n 100000 -c 500 -e "+dir_bench+"/"+format_bench_name(str(t),t,10000)+".csv http://192.168.122.49:80/")
            n +=45
            b +=1
        #if time is over, we stop the benchmark
        if t>=(DURATION):
            print_log("END BENCHMARK AT t="+str(t))
            break

##############################################
#
# cgroup limitation's thread :
#
##############################################

'''
get the VM's memory.
When we run the C exec file, mem_proc is store in constants/MemProc
This method read this file and return the value
'''
def get_mem_process_use():
    f = open("constants/MemProc","r")
    mem_process_use = f.read()
    
    return float(mem_process_use)


'''
 open the cgroup file and write the new limitation
'''
def change_limit_cgroup_file(cgroup_limit):
    with open(r"/sys/fs/cgroup/machine.slice/machine-qemu\x2d3\x2dubuntu20.04.scope/libvirt/memory.max","w") as fmax:
        fmax.write(cgroup_limit)

'''
 function called by the thread to run the cgroup limitation
 While loop last DURATION seconds
 at 1/3 of DURATION, we set the cgroup limitation at mem_proc
 at 2/3 of DURATION, we set the cgroup limitation at reduction_value*mem_proc
'''
def change_cgroup_memory_limit(start_time,reduction_value):
    

    print_log("cgroup limit is running")


    period = round((DURATION)/3.0,2)

    # start the limutation at 1/3 of the total duration of the experiements
    start_limit = period
    # end at 2/3
    end_limit = round(DURATION,2)

    n = start_limit
    change_limit_cgroup_file("2147483648")

   


    first_limit = True
   
    
    while(True):

        # calcule time 
        t = round(time.process_time() - start_time,2)

        # if t is 2/3 of total time, we end the limitation
        if t==end_limit:
            #set to 2Gb
            change_limit_cgroup_file("2147483648")
            print_log("STOP BENCHMARK")
            break

        # every DURATION we look at the VM's memory and set the limitation at this value. 
        if t==n:
            if first_limit:
                new_cgroup_limit = get_mem_process_use()
                limit_cgroup=str(int(new_cgroup_limit))
                change_limit_cgroup_file(limit_cgroup)
                first_limit=False
                n+= round(period,2)
            else:
                new_cgroup_limit = get_mem_process_use()*reduction_value
                limit_cgroup=str(int(new_cgroup_limit))
                change_limit_cgroup_file(limit_cgroup)
            

        

    #wait 1/3 of total duration to start new experiment
    time.sleep(DURATION/3)
            

##############################################
#
# Client's thread :
#
##############################################


'''
 function called by the thread to run the client
 While loop last DURATION seconds
 every FINESSE seconds, we send a GET request to the server
 server send back the VM's memory
 we store the result in a file at /outputs/<reduction_value>/<measurement_nbr>/outvm.txt
'''
def run_client(client,start_time,reduction_value,measurement,dir_output):

    print_log("client is running")

    
    t = round(time.process_time()-start_time,2)
    while t<DURATION:
        diff_t = round(time.process_time() - t - start_time,2)
        if diff_t>=FINESSE:
            t += diff_t
            get_server(client)
            donnees = client.recv(1024)
            with open(dir_output+"/outvm.txt","a+") as f_vmram:
                f_vmram.write(str(round(t,1))+" "+donnees.decode()+"\n")
                

'''
    send a GET request to the server
'''
def get_server(client):
    
    message ="GET"
    n = client.send(message.encode())
    if (n != len(message)):
            print_log('Erreur envoi.')
            

##############################################
#
# Utils :
#
##############################################

'''
 log printer
 store the output of the script in output.log
'''
def print_log(message):
    with open("output.log","a+") as flog:
        flog.write(message+"\n")


##############################################
#
# Main :
#
# - Read arguments
# - Create the output directory
# - Create the client socket
# - Connect socket to the server
#  2 nested loop :
#   - 1st loop : reduction_value
#   - 2nd loop : measurement
# 
# On each iteration, we create:
# - a thread for the client,
# - a thread for the cgroup limitation,
# - a thread for the benchmark,
# - a thread for the host's memory measurement

##############################################

if __name__ == "__main__":



    if len(sys.argv)>1:
        DURATION = float(sys.argv[1])
    if len(sys.argv)>2:
        FINESSE = float(sys.argv[2])
    if len(sys.argv)>3:
        BENCHMARK = (sys.argv[3] == str(True)) 

    with open("output.log","w") as flog:
        flog.write("")

    print_log(str(DURATION)+'-'+str(FINESSE))

    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print_log('Connexion vers {} on sur port {} réussie.'.format(HOST,PORT))

    message ="I'm client"
    n = client.send(message.encode())
    if (n != len(message)):
            print_log('Erreur envoi.')
 

    #os.system("rm -f benchmarks/*")
    
    for reduction_value in [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2]:
        for measurement in [i for i in range(5)]:
            with open("output.log","a+") as flog:
                flog.write("REDUCTION : {} - MEASURE : {} \n".format(reduction_value,measurement+1))
                
            start_time = time.process_time()

            dir_output = 'outputs/0_'+str(reduction_value).split(".")[1] +"/"+ str(measurement)
            dir_bench = 'benchmarks/0_'+str(reduction_value).split(".")[1] +"/"+ str(measurement)
            os.system("rm "+dir_bench+"/*")
    
            with open(dir_output+"/outvm.txt","w+") as f_vmram:
                f_vmram.write("")
    

            
            host_thread = threading.Thread(target=run_exec_host,args=(reduction_value,measurement,start_time))
            host_thread.start()
              
            
            cgroup_thread = threading.Thread(target=change_cgroup_memory_limit,args=(start_time,reduction_value,))
            cgroup_thread.start()
            
            client_thread = threading.Thread(target=run_client,args=(client,start_time,reduction_value,measurement,dir_output))
            client_thread.start()
            
            
            benchmark_thread = threading.Thread(target=run_benchmark,args=(start_time,reduction_value,measurement,))
            benchmark_thread.start()

            #We wait the end of execution of thread to start another loop
            
            
            host_thread.join()
            client_thread.join()
            benchmark_thread.join()
            cgroup_thread.join()
    client.close()
          

        
    


    
