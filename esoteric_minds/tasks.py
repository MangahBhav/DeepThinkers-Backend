from users.models import User
from posts.models import Like
from datetime import date, timedelta


# runs first day of the new month
def set_star_user():
    # set all users star to False
    User.objects.all().update(star=False)

    # get first and last day of the previous month
    today = date.today()
    last_day = today.replace(day=1) - timedelta(days=1)
    first_day = last_day.replace(day=1)

    # get likes from start to end of the month
    likes = Like.objects.filter(
        date__gte=first_day,
        date__lte=last_day
    )

    # give weight score for each like
    score_map = {
        "very_deep": 4,
        "deep": 3,
        "shallow": 2,
        "very_shallow": 1
    }

    user_score = {}

    for like in likes:
        if like.post.user not in user_score:
            user_score[like.post.user.email] = 0
        user_score[like.post.user.email] += score_map[like.type]

    # get user with highest score
    star_user_email = max(user_score, key=user_score.get)
    star_user = User.objects.get(email=star_user_email)
    star_user.star = True
    star_user.save()

    print('set_star_user', star_user.email, user_score[star_user.email])