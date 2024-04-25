import re


if __name__=="__main__":
    st = '8,1a8a333f-a0fb-4e8c-9c4d-8d357e439e99,,4.0,ds_8,,0,1,,Институт им Сеченова,"",,{},2147483647,{},2024-03-04 16:01:14.833861+03,,,,{},0,1,{},{},[],,2024-03-04 16:01:14.833861+03,2024-03-04 16:01:14.833861+03'

    st_list = st.split(',')

    print(st_list, '\n')

    new_st_list = []

    for ss in st_list:
        if ss.isdigit():
            new_st_list.append(ss)
        elif ss == '""':
            new_st_list.append('\'\'')
        elif ss == '':
            new_st_list.append('NULL')
        elif ss == '{}' or ss == '[]':
            new_st_list.append(f'\'{ss}\'::json')
        else:
            new_st_list.append(f'\'{ss}\'')

    out_st = "INSERT INTO adm.datasets VALUES(" + ','.join(new_st_list) + ");"
    print(out_st)