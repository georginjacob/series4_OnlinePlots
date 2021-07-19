import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec

#generate random data
nTrials=100
data = np.random.random((nTrials,100))

ltime   =   0
utime   =   4
nbin    =   10
bins =np.linspace(ltime,utime,nbin+1)

alldata = np.empty((nTrials,len(bins)-1))
alldata[:] = np.NaN

print(bins)
for i in range(50):
    counts,bins = np.histogram(data[i],bins=nbin,range=(0,1))
    alldata[i][:]=counts
marginals_alldata=np.nansum(alldata,axis=1)


array_has_nan       =   np. isnan(marginals_alldata)
deltaT              =   (5-0)/9
bin_width           =   (bins[1]-bins[0])
bin_center          =   bins[:-1]+bin_width/2
sum_alldata         =   np.nansum(alldata, axis=0)
histogram_all_data  =   sum_alldata/(100*deltaT)




fig2= plt.figure(constrained_layout=True)
#ax=[]
#widths = [4, 4, 4]
#heightratio = [2, 8]
#spec = fig.add_gridspec(ncols=3, nrows=2, width_ratios=widths,height_ratios=heightratio)
#f_ax1 = fig.add_subplot(spec[0, :])
#f_ax2 = fig.add_subplot(spec[1, :-1])
#f_ax3 = fig.add_subplot(spec[1:, -1])
#f_ax4 = fig.add_subplot(spec[-1, 0])
#f_ax5 = fig.add_subplot(spec[-1, -2])

#f_ax5.bar(bin_center,histogram_all_data,width=bin_width*0.9)
widths = [4, 4, 4]
heightratio = [2, 8]
fig2 = plt.figure(constrained_layout=True)
spec2 = gridspec.GridSpec(ncols=3, nrows=2, figure=fig2,width_ratios=widths, height_ratios=heightratio)
f2_ax1 = fig2.add_subplot(spec2[0, 0])
f2_ax2 = fig2.add_subplot(spec2[0, 1])
f2_ax3 = fig2.add_subplot(spec2[1, 0])
f2_ax4 = fig2.add_subplot(spec2[1, 1])
f2_ax1.bar(bin_center,histogram_all_data,width=bin_width*0.9)
f2_ax2.bar(bin_center,histogram_all_data,width=bin_width*0.9)
plt.show()


#f_ax5.show()





#Plot data
#fig, axs = plt.subplots(2,3,figsize=(16,9), gridspec_kw={'height_ratios': [1, 2]})
#axs[0,0].hist(z,np.arange(0,100,10))
#axs[1,0].scatter(z['level_1'], z['level_0'],c=z[0])
#plt.show()
