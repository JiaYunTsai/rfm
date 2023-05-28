import logging

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

from factor_analyzer.factor_analyzer import FactorAnalyzer
from sklearn.cluster import KMeans

import RFM0414
import CRI0428
import CAI0415
import factoranalysis0513

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def get_person_transation(df_customer_detail, df_transaction, df_card_detail):
    
    
#     # 客戶資料檔案 only
#     bins = [0, 20, 30, 40, 50, 60, float('inf')]
#     labels = [1, 2, 3, 4, 5, 6]
#     df_customer_detail['年齡_encoding'] = pd.cut(df_customer_detail['年齡'], bins=bins, labels=labels, right=False)
#     df_customer_detail['居住地_encoding'] = df_customer_detail['居住地'].astype('category').cat.codes
#     df_customer_detail['教育程度_encoding'] = df_customer_detail['教育程度'].astype('category').cat.codes
#     df_customer_detail['性別_encoding'] = df_customer_detail['性別'].astype('category').cat.codes
#     df_customer_detail['婚姻狀況_encoding'] = df_customer_detail['婚姻狀況'].astype('category').cat.codes
#     df_customer_detail['職業_encoding'] = df_customer_detail['職業'].astype('category').cat.codes

#     # 交易紀錄黨
#     df_transaction = df_transaction.iloc[:, :-4]

#     # 產品資料檔案 only
#     df_transaction = pd.merge(df_transaction, df_card_detail[['信用卡ID', '卡等']], on='信用卡ID', how='left')
#     df_transaction = pd.merge(df_transaction, df_customer_detail, on='客戶ID', how='left')

#     return df_transaction

def get_encoding_customer_detail(df_customer_detail):
    
    bins = [0, 20, 30, 40, 50, 60, float('inf')]
    labels = ['0-20歲', '21-30歲', '31-40歲', '41-50歲', '51-60歲', '61歲以上']
    df_customer_detail['年齡_encoding'] = pd.cut(df_customer_detail['年齡'], bins=bins, labels=labels, right=False)
    df_customer_detail['居住地_encoding'] = df_customer_detail['居住地']
    df_customer_detail['教育程度_encoding'] = df_customer_detail['教育程度']
    df_customer_detail['性別_encoding'] = df_customer_detail['性別']
    df_customer_detail['婚姻狀況_encoding'] = df_customer_detail['婚姻狀況']
    df_customer_detail['職業_encoding'] = df_customer_detail['職業']

    return df_customer_detail

def get_rfm_data(df):
    RFM_base_dict = RFM0414.get_RFM_base_dict(df)
    RFM_score_add_self_define = RFM0414.get_rfm_score_5split(RFM_base_dict)
    
    return pd.DataFrame(RFM_score_add_self_define)

def get_CRI_data(df_customer_detail, df_transaction, df_card_detail):
    df_group = CRI0428.get_group(df_customer_detail, df_card_detail)
    df_clean_transaction = CRI0428.get_transaction_record(df_transaction)
    clean_transaction_and_group = CRI0428.get_transaction_and_group(df_group, df_clean_transaction)
    person_transaction_statistics = CRI0428.get_person_transaction_statistics(clean_transaction_and_group)
    group_transaction_statistics = CRI0428.get_group_transaction_statistics(clean_transaction_and_group)
     
    return CRI0428.CRI(df_group, 
                       person_transaction_statistics, 
                       group_transaction_statistics)

def get_revenue_metrics(df):
    df = df.loc[:, ['客戶ID', '刷卡金額']]
    df = df.groupby(['客戶ID']).agg({'刷卡金額':['sum', 'mean'] })
    df.columns = ['總消費金額', '平均消費金額']
    return df

def pearson_chi_squared_test(encoding_columns, df):
    res_df = pd.DataFrame()

    for column in encoding_columns:
    
        cross_tab = pd.crosstab(df[column], df['cluster'])
        chi2, p_value, dof, expected = chi2_contingency(cross_tab)  

        cross_tab.columns = ['cluster_0', 'cluster_1', 'cluster_2']
        cross_tab['total'] = cross_tab.sum(axis=1)
        cross_tab['cluster_0'] = cross_tab['cluster_0'] / cross_tab['total']
        cross_tab['cluster_1'] = cross_tab['cluster_1'] / cross_tab['total']
        cross_tab['cluster_2'] = cross_tab['cluster_2'] / cross_tab['total']
        cross_tab = cross_tab.drop(columns=['total'])
        cross_tab = cross_tab.applymap(lambda x: f'{x:.2%}' if x > 0 else 0)
        cross_tab['p-value'] = p_value
        cross_tab['encoding_columns'] = column
        cross_tab = cross_tab.reset_index()
        cross_tab = cross_tab.rename(columns={column: 'encoding_values'})
        cross_tab = cross_tab.set_index('encoding_columns')
        cross_tab = cross_tab.reset_index()
        cross_tab = cross_tab.rename(columns={'index': 'encoding_columns'})

        res_df = pd.concat([res_df, cross_tab], axis=0) 

    res_df = res_df.reset_index(drop=True)

    return res_df

def clustering_kmeans(df):
    #cluster:twostep k-mean 層集法
    feature = df.loc[:,['R_score_5split', 'F_score_5split', 
                        'M_score_5split','CRI', 'CAI']]
    feature = feature.fillna(0)
    kmeans = KMeans(n_clusters=3, random_state=0).fit(feature)

    logging.info(f'check k-means report\n{kmeans.cluster_centers_}')

    df['cluster'] = kmeans.labels_
    logging.info(f'check cluster count\n{df.cluster.value_counts()}')

    return df
       
def main():
    #STP 才能做心理與行為的市場區隔
    df_customer_detail = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=0)
    df_transaction = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=2)
    df_card_detail = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=1)

    df_customer_encoding = get_encoding_customer_detail(df_customer_detail)
    df_rfm = get_rfm_data(df_transaction)
    df_CRI = get_CRI_data(df_customer_detail, df_transaction, df_card_detail)
    df_CRI = df_CRI.loc[:, ['客戶ID', 'CRI']]
    df_CAI = CAI0415.CAI(df_transaction)
    df_CAI = df_CAI.loc[:, ['客戶ID', 'CAI']]
    df_revenue_metrics = get_revenue_metrics(df_transaction)

    df_customer = (
        df_customer_encoding
        .merge(df_rfm, left_on='客戶ID', right_on='customer_id', how='left')
        .merge(df_CRI.loc[:, ['客戶ID', 'CRI']], on='客戶ID', how='left')
        .merge(df_CAI.loc[:, ['客戶ID', 'CAI']], on='客戶ID', how='left')
        .merge(df_revenue_metrics, on='客戶ID', how='left')
    )

    df_customer['總消費金額'] = np.log(df_customer['總消費金額'])

    encoding_columns = ['年齡_encoding', '居住地_encoding', '教育程度_encoding', 
                        '性別_encoding','婚姻狀況_encoding', '職業_encoding']

    df_with_clustering = clustering_kmeans(df_customer)

    #Is there a significant difference in the proportion between males and females? 
    # with_pearson's chi squared
    df_pearson_chi_squared_test_report = pearson_chi_squared_test(encoding_columns, df_with_clustering)

    #Is there a significant difference in purchasing power between males and females?
    # with_f-test
    # video 50:00
    # 整體檢定
    # 事後檢定
    # df_f_test_report = f_test(encoding_columns, df)
    
    with pd.ExcelWriter('output/clustering.xlsx') as writer:
        df_pearson_chi_squared_test_report.to_excel(writer, sheet_name='數量比例不同檢定', index=False)
        
    
if __name__ == '__main__':
    main()