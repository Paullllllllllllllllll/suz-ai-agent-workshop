# analysis.py -- wages, cities and the Reformation, quick look
# TODO clean up before sending to coauthor!!
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

w = pd.read_csv("data/allen_wages_region_panel.csv")
u = pd.read_csv("data/buringh_urban_pop_panel.csv")
r = pd.read_csv("data/religion_panel.csv")
c = pd.read_csv("data/clio_infra_panel.csv")

m = w.merge(u, on=["region", "period"]).merge(r, on=["region", "period"])
m = m.merge(
    c[["region", "period", "urbanization_ratio_mean", "total_population_mean"]],
    on=["region", "period"],
)

# fill the gaps in the urban pop
m["total_urban_pop"] = m.total_urban_pop.ffill()

m["lurb"] = np.log(m.total_urban_pop)
m["lwage"] = np.log(m.craft_real_wage_mean)
m["lpop"] = np.log(m.total_population_mean)
m = m.dropna()

# early modern only
m = m[m.period_start < 1850]

X = np.column_stack([np.ones(len(m)), m.lurb, m.protestant_dummy, m.lpop])
b = np.linalg.lstsq(X, m.lwage, rcond=None)[0]
print("coef: const %.3f  log urban pop %.3f  protestant %.3f  log pop %.3f" % tuple(b))
print("n =", len(m))
print("regions:", m.region.nunique())

plt.scatter(m.lurb, m.lwage, c=m.protestant_dummy)
plt.xlabel("log urban pop")
plt.ylabel("log craftsmen real wage")
plt.savefig("scatter.png")
