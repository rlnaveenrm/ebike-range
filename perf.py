
import math
import sys, os
import matplotlib.pyplot as plt

pathname = os.path.dirname(sys.argv[0])


cfig = {}
with open(pathname+"\config.cycle", "r") as c:
    for line in c.readlines():
        li = line.lstrip()
        if not li.startswith("#") and '=' in li:
            key, value = line.split('=', 1)
            cfig[key] = float(value.strip())

iprofile = []
with open(pathname+"\drivingcycle.csv", "r") as p:
    for line in p.readlines():
        li = line.rstrip()
        if not li.startswith("#"):
            iprofile.append(li)

profile = [list(map(float,line.split(','))) for line in iprofile]


roll_arr, air_arr, grad_arr, iner_arr, tr_arr, tp_arr, ep_arr, batcap_arr, range_arr = [[] for i in range(9)]

def roll_res(crr,m,theta):
    val = crr*m*9.8*math.cos(math.radians(theta))
    roll_arr.append(val)
    return val

def air_res(airden,v,farea,cd):
    val = .5*airden*v*v*farea*cd
    air_arr.append(val)
    return val

def grad_res(m,theta):
    val = m*9.8*math.sin(math.radians(theta))
    grad_arr.append(val)
    return val

def iner_res(m,a,J,reff):
    val = (m+(J/(reff*reff)))*a
    iner_arr.append(val)
    return val

def tot_res(crr,m,theta,airden,v,farea,cd,a,J,reff):
    val = roll_res(crr,m,theta) + air_res(airden,v,farea,cd) + grad_res(m,theta) + iner_res(m,a,J,reff)
    tr_arr.append(val)
    return val

def tot_power(crr,m,theta,airden,v,farea,cd,a,J,reff):
    val = tot_res(crr,m,theta,airden,v,farea,cd,a,J,reff) * v
    tp_arr.append(val)
    return val

def eff_power(crr,m,theta,airden,v,farea,cd,a,J,reff,hupo):
    val = tot_power(crr,m,theta,airden,v,farea,cd,a,J,reff) - hupo
    ep_arr.append(val)

acc_arr = [0]
for i in list(range(len(iprofile)-1)):
    acc_arr.append ((profile[i+1][1]-profile[i][1])/(profile[i+1][0]-profile[i][0]))

for i in range(len(iprofile)):
    eff_power(cfig['crr'], cfig['m'], profile[i][2], cfig['airden'], profile[i][1], cfig['farea'], cfig['cd'], acc_arr[i], cfig['J'], cfig['reff'], cfig['hupo'])

batcap = cfig['batcap']*3600
if cfig['regen']==1:
    for ep in ep_arr:
        batcap = batcap - ep
        batcap_arr.append(batcap/(cfig['batcap']*36))
elif cfig['regen']==0:
    for ep in ep_arr:
        if ep>=0:
            batcap = batcap - ep
        batcap_arr.append(batcap/(cfig['batcap']*36))

range_arr=[0,0,0,0,0,0,0,0,0]

for i in list(range(len(iprofile)-9)):
    val=0
    for  j in list(range(10)):
        val += profile[i+j][1]

    val2 = (batcap_arr[i]-batcap_arr[i+9])*cfig['batcap']/100

    range_arr.append((val/val2)*batcap_arr[i+9]/100000*cfig['batcap'])

print("Dumping performance data to a csv file in the same directory....please wait")
with open(pathname+'\datadump.csv', 'w+') as o:
    o.write("time,velocity,angle of road,acceleration,rolling resistance,air resistance,gradient resistance,inertial resistance,total resistance,total power,effective power,battery capacity,range"+'\n')
    for i in list(range(len(iprofile))):
        o.write(str(profile[i][0])+','+str(profile[i][1])+','+str(profile[i][2])+','+str(acc_arr[i])+','+str(roll_arr[i])+','+str(air_arr[i])+','+str(grad_arr[i])+','+str(iner_arr[i])+','+str(tr_arr[i])+','+str(tp_arr[i])+','+str(ep_arr[i])+','+str(batcap_arr[i])+','+str(range_arr[i])+'\n')
"""
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(list(range(len(iprofile))), ep_arr, color='red', label='effective power')
ax1.plot(list(range(len(iprofile))), tp_arr, color='green', label='total power')

ax2.plot(list(range(len(iprofile))), batcap_arr, color='grey', label='battery percent left')
ax2.plot(list(range(len(iprofile))),roll_arr, color='blue', label='roll resistance')
ax2.plot(list(range(len(iprofile))),air_arr, color='yellow', label='air resistance')
ax2.plot(list(range(len(iprofile))),grad_arr, color='orange', label='gradient resistance')
ax2.plot(list(range(len(iprofile))),iner_arr, color='violet', label='inertial resistance')
ax2.plot(list(range(len(iprofile))),tr_arr, color='black', label='total resistance')

ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Power (W)')
ax2.set_ylabel('Force (N)')
ax2.set_ylim([0,250])
plt.title('Performance characteristics - ebike')
plt.grid(True)
plt.savefig("test.png")
ax1.legend(loc = "upper left")
ax2.legend(loc = "upper right")
plt.show()"""
