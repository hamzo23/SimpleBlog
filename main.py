#IMPORTS
import streamlit as st
# EDA PKGS
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Database
import sqlite3

#API
import requests

#Files
from os.path import exists
import json

#DB variables
conn = sqlite3.connect('data.db')
c = conn.cursor()

#API link
base_url = "https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=b8268e4560784be797d0f0f9bb979148"

#FUNCTIONS
def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT,title TEXT,article TEXT,postdate DATE)')

#Create post
def add_data(author, title, article, postdate):
    c.execute('INSERT INTO blogtable(author,title,article,postdate) VALUES (?,?,?,?)',
              (author, title, article, postdate))
    conn.commit()

#Retrieve all posts for interactive table
def view_all_notes():
    c.execute('SELECT * FROM blogtable')
    data = c.fetchall()
    return data

#Retrieve all posts for display
def view_all_titles():
    c.execute('SELECT DISTINCT title FROM blogtable')
    data = c.fetchall()
    return data

#Retrieve post by title
def get_blog_by_title(title):
    c.execute('SELECT * FROM blogtable WHERE title="{}"'.format(title))
    data = c.fetchall()
    return data

#Retrieve post by author
def get_blog_by_author(author):
    c.execute('SELECT * FROM blogtable WHERE author="{}"'.format(author))
    data = c.fetchall()
    return data

#Remove post
def delete_data(title):
    c.execute('DELETE FROM blogtable WHERE title="{}"'.format(title))
    conn.commit()

#Function to display loading time for 'x' post
def readingTime(mytext):
    total_words = len([token for token in mytext.split(" ")])
    estimatedTime = total_words/200.0
    return estimatedTime

#Update post data
def edit_blog_data(new_author, new_title, new_article, new_post_date, author, title, article, postdate):
    c.execute("UPDATE blogtable SET author =?, title=?, article=?, postdate=? WHERE author=? and title=? and article=? and postdate=? ",(new_author, new_title, new_article, new_post_date, author, title, article, postdate))
    conn.commit()
    data = c.fetchall()
    return data

#Retrieve API data
def get_data(url):
    resp = requests.get(url)
    return resp.json()

#Save API data into JSON file
def save_to_file(data,filename):
    with open (filename, 'w') as write_file:
        json.dump(data,write_file,indent=2)

#Read JSON file
def read_from_file(filename):
    with open(filename,'r') as read_file:
        data = json.load(read_file)
    return data

#LAYOUT TEMPLATES
html_temp = """
<div style="background-color:{};padding:10px;border-radius:10px">
<h1 style="color:{};text-align:center;">Simple Blog </h1>
</div>
"""
title_temp = """
<div style="background-color:#A19E99;padding:10px;border-radius:10px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;" >
<h6>Author:{}</h6>
<br/>
<br/>
<p style="text-align:justify">{}</p>
</div>
"""
article_temp = """
<div style="background-color:#A19E99;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<h6>Author:{}</h6>
<h6>Post Date: {}</h6>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;" >
<br/>
<br/>
<p style="text-align:justify">{}</p>
</div>
"""
head_message_temp = """
<div style="background-color:#A19E99;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author:{}</h6>
<h6>Post Date: {}</h6>
</div>
"""
full_message_temp = """
<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""


def main():
    """A Simple CRUD Blog"""

    #Create Database
    create_table()

    #Add all API articles into DB once
    file_exists = exists("articles.json")
    if file_exists == 0:
        data = get_data(base_url)
        save_to_file(data, "articles.json")
        articlesData = read_from_file("articles.json")
        for i in articlesData["articles"]:
            api_author =  i['author']
            api_title =  i['title']
            api_article =  i['description']
            api_post_date_temp =  i['publishedAt']
            api_post_date = api_post_date_temp[0:10]
            add_data(api_author, api_title, api_article, api_post_date)

    #WEBSITE FORMATTING
    st.markdown(html_temp.format('royalblue', 'white'), unsafe_allow_html=True)
    menu = ["Home", "View Post", "Add Posts", "Search", "Manage Blog"]
    choice = st.sidebar.selectbox("Menu", menu)

    #Conditional for Sidebar Menu Items
    if choice == "Home":
        st.subheader("Home")
        result = view_all_notes()
        #Display all posts
        for i in result:
            b_author = i[0]
            b_title = i[1]
            b_article = str(i[2])[0:200]
            b_post_date = i[3]
            st.markdown(title_temp.format(b_title, b_author, b_article, b_post_date), unsafe_allow_html=True)

    #Read Specific Post
    elif choice == "View Post":
        st.subheader("View Article")
        all_titles = [i[0] for i in view_all_titles()]
        postlist = st.sidebar.selectbox("View Posts", all_titles)
        post_result = get_blog_by_title(postlist)
        #Display post based on title selected
        for i in post_result:
            b_author = i[0]
            b_title = i[1]
            b_article = i[2]
            b_post_date = i[3]
            #st.text("Reading Time:{}".format(readingTime(b_article)))
            st.markdown(head_message_temp.format(b_title, b_author, b_post_date), unsafe_allow_html=True)
            st.markdown(full_message_temp.format(b_article), unsafe_allow_html=True)

    #Create Post
    elif choice == "Add Posts":
        st.subheader("Add Articles")
        blog_author = st.text_input("Enter Author Name", max_chars=50)
        blog_title = st.text_input("Enter Post Title")
        blog_article = st.text_area("Post Article Here", height=200)
        blog_post_date = st.date_input("Date")
        check = st.checkbox("I certify my post does not contain anything inappropriate.")
        if st.button("Add"):
            if(blog_author != "" and blog_title != "" and blog_article != "" and check != 0):
                add_data(blog_author, blog_title, blog_article,blog_post_date)
                st.success("Post Saved: {}".format(blog_title))
            else:
                st.warning("ERROR: Post not saved. Please fill all fields and acknowledge the checkbox!")

    #Read Post by Search
    elif choice == "Search":
        st.subheader("Search Articles")
        search_term = st.text_input('Enter Search Term')
        search_choice = st.radio("Field to Search By", ("title", "author"))

        if st.button("Search"):

            if search_choice == "title":
                article_result = get_blog_by_title(search_term)
            elif search_choice == "author":
                article_result = get_blog_by_author(search_term)

            for i in article_result:
                b_author = i[0]
                b_title = i[1]
                b_article = i[2]
                b_post_date = i[3]
                st.text("Reading Time:{}".format(readingTime(b_article)))
                st.markdown(head_message_temp.format(b_title, b_author, b_post_date), unsafe_allow_html=True)
                st.markdown(full_message_temp.format(b_article), unsafe_allow_html=True)

    #Update Posts
    elif choice == "Manage Blog":
        st.subheader("Manage Articles")

        #Interactive Table
        result = view_all_notes()
        clean_db = pd.DataFrame(result, columns=["Author", "Title", "Articles", "Post Date"])
        st.dataframe(clean_db)

        unique_titles = [i[0] for i in view_all_titles()]
        delete_blog_by_title = st.selectbox("Select Blog", unique_titles)
        new_df = clean_db
        post_result = get_blog_by_title(delete_blog_by_title)

        #Display Post in Editable Boxes
        if post_result:
            blog_author = post_result[0][0]
            blog_title = post_result[0][1]
            blog_article = post_result[0][2]
            blog_post_date =post_result[0][3]

            new_author = st.text_input("Author", blog_author)
            new_title = st.text_input("Title", blog_title)
            new_article = st.text_area("Article", blog_article)
            new_post_date = st.date_input(blog_post_date)

        col1, col2 = st.beta_columns(2)
        
        #Delete and Update Buttons
        with col1:
            if st.button("Delete"):
                delete_data(delete_blog_by_title)
                st.warning("Deleted: '{}'".format(delete_blog_by_title))

        with col2:
            if st.button("Update"):
                if(new_author != "" and new_title != "" and new_article != ""):
                    edit_blog_data(new_author, new_title, new_article, new_post_date, blog_author, blog_title, blog_article, blog_post_date)
                    st.success("Blog Updated: '{}'".format(delete_blog_by_title))
                else:
                    st.warning("ERROR: Post not updated. Please fill all fields!")

        #View Updated Data Drop Down
        with st.beta_expander("View Updated Data"):
                result = view_all_notes()
                clean_db = pd.DataFrame(result, columns=["Author", "Title", "Articles", "Post Date"])
                st.dataframe(clean_db)

        #Graphs
        if st.checkbox("Author Stats"):
            st.subheader("Bar Chart")
            new_df["Author"].value_counts().plot(kind='bar')
            st.pyplot()

            st.subheader("Pie Chart")
            new_df['Author'].value_counts().plot.pie(autopct="%1.1f%%")
            st.pyplot()

        if st.checkbox("Active Blog Users"):
            st.subheader("Map")
            df = pd.DataFrame(
            np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
            columns=['lat', 'lon'])

            st.map(df)

        if st.checkbox("Article Lengths"):
            st.subheader("Line Chart")
            chart_data = pd.DataFrame(
                np.random.randn(20, 3),
                columns=['Author', 'Length', 'figsize=(20, 10)'])

            st.line_chart(chart_data)

#Run Code
if __name__ == '__main__':
    main()