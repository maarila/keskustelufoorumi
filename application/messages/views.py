from flask import redirect, render_template, request, url_for
from flask_login import login_required, current_user

from application import app, db
from application.topics.models import Topic
from application.service.methods import mark_messages_read, delete_message
from application.messages.models import Message
from application.messages.forms import MessageForm


@app.route("/messages/", methods=["GET"])
@login_required
def messages_index(page=1):
    per_page = 10
    messages = Message.query.order_by(Message.date_created.desc()).paginate(
        page, per_page, False)
    return render_template("messages/list.html", messages=messages)


@app.route("/messages/<int:page>", methods=["GET"])
@login_required
def messages_paginated(page=1):
    per_page = 10
    messages = Message.query.order_by(Message.date_created.desc()).paginate(
        page, per_page, False)
    return render_template("messages/list.html", messages=messages)


@app.route("/messages/<message_id>/edit", methods=["GET"])
@login_required
def messages_get_for_edit(message_id):
    m = Message.query.get(message_id)
    return render_template("messages/edit.html", form=MessageForm(name=m.content),
                           message=Message.query.get(message_id))


@app.route("/messages/<message_id>/edit", methods=["POST"])
@login_required
def messages_edit(message_id):
    form = MessageForm(request.form)

    if not form.validate():
        return render_template("messages/edit.html", form=form,
                               message=Message.query.get(message_id))

    m = Message.query.get(message_id)
    m.content = form.name.data

    if current_user.id == m.account_id:
        db.session.commit()

    return redirect(url_for("messages_read_one", topic_id=m.topic_id, message_id=m.id))


@app.route("/messages/<message_id>/delete/", methods=["POST"])
@login_required
def messages_delete(message_id):
    m = Message.query.get(message_id)

    if current_user.admin:
        delete_message(m)

    return redirect(url_for("messages_index"))

@app.route("/topics/<topic_id>/messages/<message_id>/delete/", methods=["POST"])
@login_required
def messages_delete_from_topic(topic_id, message_id):
    msg = Message.query.get(message_id)

    if current_user.admin:
        delete_message(msg)

    return redirect(url_for("topics_get_one", topic_id=topic_id))


@app.route("/topics/<topic_id>/messages/<message_id>/", methods=["GET"])
@login_required
def messages_read_one(topic_id, message_id):

    replies = Message.query.filter_by(reply_id=message_id).all()
    further_replies = Message.query.filter_by(topic_id=topic_id)
    mark_messages_read(replies)

    return render_template("messages/one.html", topic=Topic.query.get(topic_id),
                           form=MessageForm(), message=Message.query.get(message_id),
                           replies=replies, further_replies=further_replies)


@app.route("/topics/<topic_id>/messages/new", methods=["POST"])
@login_required
def messages_create(topic_id):
    form = MessageForm(request.form)

    if not form.validate():
        return render_template("topics/one_topic.html", form=form,
                               topic=Topic.query.get(topic_id),
                               messages=Message.query.filter_by(
                                   topic_id=topic_id, reply_id=None)
                               .paginate(page=1, per_page=5, error_out=False))

    m = Message(form.name.data)
    m.author = current_user.name
    m.account_id = current_user.id
    m.topic_id = topic_id

    db.session.add(m)
    db.session.commit()

    return redirect("/topics/" + topic_id + "/")


@app.route("/topics/<topic_id>/messages/<message_id>/reply", methods=["POST"])
@login_required
def messages_reply(topic_id, message_id):
    form = MessageForm(request.form)

    if not form.validate():
        return render_template("messages/one.html", topic=Topic.query.get(topic_id),
                               form=form, message=Message.query.get(
                                   message_id),
                               replies=Message.query.filter_by(
                                   reply_id=message_id).all(),
                               further_replies=Message.query.filter_by(topic_id=topic_id))

    reply = Message(form.name.data)
    reply.author = current_user.name
    reply.account_id = current_user.id
    reply.topic_id = topic_id
    reply.reply_id = message_id

    db.session.add(reply)
    db.session.commit()

    return redirect("/topics/" + topic_id + "/" + "messages" + "/" + message_id + "/")
