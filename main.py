# game.py
from pyscript import display
from tilemap import Tilemap
import random, math, time, pygame, asyncio, logging, os

# define custom errors

class MaterialException(Exception):
    pass

class BuildingException(Exception):
    pass

class SaveError(Exception):
    pass

# define game object classes

class Material: # parent class for all materials
    def __init__(self, name:str, quantity:int):
        self.name = name
        self.quantity = quantity
    
    def add(self, quantity):
        # adds a quantity of material to the material
        self.quantity += quantity

    def canuUse(self, quantity):
        # checks if there is enough material to use
        if self.quantity >= quantity:
            return True
        else:
            return False
        
    def use(self, quantity):
        # uses a quantity of material
        if self.canuUse(quantity):
            return True
        else:
            return False

class PrimaryMaterial(Material): # primary material ie. a material that doesnt need to b processed
    def __init__(self, name:str, quantity:int, productionRate:int):
        self.name = name
        self.quantity = quantity

class SecondaryMaterial(Material): # secondary material ie. a material that needs to be processed
    def __init__(self, name:str, quantity:int, requiredMaterials:dict):
        self.name = name
        self.quantity = quantity
        self.requiredMaterials = requiredMaterials

    def make(self):
        for material, required_quantity in self.requiredMaterials.items():
            if material.canuUse(required_quantity):
                material.use(required_quantity)
            else:
                raise MaterialException("Not enough materials to make this item")
        self.add(1)

class Building: # parent class for all buildings
    def __init__(self, reference:hex, name:str, width:int, height:int):
        self.name = name
        self.width = width
        self.height = height
        self.reference = reference

class Workplace(Building): # a building where citizens work
    def __init__(self, reference:hex, name:str, width:int, height:int, productionMaterial:Material, maxWorkers:int, productionRate:int, productionQuantity:int, workers:list=[]):
        self.name = name
        self.width = width
        self.height = height
        self.reference = reference
        self.productionMaterial = productionMaterial
        self.workers = workers
        self.productionRate = productionRate
        self.productionQuantity = productionQuantity
        self.maxWorkers = maxWorkers
    
    def produce(self):
        if self.workers == self.maxWorkers:
            self.productionMaterial.add(self.productionQuantity)
        else:
            self.productionMaterial.add(self.productionQuantity*(self.workers/self.maxWorkers))

class Home(Building): # a building where citizens live
    def __init__(self, reference:hex, name:int, width:int, height:int, maxResidents:int, residents:list=[]):
        self.name = name
        self.width = width
        self.height = height
        self.reference = reference
        self.residents = residents
        self.maxResidents = maxResidents
    
    def addResident(self, resident):
        if len(self.residents) < self.maxResidents:
            self.residents.append(resident)
        else:
            raise BuildingException('Home is full')
    
    def removeResident(self, resident):
        if resident in self.residents:
            self.residents.remove(resident)
        else:
            raise BuildingException("Resident not found")

class Citizen: # a citizen of the city
    def __init__(self, reference: hex, name: str, happiness: float = 100, health: float = 100, age: float = 0, productivity: float = 0, home:Home = None):
        self.name = name
        self.happiness = happiness
        self.health = health
        self.age = age
        self.productivity = productivity
        self.reference = reference
        self.home = home
        citizens.append(self)
    
    def transferClass(self, newClass):
        self.__class__ = newClass
    
    def move(self, destination):
        global logger
        # Use A* Algorithm to pathfind
        print(f"Moving {self.name} to {destination}")

class StatusWorker: # a status for a worker
    def __init__(self, name:str):
        self.name = name

class Worker(Citizen): # a worker citizen
    def __init__(self, reference: hex, name: str, status: 'StatusWorker', home:Home = None, workplace:Workplace = None, happiness: float = 100, health: float = 100, age: float = 0, productivity: float = 0):
        super().__init__(reference, name, happiness, health, age, productivity, home)
        self.workplace = workplace
        self.status = status
    
    def assignHome(self,homes):
        if len(homes) > 1:
            self.workplace = random.choice(homes)
        else:
            raise BuildingException("No available homes to assign to")
    
    def assignWorkplace(self, type, workplaces):
        if len(workplaces) > 1:
            pass
    
    def entertain(self):
        destination = random.choice(entertainmentBuildings)
        self.move(destination)


class Student(Citizen):
    def __init__(self, reference: hex, name: str, home:Home = None, happiness: float = 100, health: float = 100, age: float = 0, productivity: float = 0):
        super().__init__(reference, name, happiness, health, age, productivity, home)
    
    def study(self):
        destination = random.choice(workplaces)
        self.move(destination)

def draw_cursor(x, y):
    screen.blit(cursor, (x, y) ) 

# begin game code and get logger

logger = logging.getLogger(__name__)
logger.info('THE VEGA INITIATIVE')
logger.info('Game initialized, starting')

# define game functions

def getLocalVarName(var):
    for name, value in locals().items():
        if value == var:
            return name

def getGlobalVarName(var):
    for name, value in globals().items():
        if value == var:
            return name

def setLocalVarValue(name,value):
    locals()[name] = value

def setGlobalVarValue(name,value):
    globals()[name] = value

def loadGame(file = 'save.json'):
    if os.path.exists(file):
        with open(file,'r') as fileDescriptor:
            loadJson = fileDescriptor.read()
        
        # now we should have a dict with the names and values of all the variables
        loadDict = json.loads(loadJson)

        # we then set global variables
        for name, value in loadDict:
            setGlobalVarValue(name,value)
        return True
    else:
        return False


def saveGame(vars,file = 'save.json'):
    saveDict = dict()
    for var in vars:
        saveDict[getGlobalVarName(var)] = var
    
    # now we should have a dict with the names and values of all the variables
    saveJson = json.dumps(saveDict)

    # we then save this to a file
    with open(file,'w') as fileDescriptor:
        fileDescriptor.write(saveJson)
    
    # then we verify the file
    with open(file,'r') as fileDescriptor:
        if fileDescriptor.read() != saveJson:
            return False # if data is incorrect, tell the game loop saving has failed

    return True

# define load-specific variables, that must be saved

if not loadGame():
    entertainmentBuildings = []
    workplaces = []
    homes = []
    citizens = []

saveVars = [entertainmentBuildings,workplaces,homes,citizens] # (all variables above should be listed here)

# define load-specific variables, that do not need to be saved
numCitizens = len(citizens)

# define setting-specific variables, that depend on game settings
timeStep = 1/60
accumulator = 0.0
FPS = 60
WIDTH, HEIGHT = 800, 600

# define constant variables, that do not change ever

if not loadGame('materials.json'):
    # define primary materials...
    wood = PrimaryMaterial("wood", 0, 0)
    stone = PrimaryMaterial("stone", 0, 0)
    food = PrimaryMaterial("food", 0, 0)
    water = PrimaryMaterial("water", 0, 0)
    iron = PrimaryMaterial("iron", 0, 0)
    sulfur = PrimaryMaterial("sulpur", 0, 0)
    copper = PrimaryMaterial("copper", 0, 0)
    oil = PrimaryMaterial("oil", 0, 0)
    gas = PrimaryMaterial("gas", 0, 0)
    sand = PrimaryMaterial("sand", 0, 0)
    alien_biology = PrimaryMaterial("alien_biology", 0, 0)
    earth_biology = PrimaryMaterial("earth_biology", 0, 0)
    silicon = PrimaryMaterial("silicon", 0, 0)

    # ... and secondary materials
    concrete = SecondaryMaterial("concrete", 0, {sand: 2, water: 1, sulfur: 1})

saveMaterials = [wood, stone, food, water, iron, sulfur, copper, oil, gas, sand, alien_biology, earth_biology, silicon, concrete]

logger.info('Materials initialized')

# load the cursor and cursor-specific settings
cursor = pygame.image.load("cursor.png")
cursorX = 376
cursorY = 480
cursorX_change = 0
cursorY_change = 0

# load important pygame objects, and set game to running
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
lastTime = time.time()
game = True

logger.info('Screen initialized')
logger.info('Cursor initialized')
logger.info('Clock initialized')

# define sprites
starSprite = pygame.image.load('assets/star.png')

# main game loop in async

async def main():
    global saveVars, saveMaterials
    logger.info('Main function has been started')
    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info('Quit received, ending game loop')
                if saveGame(saveVars):
                    logger.info('Saved game')
                else:
                    raise SaveError('Game could not be saved - check perms?') # should be replaced with a graphical error and a logger.warning() when we have assets
                if saveGame(saveMaterials,'materials.json'):
                    logger.info('Saved materials')
                else:
                    raise SaveError('Materials could not be saved - check perms?')
                game = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    cursorX_change = -1
                if event.key == pygame.K_RIGHT:
                    cursorX_change = 1
                if event.key == pygame.K_UP:
                    cursorY_change = -1
                if event.key == pygame.K_DOWN:
                    cursorY_change = 1
        
        # movement updates
        cursorX += cursorX_change
        cursorY += cursorY_change
        await asyncio.sleep(0)
        # game updates
        pygame.display.flip()
        clock.tick(FPS)

asyncio.run(main())