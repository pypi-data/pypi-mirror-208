import pyfdstools as fds
import os
import numpy as np
resultDir = "examples\\case001_multimesh\\"
chid = "case001_multimesh"
fdsFilePath = os.path.join(resultDir, chid + '.fds')
fdsQuantities = ['WALL TEMPERATURE']
fdsUnits = ['C']
(axis, value) = (-2, 4.4)
(tStart, tEnd) = (0, 120)
datas, times = fds.queryBndf(resultDir, chid, fdsFilePath, fdsQuantities, fdsUnits, axis, value)


qty = fdsQuantities[0]
data = datas[qty]['DATA']
x = datas[qty]['X']
z = datas[qty]['Z']

for i, t in enumerate(times):
    d = data[:, :, i]
    np.savetxt('%s%s_t_%03d.csv'%(resultDir, chid, t), data[:, :, i], delimiter=',',fmt='%.4f')
tStartInd = np.argwhere(times >= tStart)[0][0]
tEndInd = np.argwhere(times <= tEnd)[-1][0]

meanData = np.mean(data[:, :, tStartInd:tEndInd], axis=2)
fig = fds.plotSlice(x, z, meanData, axis)