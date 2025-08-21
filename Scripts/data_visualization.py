import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd
import seaborn as sns

stats = pd.read_csv('../NFL Fantasy Stats/2024 fantasy stats.csv')
# Keep only X number of rows
stats = stats.head(251)

n, bins, patches = plt.hist(stats['Age'], bins = range(int(stats.Age.min()), int(stats.Age.max()) + 1), edgecolor = 'black')
plt.xlabel('Age')
plt.ylabel('Frequency')

for i in range(len(n)):
    plt.text(bins[i] + (bins[i+1] - bins[i]) / 2, n[i], str(int(n[i])), ha='center', va='bottom')

plt.show()

print(stats)
