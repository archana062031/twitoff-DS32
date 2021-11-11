from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .predict import predict_user
from .twitter import add_or_update_user, get_all_usernames


def create_app():
    # initializes our app
    app = Flask(__name__)

    # Database configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite3'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Give our APP access to our database
    DB.init_app(app)

    # Listen to a "route"
    # '/' is the home page route
    @app.route('/')
    def root():
        # query the DB for all users
        # users = User.query.all()
        # tweets = Tweet.query.all()
        # what I want to happen when somebody goes to home page
        return render_template('base.html', title="Home", users=User.query.all())

    @app.route('/update')
    def update():
        '''update all users'''
        usernames = get_all_usernames()
        for username in usernames:
            add_or_update_user(username)
        return "All users have been updated"

    # @app.route('/populate')
    # def populate():
    #     ryan = User(id=1, username='Ryan')
    #     DB.session.add(ryan)
    #     julian = User(id=2, username='Julian')
    #     DB.session.add(julian)
    #     tweet1 = Tweet(id=1, text='tweet text', user=ryan)
    #     DB.session.add(tweet1)
    #     tweet2 = Tweet(id=2, text="julian's tweet", user=julian)
    #     DB.session.add(tweet2)
    #     # save the database
    #     DB.session.commit()
    #     return '''Created some users.
    #     <a href='/'>Go to Home</a>
    #     <a href='/reset'>Go to reset</a>
    #     <a href='/populate'>Go to populate</a>'''

    @app.route('/reset')
    def reset():
        # remove everything from the database
        DB.drop_all()
        # Creates the database file initially.
        DB.create_all()
        return render_template('base.html', title='Reset Database')

    # API ENDPOINTS (Querying and manupulating data in Database)
    @app.route('/user', methods=["POST"])
    @app.route('/user/<name>', methods=["GET"])
    def user(name=None, message=''):

        # we either take name that was passed in or we pull it
        # from our request.values which would be accessed through the
        # user submission
        name = name or request.values['user_name']
        try:
            # if user exist in db update it and query for it
            # if not add the user
            if request.method == 'POST':
                add_or_update_user(name)
                message = f"User {name} Succesfully added!"
            # from user added/updated get their tweets to display on /user<name> page
            tweets = User.query.filter(User.username == name).one().tweets

        except Exception as e:
            message = f"Error adding {name}: {e}"

            tweets = []

        return render_template("user.html", title=name, tweets=tweets, message=message)

    @app.route('/compare', methods=["POST"])
    def compare():
        user0, user1 = sorted(
            [request.values['user0'], request.values["user1"]])

        if user0 == user1:
            message = "Cannot compare users to themselves!"

        else:
            # prediction returns a 0 or 1
            prediction = predict_user(
                user0, user1, request.values["tweet_text"])
            message = "'{}' is more likely to be said by {} than {}!".format(
                request.values["tweet_text"],
                user1 if prediction else user0,
                user0 if prediction else user1
            )

        return render_template('prediction.html', title="Prediction", message=message)

    return app
