import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import preprocessor
import helper

st.title("Chat Insights 🔍💬")
st.set_page_config(page_title="Chat Insights", layout="wide")

# ================= SIDEBAR =================
st.sidebar.title("Chat Insights")
uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)")

if uploaded_file is not None:
    try:
        data = uploaded_file.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        data = uploaded_file.getvalue().decode("latin-1")

    df = preprocessor.preprocess(data)

    # ================= USER SELECTION =================
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, 'Overall')

    selected_user = st.sidebar.selectbox("Select User", user_list)

    if st.sidebar.button("Show Analysis"):
        st.title("📊 WhatsApp Chat Analysis Dashboard")

        # ==================================================
        # 1️⃣ OVERVIEW METRICS
        # ==================================================
        num_msg, num_abuse, num_media, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", num_msg)
        col2.metric("Abusive Words", num_abuse)
        col3.metric("Media Shared", num_media)
        col4.metric("Links Shared", num_links)

        st.divider()

        # ==================================================
        # 2️⃣ TIMELINES
        # ==================================================
        st.header("📅 Timeline Analysis")

        monthly = helper.monthly_timeline(selected_user, df)
        daily = helper.daily_timeline(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Monthly Timeline")
            fig, ax = plt.subplots()
            ax.plot(monthly['time'], monthly['message'], color='green')
            plt.xticks(rotation=90)
            st.pyplot(fig)

        with col2:
            st.subheader("Daily Timeline")
            fig, ax = plt.subplots()
            ax.plot(daily['only_date'], daily['message'], color='green')
            plt.xticks(rotation=90)
            st.pyplot(fig)

        st.divider()

        # ==================================================
        # 3️⃣ ACTIVITY MAPS
        # ==================================================
        st.header("⏰ Activity Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Active Days")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(busy_day.index, busy_day.values, color='green')
            st.pyplot(fig)

        with col2:
            st.subheader("Most Active Months")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(busy_month.index, busy_month.values, color='green')
            st.pyplot(fig)

        st.subheader("Daily Activity Heatmap")
        heatmap_df = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(heatmap_df, ax=ax)
        st.pyplot(fig)

        st.divider()

        # ==================================================
        # 4️⃣ MOST BUSY USERS
        # ==================================================
        if selected_user == 'Overall':
            st.header("👥 Most Busy Users")

            x, percent_df = helper.mostBusyUser(df)
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='green')
                plt.xticks(rotation=90)
                st.pyplot(fig)

            with col2:
                st.dataframe(percent_df)

            st.divider()

        # ==================================================
        # 5️⃣ WORD CLOUD & COMMON WORDS
        # ==================================================
        st.header("📝 Text Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Word Cloud")
            wc = helper.create_wordCloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig)

        with col2:
            st.subheader("Most Common Words")
            common_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(common_df['word'], common_df['count'], color='green')
            st.pyplot(fig)

        st.divider()

        # ==================================================
        # 6️⃣ EMOJI ANALYSIS
        # ==================================================
        st.header("😊 Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)

            with col2:
                top = emoji_df.head(6)
                fig, ax = plt.subplots()
                ax.pie(
                    top['count'],
                    labels=top['emoji'],
                    autopct="%0.2f%%"
                )
                st.pyplot(fig)
        else:
            st.info("No emojis found in this chat.")

        st.divider()

        # ==================================================
        # 7️⃣ ADVANCED INSIGHTS (NEW)
        # ==================================================
        st.header("🧠 Advanced Insights")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Avg Response Time (sec)",
                helper.average_response_time(df)
            )

        with col2:
            st.metric(
                "One-word Replies (%)",
                helper.one_word_reply_percentage(selected_user, df)
            )

        with col3:
            st.metric(
                "Chat Balance (Gini)",
                helper.chat_balance(df)
            )

        q, e = helper.question_exclamation_ratio(selected_user, df)
        st.subheader("Questions vs Exclamations")
        st.write(f"❓ Questions: {q}  ❗ Exclamations: {e}")

        st.subheader("Top Shared Domains")
        domain_df = helper.domain_analysis(df)
        if not domain_df.empty:
            st.dataframe(domain_df.head(10))
        else:
            st.info("No links shared in this chat.")


        st.header("⏰ Temporal Patterns")
        col1, col2 = st.columns(2)

        col1.subheader("Night Owl Users")
        col1.dataframe(helper.night_owl_users(df))

        col2.subheader("Weekend vs Weekday")
        col2.dataframe(helper.weekend_vs_weekday(df))

        st.divider()

        st.subheader("⏳ Long Inactivity Periods")


        inactive_df = helper.inactivity_periods(df, hours=24)

        if inactive_df.empty:
            st.info(f"No inactivity period longer than 24 hours found.")
        else:
            st.write(f"Periods where the chat was inactive for more than 24 hours:")
            st.dataframe(inactive_df)

