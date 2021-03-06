from flask import render_template, url_for, redirect, request

from application import app
from application.topics.models import Topic
from application.messages.models import Message

from application.search.forms import SearchForm, SearchDateForm


@app.route("/search/", methods=["GET"])
def search_index():
    return render_template("search/search.html", form=SearchForm())


@app.route("/search/topic/", methods=["POST"])
def search_topic():
    topics = []
    messages = []
    results = []

    form = SearchForm(request.form)
    search_term = form.search_phrase.data

    if not form.validate():
        return render_template("search/search.html", form=form)

    searching_for = form.searching_for.data

    if searching_for == "topic":
        topics = Topic.query.filter(
            Topic.title.like("%" + search_term + "%")).order_by(
            Topic.date_created.desc()).limit(30).all()
    elif searching_for == "author":
        messages = Message.query.filter(
            Message.author.like("%" + search_term + "%")).order_by(
            Message.date_created.desc()).limit(30).all()
    elif searching_for == "all":
        results = Message.find_all(search_term)

    return render_template("search/search.html", topics=topics, messages=messages,
                           results=results, form=SearchForm())


@app.route("/search/topic/date", methods=["POST"])
def search_topic_by_date():
    topics = []
    messages = []

    start = request.form['start']
    end = request.form['end']

    dated_messages = Message.find_messages_by_date(start, end)

    return render_template("search/search.html", dated_messages=dated_messages,
                           form=SearchForm())
