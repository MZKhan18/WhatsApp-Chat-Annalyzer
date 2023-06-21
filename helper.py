import pandas as pd
from urlextract import URLExtract
from wordcloud import  WordCloud
from collections import Counter
import emoji
def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]

    #1 fetch total message
    num_message = df.shape[0]

    #2 fetch abuses
    f = open("abuses.txt", 'r')
    data = f.read()

    ab = []
    word = ""

    for line in data:
        line = line
        word = word + line
        if line == '\n':
            ab.append(word)
            word = ""

    abuses = []

    for message in df['message']:
        for word in message.lower().split():
            if ab.count(word + " \n") > 0:
                abuses.append(word)

    num_abuse = len(abuses)
    abuse = pd.DataFrame({'abuse': abuses})

    #3 fetch number of media shares
    num_media = df[df['message']=='<Media omitted>\n'].count()[0]

    #4 fetch links
    extractor = URLExtract()
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))
    num_links = len(links)

    return num_message, num_abuse, num_media, num_links

def mostBusyUser(df):
    x = df['user'].value_counts().head()
    df =round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns = {'index':'name','user':'percent'})
    return x, df

def create_wordCloud(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]

    temp = df[df['user'] != 'grpup_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    f = open('hinglish_stopwords.txt', 'r')
    stop_words = f.read()

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width = 300, height= 300, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc

def most_common_words(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]
    temp = df[df['user'] != 'grpup_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    f = open('hinglish_stopwords.txt', 'r')
    stop_words = f.read()
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    most_common_df = pd.DataFrame(Counter(words).most_common(20))

    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]

    emojis = []
    for message in df['message']:
        for c in message.split():
            if c in emoji.EMOJI_DATA:
                emojis.extend(c)
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap