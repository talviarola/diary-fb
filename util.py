#!/usr/bin/env python3

import unicodedata
import unittest
import re


# Loads text encoded with UTF8
def load(filename):
    f = open(filename, "rt", encoding="utf8")
    text = f.read()
    f.close()
    return text


def store(filename, text):
    f = open(filename, "wt", encoding="utf8")
    f.write(text)
    f.close()


def _replace(text: str, pattern, replacement):
    while True:
        m = re.search(pattern, text)
        if m is None:
            break

        m2 = re.search(r'$([1-9])', replacement)
        if m2:
            i = int(m2.group(1))
            r = replacement.replace(m2.group(0), m.group(i))
        else:
            r = replacement
        text = text.replace(m.group(0), r)
    return text


# Based on https://vsemozhetbyt.ucoz.ru/varia/word_count.html
def count_words(text):
    text = _replace(text, r'<.+?\btitle=(["\'])(.+?)\1.*?>', ' $2 ')
    text = _replace(text, r'\[.+?\btitle=(["\'])(.+?)\1.*?\]', ' $2 ')
    text = _replace(text, r'<.+?>', '')
    text = _replace(text, r'\[.+?\]', '')
    text = _replace(text, r'&#?\w+;', ' ')

    # for alphanum only: ['’\u002D\w\u0401\u0410-\u0451] instead of \S*
    m = re.findall(r'[\w\u0401\u0410-\u0451]\S*', text)
    return len(m)


def replace_word_counter(text, counter):
    m = re.search(r'\d+ слов[ао]?', text)
    if m is None:
        print("Warning: can't find word counter in the header file")
        return text
    d = counter % 10
    if d == 1:
        ending = "слово"
    elif d in [2, 3, 4]:
        ending = "слова"
    else:
        ending = "слов"
    s = str(counter) + " " + ending
    return text.replace(m.group(0), s)


def estimated_render(text):
    text = text.replace("\n", "<br>")

    pre = '<a href="https://fk-2018.diary.ru/p216265903.htm?oam#more1" class="LinkMore" onclick="var e=event; if (swapMore(&quot;216265903m1&quot;, e.ctrlKey || e.altKey)) document.location = this.href; return false;" id="linkmore216265903m1">'
    post = '</a><span id="more216265903m1" ondblclick="return swapMore(&quot;216265903m1&quot;);" style="display:none;"><a name="more216265903m1start"></a>'
    text = _replace(text, r'\[MORE=([^\]]+)\]', pre + "$1" + post)

    text = text.replace("[/MORE]", '<a name="more216265903m2end"></a></span>')

    text = _replace(text, r'\[L\]([^\]]*)\[/L\]', '<a class="TagL" href="https://$1.diary.ru" title="$1" target="_blank">$1</a>')

    text = text.replace('border="0" width="100%;"', 'width="100%;" border="0"')  # Don't ask...

    return text


def estimated_rendered_size(text):
    return len(estimated_render(text))


def fix_characters(text: str):
    try:
        text.encode("cp1251")
        return text
    except:
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.replace(chr(0x301), '&#769;')  # stress
    text = text.replace(chr(0x308), '&#776;')  # umlaut

    # TODO: fix this maybe
    #text = text.replace(' - ', ' &mdash; ')
    #text = text.replace("\n- ", "\n&mdash; ")
    text = text.replace(chr(0x2013), '&ndash;')
    text = text.replace(chr(0x2014), '&mdash;')
    text = text.replace(chr(0x2012), '&#8210;')
    text = text.replace(chr(0x2015), '&#8213;')

    text = text.replace('"', '&#34;')
    text = text.replace('«', '&#171;')
    text = text.replace('»', '&#187;')

    text = text.replace('©', '&#169;')
    text = text.replace('§', '&#167;')

    return text


class TestWordCounter(unittest.TestCase):
    def test_trivial(self):
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("два слова"), 2)

    def test_text1(self):
        text = load("tests/text1.txt")
        self.assertEqual(count_words(text), 1348)

    def test_text2(self):
        text = load("tests/text2.txt")
        self.assertEqual(count_words(text), 1348)

    def test_text3(self):
        text = load("tests/text3.txt")
        self.assertEqual(count_words(text), 9164)


class WeirdCharacters(unittest.TestCase):
    def test_trivial(self):
        self.assertEqual("", fix_characters(""))
        self.assertEqual("слово", fix_characters("слово"))

    def test_stress(self):
        self.assertEqual("Ударе&#769;ние", fix_characters("Ударе́ние"))

    def test_umlaut(self):
        self.assertEqual("Moto&#776;rhead", fix_characters("Motörhead"))

    def test_dash(self):
        self.assertEqual("l &mdash; Lol", fix_characters("l - Lol"))


if __name__ == "__main__":
    unittest.main()
