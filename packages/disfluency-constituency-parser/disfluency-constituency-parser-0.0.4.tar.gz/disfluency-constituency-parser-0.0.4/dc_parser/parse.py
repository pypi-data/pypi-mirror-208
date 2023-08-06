from typing import List
import torch
import logging
from . import parse_nk
from .utils import preprocess_sentence

logger = logging.getLogger(__name__)


class DC_Model:
    def __init__(
            self,
            model_path: str,
            bert_model_path: str,
            bert_vocab_path: str,
            device: str = "auto",
    ):
        """Initialize the disfluency constituency parsing model

        Args:
            model_path: path to the pre-training parsing model
            bert_model_path: path to the bert model
            bert_vocab_path: path to the bert model vocabulary file
            device: Device to use for computation ("cpu", "cuda", "auto").
        """
        if device == "auto":
            use_cuda = torch.cuda.is_available()
        elif device == "cuda":
            if not torch.cuda.is_available():
                logger.info("CUDA is not available, device is det to CPU.")
                use_cuda = False
            else:
                use_cuda = True
        else:
            use_cuda = False

        logger.info("Loading model from {}...".format(model_path))
        assert model_path.endswith(".pt"), "Only support pytorch savefiles"

        if use_cuda:
            model = torch.load(model_path)
        else:
            model = torch.load(
                model_path,
                map_location=lambda storage,
                                    location: storage,
            )
        assert "hparams" in model["spec"], "Older savefiles are not supported"
        self.parser = parse_nk.NKChartParser.from_spec(
            model["spec"],
            model["state_dict"],
            bert_model_path,
            bert_vocab_path,
            use_cuda,
        )

    def parse(self, sentences: List[str], eval_batch_size: int = 1) -> List[str]:
        """

        Args:
            sentences: a list of sentences (utf-8 strings) to parse.
            eval_batch_size: the number of sentences to parse at a time.

        Returns:
            A list of parsed trees (in flattened strings), one per input sentence.
            e.g. ['(S (NP (UNK today)) (VP (UNK is) (NP (UNK a) (ADJP (UNK very) (UNK good)) (UNK day))))']
        """
        sentences = [preprocess_sentence(s) for s in sentences]
        words_list = [s.split() for s in sentences]

        # Tags are not available when parsing from raw text, so use a dummy tag
        if "UNK" in self.parser.tag_vocab.indices:
            dummy_tag = "UNK"
        else:
            dummy_tag = self.parser.tag_vocab.value(0)

        all_predicted = []
        for start_index in range(0, len(words_list), eval_batch_size):
            subbatch_sentences = words_list[start_index:start_index + eval_batch_size]
            subbatch_sentences = [[(dummy_tag, word) for word in sentence] for sentence in subbatch_sentences]
            print(subbatch_sentences)
            predicted, _ = self.parser.parse_batch(subbatch_sentences)
            del _
            all_predicted.extend([p.convert() for p in predicted])

        parse_trees = []
        for tree in all_predicted:
            linear_tree = tree.linearize()
            parse_trees.append(linear_tree)

        return parse_trees
