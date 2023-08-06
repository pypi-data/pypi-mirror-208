import datetime

CHAT_ID = 'TELEGRAM CHAT IT'


def job_handler(context):
    yesterday = datetime.datetime.today() + datetime.timedelta(days=-1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    message = context.bot.send_poll(
        CHAT_ID,
        f"What did you do in {yesterday_str}?",
        duties,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    payload = {
        message.poll.id: {
            "questions": duties,
            "message_id": message.message_id,
            "chat_id": CHAT_ID,
            "answers": 0,
        },
        "poll_date": yesterday_str,
        "poll_type": PollTypes.SELECT_DUTIES,
    }
    context.bot_data.update(payload)


POLL_HOURS = 0
POLL_MINUTES = 0


def job(update, context):
    first = datetime.datetime.now().replace(
        hour=POLL_HOURS,
        minute=POLL_MINUTES,
        second=0,
    ) + datetime.timedelta(hours=-1*int('+03'))
    new_job = context.job_queue.run_repeating(
        job_handler,
        first=first,
        interval=datetime.timedelta(days=1),
        context=CHAT_ID,
    )
    context.chat_data['job'] = new_job
    update.message.reply_text('Job is successfully set!')
