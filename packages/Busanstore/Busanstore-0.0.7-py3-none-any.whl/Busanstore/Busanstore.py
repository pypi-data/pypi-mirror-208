import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import matplotlib.patches as mpatches
import pkg_resources

data_path = pkg_resources.resource_filename('Busanstore', 'data/busan.csv')

font_path = pkg_resources.resource_filename('Busanstore', 'data/NanumBarunGothicLight.ttf')
fontprop = fm.FontProperties(fname=font_path, size=10)


df = pd.read_csv(data_path,low_memory=False)
df_sorted_by_values = df.sort_values(by='시군구명')
df_sorted_by_values = df_sorted_by_values.sort_values(by='행정동명')
df_s = df_sorted_by_values[['시군구명','행정동명']]
df_s = df_s[['시군구명','행정동명']]
df_s = df_s.groupby(['시군구명','행정동명'])
df_count = df_s['행정동명'].value_counts()

df_count = df_count.reset_index()
df_count.columns = ['시군구명','행정동명', 'count']
df_count = pd.DataFrame(df_count)

gu = list(sorted(set(df_count['시군구명'])))
dong = list(sorted(set(df_count['행정동명'])))
df_count = df_count.sort_values(by='count', ascending=True)


def gu_list():
    return gu

def dong_list():
    return dong

def dong_dataframe(select):
    df_gu = df_count[df_count['행정동명'] == select]
    df_gu = pd.DataFrame(df_gu)
    print(df_gu)

def gu_dataframe(select):
    df_select = df_count[df_count['시군구명'] == select]
    df_select = pd.DataFrame(df_select)
    print(df_select)

def graph(select):
    df_gu = df_count[df_count['시군구명'] == select]
    fig, ax = plt.subplots(figsize=(12, 8)) 
    bars = df_gu.plot(kind='bar',legend=False,ax=ax)  
    ax.set_ylabel("Count",fontproperties=fontprop)   
    ax.set_title(select,fontproperties=fontprop,size=20)  
    for bar in bars.patches:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.01, yval, ha='center', va='bottom') 
    ax.set_xticklabels(df_gu['행정동명'], rotation=0,fontproperties=fontprop)
    plt.show()
