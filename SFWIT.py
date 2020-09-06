'''
Twitter interface for sfwiT
'''
import json
import twitter
import TwitterTokens as T

class SFWIT ():
        '''
        Stop Fiddling With It Twitter class
        '''
        def __init__(self):
            '''
            SFWIT constructor
            '''
            self.api = twitter.Api(consumer_key=T.CONSUMER_KEY, consumer_secret=T.CONSUMER_SECRET, access_token_key=T.ACCESS_TOKEN_KEY, access_token_secret=T.ACCESS_TOKEN_SECRET, tweet_mode='extended')
            self.following = []
        def getEmbeddedStatus(self, statusID):
            '''
            Get a status record in an embedded format
            '''
            try:
                status = self.api.GetStatusOembed(status_id=int(statusID))
            except twitter.error.TwitterError as err:
                print("Execption: ", err, err.message, err.args, statusID, int(statusID))
                #print(dir(err))
                status = err.message
            return json.dumps(status)
        def getUserTimeline(self, screenName):
            '''
            Get the timeline text of someone that is being followed
            '''
            timeLine =  self.api.GetUserTimeline(screen_name=screenName)
            textList = []
            for entry in timeLine:
                if 'retweeted_status' in entry.AsDict():
                    textList.append((entry.created_at, entry.full_text, entry.AsDict()['retweeted_status']['full_text'], str(entry.id)))
                else:
                    textList.append((entry.created_at, entry.full_text, str(entry.id)))
            return json.dumps(textList)
        def printUserTimeline(self, timelineList):
            '''
            Print a list generated from getUserTimeline - assumes JSON format
            '''
            timelineList = json.loads(timelineList)
            for entry in timelineList:
                if len(entry) == 3:
                    print(entry[0])
                    print(entry[1])
                    print(entry[2])
                else:
                    print(entry[0])
                    print(entry[1])
                    print(entry[2])
                    print(entry[3])
        def getFollowing(self):
            '''
            Get the list of screen names being followed
            '''
            self.following = []
            for friend in self.api.GetFriends():
                self.following.append(friend.AsDict()['screen_name'])
            return json.dumps(self.following)
