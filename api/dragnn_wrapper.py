from __future__ import print_function, unicode_literals

import os
import warnings

import tensorflow as tf
from dragnn.protos import spec_pb2
from dragnn.python import graph_builder, spec_builder
from google.protobuf import text_format
from syntaxnet import sentence_pb2
from syntaxnet.ops import gen_parser_ops

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

warnings.filterwarnings("ignore", message="Conversion of the second argument")


class SyntaxNet(object):
    def __init__(self, lang="English", model_dir="/usr/local/tfmodels/"):
        tf.logging.set_verbosity(tf.logging.ERROR)
        segmenter_path = os.path.join(model_dir, lang, "segmenter")
        parser_path = os.path.join(model_dir, lang)
        self.segmenter = self._load_model(segmenter_path, "spec.textproto")
        self.parser = self._load_model(parser_path, "parser_spec.textproto")

    def parse(self, sentence):
        return [
            {
                "word": token.word,
                "label": token.label,
                "attributes": self._parse_attribute(token.tag),
                "head": token.head + 1,
            }
            for token in self._annotate(sentence).token
        ]

    def _load_model(self, base_dir, master_spec_name):
        master_spec = spec_pb2.MasterSpec()
        with open(os.path.join(base_dir, master_spec_name)) as f:
            text_format.Merge(f.read(), master_spec)
        spec_builder.complete_master_spec(master_spec, None, base_dir)

        graph = tf.Graph()
        with graph.as_default():
            hyperparam_config = spec_pb2.GridPoint()
            builder = graph_builder.MasterBuilder(
                master_spec,
                hyperparam_config
            )
            annotator = builder.add_annotation(enable_tracing=True)
            builder.add_saver()

        sess = tf.Session(graph=graph)
        with graph.as_default():
            builder.saver.restore(sess, os.path.join(base_dir, "checkpoint"))

        def annotate_sentence(sentence):
            with graph.as_default():
                return sess.run(
                    [annotator['annotations'], annotator['traces']],
                    feed_dict={annotator['input_batch']: [sentence]}
                )
        return annotate_sentence

    def _parse_attribute(self, attributed_tag):
        '''
        ex) attribute { name: \"Case\" value: \"Nom\" }
            attribute { name: \"Number\" value: \"Sing\" }
            attribute { name: \"Person\" value: \"1\" }
            attribute { name: \"PronType\" value: \"Prs\" }
            attribute { name: \"fPOS\" value: \"PRP++PRP\" }
        =>
            {'Case':'Nom', ..., 'fPOS':'PRP++PRP'}
        '''
        return {
            line.strip().split('\"')[1]: line.strip().split('\"')[3]
            for line in attributed_tag.split("attribute")
            if line
        }

    def _annotate(self, text):
        sentence = sentence_pb2.Sentence(
            text=text,
            token=[sentence_pb2.Token(word=text, start=-1, end=-1)]
        )
        with tf.Session(graph=tf.Graph()) as tmp_session:
            char_input = gen_parser_ops.char_token_generator([
                sentence.SerializeToString()
            ])
            preprocessed = tmp_session.run(char_input)[0]

        segmented, _ = self.segmenter(preprocessed)
        annotations, traces = self.parser(segmented[0])

        assert len(annotations) == 1
        assert len(traces) == 1

        return sentence_pb2.Sentence.FromString(annotations[0])
