from keras.layers import Input
from keras.models import Model
from keras import backend as K
from .. import layers
from .. import utils

class Transformer(Model):
    """Classic Transformer implementation.
    args:
        - sequence_len: Length of the input sequence
        - embedding_dim: Dimensions of input_embedding and outpute_mbedding
        - num_heads: Number of heads in a multi head attention layer
        - hidden_dim: Dimensions of queries, keys, and values for each attention head 
        - linear_dim: Dimension of Linear projection of feedforward
        - encoder_depth: Number of encoder_block stacks
        - decoder_depth: Number of decoder_block stacks
        - dropout: Dropout probability, default to 0.1
        - activation: Activation function of feedforward layer, default to "leaky_relu"
        - vocabulary_size: Size of vocabulary,  it is equal to the output dimension of the decoder
        - parameter_sharing: Whether to share parameters of input_embedding, output_embedding and linear, default to True
        - posencoding_learnable: Whether to use learnable position encoding, default to False
        - padding: Padding values in the input sequence, default to 0.
    call args:
        - inputs: List of encoder and decoder inputs, shape: [(batch, sequence_len), (batch, sequence_len)]
    """
    def __init__(
        self, 
        sequence_len, 
        embedding_dim, 
        num_heads,
        hidden_dim,
        linear_dim,
        encoder_depth,
        decoder_depth,
        dropout=0.1,
        activation="leaky_relu",
        vocabulary_size=1e4,
        parameter_sharing=True,
        posencoding_learnable=False,
        padding=0.,
        **kwargs
        ):
        super().__init__(**kwargs)
        self.sequence_len = sequence_len
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        self.hidden_dim = hidden_dim
        self.linear_dim = linear_dim
        self.encoder_depth = encoder_depth
        self.decoder_depth = decoder_depth
        self.dropout = dropout
        self.activation = activation
        self.vocabulary_size = vocabulary_size
        self.parameter_sharing = parameter_sharing
        self.posencoding_learnable = posencoding_learnable
        self.padding = padding
        self.build([(None, self.sequence_len), (None, self.sequence_len)])

    def build(self, input_shape):
        if self.parameter_sharing:
            self.input_embedding=layers.Embedding(self.vocabulary_size, self.embedding_dim, name="shared_embedding")
            self.output_embedding=self.input_embedding
        else:
            self.input_embedding=layers.Embedding(self.vocabulary_size, self.embedding_dim, name="input_embedding")
            self.output_embedding=layers.Embedding(self.vocabulary_size, self.embedding_dim, name="output_embedding")
        self.position_encoding=layers.PositionalEncoding(self.posencoding_learnable, name="get_positiaonal_encoding")
        self.encoders = [
            layers.TransformerEncoderBlock(
                self.num_heads,
                self.hidden_dim,
                self.linear_dim,
                self.dropout,
                self.activation,
                name=f"encoder_blockd_{i}"
                ) for i in range(self.encoder_depth)
            ]
        self.decoders = [
            layers.TransformerDecoderBlock(
                self.num_heads,
                self.hidden_dim,
                self.linear_dim,
                self.dropout,
                self.activation,
                name=f"decoder_blockd_{i}"
                ) for i in range(self.decoder_depth)
            ]
        if not self.parameter_sharing:
            self.linear = layers.Linear(self.vocabulary_size, name="linear")
        super().build(input_shape)
        self.call([Input((shape[1:])) for shape in input_shape])


    def call(self, inputs):
        encoder_inputs, decoder_inputs = inputs
        padding_mask = utils.get_padding_mask(encoder_inputs, self.padding)
        sequence_mask = utils.get_sequence_mask(decoder_inputs)
        encoder_x = self.input_embedding(encoder_inputs)
        decoder_x = self.output_embedding(decoder_inputs)
        encoder_x += self.position_encoding(encoder_x)
        decoder_x += self.position_encoding(decoder_x)

        for block in self.encoders:
            encoder_x = block(encoder_x, padding_mask)
        
        for block in self.decoders:
            decoder_x = block(decoder_x, encoder_x, sequence_mask, padding_mask)

        if not self.parameter_sharing:
            decoder_y = self.linear(decoder_x)
        else:
            decoder_y = K.dot(decoder_x, K.transpose(self.input_embedding.weights[0]))
        return K.softmax(decoder_y)      