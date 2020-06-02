# import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


# set title for the dashboard
st.title('Sentiment Analysis of Tweets about US Airlines')
# set title for the dashboard sidebar
st.sidebar.title('Sentiment Analysis of Tweets about US Airlines')
# add markdown text under the dashboard title
st.markdown('This application is a Streamlit dashboard to analyze the sentiment\
 of Tweets 🐦')
# add markdown text under the dashboard sidebar title
st.sidebar.markdown('This application is a Streamlit dashboard to analyze the\
 sentiment of Tweets 🐦')

# define the dataset location
DATA_URL = os.path.join(os.getcwd(), 'tweets.csv')

# use streamlit cache decorator to upload only the data that have been changed
@st.cache(persist=True)
# function to load data
def load_data():
    # load dataset
    data = pd.read_csv(DATA_URL)
    # convert time column into datetime format
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data


data = load_data()  # load data

# add subheader to the sidebar
st.sidebar.subheader('Show random tweet')
# add radio buttoin to the sidebar to choose between tweets
random_tweet = (st.sidebar
                .radio('Sentiment', ('positive', 'neutral', 'negative')))
# show the tweet based on the radio button selection
# samle function is used here to get random tweet for the selected sentiment
# category
st.sidebar.markdown(data.query('airline_sentiment == @random_tweet')[['text']]
                    .sample(n=1).iat[0, 0])
# set title for the selection box
st.sidebar.markdown('### Number of tweets by sentiment')
# define section box; key is used to define selection by default
select = st.sidebar.selectbox('Visualization type',
                              ['Histogram', 'Pie chart'], key='1')
# count unique tweets by sentiment category
sentiment_count = data['airline_sentiment'].value_counts()
# build dataframe for passing to the plot
sentiment_count = pd.DataFrame({'Sentiment': sentiment_count.index,
                                'Tweets': sentiment_count.values})
# allow plot hiding
if not st.sidebar.checkbox('Hide', True):
    # add title to the chart
    st.markdown('### Number of tweets by sentiment')
    if select == 'Histogram':
        # plot histogram with plotly
        fig = px.bar(sentiment_count, x='Sentiment', y='Tweets',
                     color='Tweets', height=500)
        st.plotly_chart(fig)
    else:
        # plot pie chart with plotly
        fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
        st.plotly_chart(fig)

# add title fot the sidebar slider/number input widget
st.sidebar.subheader('When and where are users tweeting from?')
# add slider
hour = st.sidebar.slider('Hour of day', 0, 23)
# or add nuber input widget
# hour = st.sidebar.numbner_input('Hour of day', min_values=1, max_value=24)

# store modified data based on user selection
modified_data = data[data['tweet_created'].dt.hour == hour]
# set checkbox to hide visualization
if not st.sidebar.checkbox('Close', True, key='1'):
    # set title
    st.markdown('### Tweets location based on the time of day')
    # show hours range selected
    st.markdown('{} tweets between {}:00 and {}:00'.format(
                len(modified_data), hour, (hour+1) % 24))
    # show tweets on the map
    st.map(modified_data)
    # make checkbos to show raw data - unselected by default
    if st.sidebar.checkbox('Show raw data', False):
        # show table whith raw data
        st.write(modified_data)

# make a multiselection box for user to choose airlines
st.sidebar.subheader('Breakdown airlines tweets by sentiment')
choice = st.sidebar.multiselect('Pick airlines',
                                ('US Airways', 'United', 'American',
                                 'Southwest', 'Delta', 'Virgin America'),
                                key='0')
# plot tweets counts for selected airlines using plotly histogram chart
if len(choice) > 0:
    # get data based on selection
    choice_data = data[data.airline.isin(choice)]
    fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment',
                              histfunc='count', color='airline_sentiment',
                              facet_col='airline_sentiment',
                              labels={'airline_sentiment:tweets'},
                              height=600, width=800)
    st.plotly_chart(fig_choice)

# add wordcloud for tweets
st.sidebar.header('Word Cloud')
word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?',
                                  ('positive', 'neutral', 'negative'))

if not st.sidebar.checkbox('Close', True, key='3'):
    st.header('Word clouds for {} sentiment'.format(word_sentiment))
    # get dataset based on uesr selection
    df = data[data['airline_sentiment'] == word_sentiment]
    # join all words for selected tweets
    words = ' '.join(df['text'])
    # prodess tweet text to get gid of unwanted words or simbols
    process_words = ' '.join([word for word in words.split() if 'http' not in
                              word and not word.startswith('@')
                              and word != 'RT'])
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white',
                          height=640, width=800).generate(process_words)
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot()
