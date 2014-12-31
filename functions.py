from itertools import islice
import math
import numpy
from force import force_graph

__author__ = 'Roman'
# -*- coding: UTF-8 -*-
import urllib, time
import json
import timeit
import networkx as nx
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from settings import *
from calc_properties import *
import sys, codecs

class Logger(object):


    def __init__(self):
        self.terminal = sys.stdout
        self.log = codecs.open("logfile.log", "w+", 'utf-8-sig')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

def get_user(uid = default_id):
    raw_data = urllib.urlopen(API + 'users.get?user_ids=%s&fields=deactivated&v=5.27' % uid)
    data = json.load(raw_data)
    # time.sleep(sleep)
    print data['response'][0]['first_name'], data['response'][0]['last_name'] # print First & Last name
    return data['response']

def get_user_followers(uid = default_id):
    raw_data = urllib.urlopen(API + 'users.getFollowers?user_id=%s&v=5.27' % uid)
    data = json.load(raw_data)
    time.sleep(sleep)
    # print str(data['response']['count']) + ' followers' # print if needed
    # return data['response']['items'] # return data if needed
    return data['response']['count'] # return number of followers

def get_user_friends(uid = default_id):
    user_data = get_user(uid)

    try:
        if (user_data[0]['deactivated'] == 'deleted') or (user_data[0]['deactivated'] != []) or (user_data[0]['deactivated'] != ['banned']):
            return (0,0)
    except KeyError: pass

    raw_data = urllib.urlopen(API + 'friends.get?user_id=%s&v=5.27' % uid)
    data = json.load(raw_data)
    # time.sleep(sleep)
    # print str(data['response']['count']) + ' friends' # printing number of friends of the user
    return data['response']['count'], data['response']['items']

def get_common_friends(source_uid, target_uid):
    raw_data = urllib.urlopen(API + 'friends.getMutual?source_uid=%s'
                                    '&target_uids=%s'
                                    '&v=5.27'
                                    '&access_token=%s'% (source_uid, target_uid, token))
    data = json.load(raw_data)
    # print str(len(data['response'])) + ' mutual friends with %s'% (target_uid) # print number of mutual friends
    # return data["response"]
    return len(data['response']) # number of mutual friends

def get_wall_posts(uid = default_id, offset = 0, count = 100):
    # 100 posts max at a time
    # we use offset as a measure of chunks of posts - how many to process
    raw_data = urllib.urlopen(API + 'wall.get?owner_id=%s'
                                    '&filter=owner'
                                    '&offset=%s'
                                    '&count=%s'
                                    '&v=5.27'
                                    '&access_token=%s' % (uid, offset, count, token))
    data = json.load(raw_data)
    time.sleep(sleep)
    # print str(data['response']['count']) + ' posts'

    if offset != 0: # to get total number of posts in the first time (when offset = 0)
        return data['response']['items']
    else:
        return data['response']['count'], data['response']['items'] # get total number of posts for further processing

def get_post_by_id(post_id, uid = default_id):
    # get post data by post_id
    raw_data = urllib.urlopen(API + 'wall.getById?posts=%s_%s'
                                    '&v=5.27'
                                    '&access_token=%s' % (uid, post_id, token))
    data = json.load(raw_data)
    time.sleep(sleep)
    return data['response']

def get_max_post(uid, posts_data, total_posts, flag, top_num):
    temp = [] # temp list of posts with max number of flag - likes, comments or reposts
    offset = 100 # number of posts to analyze
    num_iter = (total_posts / offset) #

    temp.extend( get_max_from_100(posts_data, flag) ) #put max from 1st chunk - 100 initial posts

    for i in range(0, num_iter): # number of chunks of 100 posts to analyze
        new_post_data = get_wall_posts(uid, offset)
        temp.extend( get_max_from_100(new_post_data, flag) )
        temp = sort_list_of_tuples(temp)[0:top_num]
        # print str(offset + 100) + ' posts analyzed...'
        offset += 100
        print '.',

    print ' ' + flag + ' are analyzed.'

    return sort_list_of_tuples(temp)[0:top_num]

def get_max_from_100(data_100posts, flag):
    temp = []
    num_iter = len(data_100posts)

    for i in range(0, num_iter):
        temp.append( ( data_100posts[i]['id'], data_100posts[i][flag]['count'] ) ) # (id, count of flag) tuple

    return sort_list_of_tuples(temp)[0:5]

def sort_list_of_tuples(list):

    def getKey(item):
        return item[1]

    list.sort(key = getKey, reverse=True)

    return list

def print_one_post_data(post_tuple, top_id, top_num, flag, uid = default_id):
    post_id, flag_count = post_tuple # decouple the tuple
    post_data = get_post_by_id(post_id, uid)
    print '%s from TOP-%s posts: http://vk.com/id%s?w=wall%s_%s (%s: %s)' % (top_id, top_num, uid, uid, post_id, flag, flag_count)

def print_top_posts(top_posts_data, flag, top_num, uid = default_id):
    # print 'User: http://vk.com/id%s' % uid
    print '='*20, str(flag).upper(), '='*20
    for i in range(0, top_num):
        print_one_post_data(top_posts_data[i], i+1, top_num, flag, uid)
    print '='*20, "END", '='*20

def print_to_file(target_uid, uid, num_friends, num_common_friends, num_followers, num_posts, num_max_likes, num_max_comments, num_max_reposts):
    with open('csv/data_%s.csv' % target_uid, 'a+') as fp:
        fp.write( str(uid) + ';'
                  + str(num_friends) + ';'
                  + str(num_common_friends) + ';'
                  + str(num_followers) + ';'
                  + str(num_posts) + ';'
                  + str(num_max_likes) + ';'
                  + str(num_max_comments) + ';'
                  + str(num_max_reposts) + '\n'
        )
        fp.close()

def compute_top_posts(flag, posts, total_posts, uid = default_id):
    top_num = 5
    # get top-5 max posts according to flag
    top_posts = get_max_post(uid, posts, total_posts, flag, top_num)
    if top_posts != []:
        post_id, flag_count = top_posts[0] # if the user ever posted anything we have a non-empty response list
    else:
        flag_count = 0 # otherwise just return 0 value

    print_top_posts(top_posts, flag, top_num, uid)
    return flag_count

def compute_all_for_uid(uid, target_uid, counter):
    print str(counter) + '.',
    user_data = get_user(uid)

    try:
        if (user_data[0]['deactivated'] == 'deleted') or (user_data[0]['deactivated'] != []) or (user_data[0]['deactivated'] != ['banned']):
            return 0
    except KeyError: pass


    num_friends, friends = get_user_friends(uid)
    num_common_friends = get_common_friends(uid, target_uid)
    num_followers = get_user_followers(uid)
    total_posts, posts = get_wall_posts(uid) # retrieve 100 first posts of the user

    print str(total_posts) + ' posts'

    flag1 = 'likes'
    flag2 = 'comments'
    flag3 = 'reposts'

    num_max_likes = compute_top_posts(flag1, posts, total_posts, uid) # compute top posts
    num_max_comments = compute_top_posts(flag2, posts, total_posts, uid)
    num_max_reposts = compute_top_posts(flag3, posts, total_posts, uid)

    print_to_file(target_uid, uid, num_friends, num_common_friends, num_followers, total_posts, num_max_likes, num_max_comments, num_max_reposts)

def split_line(line):
    line = line.strip()
    list = line.split(';')
    list = map(int, list)
    return list

def read_all_lines_from_file(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

def plot_histogram(x, figure_title, fig_num):

    plt.close()

    num_bins = 40

    fig = plt.figure()
    fig.suptitle(figure_title, fontsize=20)
    fig1 = plt.subplot(2,2,1)
    fig1.boxplot(x)
    plt.title('Boxplot')

    fig2 = plt.subplot(2,2,2)
    fig2.hist(x, facecolor='green', alpha=0.5)
    fig2.set_yscale('log')
    plt.title('Logscale histogram')

    fig3 = plt.subplot(2,2,3)
    fig3.hist(x, bins=num_bins, facecolor='green', alpha=0.5)
    plt.title('Histogram with outliers')

    fig4 = plt.subplot(2,2,4)
    fig4.hist(x, range=[numpy.mean(x), max(x)], facecolor='green', alpha=0.5)
    plt.title('Mostly outliers (xrange = (mean(x), max(x) )')

    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    plt.show()
    fig.savefig('figures_new/%s. %s.png' % (fig_num, figure_title))

def plot_friends_stats(uid):
    num_features = 7
    features_names = ['# of friends',
                      '# of common friends',
                      '# of subscribers',
                      '# of posts',
                      'max # of likes per post',
                      'max # of reposts per post',
                      'max # of comments per post']

    lines = read_all_lines_from_file('csv/data_%s.csv' % uid)
    featureArray = []
    for j in range(0,num_features):
        featureArray = []
        for i in range(0, len(lines)):
            featureArray.append( split_line(lines[i])[j+1] )
        plot_histogram(featureArray, features_names[j], j+1)

def is_friends(uids):
    '''
    uids = str(friends[k]) + "," + tempString
    '''
    raw_data = urllib.urlopen(API + 'friends.areFriends?&user_ids=%s&access_token=%s&v=5.27' % (uids, token))
    data = json.load(raw_data)
    time.sleep(sleep)
    return data['response']

def get_mutual_friends(source_uid, target_uids):
    target_uids = ','.join(map(str, target_uids))

    raw_data = urllib.urlopen(API + 'friends.getMutual?source_uid=%s'
                                    '&target_uids=%s'
                                    '&v=5.27'
                                    '&access_token=%s'% (source_uid, target_uids, token))
    data = json.load(raw_data)
    time.sleep(sleep)
    listOfDict = data["response"]
    tempList = []

    for k in range(0, len(listOfDict)):
        if listOfDict[k]['common_count'] != 0: # listOfDict[k] == nodes[i+1]
            tempList.append(1)
        else:
            if listOfDict[k]['common_count'] == 0:
                tempList.append(0)

    return tempList

def create_adjacency_matrix(nodes):
    size = len(nodes)
    # temp = numpy.zeros((size, size)) # adjacency matrix
    temp = []

    for i in range(0, size):
        rest = size - 1
        max100iters = rest / 100
        restIters = rest % 100
        tempList = [] # one row of adjacency matrix

        for j in range(0, max100iters):
            tempList.extend( get_mutual_friends( nodes[i], nodes[i+100*j:i+100*(1+j)] ) ) # find mutual friends with 100 users

        tempList.extend(get_mutual_friends( nodes[i], nodes[i+max100iters*100:size] ) ) # find mutual friends with 100 users

        print str(i) + " string"
        temp.append(tempList)
        # print tempList
        # temp[i][i:size] = tempList
        # print 1
        print temp[i:size][i]
        # temp[i:size-1][i] = tempList
        # print 2

    return temp

def check_friends(uid, friends):
    num_uid_friends, uid_friends = get_user_friends(uid)
    edgeList = []

    for i in friends:
        if num_uid_friends != 0:
            if i in uid_friends:
                tuple = ( uid, i )
                if tuple not in edgeList:
                    edgeList.append( tuple )
    return edgeList

def createGraph(uid, friends):
    G=nx.Graph()
    edgeList = []
    tempString = ""
    num_friends = len(friends)

    for i in range(0,num_friends):
        edgeList.append((uid, friends[i]))

    for k in range(0, num_friends): # going through uids in the list of friends till the one before the last
        edgeList.extend( check_friends( friends[k], friends[k:] ) )
        print k

    G.add_edges_from(edgeList)
    calc_prop(G)
    # print G.number_of_nodes()
    nx.draw(G)

    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    plt.savefig('graph/%s.png' % uid)
    plt.show()

    force_graph(G)

def main():
    sys.stdout = Logger()

    default_id = '53083705' # Medvedev

    print "="*40
    print "VK social network analysis with Python"
    print "="*40

    target_uid = raw_input("Enter VK user ID to analyse (or press ENTER to use default_id=%s): " % default_id)

    if target_uid == '':
        target_uid = default_id

    print

    print "Analysing user_id=%s:" % target_uid ,

    num_friends, friends = get_user_friends(target_uid)
    print "Total: %s friends" % len(friends)
    print
    counter = 1 # counter is used to print an id of current friend being processed
    for i in friends:
        compute_all_for_uid(i, target_uid, counter) # compute all stats for specific uid
        counter += 1
    #     if counter == 2:
    #         break
    plot_friends_stats(target_uid)

    createGraph(target_uid, friends)

main()