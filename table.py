class table:
    def __init__(self, index, data, padding, entries):
        self.data_offset = data[0]
        self.data_length = data[1]
        self.padding_offset = padding[0]
        self.padding_length = padding[1]
        self.offset = index[0]
        self.length = index[1]
        self.entries = entries # [[lwp, offs, length, flg, id, typ], [...], ...]
