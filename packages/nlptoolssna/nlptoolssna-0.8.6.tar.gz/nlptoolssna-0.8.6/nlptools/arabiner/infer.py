import logging
# import argparse
from collections import namedtuple
from nlptools.arabiner.helpers import load_checkpoint
from nlptools.arabiner.data import get_dataloaders, text2segments
from nlptools.DataDownload import downloader
import os
logger = logging.getLogger(__name__)



def ner(text, model_path, batch_size=32):
    # Load tagger
    filename = 'Wj27012000/867530901NED20230418modelv28'
    path =downloader.get_appdatadir()
    model_path = os.path.join(path, filename)
    tagger, tag_vocab, train_config = load_checkpoint(model_path)

    # Convert text to a tagger dataset and index the tokens in args.text
    dataset, token_vocab = text2segments(text)

    vocabs = namedtuple("Vocab", ["tags", "tokens"])
    vocab = vocabs(tokens=token_vocab, tags=tag_vocab)

    # From the datasets generate the dataloaders
    dataloader = get_dataloaders(
        (dataset,),
        vocab,
        train_config.data_config,
        batch_size=batch_size,
        shuffle=(False,),
    )[0]

    # Perform inference on the text and get back the tagged segments
    segments = tagger.infer(dataloader)

    # Print results
    for segment in segments:
        s = [
            f"{token.text} ({'|'.join([t['tag'] for t in token.pred_tag])})"
            for token in segment
        ]
        print(" ".join(s))

