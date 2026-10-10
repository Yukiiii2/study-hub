import re

STOP_WORDS = frozenset("a an the is are was were be of to for and or in on at by with from what why how when which who explain please me this that these those does do can could would should summarize summary overview generate create quiz questions flashcards cards about give document documents pdf resource resources material materials uploaded selected".split())


def query_terms(prompt):
    words = re.findall(r"[^\W_]+", (prompt or "").casefold(), re.UNICODE)
    return list(dict.fromkeys(word for word in words if len(word) >= 3 and word not in STOP_WORDS))[:12]


def summary_request(prompt):
    words = set(re.findall(r"[a-z]+", (prompt or "").casefold()))
    return bool(words & {"summarize", "summary", "overview"}) and not query_terms(prompt)
