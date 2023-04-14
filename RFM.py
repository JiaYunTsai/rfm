import pandas as pd


def get_RFM_base_dict(df):
    customer_id_list = df['客戶ID'].unique().tolist()
    customer_id_list.sort()

    base_date = df['刷卡日期'].max() + pd.Timedelta(days=1)

    last_date_list = df.groupby('客戶ID')['刷卡日期'].max().tolist()

    R = [(base_date - last_date).days for last_date in last_date_list]
    F = df.groupby('客戶ID')['客戶ID'].count().tolist()
    M = df.groupby('客戶ID')['刷卡金額'].sum().tolist()

    RFM_base_dict = {
        "customer_id" : customer_id_list,
        "R" : R,
        "F" : F,
        "M" : M,
        "last_date" : last_date_list
    }

    return RFM_base_dict

def get_rfm_score_Bob_stone(RFM_base_dict):
    R_score = []
    for r in RFM_base_dict['R']:
        if r <= 30:
            R_score.append(5)
        elif r <= 60:
            R_score.append(4)
        elif r <= 90:
            R_score.append(3)
        elif r <= 120:
            R_score.append(2)
        else:
            R_score.append(1)

    F_score = [round(M * 4) for M in RFM_base_dict['F']] 
    M_score= [round(M * 0.25) for M in RFM_base_dict['M']]
    RFM_score = [R + F + M for R, F, M in zip(R_score, F_score, M_score)]

    RFM_base_dict['R_score_Bob_stone'] = R_score
    RFM_base_dict['F_score_Bob_stone'] = F_score
    RFM_base_dict['M_score_Bob_stone'] = M_score
    RFM_base_dict['RFM_score_Bob_stone'] = RFM_score

    RFM_base_dict['rank_Bob_stone'] = pd.Series(RFM_base_dict['RFM_score_Bob_stone']).rank(method='min', ascending=False).astype(int)

    rfm_score_dict_Bob_stone = RFM_base_dict
    return rfm_score_dict_Bob_stone    

def get_rfm_score_5split(rfm_dict):
    rfm_dict['R_score_5split'] = pd.qcut(rfm_dict['R'], 5, labels=[5, 4, 3, 2, 1])
    rfm_dict['F_score_5split'] = pd.qcut(rfm_dict['F'], 5, labels=[1, 2, 3, 4, 5])
    rfm_dict['M_score_5split'] = pd.qcut(rfm_dict['M'], 5, labels=[1, 2, 3, 4, 5])

    rfm_dict['RFM_score_5split'] = [R + F + M for R, F, M in zip(rfm_dict['R_score_5split'], 
                                                                rfm_dict['F_score_5split'],
                                                                rfm_dict['M_score_5split'])]
    rfm_dict['rank_5split'] = pd.Series(rfm_dict['RFM_score_5split']).rank(method='min', ascending=False).astype(int)


    return rfm_dict

def get_rfm_score_self_define_Bob_stone(rfm_dict):
    R_score = []
    for r in rfm_dict['R']:
        if r <= 100:
            R_score.append(5)
        elif r <= 200:
            R_score.append(4)
        elif r <= 300:
            R_score.append(3)
        elif r <= 400:
            R_score.append(2)
        else:
            R_score.append(1)

    F_score = [round(M * 2) for M in rfm_dict['F']] 
    M_score= [round(M * 0.5) for M in rfm_dict['M']]
    RFM_score = [R + F + M for R, F, M in zip(R_score, F_score, M_score)]

    rfm_dict['R_score_self_define'] = R_score
    rfm_dict['F_score_self_define'] = F_score
    rfm_dict['M_score_self_define'] = M_score
    rfm_dict['RFM_score_self_define'] = RFM_score

    rfm_dict['rank_self_define'] = pd.Series(rfm_dict['RFM_score_self_define']).rank(method='min', ascending=False).astype(int)

    rfm_score_dict_self_define = rfm_dict
    return rfm_score_dict_self_define   

def main():
    df = pd.read_excel("大數據行銷實作練習_信用卡資料.xlsx", sheet_name=2)
    RFM_base_dict = get_RFM_base_dict(df)
    RFM_score_add_Bob_stone = get_rfm_score_Bob_stone(RFM_base_dict)
    RFM_score_add_5split = get_rfm_score_5split(RFM_score_add_Bob_stone)
    RFM_score_add_self_define = get_rfm_score_self_define_Bob_stone(RFM_score_add_5split)

    rfm_df = pd.DataFrame(RFM_score_add_self_define)
    # print(rfm_df)
    print(rfm_df.shape)
    rfm_df.to_excel("rfm_df.xlsx", index=False)


if __name__ == '__main__':
    main()