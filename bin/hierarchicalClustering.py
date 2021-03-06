import sys, os
import sklearn.cluster
from pandas.io.parsers import read_csv
import numpy as np
import pandas as pd
import scipy.spatial.distance as dist
import matplotlib.pyplot as plt
from Colors import *

try:
    indata = sys.argv[1]
    ncluster = int(sys.argv[2])
    outfile = sys.argv[3]
    method = sys.argv[4]
    pdfplot = sys.argv[5]
except:
    sys.exit('Please, give input (1) table; (2) number of clusters; (3) root for output file; (4) method (hcl/acl); (5) pdfplot (y/n)')

df = read_csv(indata, sep = '\t', index_col = 0)
df.columns.name = 'cellid'
if '720M' in df.index:
    df = df.loc[['720M'] + [idx for idx in df.index if idx != '720M']]

if method == 'hcl':  #### Before cleaning ####
    hclust = sklearn.cluster.KMeans(n_clusters = ncluster, random_state = 20)
    hclust.fit(df.transpose())
elif method == 'acl': #### After cleaning ####
    hclust = sklearn.cluster.AgglomerativeClustering(n_clusters = ncluster)
    hclust.fit(df.transpose())

hclustdf = pd.DataFrame({'hclust': hclust.labels_}, index = df.columns)
hclustdf = hclustdf.sort_values(by = 'hclust')
hclustdf.to_csv(outfile + '_clust.txt', sep = '\t', header = None)

centroiddf = pd.DataFrame(index = df.index)
centroiddf.columns.name = 'centroids'
distCM = pd.DataFrame(columns = ['dmeanCM', 'dvarCM', 'numCell'])
for i in range(ncluster):
    cells = hclustdf[hclustdf['hclust'] == i].index
    rdf = df[cells]
    centroid = rdf.mean(axis=1).sort_values(ascending=False)
    centroiddf[i] = centroid
centroiddf.transpose().to_csv(outfile + '_centroid.txt', sep = '\t')

df = df[hclustdf.index].transpose()
df['hclust'] = hclustdf
df.to_csv(outfile + '_df.txt', sep = '\t')

f = open(outfile + '.gpl', 'w')
print >> f, 'set style data histogram'
print >> f, 'set style histogram rowstacked'
print >> f, 'set style fill solid'
print >> f, 'unset xtic'
print >> f, 'set key out'
print >> f, 'set ytics 0,20,100'
print >> f, 'l "var/gnuplot-extendcolor.gpl"'
print >> f, 'pl for [i=2:' + str(df.shape[1]) + '] "' + outfile + '_df.txt" us i:xtic(1) ti col'
print >> f, 'rep for [i=0:' + str(ncluster-1) + '] "' + outfile + '_clust.txt" us ($2==i?10:1/0) noti'
f.close()


if pdfplot=='y':
    fig = plt.figure(figsize=(15,5))
    bottom=np.zeros(len(df.index))
    for i, cigar in enumerate(df.columns[:-1]):
        j = np.mod(i,len(colors))
        plt.bar(range(len(df.index)), df[cigar], bottom = bottom, width = 1, color=colors[j])
        bottom += df[cigar]

    plt.ylim(0,100)
    plt.xlim(0,len(df.index))
    plt.ylabel('scar %')
    plt.xlabel('cells')
    
    art = []
    lgd = plt.legend(df.columns[:-1], loc = 9, bbox_to_anchor = (0.5, -0.1), ncol = 5)
    art.append(lgd)

    fig.savefig(outfile + '_barplot.pdf',  additional_artist=art, bbox_inches='tight')
