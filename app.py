# app.py

import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

# Connect to MongoDB
client = MongoClient("mongodb+srv://maliyuam01:tz5MF861Y82oe9Qy@advanceddbcluster.oa6lb.mongodb.net/")
db = client["LibraryDB"]

# Collections
books = db["books"]
authors = db["authors"]
borrowers = db["borrowers"]

# Helper function to format date
def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

# Sidebar options
st.sidebar.title("📚 Library Management System")
options = st.sidebar.radio("Choose an action", [
    "📖 View Books", "✍️ View Authors", "👥 View Borrowers", "➕ Insert Book",
    "➕ Insert Author", "➕ Insert Borrower", "🔍 Query Books by Author",
    "📅 Books Borrowed in Date Range", "🚩 View Overdue Borrowers",
    "📊 Aggregation Queries"
])

with st.container():
    # View Books with Delete Option
    if options == "📖 View Books":
        st.header("📚 Books Collection")
        books_list = list(books.find())
        search_query = st.text_input("Search Books by Title")
        if search_query:
            search_results = list(books.find({"title": {"$regex": search_query, "$options": "i"}}))
            st.table(search_results)
        else:
            st.table(books_list)
        
        # Delete Book by ID
        book_id_to_delete = st.number_input("Enter Book ID to Delete", min_value=1, step=1)
        if st.button("Delete Book"):
            delete_result = books.delete_one({"book_id": book_id_to_delete})
            if delete_result.deleted_count > 0:
                st.success(f"Book with ID {book_id_to_delete} has been deleted.")
            else:
                st.warning("No book found with that ID.")

    # View Authors with Delete Option
    elif options == "✍️ View Authors":
        st.header("✍️ Authors Collection")
        authors_list = list(authors.find())
        search_query = st.text_input("Search Authors by Name")
        if search_query:
            search_results = list(authors.find({"name": {"$regex": search_query, "$options": "i"}}))
            st.table(search_results)
        else:
            st.table(authors_list)
        
        # Delete Author by ID
        author_id_to_delete = st.number_input("Enter Author ID to Delete", min_value=1, step=1)
        if st.button("Delete Author"):
            delete_result = authors.delete_one({"author_id": author_id_to_delete})
            if delete_result.deleted_count > 0:
                st.success(f"Author with ID {author_id_to_delete} has been deleted.")
            else:
                st.warning("No author found with that ID.")

    # View Borrowers with Delete Option
    elif options == "👥 View Borrowers":
        st.header("👥 Borrowers Collection")
        borrowers_list = list(borrowers.find())
        search_query = st.text_input("Search Borrowers by Name")
        if search_query:
            search_results = list(borrowers.find({"name": {"$regex": search_query, "$options": "i"}}))
            st.table(search_results)
        else:
            st.table(borrowers_list)
        
        # Delete Borrower by ID
        borrower_id_to_delete = st.number_input("Enter Borrower ID to Delete", min_value=1, step=1)
        if st.button("Delete Borrower"):
            delete_result = borrowers.delete_one({"borrower_id": borrower_id_to_delete})
            if delete_result.deleted_count > 0:
                st.success(f"Borrower with ID {borrower_id_to_delete} has been deleted.")
            else:
                st.warning("No borrower found with that ID.")

    # Insert Book
    elif options == "➕ Insert Book":
        st.header("➕ Insert a New Book")
        max_book_id = books.find_one(sort=[("book_id", -1)])
        next_book_id = max_book_id["book_id"] + 1 if max_book_id else 1
        st.write(f"Next Book ID: {next_book_id}")
        
        title = st.text_input("Title")
        author_ids = st.text_input("Author IDs (comma-separated)").split(",")
        year_published = st.number_input("Year Published", min_value=1900, step=1)
        genre = st.text_input("Genre")
        available_copies = st.number_input("Available Copies", min_value=1, step=1)
        if st.button("Add Book"):
            books.insert_one({
                "book_id": next_book_id,
                "title": title,
                "author_ids": list(map(int, author_ids)),
                "year_published": year_published,
                "genre": genre,
                "available_copies": available_copies
            })
            st.success(f"Book '{title}' added to collection with ID {next_book_id}.")

    # Insert Author
    elif options == "➕ Insert Author":
        st.header("➕ Insert a New Author")
        max_author_id = authors.find_one(sort=[("author_id", -1)])
        next_author_id = max_author_id["author_id"] + 1 if max_author_id else 1
        st.write(f"Next Author ID: {next_author_id}")
        
        name = st.text_input("Name")
        nationality = st.text_input("Nationality")
        if st.button("Add Author"):
            authors.insert_one({
                "author_id": next_author_id,
                "name": name,
                "nationality": nationality
            })
            st.success(f"Author '{name}' added to collection with ID {next_author_id}.")

    # Insert Borrower
    elif options == "➕ Insert Borrower":
        st.header("➕ Insert a New Borrower")
        max_borrower_id = borrowers.find_one(sort=[("borrower_id", -1)])
        next_borrower_id = max_borrower_id["borrower_id"] + 1 if max_borrower_id else 1
        st.write(f"Next Borrower ID: {next_borrower_id}")
        
        name = st.text_input("Name")
        borrowed_books = books.find()
        borrowed_book_ids = st.multiselect(
            "Borrowed Book IDs",
            options=[(book["book_id"], book["title"]) for book in borrowed_books],
            format_func=lambda book: book[1]
        )
        borrow_date = st.date_input("Borrow Date")
        return_date = st.date_input("Return Date")
        if st.button("Add Borrower"):
            borrowed_book_ids = [book[0] for book in borrowed_book_ids]
            borrowers.insert_one({
                "borrower_id": next_borrower_id,
                "name": name,
                "borrowed_book_ids": borrowed_book_ids,
                "borrow_date": borrow_date.strftime("%Y-%m-%d"),
                "return_date": return_date.strftime("%Y-%m-%d")
            })
            st.success(f"Borrower '{name}' added to collection with ID {next_borrower_id}.")

    # Query Books by Author
    elif options == "🔍 Query Books by Author":
        st.header("🔍 Query Books by Author")
        author_id = st.number_input("Author ID", min_value=1, step=1)
        if st.button("Find Books"):
            books_by_author = list(books.find({"author_ids": author_id}))
            st.table(books_by_author)

    # Books Borrowed in Date Range
    elif options == "📅 Books Borrowed in Date Range":
        st.header("📅 Find Books Borrowed in a Date Range")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        if st.button("Search"):
            borrowed_books = list(borrowers.find({
                "borrow_date": {"$gte": start_date.strftime("%Y-%m-%d"), "$lte": end_date.strftime("%Y-%m-%d")}
            }))
            st.table(borrowed_books)

    # View Overdue Borrowers
    elif options == "🚩 View Overdue Borrowers":
        st.header("🚩 View Overdue Borrowers")
        current_date = datetime.now().strftime("%Y-%m-%d")
        overdue_borrowers = list(borrowers.find({"return_date": {"$lt": current_date}}))
        st.table(overdue_borrowers)

    # Aggregation Queries and Dashboard
    elif options == "📊 Aggregation Queries":
        st.header("📊 Aggregation Queries and Dashboard")

        # Total Books by Genre
        st.subheader("📘 Total Books by Genre")
        genre_aggregation = books.aggregate([
            {"$group": {"_id": "$genre", "total_books": {"$sum": "$available_copies"}}}
        ])
        genre_data = pd.DataFrame(list(genre_aggregation))
        st.table(genre_data)
        
        # Visualization: Total Books by Genre
        fig = px.bar(genre_data, x='_id', y='total_books', title="Total Books by Genre", labels={"_id": "Genre", "total_books": "Total Books"})
        st.plotly_chart(fig)

        # Book Count by Author
        st.subheader("📙 Books Count by Author")
        author_books = books.aggregate([
            {"$unwind": "$author_ids"},
            {"$group": {"_id": "$author_ids", "count": {"$sum": 1}}},
            {"$lookup": {
                "from": "authors",
                "localField": "_id",
                "foreignField": "author_id",
                "as": "author_info"
            }},
            {"$unwind": "$author_info"},
            {"$project": {"author": "$author_info.name", "book_count": "$count"}}
        ])
        author_books_data = pd.DataFrame(list(author_books))
        st.table(author_books_data)
        
        # Visualization: Books Count by Author
        fig = px.bar(author_books_data, x='author', y='book_count', title="Books Count by Author", labels={"author": "Author", "book_count": "Book Count"})
        st.plotly_chart(fig)

        # Books with Authors
        st.subheader("📗 Books with Authors")
        books_with_authors = books.aggregate([
            {"$lookup": {
                "from": "authors",
                "localField": "author_ids",
                "foreignField": "author_id",
                "as": "authors"
            }},
            {"$project": {
                "title": 1,
                "year_published": 1,
                "genre": 1,
                "available_copies": 1,
                "authors": "$authors.name"
            }}
        ])
        books_authors_data = pd.DataFrame(list(books_with_authors))
        st.table(books_authors_data)