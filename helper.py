import pandas as pd
import numpy as np
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import emoji
from urllib.parse import urlparse

# --------------------------------------------------
# BASIC STATS (OLD)
# --------------------------------------------------
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_message = df.shape[0]

    with open("abuses.txt") as f:
        abuse_words = [w.strip() for w in f.readlines()]

    abuses = []
    for msg in df['message']:
        for w in msg.lower().split():
            if w in abuse_words:
                abuses.append(w)

    num_abuse = len(abuses)

    num_media = df[df['message'].str.contains('<Media omitted>', na=False)].shape[0]

    extractor = URLExtract()
    links = []
    for msg in df['message']:
        links.extend(extractor.find_urls(msg))

    return num_message, num_abuse, num_media, len(links)


# --------------------------------------------------
# MOST BUSY USERS (OLD)
# --------------------------------------------------
def mostBusyUser(df):
    x = df['user'].value_counts().head()
    percent_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2)\
        .reset_index()\
        .rename(columns={'index': 'name', 'user': 'percent'})
    return x, percent_df


# --------------------------------------------------
# WORDCLOUD (OLD)
# --------------------------------------------------
def create_wordCloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    with open('hinglish_stopwords.txt') as f:
        stop_words = f.read().split()

    def remove_stop_words(msg):
        return " ".join([w for w in msg.lower().split() if w not in stop_words])

    temp['message'] = temp['message'].apply(remove_stop_words)

    wc = WordCloud(width=400, height=400, background_color='white')
    return wc.generate(temp['message'].str.cat(sep=" "))


# --------------------------------------------------
# MOST COMMON WORDS (OLD)
# --------------------------------------------------
def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('<Media omitted>', na=False)]

    with open('hinglish_stopwords.txt') as f:
        stop_words = f.read().split()

    words = []
    for msg in temp['message']:
        for w in msg.lower().split():
            if w not in stop_words:
                words.append(w)

    return pd.DataFrame(Counter(words).most_common(20),
                        columns=['word', 'count'])


# --------------------------------------------------
# EMOJI ANALYSIS (OLD + FIXED)
# --------------------------------------------------
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for msg in df['message']:
        emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emojis).most_common(),
                        columns=['emoji', 'count'])


# --------------------------------------------------
# TIMELINES (OLD)
# --------------------------------------------------
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month'])['message'] \
                 .count().reset_index()

    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date')['message'].count().reset_index()


# --------------------------------------------------
# ACTIVITY MAPS (OLD)
# --------------------------------------------------
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)


# ==================================================
# 🔥 NEW ADVANCED FEATURES (ADDED, NOT REPLACED)
# ==================================================

def night_owl_users(df):
    night = df[(df['hour'] >= 0) & (df['hour'] <= 5)]
    return night['user'].value_counts().head()


def weekend_vs_weekday(df):
    df['is_weekend'] = df['day_name'].isin(['Saturday', 'Sunday'])
    return df['is_weekend'].value_counts()


def inactivity_periods(df, hours=24):
    df = df.sort_values('date')
    df['gap'] = df['date'].diff().dt.total_seconds() / 3600
    return df[df['gap'] > hours][['date', 'gap']]

def average_response_time(df):
    df = df.sort_values('date')
    times = []

    for i in range(1, len(df)):
        if df.iloc[i]['user'] != df.iloc[i-1]['user']:
            diff = (df.iloc[i]['date'] - df.iloc[i-1]['date']).total_seconds()
            if diff > 0:
                times.append(diff)

    return round(np.mean(times), 2) if times else 0


def one_word_reply_percentage(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    one_word = df[df['message'].apply(lambda x: len(x.split()) == 1)].shape[0]
    return round((one_word / df.shape[0]) * 100, 2) if df.shape[0] else 0


def question_exclamation_ratio(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    q = df['message'].str.endswith('?', na=False).sum()
    e = df['message'].str.endswith('!', na=False).sum()
    return q, e


def chat_balance(df):
    counts = df['user'].value_counts().values
    counts = np.sort(counts)
    n = len(counts)
    idx = np.arange(1, n + 1)
    return round(np.sum((2 * idx - n - 1) * counts) / (n * np.sum(counts)), 3)


def domain_analysis(df):
    extractor = URLExtract()
    domains = []

    for msg in df['message']:
        for url in extractor.find_urls(msg):
            domains.append(urlparse(url).netloc)

    return pd.DataFrame(Counter(domains).most_common(),
                        columns=['domain', 'count'])

def inactivity_periods(df, hours=24):

    df = df.sort_values('date').copy()
    df['gap'] = df['date'].diff().dt.total_seconds() / 3600

    return df[df['gap'] > hours][['date', 'gap']]
