import numpy as np
import torch
from sentence_transformers import util
from sentence_transformers.SentenceTransformer import SentenceTransformer
from transformers import AutoModel, AutoTokenizer

import autumn8

query = "How many people live in London?"
docs = [
    "Around 9 Million people live in London",
    "London is known for its financial district",
]

# Load the model
model = SentenceTransformer("sentence-transformers/multi-qa-mpnet-base-dot-v1")
tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/multi-qa-mpnet-base-dot-v1"
)


def preprocess(texts):
    query, docs = texts
    encoded_query = tokenizer(
        query, padding=True, truncation=True, return_tensors="pt"
    )
    encoded_docs = tokenizer(
        docs, padding=True, truncation=True, return_tensors="pt"
    )
    return (encoded_query, encoded_docs)


def model_func(input):
    query, docs = input
    doc_emb = model(docs)["sentence_embedding"]
    query_emb = model(query)["sentence_embedding"]
    return (query_emb, doc_emb)


def postprocess(model_output):
    query_emb, doc_emb = model_output
    # Compute dot score between query and all document embeddings
    scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()

    # Combine docs & scores
    doc_score_pairs = list(zip(docs, scores))

    # Sort by decreasing score
    doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)

    # Output passages & scores
    for doc, score in doc_score_pairs:
        print(score, doc)

    return doc_score_pairs


autumn8.lib.attach_model(
    model_func,
    (query, docs),
    preprocess=preprocess,
    postprocess=postprocess,
    interns=[],
    externs=[
        "torch",
        "torchvision",
        "sentence_transformers",
        "sentence_transformers.SentenceTransformer",
        "sentence_transformers.util",
        "jinja",
        "huggingface_hub",
        "yaml",
        "transformers.models.mpnet.modeling_mpnet",
        "tensorflow",
        "transformers.activations",
        "transformers.models.mpnet.configuration_mpnet",
        "transformers.models.mpnet.tokenization_mpnet_fast",
        "tokenizers",
        "tokenizers.models",
        "requests",
        "numpy",
        "transformers",
        "tqdm.autonotebook",
        "sys",
        "packaging.version",
        "requests.exceptions",
        "filelock",
        "tqdm",
        "tqdm.auto",
        "_io",
        "requests.auth",
        "tensorboard.summary._tf.summary",
    ],
)
