import os
from enum import Enum
from functools import lru_cache
from typing import Type, List, cast

import blingfire
from collections_extended import RangeMap
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.processor import ProcessorParameters, ProcessorBase
from pymultirole_plugins.v1.schema import Document, Sentence


class ChunkingUnit(str, Enum):
    character = "character"
    token = "token"


class TokenModel(str, Enum):
    wbd = "wbd"
    bert_base_tok = "bert_base_tok"
    bert_base_cased_tok = "bert_base_cased_tok"
    bert_chinese = "bert_chinese"
    bert_multi_cased = "bert_multi_cased"
    xlm_roberta_base = "xlm_roberta_base"
    gpt2 = "gpt2"
    roberta = "roberta"
    laser100k = "laser100k"
    laser250k = "laser250k"
    laser500k = "laser500k"


class ChunkSentencesParameters(ProcessorParameters):
    unit: ChunkingUnit = Field(
        ChunkingUnit.character,
        description="""Which chunking unit to use to compute boundaries, can be one of:<br/>
                            <li>`character`: group consecutive sentences until their size is just below `chunk_char_max_length` characters.
                            <li>`token`: group consecutive sentences until their size is just below `chunk_token_max_length` tokens.""")

    model: TokenModel = Field(
        TokenModel.wbd,
        description="""Which [Blingfire tokenization](
                            https://github.com/microsoft/BlingFire) model to use, can be one of:<br/>
                            <li>`wbd`: Default Tokenization Model - Pattern based
                            <li>`bert_base_tok`: BERT Base/Large - WordPiece
                            <li>`bert_base_cased_tok`: BERT Base/Large Cased - WordPiece
                            <li>`bert_chinese`: BERT Chinese - WordPiece
                            <li>`bert_multi_cased`: BERT Multi Lingual Cased - WordPiece
                            <li>`xlm_roberta_base`: XLM Roberta Tokenization - Unigram LM
                            <li>`gpt2`: Byte-BPE tokenization model for GPT-2 - byte BPE
                            <li>`roberta`: Byte-BPE tokenization model for Roberta model - byte BPE
                            <li>`laser100k`: Trained on balanced by language WikiMatrix corpus of 80+ languages - Unigram LM
                            <li>`laser250k`: Trained on balanced by language WikiMatrix corpus of 80+ languages - Unigram LM
                            <li>`laser500k`: Trained on balanced by language WikiMatrix corpus of 80+ languages - Unigram LM""",
        extra="advanced")
    chunk_char_max_length: int = Field(
        1024, description="Maximum size of chunks (number of characters)"
    )
    chunk_token_max_length: int = Field(
        128, description="Maximum size of chunks (number of tokens)"
    )


class ChunkSentencesProcessor(ProcessorBase):
    """Group sentences by chunks of given max length.
    To be used in a segmentation pipeline."""

    def process(
            self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        params: ChunkSentencesParameters = cast(ChunkSentencesParameters, parameters)
        for document in documents:
            sentences = []
            for cstart, cend in self.group_sentences(document.text, document.sentences,
                                                     params):
                sentences.append(Sentence(start=cstart, end=cend))
            if len(sentences) == 0:
                sentences.append(Sentence(start=0, end=len(document.text)))
            document.sentences = sentences
        return documents

    @classmethod
    def group_sentences(cls, text: str, sentences: List[Sentence], params: ChunkSentencesParameters):
        uncase = 'bert' in params.model.value and 'cased' not in params.model.value
        h = get_blingfire(params.model.value) if params.unit == ChunkingUnit.token else None
        chunk_size = params.chunk_token_max_length if params.unit == ChunkingUnit.token else params.chunk_char_max_length
        chunks = RangeMap()
        start = 0
        text_length = 0 if params.unit == ChunkingUnit.token else len(text)
        for sent in sentences:
            if h is not None:
                stext = text[sent.start:sent.end].lower() if uncase else text[sent.start:sent.end]
                tokens = cls.tokenize_with_model(h, stext)
                text_length += len(tokens)
                end = start + len(tokens)
                chunks[start:end] = WrappedSentence(sent, start=start, end=end)
                start = end
            else:
                chunks[sent.start:sent.end] = WrappedSentence(sent)

        cstart = 0
        cend = 0
        while cend < text_length:
            ranges = chunks.get_range(cstart, cstart + chunk_size)
            if ranges.start is None or ranges.end is None:
                break
            chunk = list(ranges.values())
            csstart = chunk[0].sentence.start
            cend = chunk[0].end
            csend = chunk[0].sentence.end
            if len(chunk) > 0:
                if ranges.end == chunk[-1].end:
                    cend = chunk[-1].end
                    csend = chunk[-1].sentence.end
                elif len(chunk) > 1:
                    cend = chunk[-2].end
                    csend = chunk[-2].sentence.end
            yield (csstart, csend)
            cstart = cend

    @classmethod
    def tokenize_with_model(cls, model, stext):
        tokens = blingfire.text_to_ids(model, stext, len(stext), unk=0,
                                       no_padding=True) if model != -1 else blingfire.text_to_words(
            stext).split(' ')
        return tokens

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return ChunkSentencesParameters


class WrappedSentence:
    def __init__(self, sentence: Sentence, start=None, end=None):
        self.sentence = sentence
        self.start = start or sentence.start
        self.end = end or sentence.end


@lru_cache(maxsize=None)
def get_blingfire(model: str):
    # load a provided with the package model
    if model == TokenModel.wbd.value:
        return -1
    h = blingfire.load_model(os.path.join(os.path.dirname(blingfire.__file__), f"{model}.bin"))
    return h
