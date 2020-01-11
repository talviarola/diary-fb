#!/usr/bin/env python3

import util

# text = util.load("tests/text_midi.txt")
# header = util.load("tests/text_midi_hdr.txt")
# word_count = util.count_words(text)
# print("Words:", word_count)
# util.estimated_rendered_size(text)
#
# header = util.replace_word_counter(header, word_count)


def main():
    post, comments = split_text_with_comments(header, text)
    print("comments:", len(comments))
    util.store("split_part1.txt", post)
    util.store("split_part2.txt", comments[0])


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
    if len(post) >= 62000:
        return False
    return util.estimated_rendered_size(post) < 65520


def comment_criterion(text):
    comment = compile_comment(text)
    return len(comment) < 10240


def compile_post(text):
    text_more = _wrap(text, "design/post_more.txt")
    if header:
        post_body = header + "\n\n" + text_more
    else:
        post_body = text_more
    post = _wrap(post_body, "design/post.txt")
    return post


def compile_comment(text):
    return _wrap(text, "design/comment.txt")


def _wrap(text, template):
    template = util.load(template)
    return template.replace("@BODY@", text)


if __name__ == "__main__":
    main()
