import pandas as pd

def get_dataframes_check_report(df):
    print("shape", df.shape)
    df_columns = df.columns.tolist()
    print("df_columns", df_columns)
    print(df.head(10))
    print(df.tail(10))

def CAI(writer, df):
    df = df.loc[:, ['客戶ID', '刷卡日期']]
    df = df.drop_duplicates(subset=['客戶ID', '刷卡日期'], keep='first')
    df = df.reset_index(drop=True)
    df = df.sort_values(by=['客戶ID', '刷卡日期'], ascending=True)

    df['刷卡間隔'] = df.groupby(['客戶ID'])['刷卡日期'].diff().shift(-1).dt.days
    df = df.dropna(subset=['刷卡間隔'])

    df['權重'] = df.groupby(['客戶ID']).cumcount() + 1
    df['刷卡間隔*權重'] = df['刷卡間隔'] * df['權重']

    df_person_CAI = df.groupby(['客戶ID']).agg({'刷卡間隔': 'mean', '權重': 'sum', '刷卡間隔*權重': 'sum'})
    df_person_CAI = df_person_CAI.rename(columns={'刷卡間隔': 'MLE', "權重": '加權加總', '刷卡間隔*權重': '加權值加總'})

    df_person_CAI['WMLE'] = df_person_CAI['加權值加總'] / df_person_CAI['加權加總']
    df_person_CAI['CAI'] = ((df_person_CAI['MLE']-df_person_CAI['WMLE'])/ df_person_CAI['MLE'])*100

    df_person_CAI = df_person_CAI.sort_values(by=['CAI'], ascending=True)

    df_person_CAI.to_excel(writer, sheet_name='CAI')

    return df_person_CAI

def get_active_customer(writer, df):
    df_active = df[df['CAI'] < df['CAI'].quantile(0.2)]
    df_active = df_active.reset_index(drop=True)

    df_active.to_excel(writer,  sheet_name='active_customer')

def get_inactive_customer(writer, df):
    df_inactive = df[df['CAI'] > df['CAI'].quantile(0.8)]
    df_inactive = df_inactive.reset_index(drop=True)

    df_inactive.to_excel(writer, sheet_name='inactive_customer')

def get_normal_customer(writer, df):
    df_nomal = df[df['CAI'] > df['CAI'].quantile(0.2)]
    df_nomal = df_nomal[df_nomal['CAI'] < df_nomal['CAI'].quantile(0.8)]
    df_nomal = df_nomal.reset_index(drop=True)

    df_nomal.to_excel(writer, sheet_name='normal_customer')

def main():
    df = pd.read_excel("input/大數據行銷實作練習_信用卡資料.xlsx", sheet_name=2)

    with pd.ExcelWriter('output/CAI_作業2_蔡佳芸_M11108040.xlsx') as writer:
        df_person_CAI = CAI(writer, df)

        get_active_customer(writer, df_person_CAI)
        get_inactive_customer(writer, df_person_CAI)
        get_normal_customer(writer, df_person_CAI)
    
if __name__ == '__main__':
    main()