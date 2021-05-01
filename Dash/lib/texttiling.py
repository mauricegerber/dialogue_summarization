import re
import numpy as np

# based on https://www.nltk.org/_modules/nltk/tokenize/texttiling.html

def texttiling(transcript, stopwords, w, k, n, min_boundary_distance=20):

    class TokenSequence(object):
        def __init__(self, index, word_list):
            self.__dict__.update(locals())
            del self.__dict__["self"]

    class TokenTable(object):
        def __init__(self, total_count, ts_occurrences, last_ts):
            self.__dict__.update(locals())
            del self.__dict__["self"]

    def divide_to_token_sequences(text):
        """Divides the text into pseudosentences of fixed size."""
        word_list = []
        matches = re.finditer("\w+", text)
        for match in matches:
            word_list.append((match.group(), match.start()))
        return [TokenSequence(int(i / w), word_list[i : i + w]) for i in range(0, len(word_list), w)]

    def create_token_table(token_sequences):
        """Creates a table of TokenTable."""
        token_table = {}
        current_ts = 0
        for ts in token_sequences:
            for word, index in ts.word_list:
                if word in token_table:
                    token_table[word].total_count += 1
                    if token_table[word].last_ts != current_ts:
                        token_table[word].last_ts = current_ts
                        token_table[word].ts_occurrences.append([current_ts, 1])
                    else:
                        token_table[word].ts_occurrences[-1][1] += 1
                else:
                    token_table[word] = TokenTable(
                        total_count=1,
                        ts_occurrences=[[current_ts, 1]],
                        last_ts=current_ts,
                    )
            current_ts += 1
        return token_table

    def block_comparison(token_sequences, token_table):
        """Implements the block comparison method."""
        def blk_frq(tok, block):
            ts_occs = filter(lambda o: o[0] in block, token_table[tok].ts_occurrences)
            freq = sum([tsocc[1] for tsocc in ts_occs])
            return freq

        gap_scores = []
        n_gaps = len(token_sequences) - 1

        for current_gap in range(n_gaps):
            score_dividend, score_divisor_b1, score_divisor_b2 = 0.0, 0.0, 0.0
            if current_gap < k - 1:
                window_size = current_gap + 1
            elif current_gap > n_gaps - k:
                window_size = n_gaps - current_gap
            else:
                window_size = k
            b1 = [ts.index for ts in token_sequences[current_gap - window_size + 1 : current_gap + 1]]
            b2 = [ts.index for ts in token_sequences[current_gap + 1 : current_gap + window_size + 1]]
            for t in token_table:
                score_dividend += blk_frq(t, b1) * blk_frq(t, b2)
                score_divisor_b1 += blk_frq(t, b1) ** 2
                score_divisor_b2 += blk_frq(t, b2) ** 2
            try:
                score = score_dividend / np.sqrt(score_divisor_b1 * score_divisor_b2)
            except ZeroDivisionError:
                pass
            gap_scores.append(score)
        
        return gap_scores

    def calculate_depth_scores(scores):
        """Calculates the depth of each gap, i.e. the average difference
        between the left and right peak and the gap's score."""
        depth_scores = [0 for x in scores]
        clip = 5
        index = clip
        for gapscore in scores[clip:-clip]:
            lpeak = gapscore
            for score in scores[index::-1]:
                if score >= lpeak:
                    lpeak = score
                else:
                    break
            rpeak = gapscore
            for score in scores[index:]:
                if score >= rpeak:
                    rpeak = score
                else:
                    break
            depth_scores[index] = lpeak + rpeak - 2 * gapscore
            index += 1
        return depth_scores

    def identify_boundaries(depth_scores):
        """Identifies boundaries at the peaks of similarity score differences."""
        boundaries = sorted(np.argsort(depth_scores)[-n:])
        removed_boundaries = []
        for i in range(1, len(boundaries)):
            if boundaries[i] <= boundaries[i-1] + min_boundary_distance:
                removed_boundaries.append(boundaries[i])
        boundaries = [b for b in boundaries if b not in removed_boundaries]
        return boundaries

    text = ""
    utterance_break = 0
    utterance_breaks = [0]
    # utterance_breaks are the position of the first letter of each utterance in the concatenated text
    for utterance in transcript["Utterance"].str.lower():
        text += utterance
        utterance_break += len(utterance)
        utterance_breaks.append(utterance_break)
    del utterance_breaks[-1]

    print(utterance_breaks)

    tokseqs = divide_to_token_sequences(text)
    for ts in tokseqs:
        ts.word_list = [wi for wi in ts.word_list if wi[0] not in stopwords]

    token_table = create_token_table(tokseqs)

    gap_scores = block_comparison(tokseqs, token_table)
    depth_scores = calculate_depth_scores(gap_scores)

    boundaries = identify_boundaries(depth_scores)

    print(boundaries)

    boundaries_last_word_index = []
    for ts in tokseqs:
        if ts.index in boundaries:
            boundaries_last_word_index.append(ts.word_list[-1][1])

    print(boundaries_last_word_index)

    normalized_boundaries = []
    for bi in boundaries_last_word_index:
        # calculate difference between current boundaries_last_word_index (bi) and all utterance_breaks (ub)
        diff = list(map(lambda ub: bi - ub, utterance_breaks))
        print(diff)
        # get index of smallest positive value from diff list
        # the reason for this procedure is that the boundaries calculated by the texttiling algorithm do not
        # necessarily match with the utterance breaks
        # one needs to define what happens when topic boundary is detected within one utterance
        # in this case, the utterance is added to the previous topic
        # more technical: if an utterance break occurs at text position 1000 and another one at position 1200
        # texttiling calculates a boundary at position 20 (the gap between pseudosentence 20 and 21)
        # now, the starting position of the last word in pseudosentence 20 is extracted which is 1100
        # the difference between the boundary and all utterance breaks is calculated which is [100, -100]
        # the index of the smallest positive value is extracted which is the one of the number 100, e.g. 10
        # this number means that the first topic includes utterances 0 to and with 10

        smallest_positive_value_index = max([i for i in range(len(diff)) if diff[i] > 0])
        print(smallest_positive_value_index)
        normalized_boundaries.append(smallest_positive_value_index)

    print(normalized_boundaries)

    return normalized_boundaries, depth_scores