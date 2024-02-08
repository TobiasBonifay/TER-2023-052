# TER-2023-052
Code repository and experiment results for TER-2023-052

```
TER-2023-052
│   README.md : this file   
│   LOG.md : working log
│   TOPIC.md : the original topic from the supervisor
│
│───lab
│   │
│   └───README.md
│   │
│   └───requirements.txt -> the python packages needed to run the code
│   │
│   └───Plot.py -> script used to plot the data
│   │
│   └───create-lab.md -> the steps to create the lab
│   │
│   └───create-vm.md -> the steps to create the VM
│   │
│   └───apache2 (VM 1) -> script and file used to understand the behavior of the Apache2 server when restricting memory
│   │
│   └───client (VM 2) -> file that sends requests to the server and logs the response time + bandwidth
│   │
│   └───host (Machine) -> handle the experience and do the predict + plot + save the data
│   │
│   └───model -> the used/trained model to predict the response time
│   │
│   └───output -> the output of the experience
│
└───previousWork──data-generations -> script and file used to generate data to understand VM behavior when restricting memory. These datas have been too used to train the LSTM model
    │   │
    │   └───data
    │   │   │   
    │   │   └───benchmarks
    │   │   │   
    │   │   └───outputs
    │   │
    │   └───data-vizualisation
    │   │   │
    │   │   └─── graphs
    │   │
    │   └───scritps
    │
    └───model-lstm
    │
    └───MOIM
    │
    └───README.md
```
