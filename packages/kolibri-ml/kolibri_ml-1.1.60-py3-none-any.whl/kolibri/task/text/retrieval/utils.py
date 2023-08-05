from kolibri.tokenizers import tokenize_sentences

def find_answer_sentence(answer_pos: int, context: str) -> str:
    answer_sentence = ""
    context_sentences = tokenize_sentences(context)
    start = 0
    context_sentences_offsets = []
    for sentence in context_sentences:
        end = start + len(sentence)
        context_sentences_offsets.append((start, end))
        start = end + 1

    for sentence, (start_offset, end_offset) in zip(context_sentences, context_sentences_offsets):
        if start_offset < answer_pos < end_offset:
            answer_sentence = sentence
            break

    return answer_sentence
