import spacy  # https://spacy.io
import en_core_web_sm

nlp = en_core_web_sm.load()

MODEL_NAME = 'en_core_web_sm'
try:
    nlp = spacy.load(MODEL_NAME)
except Exception:
    spacy.cli.download(MODEL_NAME)
    nlp = spacy.load(MODEL_NAME)
