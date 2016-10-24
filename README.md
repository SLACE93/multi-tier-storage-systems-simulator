# StorageSim - A multi-tier storage system simulator

StorageSim is a process-based discrete-event simulator developed using the SimPy simulation framework. It
simulates the operation of a multi-tiered storage system; for example, a system that stores super “hot” files 
in non-volatile RAM, less “hot” files in solid state drives (SSDs) and “warm” and “cold” files in hard disk
drives (HDDs). StorageSim comes with three data-placement policies, and can be extended to support other policies. 
It can replay publicly available storage traces from the Storage Networking Industry Association (SNIA) 
and other public sources, and can be used to evaluate data-placement policies prior to implementing them on a real system.
By abstracting away many complex details, StorageSim provides a fast simulation framework that can be used to simulate large
scale storage systems. Experimental results show that StorageSim is useful, can reproduce prior results from real 
deployments, and is fast enough to handle Big Data workloads in a timely manner.

The current version of the software includes the following policies:

+ **Hashed:** A simple policy that places files randomly in each tier, based on a user-defined hashing function.
+ **SSD caching:** All files are initially placed in the HDD layer; hot files are copied (cached) on SSD for faster access.
+ **f4:** based on Facebook’s storage architecture; includes a fast layer for hot files and a lower-throughput layer for  warm files. Tiering is based on the age: files younger than 
3 months old are hot while older files are warm.

## Requirements
+ Python 2.7
+ Simpy 3

## Installation
+ pip install simpy
+ Download multi-tier-storage-system-simulator repository

## Usage
Change the values for your simulation in the **settings.py** file of StorageSim. It's located in 
[change-working-directory]/multi-tier-storage-system-simulator/

Workload traces input format used by StorageSim. The following components of the input format are configurable:
+ Field separator
+ Timestamp unit
+ Order of the fields
+ Presence of the operation field (i.e., this field is optional)
+ Presence of the default tier field (i.e., this field is optional)
+ Presence of the size file field (i.e., this field is optional)

While you edit the settings.py file, for use one of the policies in your simulation, you need to change the variable value to the name of the policy. 
For example REPLACEMENT_POLICY= 'ssd_caching' (in lower case)

After finish configure correctly the settings file. Change the directory where you workload file is located

**cd ~/[workload_directory]/**

**cat workload_name.txt | python [working-directory]/multier-storage-system-simulator**

## Results
Generate a report with useful system metrics, like throughput and tier load distribution. 
The report is stored in a file called summary.txt at ~/[workload_directory]/

## Limitation.
Currently StorageSim only supports one type of IO operations: regular accesses, which are any type of read or write operation.


