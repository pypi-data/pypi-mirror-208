import random
from datetime import datetime

import MetaTrader5 as mt5
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

ini = mt5.initialize()

LOOK_BACK = 5
MA_PERIODS = [15, 55, 150, 250]

SYMBOL = 'EURUSD'
MARKUP = 0.00010
TIMEFRAME = mt5.TIMEFRAME_H1
START_DATE = datetime(2020, 1, 1)
TSTART_DATE = datetime(2015, 1, 1)
STOP_DATE = datetime(2021, 1, 1)


def get_prices(START, STOP):
    prices = pd.DataFrame(mt5.copy_rates_range(SYMBOL, TIMEFRAME, START, STOP),
                          columns=['time', 'close']).set_index('time')
    prices.index = pd.to_datetime(prices.index, unit='s')
    prices = prices.dropna()
    pr = prices.copy()
    count = 0
    for i in MA_PERIODS:
        returns = pr - pr.rolling(i).mean()
        for l in range(LOOK_BACK):
            prices[str(count)] = returns.shift(l)
            count += 1
    return prices.dropna()


def add_labels(dataset, min_, max_, add_noize=0.1):
    labels = []
    for i in range(dataset.shape[0] - max_):
        rand = random.randint(min_, max_)
        curr_pr = dataset['close'][i]
        future_pr = dataset['close'][i + rand]

        if future_pr + MARKUP < curr_pr:
            labels.append(1.0)
        elif future_pr - MARKUP > curr_pr:
            labels.append(0.0)
        else:
            labels.append(2.0)
    dataset = dataset.iloc[:len(labels)].copy()
    dataset['labels'] = labels
    dataset = dataset.dropna()
    dataset = dataset.drop(dataset[dataset.labels == 2].index).reset_index(drop=True)

    if add_noize == 0:
        return dataset

    # add noize to samples
    noize_b = dataset[dataset.labels == 0]['labels'].sample(frac=add_noize)
    noize_s = dataset[dataset.labels == 1]['labels'].sample(frac=add_noize)
    noize_b = noize_b + 1
    noize_s = noize_s - 1
    dataset.update(noize_b)
    dataset.update(noize_s)
    return dataset


def tester(dataset, markup=0.0, plot=False):
    last_deal = int(2)
    last_price = 0.0
    report = [0.0]
    for __k in range(dataset.shape[0]):
        pred = dataset['labels'][__k]
        if last_deal == 2:
            last_price = dataset['close'][__k]
            last_deal = 0 if pred <= 0.5 else 1
            continue
        if last_deal == 0 and pred > 0.5:
            last_deal = 1
            report.append(report[-1] - markup + (dataset['close'][__k] - last_price))
            last_price = dataset['close'][__k]
            continue
        if last_deal == 1 and pred < 0.5:
            last_deal = 0
            report.append(report[-1] - markup + (last_price - dataset['close'][__k]))
            last_price = dataset['close'][__k]

    y = np.array(report).reshape(-1, 1)
    X = np.arange(len(report)).reshape(-1, 1)
    lr = LinearRegression()
    lr.fit(X, y)

    l = lr.coef_
    if l >= 0:
        l = 1
    else:
        l = -1

    if (plot):
        plt.plot(report)
        plt.show()

    return lr.score(X, y) * l


def pca_plot(data):
    from sklearn.decomposition import PCA
    pca = PCA(n_components=5)
    components = pd.DataFrame(pca.fit_transform(data[data.columns[1:-1]]))
    g = sns.PairGrid(components, hue="labels", height=1.2)
    g.map_diag(sns.histplot)
    g.map_offdiag(sns.scatterplot)
    g.add_legend()
    plt.show()


def export_model_to_MQL_code(model):
    model.save_model('catmodel.h',
                     format="cpp",
                     export_parameters=None,
                     pool=None)

    # add variables
    code = 'int ' + 'loock_back = ' + str(LOOK_BACK) + ';\n'
    code += 'int hnd[];\n'
    code += 'int OnInit() {\n'
    code += 'ArrayResize(hnd,' + str(len(MA_PERIODS)) + ');\n'

    count = len(MA_PERIODS) - 1
    for i in MA_PERIODS:
        code += 'hnd[' + str(count) + ']' + ' =' + ' iMA(NULL,PERIOD_CURRENT,' + str(i) + ',0,MODE_SMA,PRICE_CLOSE);\n'
        count -= 1

    code += 'return(INIT_SUCCEEDED);\n'
    code += '}\n\n'

    # get features
    code += 'void fill_arays(int look_back, double &features[]) {\n'
    code += '   double ma[], pr[], ret[];\n'
    code += '   ArrayResize(ret,' + str(LOOK_BACK) + ');\n'
    code += '   CopyClose(NULL,PERIOD_CURRENT,1,look_back,pr);\n'
    code += '   for(int i=0;i<' + str(len(MA_PERIODS)) + ';i++) {\n'
    code += '       CopyBuffer(hnd[' + 'i' + '], 0, 1, look_back, ma);\n'
    code += '       for(int f=0;f<' + str(LOOK_BACK) + ';f++)\n'
    code += '           ret[f] = pr[f] - ma[f];\n'
    code += '       ArrayInsert(features, ret, ArraySize(features), 0, WHOLE_ARRAY); }\n'
    code += '   ArraySetAsSeries(features, true);\n'
    code += '}\n\n'

    # add CatBosst
    code += 'double catboost_model' + '(const double &features[]) { \n'
    code += '    '
    with open('catmodel.h', 'r') as file:
        data = file.read()
        code += data[data.find("unsigned int TreeDepth"):data.find("double Scale = 1;")]
    code += '\n\n'
    code += 'return ' + 'ApplyCatboostModel(features, TreeDepth, TreeSplits , BorderCounts, Borders, LeafValues); } \n\n'

    code += 'double ApplyCatboostModel(const double &features[],uint &TreeDepth_[],uint &TreeSplits_[],uint &BorderCounts_[],float &Borders_[],double &LeafValues_[]) {\n\
    uint FloatFeatureCount=ArrayRange(BorderCounts_,0);\n\
    uint BinaryFeatureCount=ArrayRange(Borders_,0);\n\
    uint TreeCount=ArrayRange(TreeDepth_,0);\n\
    bool     binaryFeatures[];\n\
    ArrayResize(binaryFeatures,BinaryFeatureCount);\n\
    uint binFeatureIndex=0;\n\
    for(uint i=0; i<FloatFeatureCount; i++) {\n\
       for(uint j=0; j<BorderCounts_[i]; j++) {\n\
          binaryFeatures[binFeatureIndex]=features[i]>Borders_[binFeatureIndex];\n\
          binFeatureIndex++;\n\
       }\n\
    }\n\
    double result=0.0;\n\
    uint treeSplitsPtr=0;\n\
    uint leafValuesForCurrentTreePtr=0;\n\
    for(uint treeId=0; treeId<TreeCount; treeId++) {\n\
       uint currentTreeDepth=TreeDepth_[treeId];\n\
       uint index=0;\n\
       for(uint depth=0; depth<currentTreeDepth; depth++) {\n\
          index|=(binaryFeatures[TreeSplits_[treeSplitsPtr+depth]]<<depth);\n\
       }\n\
       result+=LeafValues_[leafValuesForCurrentTreePtr+index];\n\
       treeSplitsPtr+=currentTreeDepth;\n\
       leafValuesForCurrentTreePtr+=(1<<currentTreeDepth);\n\
    }\n\
    return 1.0/(1.0+MathPow(M_E,-result));\n\
    }'

    file = open(
        'C:/Users/dmitrievsky/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Include/' + 'cat_model' + '.mqh',
        "w")
    file.write(code)
    file.close()
    print('The file ' + 'cat_model' + '.mqh ' + 'has been written to disc')


# make dataset
pr = get_prices(START_DATE, STOP_DATE)
pr = add_labels(pr, min_=10, max_=25, add_noize=0)
res = tester(pr, plot=True)

# perform GMM clasterizatin over dataset
from sklearn import mixture

pr_c = pr.copy()
X = pr_c[pr_c.columns[1:]]
gmm = mixture.GaussianMixture(n_components=75, covariance_type='full', n_init=1).fit(X)


# plot resampled components
# generated = gmm.sample(5000)
# gen = pd.DataFrame(generated[0])
# gen.rename(columns={ gen.columns[-1]: "labels" }, inplace = True)
# gen.loc[gen['labels'] >= 0.5, 'labels'] = 1
# gen.loc[gen['labels'] < 0.5, 'labels'] = 0
# pca_plot(gen)

# brute force loop
def brute_force(samples=5000):
    # sample new dataset
    generated = gmm.sample(samples)
    # make labels 
    gen = pd.DataFrame(generated[0])
    gen.rename(columns={gen.columns[-1]: "labels"}, inplace=True)
    gen.loc[gen['labels'] >= 0.5, 'labels'] = 1
    gen.loc[gen['labels'] < 0.5, 'labels'] = 0
    X = gen[gen.columns[:-1]]
    y = gen[gen.columns[-1]]
    # train\test split
    train_X, test_X, train_y, test_y = train_test_split(X, y, train_size=0.5, test_size=0.5, shuffle=True)
    # learn with train and validation subsets
    model = CatBoostClassifier(iterations=500,
                               depth=6,
                               learning_rate=0.1,
                               custom_loss=['Accuracy'],
                               eval_metric='Accuracy',
                               verbose=False,
                               use_best_model=True,
                               task_type='CPU')
    model.fit(train_X, train_y, eval_set=(test_X, test_y), early_stopping_rounds=25, plot=False)
    # test on new data
    pr_tst = get_prices(TSTART_DATE, START_DATE)
    X = pr_tst[pr_tst.columns[1:]]
    X.columns = [''] * len(X.columns)

    # test the learned model
    p = model.predict_proba(X)
    p2 = [x[0] < 0.5 for x in p]
    pr2 = pr_tst.iloc[:len(p2)].copy()
    pr2['labels'] = p2
    R2 = tester(pr2, MARKUP, plot=False)

    return [R2, samples, model]


def test_model(result):
    pr_tst = get_prices(TSTART_DATE, STOP_DATE)
    fg_ = pr_tst[pr_tst.columns[1:]]
    fg_.columns = [''] * len(fg_.columns)

    # test the learned model
    p = result[2].predict_proba(fg_)
    p2 = [x[0] < 0.5 for x in p]
    pr2 = pr_tst.iloc[:len(p2)].copy()
    pr2['labels'] = p2
    tester(pr2, MARKUP, plot=True)


# iterative learning
res = []
for i in range(50):
    res.append(brute_force(10000))
    print('Iteration: ', i, 'R^2: ', res[-1][0])

# test best model
res.sort()
test_model(res[-2])
var = res[-2][0]

# export best model to mql
export_model_to_MQL_code(res[-1][2])
