import facebook
import auth_fb
import pickle
import sys
from csc import divisi2

class User:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.data = data
        self.likes = []

    def __unicode__(self):
        self.name

class Page:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.category = data['category']

    def __unicode__(self):
        self.name

class FBGraph():
    def __init__(self):
        self.token = auth_fb.get_access_token()
        self.graph = facebook.GraphAPI(self.token)
        self.id_table = {}
        self.friends = []
        self.pages = []

        self.dlMe()
        self.dlFriends()
        self.dlLikes(self.me)
        count = 0
        for friend in self.friends:
            print 'downloading like',count,'/',len(self.friends),'\r',
            sys.stdout.flush()
            self.dlLikes(friend)
            count += 1
        print 'downloading like',count,'/',len(self.friends)
        print 'finished.'

    def dlMe(self):
        print 'downloading me 0/1','\r',
        sys.stdout.flush()
        self.me = User(self.graph.get_object("me"))
        self.id_table[self.me.id] = self.me
        print 'downloading me 1/1'
        
    def dlFriends(self):
        count = 0
        friendData = self.graph.get_connections(self.me.id,"friends")['data']
        for f in friendData:
            print 'downloading friends',count,'/',len(friendData),'\r',
            sys.stdout.flush()
            friend = User(self.graph.get_object(f['id']))
            self.friends.append(friend)
            self.id_table[friend.id] = friend
            count += 1
        print 'downloading friends',count,'/',len(friendData)

    def dlLikes(self,user):
        for l in self.graph.get_connections(user.id, "likes")['data']:
            if l['id'] in self.id_table:
                break
            like = Page(l)
            self.pages.append(like)
            user.likes.append(like)
            self.id_table[like.id] = like

    def append_to_file(self,subject,object,rel):
        line = subject+'\t'+object+"\t{'freq': 1, 'score': 1, 'rel': u'"+rel+"'}\n"
        with open(self.filename,'a') as gf:
            gf.write(line)

    def save_graph(self,filename='fb.graph'):
        self.filename = filename
        f = open(filename,'w')
        f.close()
        with open(filename,'a') as gf:
            self.add_user_to_graph(self.me,gf)
            for user in self.friends:
                self.add_user_to_graph(user,gf)
            for page in self.pages:
                self.add_page_to_graph(page,gf)

    def add_user_to_graph(self,user,file):
        if 'gender' in user.data:
            if user.data['gender'] not in self.id_table:
                self.id_table[user.data['gender']] = user.data['gender']
            self.append_to_file(user.data['id'],user.data['gender'],"hasProperty")
        if 'hometown' in user.data:
            if user.data['hometown']['id'] not in self.id_table:
                self.id_table[user.data['hometown']['id']] = user.data['hometown']['name']
            self.append_to_file(user.data['id'],user.data['hometown']['id'],"isFrom")
        for like in user.likes:
            self.append_to_file(user.id,like.id,"likes")

    def add_page_to_graph(self,page,file):
        self.append_to_file(page.id,page.category,"isA")

    def save(self,filename="FBGraph.pickle"):
        with open(filename,'w') as fbg:
            pickle.dump(self,fbg)
