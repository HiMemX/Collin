class section:
    def __init__(self, offset, length, layer_count, layers):
        self.offset = offset
        self.length = length
        self.layer_count = layer_count
        
        self.layers = layers # [table, table, ...]
