#!/usr/bin/env python3

import util


def find_header(text_with_header):
    if "<b>Для голосования:</b>" not in text_with_header:
        raise Exception("Шапка не найдена (<b>Для голосования:</b>)")

    a = text_with_header.split("\n")
    for (i, line) in enumerate(a):
        if line.startswith("<b>Для голосования:</b>"):
            header = "\n".join(a[:i+1])
            text = "\n".join(a[i+1:])
            return header, text.strip()


def split_text_with_comments(_header, text):
    global header
    header = _header
    post_text, rest = find_max_split(text, post_criterion)
    post = compile_post(post_text)
    comments = []
    while len(rest) > 0:
        part1, part2 = find_max_split(rest, comment_criterion)
        comments.append(compile_comment(part1))
        rest = part2
    return post, comments


def split_text_with_posts(_header, text):
    global header
    header = _header
    posts = []

    while len(text) > 0:
        post_text, text = find_max_split(text, post_criterion)
        post = compile_post(post_text)
        posts.append(post)
        header = None
    return posts


def find_max_split(text, criterion):
    if criterion(text):
        return text, ""
    a = text.split("\n")

    good_split = None
    for i in range(len(a) - 1):
        part1 = "\n".join(a[:i])
        part2 = "\n".join(a[i:])
        if criterion(part1):
            good_split = (part1, part2)
        else:
            return good_split


def post_criterion(text):
    post = compile_post(text)
    if len(post) < 40000:
        return True
    if len(post) >= 61000:
        return False
    return util.estimated_rendered_size(post) < 0xF800


def comment_criterion(text):
    comment = compile_comment(text)
    return len(comment) < 10050


def compile_post(text):
    template = util.load("design/post.txt")
    post = template.replace("@BODY@", text)
    if header:
        post = post.replace("@HEADER@", header)
    else:
        # Subsequent posts do not have header, the "header" variable is set to None
        post = post.replace("@HEADER@\n\n", "")
        post = post.replace("@HEADER@\n", "")
        post = post.replace("@HEADER@", "")
    return post


def compile_comment(text):
    template = util.load("design/comment.txt")
    return template.replace("@BODY@", text)
