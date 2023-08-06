from keras import layers
from keras import activations
from .. import utils


class Embedding(layers.Layer):
    def __init__(self, size, dim, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.dim = dim
        
    def build(self, input_shape):
        self.embedding=layers.Embedding(self.size, self.dim)
        return super().build(input_shape)

    def call(self, inputs):
        return self.embedding(inputs)


class PositionalEncoding(layers.Layer):
    """Positional encoding.
    args:
        - trainable=False: Can the weight parameters of position encoding be learned
    """
    def __init__(self, trainable=False, **kwargs):
        super().__init__(**kwargs)
        self.trainable = trainable

    def build(self, input_shape):
        if self.trainable:
            self.pe = self.add_weight(
                shape=(1,*input_shape[1:]),
                trainable=self.trainable
                )
        else:
            self.pe = utils.get_positional_encoding(
                pos=input_shape[1], 
                dim=input_shape[2]
                )
        return super().build(input_shape)

    def call(self, _):
        return self.pe


class MultiHeadAttention(layers.Layer):
    """MultiHeadAttention layer
    args:
        - num_heads: Number of heads in a multi head attention layer
        - hiddem_dim: Dimensions of queries, keys, and values for each attention head 
        - dropout: Dropout probability
    callargs:
        - query, shape like (B, T, dim)
        - value, shape like (B, S, dim)
        - key=None, shape like (B, S, dim)
        - attention_mask=None, shape like (B, T, S)
    """
    def __init__(
        self, 
        num_heads, 
        hiddem_dim, 
        dropout,
        **kwargs):
        super().__init__(**kwargs)
        self.num_heads = num_heads
        self.hiddem_dim = hiddem_dim
        self.dropout = dropout

    def build(self, input_shape):
        self.multi_head_attetion = layers.MultiHeadAttention(
            key_dim=self.hiddem_dim,
            num_heads=self.num_heads, 
            dropout=0.2,
            )
        return super().build(input_shape)

    def call(self, query, value, key=None, attention_mask=None):
        return self.multi_head_attetion(query, value, key=key, attention_mask=attention_mask)


class AddNorm(layers.Layer):
    """Add and Norm"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.layer_norm = layers.LayerNormalization(epsilon=1e-6)
        return super().build(input_shape)

    def call(self, inputs_a, inputs_b):
        return self.layer_norm(inputs_a + inputs_b)


class FeedForward(layers.Layer):
    """FeedForward layer for encoder and decoder.
    args:
        - linear_dim: Dimension of the first linear projection
        - output_dim=None: The Dimension of the Second Linear Projection
        - activation=None: Activation function of the first linear projection
    """
    def __init__(
        self, 
        linear_dim, 
        output_dim=None, 
        activation=None,
        **kwargs):
        super().__init__(**kwargs)
        self.linear_dim = linear_dim
        self.output_dim = output_dim
        self.activation = activations.get(activation)

    def build(self, input_shape):
        if self.output_dim is None:
            self.output_dim = input_shape[-1]
        self.linear_1 = layers.Dense(self.linear_dim, self.activation)
        self.linear_2 = layers.Dense(self.output_dim)
        return super().build(input_shape)

    def call(self, inputs):
        x = self.linear_1(inputs)
        x = self.linear_2(x)
        return x


class Linear(layers.Layer):
    """linear projection
    args:
        - output_dim: Linear projection output dimension
        - use_bias=False: Whether to use bias
    """
    def __init__(self, output_dim, use_bias=False, **kwargs):
        super().__init__(**kwargs)
        self.output_dim = output_dim
        self.use_bias = use_bias

    def build(self, input_shape):
        self.linear = layers.Dense(self.output_dim, use_bias=self.use_bias)
        return super().build(input_shape)

    def call(self, inputs):
        return self.linear(inputs)


class TransformerEncoderBlock(layers.Layer):
    """Classic Transformer Encoder Block.
    args:
        - num_heads: The number of heads in a multi head attention layer
        - hidden_dim: Dimensions of queries, keys, and values for each attention head 
        - linear_dim: The linear projection dimension of feedforward
        - dropout: Default to 0.1
        - activation: Activation function of feedforward layer
    call args:
        - inputs, shape like (B, T, dim)
        - padding_mask=None, shape like (B, T, T)
    """
    def __init__(
        self, 
        num_heads,
        hidden_dim,
        linear_dim,
        dropout=0.1,
        activation="leaky_relu",
        **kwargs
        ):
        super().__init__(**kwargs)
        self.num_heads = num_heads
        self.hidden_dim = hidden_dim
        self.linear_dim = linear_dim
        self.dropout = dropout
        self.activation = activation
        
    def build(self, input_shape):
        self.multi_head_attention = MultiHeadAttention(
            num_heads=self.num_heads,
            hiddem_dim=self.hidden_dim, 
            dropout=self.dropout,
            )
        self.add_and_norm_1 = AddNorm()
        self.feed_forward = FeedForward(
            linear_dim=self.linear_dim,
            activation=self.activation
            )
        self.add_and_norm_2 = AddNorm()
        super().build(input_shape)

    def call(self, inputs, padding_mask):
        x = self.multi_head_attention(inputs, inputs, attention_mask=padding_mask)
        x = self.add_and_norm_1(x, inputs)
        y = self.feed_forward(x)
        y = self.add_and_norm_2(x, y)
        return y


class TransformerDecoderBlock(layers.Layer):
    """Classic Transformer Decoder Block.
    args:
        - num_heads: The number of heads in a multi head attention layer
        - hidden_dim: Dimensions of queries, keys, and values for each attention head 
        - linear_dim: The linear projection dimension of feedforward
        - dropout: Default to 0.1
        - activation: Activation function of feedforward layer
    call args:
        - decoder_inputs, shape like (B, T, dim)
        - encoder_outputs, shape like (B, T, dim)
        - sequence_mask, shape like (B, T, T)
        - padding_mask, shape like (B, T, T)
    """
    def __init__(
        self, 
        num_heads,
        hidden_dim,
        linear_dim,
        dropout=0.1,
        activation="leaky_relu",
        **kwargs
        ):
        super().__init__(**kwargs)     
        self.num_heads = num_heads
        self.hidden_dim = hidden_dim
        self.linear_dim = linear_dim
        self.dropout = dropout
        self.activation = activation

    def build(self, input_shape):
        self.masked_multi_head_attention = MultiHeadAttention(
            num_heads=self.num_heads,
            hiddem_dim=self.hidden_dim, 
            dropout=self.dropout,
            )
        self.add_and_norm_1 = AddNorm()
        self.multi_head_attention = MultiHeadAttention(
            num_heads=self.num_heads,
            hiddem_dim=self.hidden_dim, 
            dropout=self.dropout,
            )
        self.add_and_norm_2 = AddNorm()
        self.feed_forward = FeedForward(
            linear_dim=self.linear_dim,
            activation=self.activation
            )
        self.add_and_norm_3 = AddNorm()
        super().build(input_shape)

    def call(self, decoder_inputs, encoder_outputs, sequence_mask, padding_mask):
        x = self.masked_multi_head_attention(decoder_inputs, decoder_inputs, attention_mask=sequence_mask)
        x = self.add_and_norm_1(x, decoder_inputs)
        y = self.multi_head_attention(x, encoder_outputs, attention_mask=padding_mask)
        y = self.add_and_norm_2(x, y)
        z = self.feed_forward(y)
        z = self.add_and_norm_3(y, z)
        return z