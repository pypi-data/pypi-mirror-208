from keras import backend as K

def get_padding_mask(batch_inputs, padding_value):
    """Generate padding mask based on input sequence.
    args:
        - batch_inputs: batch input sequence, shape: [b, len]
        - padding_value: Padding values in the input sequence
    return:
        - mask: Boolean type mask, Masked out as False, retained as True
    """
    mask = K.not_equal(batch_inputs, padding_value)
    mask = K.tile(K.expand_dims(mask, 1), [1, K.shape(batch_inputs)[-1], 1])
    return mask

def get_sequence_mask(batch_inputs):
    """Generate sequence mask based on input sequence.
    args:
        - batch_inputs: batch input sequence, shape: [b, len]
    return:
        - mask: Upper triangular mask of Boolean type, Masked out as False, retained as True
    """
    mask = K.cast(K.np.tri(K.int_shape(batch_inputs)[-1], K.int_shape(batch_inputs)[-1]), bool)
    mask = K.tile(K.expand_dims(mask, 0), [1, 1, 1])
    return mask

def get_positional_encoding(pos, dim):
    """Generate positional encoding.
    args:
        - pos: Position length of position encoding
        - dim: Encoding dimension for each position
    return:
        - positional encoding: Shape like: [1, pos, dim]
    """
    numerator = K.tile(K.constant(range(pos), shape=(pos,1)), [1, dim])
    denominator = 1e4 ** (K.tile(K.constant([[i if i%2==0 else i-1 for i in range(dim)]]), [pos,1]) / dim)
    pe = K.np.zeros((1,pos, dim))
    pe[0,:,0::2] = K.sin((numerator/denominator)[:,0::2])
    pe[0,:,1::2] = K.cos((numerator/denominator)[:,1::2])
    return K.constant(pe)

def get_pe(shape):
    n, m = shape
    pos = K.tile(K.constant(range(n), shape=(n,1)), [1, m])
    den = 1e4 ** (K.tile(K.constant([[i if i%2==0 else i-1 for i in range(m)]]), [n,1]) / m)
    pe = K.np.zeros((1,n, m))
    pe[0,:,0::2] = K.sin((pos/den)[:,0::2])
    pe[0,:,1::2] = K.cos((pos/den)[:,1::2])
    return K.constant(pe)

