# parse and plot output from LibPaxos3 and LibFPaxos

import csv
import numpy as np

# parse csv output
def read(filename):
    latency = []
    throughput = []
    with open(filename, newline='') as csvfile:
        for row in csv.reader(csvfile):
            if len(row) == 3:
                thr = row[0].rsplit(" ")
                bw = row[1].rsplit(" ")
                lat = row[2].rsplit(" ")
                if len(thr) == 2 and len(bw) == 3 and len(lat) == 11 and lat[9].isdigit() and thr[0].isdigit():
                    latency.append(int(lat[9])/1000)
                    throughput.append(int(thr[0]))
    return (latency, throughput)

# average over averaged values
def average (arr1,arr2):
    total = 0
    items = 0
    for x,y in zip(arr1,arr2):
        total =+ x*y
        items =+ y
    if items == 0:
        return 0
    else:
        return (total/items)

# get phase data from LibPaxos3

paxos_data = {}
paxos_throughput = {}
for n in range(9,15,1):
    maj = int(floor(n/2)+1)
    paxos_data[n], paxos_throughput[n] = read(
        "paxos/client-config_r"+str(n)+"_q"+str(maj)+"_g"+str(n)+".log")


replicas = list(range(3,15,1))
avg_latency = []
avg_throughput = []
for n in replicas:
    if len(paxos_data[n]) > 0 and len(paxos_throughput[n]) > 0:
        thr_array = paxos_throughput[n][20:100]
        lat_array = paxos_data[n][20:100]
        avg_latency.append(average(lat_array,thr_array))
        avg_throughput.append(np.mean(thr_array))

# figure of latency/throughput of LibPaxos3

fig = plt.figure()
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
axes.set_xlim([2,15])

axes.set_xlabel('Number of replicas')

axes.set_ylabel('Latency (ms)')
axes.set_title('Throughput and Latency for LibPaxos3')

l = axes.plot(replicas, avg_latency,"bx-", label='latency')
axes.set_ylim([0,80])

axes2 = axes.twinx()
axes2.set_ylabel('Throughput (reqs/sec)')
t = axes2.plot(replicas, avg_throughput,"ro-", label='throughput')
axes2.set_ylim([0,400])
axes2.set_xlim([2.5,14.5])
axes2.set_xticks(np.arange(3, 15, 1.0))

lns = l+t
labs = [l.get_label() for l in lns]
axes2.legend(lns, labs, loc=0,frameon=False)

fig.savefig('paxos.pdf', bbox_inches='tight')

fig = plt.figure()
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

axes.set_xlabel("Time")
axes.set_ylabel("latency")

axes.set_ylim([0,200])
axes.set_xlim([0,100])

lines = list(range(3,15,1))

for n in lines:
    axes.plot(paxos_data[n])

axes.legend(lines,loc=1,frameon=False)

fig = plt.figure()
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

axes.set_xlabel("Time")
axes.set_ylabel("Throughput (reqs/sec)")

axes.set_ylim([0,400])
axes.set_xlim([0,100])

for n in lines:
    axes.plot(paxos_throughput[n])

axes.legend(lines,loc=1,frameon=False)

# Now for FPaxos

fpaxos_data = {}
fpaxos_throughput = {}

replicas = list(range(3,11,1))

for n in replicas:
    maj = int(floor(n/2)+1)
    fpaxos_data[n] = {}
    fpaxos_throughput[n] = {}
    for q in range(1,maj+1):
         fpaxos_data[n][q], fpaxos_throughput[n][q] = read("fpaxos-results/client-config_r"+str(n)+"_q"+str(q)+"_g"+str(q)+".log")

for n in replicas:
    maj = int(floor(n/2)+1)
    lines = list(range(1,maj+1))
    n_latency = []
    n_throughput = []
    labels = []
    for q in lines:
        if len(fpaxos_throughput[n][q]) > 0 and len(fpaxos_data[n][q]) > 0:
            thr_array = fpaxos_throughput[n][q][20:100]
            lat_array = fpaxos_data[n][q][20:100]
            print(n,q,average(lat_array,thr_array),np.mean(thr_array))
            n_latency.append(average(lat_array,thr_array))
            n_throughput.append(np.mean(thr_array))
            labels.append('FPaxos '+str(q))

    n_throughput.append(avg_throughput[n])
    n_latency.append(avg_latency[n])
    labels.append('Paxos')

    ind = np.arange(maj+1)  # the x locations for the groups
    width = 0.15
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.set_xlim([-1,maj])
    axes.set_ylim([0,50])
    axes.set_ylabel('Latency (ms)')
    axes.set_title('FPaxos and LibPaxos3 for '+str(n)+' replicas')
    l = axes.bar(ind, n_latency, width, color="blue",label="latency")

    axes2 = axes.twinx()
    t = axes2.bar(width + ind, n_throughput, width, color="red",label="throughput")
    axes2.set_ylabel('Throughput (reqs/sec)')

    axes.set_xticks(ind + width)
    axes.set_xticklabels(labels)
    axes2.set_ylim([0,500])

    lns = [l[1],t[1]]
    labs = ['latency','throughput']
    axes2.legend(lns, labs, loc=0,frameon=False,ncol=2)

    fig.savefig('fpaxos_'+str(n)+'.pdf', bbox_inches='tight')

for n in replicas:
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    axes.set_xlabel("Time")
    axes.set_ylabel("latency")

    axes.set_ylim([0,400])
    axes.set_xlim([20,100])

    maj = int(floor(n/2)+1)
    lines = list(range(1,maj+1))

    for q in lines:
        axes.plot(fpaxos_data[n][q])

    axes.legend(lines,loc=1,frameon=False)

    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    axes.set_xlabel("Time")
    axes.set_ylabel("Throughput (reqs/sec)")

    axes.set_ylim([0,200])
    axes.set_xlim([20,100])

    for q in lines:
        axes.plot(fpaxos_throughput[n][q])

    axes.legend(lines,loc=1,frameon=False)
