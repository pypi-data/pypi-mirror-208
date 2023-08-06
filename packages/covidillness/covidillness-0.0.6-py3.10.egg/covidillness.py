import pandas as pd
import subprocess as sp
import sys
import numpy as np
import matplotlib.pyplot as plt

sp.call('wget -nc https://covid.ourworldindata.org/data/owid-covid-data.csv', shell=True)

d = pd.read_csv('owid-covid-data.csv')
d.fillna(0, inplace=True)
lastday = str(d.date.iloc[-1:]).split()[1]
print(lastday)

n = len(sys.argv) - 1
print('countries:', n)

countries = []
for i in range(n):
    countries.append(sys.argv[i+1])

from datetime import date
d0 = date(2020, 2, 29)
d1 = date(int(lastday.split('-')[0]), int(lastday.split('-')[1]), int(lastday.split('-')[2]))
delta = d1 - d0
days = delta.days

daysdate = sorted(d.date.unique())
daysdate = daysdate[len(daysdate)-days:-1]

dd = pd.DataFrame(
    {
        "date": daysdate,
        "cases": range(len(daysdate)),
        "icu_patients": range(len(daysdate)),
    })

for i in countries:
    print(i)
    for j in daysdate:
        if d.loc[(d.date == j) & (d.location == i), 'new_cases'].any():
            dd.loc[dd.date == j, 'cases'] = d.loc[(d.date == j) & (d.location == i), 'new_cases'].values[0]
        dd.loc[dd.date == j, 'icu_patients'] = d.loc[(d.date == j) & (d.location == i), 'icu_patients'].values[0]
    dd.to_csv(i + '.csv', index=False)

def main():
    fig = plt.figure(figsize=(8, 6), dpi=100)
    for i in range(len(countries)):
        data = pd.read_csv(countries[i] + '.csv') 
        ax1 = fig.add_subplot(211, title="The number of new Covid-19 cases", ylabel="Covid-19 Cases")
        ax1.plot(data.date, data.cases)
        ax1.set_xticks(np.arange(0, days, 30*days/770))
        ax1.set_xticklabels(data.date[::30], rotation=90)
        ax1.legend(countries)
        ax2 = fig.add_subplot(212, title="The number of Icu patients", xlabel="Date", ylabel="Icu Patients")
        ax2.plot(data.date, data.icu_patients)
        ax2.set_xticks(np.arange(0, days, 30*days/770))
        ax2.set_xticklabels(data.date[::30], rotation=90)
        ax2.legend(countries)
    fig.tight_layout()
    fig.savefig('result.png', bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    main()