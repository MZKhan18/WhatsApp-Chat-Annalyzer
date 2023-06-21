import streamlit as st
import preprocessor
import helper
import seaborn as sns
import matplotlib.pyplot as plt

st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)


    #fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,'Overall')

    selected_user = st.sidebar.selectbox("Show Analysis With Respect To User",user_list)

    if st.sidebar.button("Show Analysis"):
        st.title("Analysis of chats")
        num_message, num_abuse, num_media, num_links = helper.fetch_stats(selected_user,df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_message)

        with col2:
            st.header("Total Abuses")
            st.title(num_abuse)

        with col3:
            st.header("Media Shared")
            st.title(num_media)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        #Timeline analysis
        timeline = helper.monthly_timeline(selected_user,df)
        daily_timeline = helper.daily_timeline(selected_user,df)
        col1, col2 = st.columns(2)

        #monthly timeline
        with col1:
            st.header("Monthly Timeline")
            fig,ax= plt.subplots()
            ax.plot(timeline['time'], timeline['message'],color = 'green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        #daily timeline
        with col2:
            st.header("Daily Timeline")
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        #acivity map
        col1, col2 = st.columns(2)

        with col1:
            #most busy day of month
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.barh(busy_day.index,busy_day.values,color ='green')
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user,df)
            fig, ax = plt.subplots()
            ax.barh(busy_month.index, busy_month.values, color = 'green')
            st.pyplot(fig)


        user_heatmap = helper.activity_heatmap(selected_user,df)
        st.header("Daily Activity Map")
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        #finding the busiest level in the group
        if selected_user == 'Overall':

            x , newDf= helper.mostBusyUser(df)

            fig,axis = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                st.header("Most Busy Users")
                axis.bar(x.index, x.values, color = 'green')
                plt.xticks(rotation = 'vertical')
                st.pyplot(fig)
            with col2:
                st.header("Message Percent")
                st.dataframe(newDf)

        #forming wordcloud
        col1, col2 = st.columns(2)

        df_wc = helper.create_wordCloud(selected_user,df)

        with col1:

            st.header("Word Cloud")
            fig, axis = plt.subplots()
            axis.imshow(df_wc)
            st.pyplot(fig)

        most_common_df = helper.most_common_words(selected_user,df)

        with col2:

            st.header("Most Common Words")
            # st.dataframe(most_common_df)
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0],most_common_df[1],color = 'green')
            st.pyplot(fig)

        #emoji analysys
        emoji_df = helper.emoji_helper(selected_user,df)
        st.header("Emoji Analysis")
        col1,col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1][0:6],labels = emoji_df[0][0:6], autopct = "%0.2f")
            st.pyplot(fig)
