class simple_object: # Type = AF 4D 62 21
    def __init__(self, root, id_, position, rotation, scale, model_id, anim_id, mass, friction):
        self.root = root # [WhatSection, WhatTable, WhatEntry]
        self.id = id_
        
        self.position = position
        self.rotation = rotation
        self.scale = scale
        
        self.model_id = model_id
        self.anim_id = anim_id
        self.anim_amount = 0
        
        self.model = [] # [VertRoot, AORoot, VertColRoot, UVRoot, FaceRoot]
        self.texture = [] # TextRoot
        
        self.mass = mass
        self.friction = friction
        
        self.name = ""
