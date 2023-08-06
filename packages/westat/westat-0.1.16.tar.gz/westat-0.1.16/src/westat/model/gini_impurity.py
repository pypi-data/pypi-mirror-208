import pandas as pd


def gini_impurity(l=None,c=None):
    """
    根据传入的数据列表，计算基尼不纯度
    Args:
        l: 需要计算不纯度的数据列表，支持pandas.Series和python列表、元组格式
        c: 已统计的数值结果列表

    Returns:
        基尼不纯度 gini impurity
    """

    if not isinstance(l, pd.Series):
        l = pd.Series(l)

    if not isinstance(c, pd.Series):
        c = pd.Series(c)

    if len(l)>0:
        r = l.value_counts()
        df = pd.DataFrame(r)
        df['ratio'] = df['count'] / len(l)
        df.reset_index(drop=True, inplace=True)
    else:
        df = pd.DataFrame({'count':c},index=range(len(c)))
        df['ratio'] = df['count'] / sum(c)
        df.reset_index(drop=True, inplace=True)
    

    gini_impurity = 1 - sum([p ** 2 for p in df['ratio']])

    return gini_impurity