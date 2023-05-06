import pandas as pd
import numpy as np

def EDA(df, name):
    print("quick peek", df.head(5), '\n')
    print("data types",df.dtypes, '\n')
    print(df.describe(), '\n')
    print(df.describe(include=['object']), '\n')
    print(f"最新的刷卡日期為: {df['刷卡日期'].max()}\n")
    df['刷卡日期'] = pd.to_datetime(df['刷卡日期'])
    print(df['刷卡日期'])

    object_columns = df.select_dtypes(include=['object']).columns.tolist()
    # for col in object_columns:
    #     content = df[col].unique()
    #     print(f"{col}的內容有: {content}\n")

    df_list = [
        pd.DataFrame({
            'table_name': name,
            'col_name': col,
            'item': df[col].value_counts().index,
            'count': df[col].value_counts().values,
        })for col in object_columns]

    object_columns_count_df = pd.concat(df_list, axis=0, ignore_index=True)
    print(object_columns_count_df)

    return object_columns_count_df

def get_purchase_matrix_without_condition(df, writer):
    one_year_ago = df['刷卡日期'].max() - pd.Timedelta(days=365)
    df = df[df['刷卡日期'] >= one_year_ago]
    df = df.loc[:, ['客戶ID', '刷卡產品產業分類']]
    df = pd.get_dummies(df, columns=['刷卡產品產業分類'], prefix='', prefix_sep='')

    df = df.groupby(['客戶ID']).sum()
    df = df.applymap(lambda x: 1 if x > 0 else 0)
    df_corr = df.corr()
    df_corr.to_excel(writer, sheet_name='corr_matrix_without_CP')
    
    df_corr = df_corr.where(np.triu(np.ones(df_corr.shape), k=1).astype(np.bool_))
    df_corr = df_corr.unstack().reset_index()
    df_corr.columns = ['產業1', '產業2', '相關係數']
    df_corr = df_corr.sort_values(by=['相關係數'], ascending=False)
    df_corr = df_corr.reset_index(drop=True)
    df_corr = df_corr.iloc[:20, :]
    df_corr.to_excel(writer, sheet_name='corr_top20_without_CP')

    return None

def get_purchase_matrix_with_condition(df, writer):
    df = df.loc[:, ['客戶ID', '刷卡日期', '刷卡產品產業分類']]
    df['count'] = df.groupby(['客戶ID', '刷卡日期'])['刷卡產品產業分類'].transform('count')
    df = df[df['count'] > 1]
    df = df.sort_values(by=['客戶ID', '刷卡日期'])
    df['下一筆刷卡產品產業分類'] = df.groupby(['客戶ID','刷卡日期'])['刷卡產品產業分類'].shift(-1)
    df = df.dropna()
    df_pivot = pd.pivot_table(df, index=['刷卡產品產業分類'], columns=['下一筆刷卡產品產業分類'], values=['count'], aggfunc='sum', fill_value=0)
    total = df_pivot.sum(axis=1).sum()
    df_pivot = df_pivot.div(total)
    df_pivot.to_excel(writer, sheet_name='pivot_table_with_CP')

    df_pivot = df_pivot.unstack().reset_index()
    df_pivot = df_pivot.drop(df_pivot.columns[0], axis=1)
    df_pivot.columns = ['產業1', '產業2', '相關係數']
    df_pivot = df_pivot.sort_values(by=['相關係數'], ascending=False)
    df_pivot = df_pivot.reset_index(drop=True)
    df_pivot = df_pivot.iloc[:20, :]
    df_pivot.to_excel(writer, sheet_name='corr_top20_with_CP')

def main():
    df = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=2)
    with pd.ExcelWriter('output/Basket_Analysis_作業2_蔡佳芸_M11108040.xlsx') as writer:
        get_purchase_matrix_without_condition(df, writer)
        get_purchase_matrix_with_condition(df, writer)

    



if __name__ == '__main__':
    main()