import re


def preprocess_sentence(sentence: str):
    sentence = sentence.replace("_", " ")
    sentence = sentence.replace(".", "")
    sentence = sentence.replace(",", "")
    sentence = sentence.replace(";", "")
    sentence = sentence.replace("?", "")
    sentence = sentence.replace("!", "")
    sentence = sentence.replace(":", "")
    sentence = sentence.replace("\"", "")
    sentence = sentence.replace("'re", " 're")
    sentence = sentence.replace("'ve", " 've")
    sentence = sentence.replace("n't", " n't")
    sentence = sentence.replace("'ll", " 'll")
    sentence = sentence.replace("'d", " 'd")
    sentence = sentence.replace("'m", " 'm")
    sentence = sentence.replace("'s", " 's")
    sentence = re.sub("[ ]{2,}", " ", sentence)
    sentence = sentence.strip()
    sentence = sentence.lower()
    return sentence