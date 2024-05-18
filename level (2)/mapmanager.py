# напиши здесь код создания и управления картой
import pickle

class Mapmanager():
    def __init__(self):
        self.model = 'block'
        self.texture = 'block.png'

        model = 'block'
        textures = [
            'block.png',
            'stone.png',
            'wood.png',
            'brick.png'
        ]
        self.createSamples(model, textures)
        self.colors = [
            (0.2, 0.2, 0.35, 1),
            (0.2, 0.5, 0.2, 1),
            (0.7, 0.2, 0.2, 1),
            (0.5, 0.2, 0.01, 1)
        ]
        self.startNew()

    def startNew(self):
        self.land = render.attachNewNode("Land")


    def createSamples(self,model,textures):
        self.samples = list()
        for t in textures:
            block = loader.loadModel(model)
            block.setTexture(loader.loadTexture(t))
            self.samples.append(block)


    def getColor(self, z):

        if z < len(self.colors):
            return self.colors[z]
        else:
            return self.colors[-1]

    def addBlock(self, position, type = 0):
        if type >= len(self.samples):
            type = 0
        block = self.samples[type].copyTo(self.land)

        #self.block = loader.loadModel(self.model)
        #self.block.setTexture(loader.loadTexture(self.texture))
        block.setPos(position)
        if type == 0:
            self.color = self.getColor(int(position[2]))
            block.setColor(self.color)
        block.setTag('type', str(type))
        block.setTag('at', str(position))
        block.reparentTo(self.land)
    def clear(self):
        self.land.removeNode()
        self.startNew()
    def loadLand(self, filename):
        self.clear()
        with open(filename) as file:
            y = 0
            for line in file:
                x = 0
                line = line.split(' ')
                for z in line:
                    for z0 in range(int(z)+1):
                        block = self.addBlock((x,y,z0))
                    x +=1
                y +=1
        return x,y
    def findBlock(self, pos):
        return self.land.findAllMatches('=at='+str(pos))

    def isEmpty(self,pos):
        block = self.findBlock(pos)
        if block:
            return False
        else:
            return True
    def findhighestEmpty(self,pos):
        x,y,z = pos
        z = 1
        while not self.isEmpty((x,y,z)):
            z += 1
        return (x,y,z)
    def delBlock(self, position):
        x,y,z = self.findhighestEmpty(position)
        pos = x,y,z-1
        for block in self.findBlock(pos):
            block.removeNode()
    def delblockFrom(self, position):
        blocks = self.findBlock(position)
        for block in blocks:
            block.removeNode()
    def buildBlock(self,pos,type):
        x, y, z = pos
        new_pos = self.findhighestEmpty(pos)
        if new_pos[2] <= z+1:
            self.addBlock(new_pos, type)

    def saveMap(self):
        blocks = self.land.getChildren()
        with open('my_map.dat','wb') as fout:
            pickle.dump(len(blocks), fout)
            for block in blocks:
                x, y, z = block.getPos()
                pos = (int(x), int(y), int(z))
                pickle.dump(pos,fout)
                pickle.dump(int(block.getTag("type")),fout)

    def loadMap(self):
        self.clear()
        with open('my_map.dat', 'rb') as fin:
            length = pickle.load(fin)
            for i in range(length):
                x, y, z = pickle.load(fin)
                type = pickle.load(fin)
                self.addBlock((x, y, z), type)




