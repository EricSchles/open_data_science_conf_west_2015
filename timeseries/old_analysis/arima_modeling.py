import numpy as np
from scipy import stats
import pandas
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot

dta = sm.datasets.sunspots.load_pandas().data
dta.index = pandas.Index(sm.tsa.datetools.dates_from_range("1700","2008"))
del dta["YEAR"]
dta.plot(figsize=(12,8))

fig = plt.figure(figsize=(12,8))
ax1 = fig.add_subplot(211)
fig = sm.graphics.tsa.plot_acf(dta.values.squeeze(), lags=40, ax=ax1)
ax2 = fig.add_subplot(212)
fig = sm.graphics.tsa.plot_pacf(dta, lags=40, ax=ax2)

arma_mod20 = sm.tsa.ARMA(dta, (2,0)).fit()
arma_mod30 = sm.tsa.ARMA(dta, (3,0)).fit()

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
ax = arma_mod30.resid.plot(ax=ax)
resid = arma_mod30.resid
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
fig = qqplot(resid, line='q', ax=ax, fit=True)

r,q,p = sm.tsa.acf(resid.values.squeeze(), qstat=True)
data = np.c_[range(1,41), r[1:], q, p]
table = pandas.DataFrame(data, columns=['lag',"AC", "Q", "Prob(>Q)"])
print table.set_index('lag')

predict_sunspots = arma_mod30.predict("1990","2012", dynamic=True)
ax = dta.ix['1950':].plot(figsize=(12,8))
ax = predict_sunspots.plot(ax=ax, style="r--", label="Dynamic Prediction")
ax.legend()
ax.axis((-20.0,38.0,-4.0,200.0))
plt.show()
