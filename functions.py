__author__ = 'Roman'
# -*- coding: UTF-8 -*-
import urllib
import json

from python_project.settings import *


def get_user(uid = default_id):
    raw_data = urllib.urlopen(API + 'users.get?user_ids=%s&v=5.27' % uid)
    data = json.load(raw_data)
    print data['response'][0]['first_name'], data['response'][0]['last_name']
    return data['response']

def get_user_friends(uid = default_id):
    raw_data = urllib.urlopen(API + 'friends.get?user_id=%s&v=5.27' % uid)
    data = json.load(raw_data)
    print str(data['response']['count']) + ' friends'
    return data['response']['items']

def get_common_friends(source_uid, target_uid):
    raw_data = urllib.urlopen(API + 'friends.getMutual?source_uid=%s'
                                    '&target_uid=%s'
                                    '&v=5.27'
                                    '&access_token=%s'% (source_uid, target_uid, token))
    data = json.load(raw_data)
    print str(len(data['response'])) + ' mutual friends with %s'% (target_uid)
    return data["response"]

def get_user_followers(uid = default_id):
    raw_data = urllib.urlopen(API + 'users.getFollowers?user_id=%s&v=5.27' % uid)
    data = json.load(raw_data)
    print str(data['response']['count']) + ' followers'
    return data['response']['items']

def get_wall_posts(uid = default_id, offset = 0, count = 100):
    # 100 posts max at a time
    raw_data = urllib.urlopen(API + 'wall.get?owner_id=%s'
                                    '&filter=owner'
                                    '&offset=%s'
                                    '&count=%s'
                                    '&v=5.27'
                                    '&access_token=%s' % (uid, offset, count, token))
    data = json.load(raw_data)
    # print str(data['response']['count']) + ' posts'

    if offset != 0: # to get total number of posts in the first time (when offset = 0
        return data['response']['items']
    else:
        return data['response']['count'], data['response']['items']

def get_post_by_id(post_id, uid = default_id):
    raw_data = urllib.urlopen(API + 'wall.getById?posts=%s_%s'
                                    '&v=5.27'
                                    '&access_token=%s' % (uid, post_id, token))
    data = json.load(raw_data)
    return data['response']

def get_max_post(uid, posts_data, total_posts, flag, top_num):
    temp = []
    offset = 100
    num_iter = (total_posts / offset)

    temp.extend( get_max_from_100(posts_data, flag) ) #put max from 1st chunk - 100 initial posts

    for i in range(0, num_iter): # number of chunks of 100 posts to analyze
        new_post_data = get_wall_posts(uid, offset)
        temp.extend( get_max_from_100(new_post_data, flag) )
        temp = sort_list_of_tuples(temp)[0:top_num]
        print str(offset + 100) + ' posts analyzed...'
        offset += 100

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
    print 'User: http://vk.com/id%s' % uid
    for i in range(0, top_num):
        print_one_post_data(top_posts_data[i], i+1, top_num, flag, uid)

def print_line_to_file(uid, num_friends, num_common_friends, num_followers, num_posts, num_max_likes, num_max_comments, num_max_reposts):
    with open('data.csv' 'w+') as fp:
        fp.write(uid, num_friends, num_common_friends, num_followers, num_posts, num_max_likes, num_max_comments, num_max_reposts)
        fp.close()

target_uid = '5887277'
default_id = '1844128'
get_user(default_id)
get_user_friends(default_id)
get_common_friends(str(default_id), target_uid)
get_user_followers(default_id)
total_posts, posts = get_wall_posts(default_id)
print str(total_posts) + ' posts'

# flag = 'likes'
# get_max_post(default_id, posts, total_posts, flag)
flag = 'comments'
top_num = 5
top_posts = get_max_post(default_id, posts, total_posts, flag, top_num)
print top_posts
print_top_posts(top_posts, flag, top_num, default_id)

# print_line_to_file(int(default_id), num_friends, num_common_friends, num_followers, num_posts, num_max_likes, num_max_comments, num_max_reposts)
# flag = 'reposts'
# get_max_post(default_id, posts, total_posts, flag)

# posts = get_wall_posts(default_id, 100)

#print 'TOP post: http://vk.com/id%s?w=wall%s_%s' % ( user_id'], top_users[i]['user_id'], top_users[i]['top_posts'][0]['id'] )
# posts[i]['id']
# posts[i]['comments']['count']
# posts[i]['likes']['count']
# posts[i]['reposts']['count']