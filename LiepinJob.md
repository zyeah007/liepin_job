

```python
# 开始尝试画图
import pyecharts
import os
import time
import json
from pandas import DataFrame
import pandas as pd
import re
# from pyecharts.render import make_snapshot
from pyecharts.charts import Bar,Pie,Geo,Scatter,Page,WordCloud
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.globals import SymbolType
from pyecharts.globals import ChartType
# from snapshot_selenium import snapshot
from pyecharts.commons.utils import JsCode
import jieba.posseg as pseg
import jieba
```


```python
# 读取数据
json_file='./python_job_info.json'
with open(json_file,'r') as f:
    json_data=json.load(f)
    df=DataFrame(json_data['data'])

# 去重
print('共有%d条数据'%len(df))
df.drop_duplicates(subset=['company','title'],inplace=True)
df.drop_duplicates(subset=['company','description'],inplace=True)
print('去重后，还剩%d条数据'%len(df))

# 剔除缺失值
df.dropna(axis=0,inplace=True)
print('去除缺失值后，还剩%d条数据'%len(df))

# 剔除salary字段不合规记录
df=df[df['salary']!='面议']
print(len(df))

# 处理salary字段成数值型
df['months_paid']=df['salary'].map(lambda x:x[-3:-1])

match_func=lambda x: re.search(string=x,pattern=r'.*k').group(0)

df2=df.copy()
df2['pay_range']=df2['salary'].map(match_func)

df2['month_min']=df2['pay_range'].map(lambda x:x.split('-')[0].strip('k'))
df2['month_max']=df2['pay_range'].map(lambda x:x.split('-')[-1].strip('k'))

# 转换salry相关字段数值类型为数值型
df2[['months_paid','month_min','month_max']]=df2[['months_paid','month_min','month_max']].astype(float)

df2['month_pay']=(df2['month_max']+df2['month_min'])/2
df2['year_pay']=df2['month_pay']*df2['months_paid']
df2['month_pay']=df2['year_pay']/12

# 处理city字段分为城市名及城区名
df2['city_name']=df2['city'].map(lambda x:x.split('-')[0])
df2['city_district']=df2['city'].map(lambda x:x.split('-')[-1])

# 处理industry字段，只提取第一个行业
df2['industry']=df2['industry'].map(lambda x:x[0].split('/')[0])

# 处理年龄要求字段
def get_age(age_range:str):
    if len(age_range.split('-'))>1:
        max_age=age_range.split('-')[-1]
        max_age=max_age.replace('岁',"")
        return max_age
    else:
        return age_range


# 处理经验要求字段
# 转换为数字，并且按升序排列
def get_experience(exp:str):
    reg=r'\d+'
    match=re.search(reg,exp)
    if match:
        return match.group(0)
    else:
        return exp

# 处理学历要求字段
education_dict={
        '本科及以上':'本科',
        '统招本科':'本科',
        '大专及以上':'大专',
        '硕士及以上':'硕士',
        '中专/中技及以上':'中专'
    }
def normal_education_level(level_str):
    if level_str in education_dict.keys():
        return education_dict[level_str]
    else:
        return level_str

df2['age_required']=df2['age'].apply(get_age)
df2['experience_required']=df2['experience'].apply(get_experience)
df2['education_required']=df2['education'].apply(normal_education_level)

# 剔除离群值（超过上四分位数的）
q1=df2['year_pay'].quantile(q=0.05)
q3=df2['year_pay'].quantile(q=0.95)
df2=df2[df2['year_pay']<=q3]
df2=df2[df2['year_pay']>q1]

# 剔除职位数低于5的城市
city_counts=df2['city_name'].value_counts()
df2['job_count']=df2['city_name'].map(lambda x:city_counts.loc[x])
df2=df2[df2['job_count']>5]

# 只保留必要的字段
df3=df2.copy(deep=True)
df3.drop(['city','salary','pay_range','month_min','month_max','months_paid','age','experience','education'],axis=1,inplace=True)
print('剔除离群值后还剩%d条数据'%len(df3))
```

```python
# 获得各年龄段职位数量
age_distribution=df3['age_required'].value_counts()
age_num=sorted(list(age_distribution.index))
age_counts=[int(age_distribution[i]) for i in age_num]

# 年龄分布柱状图
title='PYTHON'
subtitle='年龄分布要求'
age_bar=(
    Bar()
    .add_xaxis(age_num[:-1])  # 剔除“年龄不限”类别
    .add_yaxis('',age_counts[:-1])
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_='max',name='最大值'),
                opts.MarkPointItem(type_='min',name='最小值')
            ]
        ),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title=title,subtitle=subtitle,pos_left='center'),
        xaxis_opts=opts.AxisOpts(name='年龄段',
                                 position='center',
                                 axislabel_opts=opts.LabelOpts(formatter="{value}岁")
                            ),
        yaxis_opts=opts.AxisOpts(name='职位数',),
    )
#     .render(title + '_' + subtitle + '.html')
)
```


```python
# 获得各经验段职位数量
experience_dist=df3['experience_required'].value_counts()
exp_num=sorted(list(experience_dist.index))
last_num=exp_num.pop()
exp_num=sorted([int(i) for i in exp_num])
exp_num.append(last_num)
exp_counts=[int(experience_dist[str(i)]) for i in exp_num]

# 经验年限分布图
title='PYTHON'
subtitle='经验要求'
experience_bar=(
    Bar()
    .add_xaxis(exp_num[:-1])  # 剔除“年龄不限”类别
    .add_yaxis('',exp_counts[:-1])
    .set_series_opts(
        label_opts=opts.LabelOpts(position='right'),

    )
    .reversal_axis()
    .set_global_opts(
        title_opts=opts.TitleOpts(title=title,subtitle=subtitle),
        xaxis_opts=opts.AxisOpts(name='职位数'),
        yaxis_opts=opts.AxisOpts(name='经验年限',
                                 name_location='end',
                                 name_rotate=0,
                                 axislabel_opts=opts.LabelOpts(formatter="{value}年")
                                ),
    )
#     .render(title + '_' + subtitle + '.html')
)
```


```python
# 学历分布饼图
education=df3['education_required'].value_counts()
level = ['中专','大专','本科','硕士','博士','学历不限']
edu_counts = [int(education[i]) for i in level]
data_pair=[list(z) for z in zip(level,edu_counts)]
data_pair.sort(key=lambda x:x[1])
title='PYTHON'
subtitle='学历分布'

education_pie=(
    Pie()
    .add(
        series_name='学历要求',
        data_pair=data_pair,
#         rosetype='radius',
#         radius="55%",
        center=["35%","50%"],
        label_opts=opts.LabelOpts(is_show=False,position='center'),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title='PYTHON',
            subtitle='学历分布',
            pos_left='center',
            pos_top=20,
            title_textstyle_opts=opts.TextStyleOpts(color="#fff"),
        ),
        legend_opts=opts.LegendOpts(is_show=False)
    )
    .set_series_opts(
        tooltip_opts=opts.TooltipOpts(
            trigger='item',formatter="{a}<br/>{b}: {c}({d}%)"
        ),
        label_opts=opts.LabelOpts(formatter="{b}:{d}%")
    )
#     .render(title + '_' + subtitle + '.html')
)
# pie.render_notebook()
```


```python
# 城市平均月薪
city_group=df3.groupby(['city_name'])
city_pay=city_group.mean()
city_pay.sort_values(by='year_pay',ascending=False,inplace=True)

city_name=list(city_pay.index)
city_name=[str(i) for i in city_name]
pay=list(city_pay['month_pay'].values)
pay=[round(float(i),2) for i in pay]

city_coordinates_file=os.path.join(os.getcwd(),'city_coordinates.json')
with open(city_coordinates_file,'r') as f:
    json_data=json.load(f)


title='PYTHON'
subtitle='各城市平均月薪'
city_coordinates_file=os.path.join(os.getcwd(),'city_coordinates.json')
with open(city_coordinates_file,'r') as f:
    json_data=json.load(f)
coord_bj=json_data['北京']  # 北京经纬度
coord_cq=json_data['重庆']  # 重庆经纬度
coord_cd=json_data['成都']
coord_sh=json_data['上海']
pay_cq=round(float(city_pay.loc['重庆','month_pay']),2)
pay_bj=round(float(city_pay.loc['北京','month_pay']),2)
pay_cd=round(float(city_pay.loc['成都','month_pay']),2)
pay_sh=round(float(city_pay.loc['上海','month_pay']),2)

city_geo = (
    Geo()
    .add_schema(maptype="china")
    .add(
        "",
        [list(z) for z in zip(city_name,pay)],
        type_=ChartType.EFFECT_SCATTER
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False,),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(name='重庆:'+str(pay_cq),coord=coord_cq),
                opts.MarkPointItem(name='北京:'+str(pay_bj),coord=coord_bj),
                opts.MarkPointItem(name='上海:'+str(pay_sh),coord=coord_sh),
                opts.MarkPointItem(name='成都:'+str(pay_cd),coord=coord_cd),
            ],
            symbol_size=20,
            label_opts=opts.LabelOpts(is_show=True,formatter="{b}")
        )
    )
    .set_global_opts(
        visualmap_opts=opts.VisualMapOpts(is_piecewise=True,max_=50,is_show=True), 
        title_opts=opts.TitleOpts(title="PYTHON职位分析",subtitle='平均月薪(k)')
    )
#     .render(title + '_' + subtitle + '.html')
)

```


```python
def get_title_std(title):
    jobTitleList=['开发','算法','测试','数据','运维','量化','软件','后端','爬虫']
    for std_title in jobTitleList:
        if std_title in title:
            result=std_title
            break
        else:
            result='其他'
    return result

df3['std_job_title']=df3['title'].apply(get_title_std)

title_group=df3.groupby(by=['std_job_title'])

num_agg={'month_pay':['max','min','mean','count']}
title_month_pay=title_group.agg(num_agg)
title_month_pay=title_month_pay['month_pay']

title_month_pay.sort_values(by=['count'],ascending=True,inplace=True)

titles=list(title_month_pay.index)
month_pay=list(title_month_pay['mean'].values)
month_pay=[round(float(i),2) for i in month_pay]
title_count=list(title_month_pay['count'].values)
title_count=[int(c) for c in title_count]
```


```python
# 各职位平均月薪
title='PYTHON'
subtitle='各职位平均月薪'

title_scatter = (
    Scatter()
    .add_xaxis(title_count)
    .add_yaxis("",
               [list(z) for z in zip(month_pay,titles)],
        )
    .set_global_opts(
        title_opts=opts.TitleOpts(title=title,subtitle=subtitle,pos_left='center'),
        visualmap_opts=opts.VisualMapOpts(type_="size",dimension=1,max_=40,min_=10),
        xaxis_opts=opts.AxisOpts(
            type_='value',name='职位数量'
        ),
        yaxis_opts=opts.AxisOpts(
            type_='value',name='平均月薪(k)',
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
            min_=12
        )
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=True,font_size=10,position='inside',
            formatter=JsCode(
                "function(params){return params.value[2];}"
            ),
        ),
        tooltip_opts=opts.TooltipOpts()
    )
#     .render(title + '_' + subtitle + '.html')
)
```


```python
title_analyse='算法'
da_job=df3[df3['std_job_title']==title_analyse]  # 只分析"数据"岗位的职位描述
job_desc=da_job['description'].values
descriptions=''
for d in job_desc:
    descriptions += d

# 将文本中的分词和停用词去掉
def clean_text(text:str,stopwords_file):
    pos_lit=['an','n',]
    with open(stopwords_file,'r',encoding='utf-8') as f:
        stopwords_list=f.readlines()
        stopwords=[i.strip() for i in stopwords_list]
    seg_text=pseg.cut(sentence=descriptions)  # 分词并标注词性
    output=[]
    for w in seg_text:
        if (w.word.strip() not in stopwords) and (w.flag in pos_lit):
            output.append(w.word.strip())
    return output

# text_seg=jieba.lcut(descriptions)
stopwords_file=os.path.join(os.getcwd(),'stopwords.txt')
clean_text=clean_text(descriptions,stopwords_file=stopwords_file)

s=pd.Series(data=clean_text)
word_count=s.value_counts()

key_word=list(word_count.index)
keyword_count=list(word_count.values)
keyword_count=[int(i) for i in keyword_count]

words=[tuple(z) for z in zip(key_word,keyword_count)]

wc = (
    WordCloud()
    .add("", words, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
    .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud-shape-diamond"))
#     .render("wordcloud_diamond.html")
)
```


```python
page = (
    Page()
    .add(
        age_bar,
        experience_bar,
        education_pie,
        city_geo,
        title_scatter,
        wc
    )
)
page.render("page_default_layout.html")
```


