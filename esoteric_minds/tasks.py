from users.models import User
from posts.models import Like
from datetime import date, timedelta


# runs first day of the new month
def set_star_user():
    print("hiii")
    # set all users star to False
    for user in User.objects.filter():
        user.star = False
        user.save()

    # # get first and last day of the previous month
    today = date.today()
    last_day = today.replace(day=1) - timedelta(days=1)
    first_day = last_day.replace(day=1)

    # get likes from start to end of the month
    likes = Like.objects.filter(
        date__gte=first_day,
        date__lte=last_day,
        category='very_deep'
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
        user_score[like.post.user.email] += score_map[like.category]

    if len(user_score.keys()) == 0:
        print('no star user')
        return

    # get user with highest score
    star_user_email = max(user_score, key=user_score.get)

    # only work if user has score
    if not len(user_score.keys()) or not user_score.get(star_user_email, 0):
        print('no star user')
        return

    star_user = User.objects.get(email=star_user_email)
    star_user.star = True
    star_user.save()

    print('set_star_user', star_user.email, user_score[star_user.email])