import pandas as pd

def EDA(df, name):
    print("quick peek", df.head(5), '\n')
    print("data types",df.dtypes, '\n')
    print(df.describe(), '\n')
    print(df.describe(include=['object']), '\n')

    object_cols = df.select_dtypes(include=['object']).columns.tolist()

    df_list = [
        pd.DataFrame({
            'table_name': name,
            'col_name': col,
            'item': df[col].value_counts().index,
            'count': df[col].value_counts().values,
        })for col in object_cols]

    res_df = pd.concat(df_list, axis=0, ignore_index=True)

    return res_df

def get_group(df_pd, df_cd):
    df_pd = df_pd.loc[:, ['客戶ID', '性別']]
    df_cd = df_cd.loc[:, ['客戶ID', '卡等']]
    df_cd = df_cd.drop_duplicates(subset=['客戶ID'], keep='first')
    df_group = pd.merge(df_pd, df_cd, on='客戶ID', how='inner')
    df_group = df_group.sort_values(by = ['客戶ID'], ascending=True)
    df_group = df_group.reset_index(drop=True)
    df_group['分群'] = df_group.groupby(['性別', '卡等']).ngroup()

    return df_group    

def get_transaction_record(df):
    df = df.loc[:, ['客戶ID', '刷卡日期', '刷卡金額']]
    df = df.sort_values(by=['客戶ID', '刷卡日期'], ascending=[True, True])    

    return df

def get_transaction_and_group(df_group, df_clean_transaction):

    df_group = df_group.loc[:, ['客戶ID', '分群']]
    df_transaction_and_group = pd.merge(df_clean_transaction, df_group,  on='客戶ID', how='inner')

    return df_transaction_and_group

def get_person_transaction_statistics(df):
    df = df.groupby(['客戶ID']).agg({'刷卡金額': ['count', 'mean', 'var']})
    df.columns = ['刷卡次數', '刷卡金額平均數', '刷卡金額變異數']
    df = df.round(0)
    df = df.reset_index(drop=False)    
    
    return df

def get_group_transaction_statistics(df):
    df = df.groupby(['分群']).agg({'刷卡金額': ['mean', 'var']})
    df.columns = ['分群平均數', '分群變異數']
    df = df.round(0)
    df = df.reset_index(drop=False)
    return df

def CRI(df_group, person_ts, group_ts):
    df_group = df_group.loc[:, ['客戶ID', '分群']]
    df = pd.merge(df_group, person_ts, on='客戶ID', how='inner')
    df = pd.merge(df, group_ts, on='分群', how='inner')

    tem = df['刷卡金額變異數'] / df['刷卡次數']

    df['W1'] = df['分群變異數'] / (df['分群變異數'] + tem)
    df['W2'] = tem / (df['分群變異數'] + tem)
    df['HB'] = df['W1'] * df['刷卡金額平均數'] + df['W2'] * df['分群平均數']
    df['CRI'] = (df['刷卡金額平均數'] - df['HB'])/(df['刷卡金額平均數'] - df['分群平均數'])*100

    return df

    
    
def main():
    df_transaction = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=2)
    df_person_detail = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=0)
    df_card_detail = pd.read_excel("raw/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=1)

    df_person_detail_obj_count = EDA(df_person_detail, "df_person_detail")
    df_card_detail_obj_count = EDA(df_card_detail, "df_card_detail")

    EDA_df = pd.concat([df_person_detail_obj_count, df_card_detail_obj_count], axis=0, ignore_index=True)    

    df_group = get_group(df_person_detail, df_card_detail)
    df_clean_transaction = get_transaction_record(df_transaction)

    clean_transaction_and_group = get_transaction_and_group(df_group, df_clean_transaction)

    person_transaction_statistics = get_person_transaction_statistics(clean_transaction_and_group)

    group_transaction_statistics = get_group_transaction_statistics(clean_transaction_and_group)

    df_cai = CRI(df_group, 
        person_transaction_statistics, 
        group_transaction_statistics, 
        )

    with pd.ExcelWriter('output/EDA.xlsx') as writer:
        
        EDA_df.to_excel(writer, sheet_name='EDA', index=False)

        #step0_1
        df_group.to_excel(writer, sheet_name='step0_1分群', index=False)
            
        #step0_2
        df_clean_transaction.to_excel(writer, sheet_name='step0_2交易紀錄', index=False)
        clean_transaction_and_group.to_excel(writer, sheet_name='step1交易紀錄與分群', index=False)
        person_transaction_statistics.to_excel(writer, sheet_name='step2個人交易統計值', index=False)
        group_transaction_statistics.to_excel(writer, sheet_name='step3群體交易統計值', index=False)
        df_cai.to_excel(writer, sheet_name='step4CRI', index=False)

if __name__ == '__main__':
    main()