class simple_object: # Type = AF 4D 62 21
    def __init__(self, root, id_, type_, position, rotation, scale, model_id, anim_id, mass, friction):
        self.root = root # [WhatSection, WhatTable, WhatEntry]
        self.id = id_
        self.type = type_
        
        self.position = position
        self.rotation = rotation
        self.scale = scale
        
        self.model_id = model_id
        self.anim_id = anim_id
        self.anim_amount = 0
        
        self.size_divisor = [13, 3]
        
        self.visibilities = []
        self.global_transforms = []
        self.transformation = []
        self.model = [] # [[VertRoot, AORoot, VertColRoot, UVRoot, FaceRoot]]
        self.pfst = False
        self.texture = [] # [TextRoot]
        self.texture_ids = []
        
        self.mass = mass
        self.friction = friction
        
        self.name = ""
        
        self.model_class = None # Uses a class from modelviewer.py