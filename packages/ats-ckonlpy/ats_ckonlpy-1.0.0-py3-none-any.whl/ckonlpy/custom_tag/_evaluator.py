class SimpleEvaluator:
    def __init__(self, preference=None, tagset=None):
        # self.weight = (
        # ('max_length_of_noun', 0.5),
        # ('length_of_phrase', 0.1),
        # ('exist_noun', 0.2),
        # ('single_word', -0.1),
        # ('has_force_tag', 10)
        # )

        ###### customize
        self.weight = (
            ('num_nics', 0.3),
            ('num_nouns', -0.2),
            ('num_names', 0.4),
            ('num_words', -0.5),
            ('num_not_words', -0.7),
            ('len_word', 0.7),
        )

        # preference = { (word, pos) : score }
        self.preference = preference if preference else {}
        self.tagset = tagset if tagset else {}
        self.debug = False

    def select(self, candidates):

        def evaluating_format(wordpos_list):
            formed = (
                wordpos_list,
                wordpos_list[0][2],
                wordpos_list[-1][3],
                self.evaluate(wordpos_list)
            )
            return formed

        def is_overlab(b, e, target):
            return (b < target[2]) and (target[1] < e)

        scoreds = [evaluating_format(c) for c in candidates]

        ## sorting rules. (score, begin index)
        scoreds = sorted(scoreds, key=lambda x: (-x[3], x[1]))

        selected = []
        while scoreds:
            selected.append(scoreds.pop(0))
            b = selected[-1][1]
            e = selected[-1][2]
            scoreds = [c for c in scoreds if not is_overlab(b, e, c)]

        ### sort by begin index
        selected = sorted(selected, key=lambda x: x[1])
        return selected

    ###### customize
    def evaluate(self, candidate):
        num_nics = len([word for word, pos, begin, e in candidate if pos == 'Nic'])  # 닉 단어 개수
        num_nouns = len([word for word, pos, begin, e in candidate if pos == 'Noun'])  # 명사 단어 개수
        num_names = len([word for word, pos, begin, e in candidate if pos == 'Name'])  # 이름 단어 개수
        num_not_words = len(
            [word for word, pos, begin, e in candidate if pos not in ['Noun', 'Nic', 'Name']])  # 명사 닉 이름 외 단어 개수
        len_word = max([e - begin for word, pos, begin, e in candidate])  # 단어중 제일 길이가 긴거

        num_words = len(candidate)  # 모든 단어개수
        has_no_nics = (num_nics != 0)  # 닉여부 확인
        has_no_names = (num_names != 0)  # 이름여부 확인
        has_no_not_words = (num_not_words != 0)  # 닉, 이름, 명사외 품사여부 확인

        scores = (num_nics, num_nouns, num_words, num_names, num_not_words, len_word)

        # 스코어와 웨이트를 곱한것의 합
        score = sum((score * weight for score, (_, weight) in zip(scores, self.weight)))

        if has_no_names:
            for i in [word for word, pos, begin, e in candidate if pos == 'Name']:
                score += 0.5
        if has_no_nics:
            for i in [word for word, pos, begin, e in candidate if pos == 'Nic']:
                score += 0.5
        if has_no_not_words:
            for i in [word for word, pos, begin, e in candidate if pos not in ['Noun', 'Nic', 'Name']]:
                score -= 0.5
                # print('candidate is ', candidate, score)
        return score

        # def evaluate(self, wordpos_list):

        # scores = (
        # _max_length_of_noun(wordpos_list),
        # wordpos_list[-1][3] - wordpos_list[0][2],
        # _num_of_nouns(wordpos_list) > 0,
        # _num_of_words(wordpos_list) == 1,
        # _has_force_tag(wordpos_list, self.tagset)
        # )

        # score_sum = _wordpos_preference(wordpos_list, self.preference)

        # if self.debug:
        # print('\n{}'.format(wordpos_list))
        # for score, (field, weight) in zip(scores, self.weight):
        # print('{}, w={}, s={}, prod={}'.format(
        # field, weight, score, weight * score))
        # print('preference score = {}'.format(score_sum))

        # score_sum += sum((score * weight for score, (_, weight)
        # in zip(scores, self.weight)))

        # return score_sum


def _max_length_of_noun(wordpos_list):
    satisfied = [len(wordpos[0]) for wordpos in wordpos_list if wordpos[1] == 'Noun']
    return max(satisfied) if satisfied else 0


def _num_of_nouns(wordpos_list):
    return len([wordpos for wordpos in wordpos_list if wordpos[1] == 'Noun'])


def _num_of_words(wordpos_list):
    return len(wordpos_list)


def _wordpos_preference(wordpos_list, preference):
    score = 0
    for word, pos, _, _ in wordpos_list:
        score += preference.get((word, pos), 0)
    return score


def _has_force_tag(wordpos_list, tagset):
    return len([wordpos for wordpos in wordpos_list if not (wordpos[1] in tagset)]) > 0