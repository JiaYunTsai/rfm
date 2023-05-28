import pandas as pd
from sklearn.decomposition import FactorAnalysis
from factor_analyzer.factor_analyzer import FactorAnalyzer
import matplotlib.pyplot as plt
import numpy as np

def get_dummies(df):
    one_year_ago = df['刷卡日期'].max() - pd.Timedelta(days=365)
    df = df[df['刷卡日期'] >= one_year_ago]
    df = df.loc[:, ['客戶ID', '刷卡產品產業分類']]
    df = pd.get_dummies(df, columns=['刷卡產品產業分類'], prefix='', prefix_sep='')

    df = df.groupby(['客戶ID']).sum()
    df = df.applymap(lambda x: 1 if x > 0 else 0)

    return df

def get_factor_analysis(df, writer):

    fa = FactorAnalyzer(5, rotation="varimax")
    fa.fit(df)
    res_df = pd.DataFrame(np.abs(fa.loadings_),index=df.columns)
    res_df.to_excel(writer, sheet_name='FA_分析結果')
    res_df = res_df.applymap(lambda x: 0 if x <= 0.4 else x)
    res_df.to_excel(writer, sheet_name='FA_分析結果大於0.4')
    
    return res_df

def main():
    df = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=2)
    df_dummies = get_dummies(df)
    print(df_dummies.head(10))




    with pd.ExcelWriter('output/Basket_Analysis2_作業2_蔡佳芸_M11108040.xlsx') as writer:
        res_df = get_factor_analysis(df_dummies, writer)
        
    
if __name__ == '__main__':
    main()