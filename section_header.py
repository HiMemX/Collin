class section_header:
    def __init__(self, offset, name, child_data_offset, child_data_length):
        self.offset = offset
        self.name = name
        self.child_data_offset = child_data_offset
        self.child_data_length = child_data_length
        self.child = 0
