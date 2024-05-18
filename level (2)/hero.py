from math import pi, sin, cos

from panda3d.core import WindowProperties
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from panda3d.core import CollisionTraverser, CollisionNode, CollisionBox, CollisionRay, CollisionHandlerQueue
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

key_switch_camera = 'c'
key_switch_mode = 'z'

def degToRad(degrees):
    return degrees * (pi / 180.0)

key_up = 'space'
key_down = 'shift'
key_build = 'b'
key_destroy = 'v'
key_load = 'l'
key_save = 'k'
key_btype_1 = '1'
key_btype_2 = '2'
key_btype_3 = '3'
key_btype_4 = '4'

class Hero():
    def __init__(self, pos, land):
        self.land = land
        self.hero = loader.loadModel('smiley')
        self.hero.setColor(1, 0.5, 0)
        self.hero.setScale(0.3)
        self.hero.setPos(pos)
        self.hero.reparentTo(render)
        self.mode = True
        self.btype = 0
        self.cameraBind()
        self.accept_events()
        self.captureMouse()
        self.setupSkybox()
        taskMgr.add(self.update, 'update')
        self.setup_fps_display()


    def update(self, task):
        dt = globalClock.getDt()

        playerMoveSpeed = 10

        x_movement = 0
        y_movement = 0
        z_movement = 0

        if base.keyMap['forward']:
            x_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH()))
            y_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH()))
        if base.keyMap['backward']:
            x_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH()))
            y_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH()))
        if base.keyMap['left']:
            x_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH()))
        if base.keyMap['right']:
            x_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH()))
        if base.keyMap['up']:
            z_movement += dt * playerMoveSpeed
        if base.keyMap['down']:
            z_movement -= dt * playerMoveSpeed

        camera.setPos(
            camera.getX() + x_movement,
            camera.getY() + y_movement,
            camera.getZ() + z_movement,
        )

        if base.cameraSwingActivated:
            md = base.win.getPointer(0)
            mouseX = md.getX()
            mouseY = md.getY()

            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY

            self.cameraSwingFactor = 10

            currentH = base.camera.getH()
            currentP = base.camera.getP()

            base.camera.setHpr(
                currentH - mouseChangeX * dt * self.cameraSwingFactor,
                min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                0
            )

            base.cTrav = CollisionTraverser()
            ray = CollisionRay()
            ray.setFromLens(base.camNode, (0, 0))
            rayNode = CollisionNode('line-of-sight')
            rayNode.addSolid(ray)
            rayNodePath = base.camera.attachNewNode(rayNode)
            base.rayQueue = CollisionHandlerQueue()
            base.cTrav.addCollider(rayNodePath, base.rayQueue)

            self.lastMouseX = mouseX
            self.lastMouseY = mouseY

        return task.cont

    def updateKeyMap(self, key, value):
        base.keyMap[key] = value

    def captureMouse(self):
        base.cameraSwingActivated = True

        md = base.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()

        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        base.win.requestProperties(properties)

    def releaseMouse(self):
        base.cameraSwingActivated = False

        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        base.win.requestProperties(properties)

    def setup_fps_display(self):
        self.fps_text = OnscreenText(
            text='', pos=(-1.2, 0.9), fg=(0.5, 1, 0, 1),  # Лаймовий колір тексту
            align=TextNode.ALeft, scale=0.05)
        self.fps_text.hide()

    def toggle_fps_display(self):
        if self.fps_text.isHidden():
            self.fps_text.show()
            base.taskMgr.add(self.update_fps, 'update_fps')
        else:
            self.fps_text.hide()
            base.taskMgr.remove('update_fps')

    def update_fps(self, task):
        fps = globalClock.getAverageFrameRate()
        self.fps_text.setText('FPS: {:.2f}'.format(fps))
        return task.cont


    def setupSkybox(self):
        skybox = loader.loadModel('skybox.egg')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)


    def generateTerrain(self):
        for z in range(10):
            for y in range(20):
                for x in range(20):
                    base.createNewBlock(
                        x * 2 - 20,
                        y * 2 - 20,
                        -z * 2,
                        'brick' if z == 0 else 'block'
                    )



    def cameraBind(self):
        pos = self.hero.getPos()
        # base.mouseInterfaceNode.setPos(-pos[0], -pos[1], -pos[2]-3)
        base.disableMouse()

        base.camera.setPos(0, 0, 3)
        base.camLens.setFov(80)

        crosshairs = OnscreenImage(
            image='crosshairs.png',
            pos=(0, 0, 0),
            scale=0.05,
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)


        base.camera.setH(180)
        base.camera.reparentTo(self.hero)
        base.camera.setPos(0, 0, 1.5)
        self.cameraOn = True

    def cameraUp(self):
        pos = self.hero.getPos()
        base.mouseInterfaceNode.setPos(-pos[0], -pos[1], -pos[2] - 3)
        base.camera.reparentTo(render)
        base.enableMouse()
        self.cameraOn = False

    def changeView(self):
        if self.cameraOn:
            self.cameraUp()
        else:
            self.cameraBind()

    def turn_left(self):
        self.hero.setH((self.hero.getH() + 5) % 360)

    def turn_right(self):
        self.hero.setH((self.hero.getH() - 5) % 360)

    def look_at(self, angle):
        x_from = round(self.hero.getX())
        y_from = round(self.hero.getY())
        z_from = round(self.hero.getZ())

        dx, dy = self.check_dir(angle)
        x_to = x_from + dx
        y_to = y_from + dy
        return x_to, y_to, z_from

    def just_move(self, angle):
        pos = self.look_at(angle)
        self.hero.setPos(pos)

    def move_to(self, angle):
        if self.mode:
            self.just_move(angle)
        else:
            self.try_move(angle)

    def try_move(self, angle):
        pos = self.look_at(angle)
        if self.land.isEmpty(pos):
            pos = self.land.findHighetEmpty(pos)
            self.hero.setPos(pos)
        else:
            pos = pos[0], pos[1], pos[2] + 1
            if self.land.isEmpty(pos):
                self.hero.setPos(pos)

    def check_dir(self, angle):
        if angle >= 0 and angle <= 20:
            return (0, -1)
        elif angle <= 65:
            return (1, -1)
        elif angle <= 110:
            return (1, 0)
        elif angle <= 155:
            return (1, 1)
        elif angle <= 200:
            return (0, 1)
        elif angle <= 245:
            return (-1, 1)
        elif angle <= 290:
            return (-1, 0)
        elif angle <= 335:
            return (-1, -1)
        else:
            return (0, -1)

    def forward(self):
        angle = self.hero.getH() % 360
        self.move_to(angle)

    def back(self):
        angle = (self.hero.getH() + 180) % 360
        self.move_to(angle)

    def left(self):
        angle = (self.hero.getH() + 90) % 360
        self.move_to(angle)

    def right(self):
        angle = (self.hero.getH() + 270) % 360
        self.move_to(angle)

    def up(self):
        if self.mode:
            self.hero.setZ(self.hero.getZ() + 1)

    def down(self):
        if self.mode and self.hero.getZ() > 1:
            self.hero.setZ(self.hero.getZ() - 1)
    def setBuild(self,type):
        self.btype = type

    def build(self):
        angle = self.hero.getH() % 360
        pos = self.look_at(angle)
        if self.mode:
            self.land.addBlock(pos, type = self.btype)
        else:
            self.land.buildBlock(pos, type = self.btype)

    def destroy(self):
        angle = self.hero.getH() % 360
        pos = self.look_at(angle)
        if self.mode:
            self.land.delBlock(pos)
        else:
            self.land.delBlockFrom(pos)

    def removeBlock(self):
        if base.rayQueue.getNumEntries() > 0:
            base.rayQueue.sortEntries()
            rayHit = base.rayQueue.getEntry(0)

            hitNodePath = rayHit.getIntoNodePath()
            hitObject = hitNodePath.getPythonTag('owner')
            distanceFromPlayer = hitObject.getDistance(base.camera)

            if distanceFromPlayer < 12:
                hitNodePath.clearPythonTag('owner')
                hitObject.removeNode()

    def placeBlock(self):
        if base.rayQueue.getNumEntries() > 0:
            base.rayQueue.sortEntries()
            rayHit = base.rayQueue.getEntry(0)
            hitNodePath = rayHit.getIntoNodePath()
            normal = rayHit.getSurfaceNormal(hitNodePath)
            hitObject = hitNodePath.getPythonTag('owner')
            distanceFromPlayer = hitObject.getDistance(base.camera)

            if distanceFromPlayer < 14:
                hitBlockPos = hitObject.getPos()
                newBlockPos = hitBlockPos + normal * 2
                base.createNewBlock(newBlockPos.x, newBlockPos.y, newBlockPos.z, base.btype)

    def handleLeftClick(self):
        self.captureMouse()
        self.removeBlock()

    def accept_events(self):
        base.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        base.accept('w', self.updateKeyMap, ['forward', True])
        base.accept('w-up', self.updateKeyMap, ['forward', False])
        base.accept('a', self.updateKeyMap, ['left', True])
        base.accept('a-up', self.updateKeyMap, ['left', False])
        base.accept('s', self.updateKeyMap, ['backward', True])
        base.accept('s-up', self.updateKeyMap, ['backward', False])
        base.accept('d', self.updateKeyMap, ['right', True])
        base.accept('d-up', self.updateKeyMap, ['right', False])
        base.accept('space', self.updateKeyMap, ['up', True])
        base.accept('space-up', self.updateKeyMap, ['up', False])
        base.accept('lshift', self.updateKeyMap, ['down', True])
        base.accept('lshift-up', self.updateKeyMap, ['down', False])
        base.accept('mouse1', self.handleLeftClick)
        base.accept('mouse3', self.placeBlock)



        base.accept('escape', self.releaseMouse)
        #base.accept(key_turn_left, self.turn_left)
        #base.accept(key_turn_left + '-repeat', self.turn_left)
        #base.accept(key_turn_right, self.turn_right)
        #base.accept(key_turn_right + '-repeat', self.turn_right)
        #base.accept(key_forward, self.forward)
        #base.accept(key_forward + '-repeat', self.forward)
        #base.accept(key_back, self.back)
        #base.accept(key_back + '-repeat', self.back)
        #base.accept(key_left, self.left)
        #base.accept(key_left + '-repeat', self.left)
        #base.accept(key_right, self.right)
        #base.accept(key_right + '-repeat', self.right)

        base.accept(key_switch_camera, self.changeView)
        #base.accept(key_up, self.up)
        #base.accept(key_down, self.down)

        #base.accept(key_build, self.build)
        #base.accept(key_destroy, self.destroy)
        base.accept(key_load, self.land.loadMap)
        base.accept(key_save, self.land.saveMap)

        base.accept(key_btype_1, self.setBuild,[0])
        base.accept(key_btype_2, self.setBuild,[1])
        base.accept(key_btype_3, self.setBuild,[2])
        base.accept(key_btype_4, self.setBuild,[3])
        base.accept('f3', self.toggle_fps_display)