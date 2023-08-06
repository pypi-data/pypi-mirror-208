import numpy as np
import pandas as pd
import re
import emoji

# fname = ".\selected_content.csv"
def preprocess(fname):
    df = pd.read_csv(fname)
    column_list = ['作者', '日期', '内容']
    df = df[column_list]
    df = df.dropna(subset=['作者', '内容'])
    df = df.drop_duplicates(keep='first', subset=['作者', '内容'])

    # 除emoji
    def filter_emoji(text):
        # 过滤表情
        return emoji.replace_emoji(text, replace='')

    # 除@开头
    def filter_at(text):
        return re.sub(r'@[A-Za-z]', '', text)

    # 除换行符
    def filter_strip(text):
        return text.strip()

    # 除特殊符号
    def filter_signal(text):
        return re.sub(r"[(.*?$■∎…)]+", '', text)

    # 除url
    def filter_urls(text):
        return re.sub(r'https://[a-zA-Z0-9.?/_&=:]*', '', text)

    def filter_url(text):
        return re.sub(r'http://[a-zA-Z0-9.?/_&=:]*', '', text)

    # 日期格式转换
    df['日期'] = pd.to_datetime(df['日期'])

    df['内容'] = df['内容'].map(filter_emoji)
    df['内容'] = df['内容'].map(filter_at)
    df['内容'] = df['内容'].map(filter_strip)
    df['内容'] = df['内容'].map(filter_signal)
    df['内容'] = df['内容'].map(filter_url)
    df['内容'] = df['内容'].map(filter_urls)

    df['内容'].replace('', np.nan, inplace=True)
    df = df.dropna()
    df = df.drop_duplicates(subset=['作者', '内容'], keep='first', inplace=False)
    df.to_excel('result.xlsx', index=False)
    print(df)
