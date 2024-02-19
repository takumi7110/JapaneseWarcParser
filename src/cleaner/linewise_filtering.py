# https://github.com/lighttransport/japanese-llama-experiment/blob/main/03_clean_step3_linewise/linewise_filtering.py
import re
import unicodedata


class LinewiseFilter:

    def __init__(self):

        self.num_startswith_tuzuki = 0
        self.num_endswith_tuzuki = 0

    def remove_startswith_tuzuki(self, text):
        """
        行頭の「続きを読む」を削除する
        行頭が「続きを読むには...」などとつながる文はあまりないようである.
        よりきちんとやるには形態素解析などして「続きを読む」と自然につながる文章の場合は削除しないようにする.
        """

        startswith_list = [
            '続きを読む', '[続きを読む]', '(続きを読む)', '続きをみる', '続きを見る', '[続きを見る]', '(続きを表示)', '・・・ 続きを読む']

        for s in startswith_list:
            if text.startswith(s):
                text = text[len(s):]
                self.num_startswith_tuzuki += 1

        return text

    def remove_contains(self, doc):
        """
        文中に特定のワードがあれば doc を除去
        """

        words = ['...(続きを表示)', '[ 続きを見る ]', '・・・続きを見る', '... 続きを読む']

        for word in words:
            for line in doc:
                if word in line:
                    return None

        return doc

    def remove_endswith_tuzuki(self, text):
        """
        行末の「続きを読む」を削除する
        """

        endswith_list = [
            '続きを読む', '[続きを読む]', '(続きを読む)', '続きを見る', '続きをみる', '(続く)', '(続きを表示)', '(続きをみる)', '[続きをみる]', '[続きを見る]']

        for e in endswith_list:
            if text.endswith(e):
                text = text[:-len(e)]
                self.num_endswith_tuzuki += 1

        return text

    def endswith_leading_dots(self, text):
        """
        各種処理したあとに文末が `...` で終わっているかチェック.
        文末が `...` で終わっている場合は文章が切れている場合がほとんどなので, document ごと削除がよいでしょう
        """

        if text.endswith("..."):
            return True
        if text.endswith("... "):
            return True
        if text.endswith("...　"):
            return True

        return False

    def proc_doc(self, lines):
        """
        Document(複数行)に対して一式処理を行う

        Returns:
            無効な document と判別した場合は None をかえす
        """

        in_lines = lines

        for i, in_line in enumerate(in_lines):
            line = in_line

            line = self.remove_startswith_tuzuki(line)
            line = self.remove_endswith_tuzuki(line)

            lines[i] = line

        for line in lines:
            if self.endswith_leading_dots(line):
                return None

        lines = self.remove_contains(lines)

        return lines


def test():
    lwfilter = LinewiseFilter()

    text = "続きを読む他のユーザーは"
    print(lwfilter.remove_startswith_tuzuki(text))

    text = "続きを読む \"他のユーザー\"は"
    print(lwfilter.remove_startswith_tuzuki(text))

    text = "... 続きを読む"
    print(lwfilter.remove_endswith_tuzuki(text))

    doc = ["aa ...(続きを表示)bb"]
    print(lwfilter.remove_contains(doc))

    doc = ["aa ...(続きを表bb"]
    print(lwfilter.remove_contains(doc))


lwfilter = LinewiseFilter()


def do_filter(text):
    """
    この関数は、LinewiseFilter.proc_doc に置き換えられる
    """
    if text is None:
        return None

    lines = text.split('\n')

    ret = lwfilter.proc_doc(lines)
    if ret is None:
        return None
    else:
        return "\n".join(ret)
