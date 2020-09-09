import os
import errno
import time
import csv
import calmap
import praw
import numpy as np
import pandas as pd
from pytz import timezone
import matplotlib.pyplot as plt
from collections import defaultdict


def scrape_posts(reddit, subreddit, posts_file):
    
    if not os.path.exists(os.path.dirname(posts_file)):
            try:
                os.makedirs(os.path.dirname(posts_file))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    with open(posts_file, "a",  encoding="utf-8") as outfile:
            for submission in reddit.subreddit(subreddit).top('year', limit=1000):
                print("\r", submission.title, end='')
                data = [
                    submission.title,
                    submission.author,
                    submission.created_utc,
                    submission.score,
                    submission.domain,
                    "%r" % submission.selftext,
                    submission.id,
                    submission.upvote_ratio
                ]
                writer = csv.writer(outfile)
                writer.writerow(data)
                time.sleep(1)
                
                
def get_comments(reddit, headlines_file, comments_file):
    '''Gets the top 100 comments of each top 1000 post of subreddit'''
    print("Fetching comments")
    with open(headlines_file, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        resume_flag = 0
        row_counter = 0

        for row in reader:
            if len(row) == 0:
                continue
            
            post_id = str(row[6])
            row_counter+=1

            if post_id == "6am00f":
                resume_flag = 1
            # was originally if not resume_flag
            if resume_flag:
                continue

            submission = reddit.submission(id=post_id)
            submission.comments.replace_more(limit=30, threshold=10)

            comment_count = 0

            for comment in submission.comments.list():
                if comment_count >= 100:
                    break

                if isinstance(comment, praw.models.MoreComments):
                    comment_count += 1
                    continue

                comment_str = comment.body

                comment_count += 1

                if comment_str == "[deleted]" or comment_str == "[removed]":
                    continue

                with open(comments_file, "a",  encoding="utf-8") as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow(["%r" % comment_str, post_id]) 
                 
                # with open(comments_file, "a") as outfile:
                    # outfile.write(comment_str)
                    # outfile.write("\n")
                    
                 
            print("\rFinished post:", post_id, "Row count: ", row_counter, end='')
            time.sleep(1)
            

def clear_file(file_path):
    with open(file_path, "w+") as file:
        file.close()