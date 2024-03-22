import pytest
from seldegen import Twitter, Email


@pytest.fixture()
def email(credentials) -> Email:
    return Email(credentials['TWITTER_EMAIL'], credentials['TWITTER_EMAIL_PASSWORD'])


@pytest.fixture()
def twitter(function_driver, make_twitter) -> Twitter:
    twitter = make_twitter(function_driver)
    return twitter


@pytest.mark.parametrize('method', ['standard', 'token'])
def test_sign_in(function_driver, twitter, email, method, credentials):
    if method == 'standard':
        twitter = Twitter(
            function_driver,
            credentials['TWITTER_PASSWORD'],
            email,
            two_fa_key=credentials['TWITTER_AUTH_SECRET']
        )
        twitter.sign_in()

    assert twitter.nickname and twitter.profile_url


def test_get_last_tweet(twitter):
    tweet = twitter.get_last_tweet()
    assert 'https' in tweet


def test_get_last_tweet_of(twitter):
    tweet = twitter.get_last_tweet_of('taikoxyz')
    assert 'https' in tweet

    
def test_like_tweet(twitter):
    tweet = twitter.get_last_tweet_of('taikoxyz')
    twitter.like_tweet(tweet)

    
def test_retweet(twitter):
    tweet = twitter.get_last_tweet_of('taikoxyz')
    twitter.retweet(tweet)


def test_follow(twitter):
    twitter.follow('taikoxyz')
    