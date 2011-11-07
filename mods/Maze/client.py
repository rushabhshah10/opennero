from OpenNero import *

# add the key and mouse bindings
from inputConfig import createInputMapping

from common import *
import common.gui as gui
from common.module import openWiki

from Maze.module import getMod, delMod
from Maze.constants import *
from Maze.environment import EgocentricMazeEnvironment, GranularMazeEnvironment

# Agents and the functions that start them

AGENTS = [
    ('Depth First Search',      lambda: getMod().start_dfs(),           False),
    ('Breadth First Search',    lambda: getMod().start_bfs(),           False),
    ('A* Search',  lambda: getMod().start_astar(),         False),
    ('A* Search with Teleporting',   lambda: getMod().start_astar2(),        False),
    ('A* Search with Front',         lambda: getMod().start_astar3(),        False),
#    ('Random Actions',          lambda: getMod().start_random(),        False),
#    ('Sarsa RL',                lambda: getMod().start_sarsa(),         True),
#    ('Q-Learning RL',           lambda: getMod().start_qlearning(),     True),
#    ('Q-Learning RL (more continuous)',   lambda: getMod().start_qlearning(GranularMazeEnvironment), True),
    ('Q-Learning (Coarse)',               lambda: getMod().start_customrl(),      True),
    ('Q-Learning (Fine)',       lambda: getMod().start_customrl(GranularMazeEnvironment), True),
    ('First Person (Coarse)',       lambda: getMod().start_fps(),           False),
    ('First Person (Fine)', lambda: getMod().start_fps_granular(),     False),
]

class UI:
    pass

def CreateGui(guiMan):
    guiMan.setTransparency(1.0)
    guiMan.setFont("data/gui/fonthaettenschweiler.bmp")

    ui = UI()

    window_width = 300 # width
    control_height = 30  # height

    # AGENT SELECTION BOX
    x, y = 5, 4 * control_height + 5
    w, h = window_width - 15, control_height - 10
    ui.agentBoxLabel = gui.create_text(guiMan, 'agentLabel', Pos2i(x,y), Pos2i(3*w/10,h), 'Agent Type:')
    ui.agentComboBox = gui.create_combo_box(guiMan, "agentComboBox", Pos2i(x + 5 + 3*w/10, y), Pos2i(7*w/10, h))
    for agent_name, agent_function, ee_enabled in AGENTS:
        ui.agentComboBox.addItem(agent_name)

    # EXPLORE/EXPLOIT TRADE-OFF SLIDER
    x, y = 5, 0 * control_height + 5
    w, h = window_width - 20, control_height - 5
    epsilon_percent = int(INITIAL_EPSILON * 100)
    ui.epsilonLabel = gui.create_text(guiMan, 'epsilonLabel', Pos2i(x, y), Pos2i(3*w/10, h), 'Exploit-Explore:')
    ui.epsilonScroll = gui.create_scroll_bar(guiMan, 'epsilonScroll', Pos2i(x + 3*w/10 + 5, y), Pos2i(6*w/10, h - 5), True)
    ui.epsilonValue = gui.create_text(guiMan, 'epsilonEditBox', Pos2i(x + 9*w/10 + 10, y), Pos2i(w/10, h), str(epsilon_percent))
    ui.epsilonScroll.setMax(100)
    ui.epsilonScroll.setLargeStep(10)
    ui.epsilonScroll.setSmallStep(1)
    ui.epsilonScroll.setPos(epsilon_percent)
    ui.epsilonScroll.enabled = False
    ui.epsilonValue.visible = False
    ui.epsilonLabel.visible = False
    ui.epsilonScroll.visible = False
    getMod().set_epsilon(INITIAL_EPSILON)
    ui.epsilonScroll.OnScrollBarChange = epsilon_adjusted(ui)

    # START/RESET AND PAUSE/CONTINUE AGENT BUTTONS
    x, y = 5, 3 * control_height
    w, h = (window_width - 15) / 3, control_height - 5
    ui.startAgentButton = gui.create_button(guiMan, 'startAgentButton', Pos2i(x, y), Pos2i(w, h), '')
    ui.pauseAgentButton = gui.create_button(guiMan, 'pauseAgentButton', Pos2i(x + w + 5, y), Pos2i(w, h), '')
    ui.snapshotAgentButton = gui.create_button(guiMan, 'snapshotAgentButton', Pos2i(x + w + 10, y), Pos2i(w, h), '')
    ui.startAgentButton.text = 'Start'
    ui.pauseAgentButton.text = 'Pause'
    ui.snapshotAgentButton.text = 'Snapshot'
    ui.pauseAgentButton.enabled = False
    ui.startAgentButton.OnMouseLeftClick = startAgent(ui)
    ui.pauseAgentButton.OnMouseLeftClick = pauseAgent(ui)
    ui.snapshotAgentButton.OnMouseLeftClick = snapshot(ui)

    # HELP BUTTON
    w, h = (window_width - 15) / 2, control_height - 5
    x, y = 5, 2 * control_height
    ui.helpButton = gui.create_button(guiMan, 'helpButton', Pos2i(x, y), Pos2i(w, h), '')
    ui.helpButton.text = 'Help'
    ui.helpButton.OnMouseLeftClick = openWiki('MazeMod')

    # NEW MAZE BUTTON
    x = 10 + w
    ui.newMazeButton = gui.create_button(guiMan, 'newMazeButton', Pos2i(x, y), Pos2i(w, h), '')
    ui.newMazeButton.text = 'New Maze'
    ui.newMazeButton.OnMouseLeftClick = lambda: getMod().generate_new_maze()

    # SPEEDUP SLIDER
    x, y = 5, 1 * control_height
    w, h = window_width - 20, control_height - 5
    ui.speedupLabel = gui.create_text(guiMan, 'speedupLabel', Pos2i(x, y), Pos2i(3*w/10, h), 'Speedup:')
    ui.speedupScroll = gui.create_scroll_bar(guiMan, 'speedupScroll', Pos2i(x + 5 + 3*w/10, y), Pos2i(3*w/5, h-5), True)
    ui.speedupValue = gui.create_text(guiMan, 'speedupEditBox', Pos2i(x + 10 + 9*w/10, y), Pos2i(w/10, h), str(0))
    ui.speedupScroll.setMax(100)
    ui.speedupScroll.setLargeStep(10)
    ui.speedupScroll.setSmallStep(1)
    ui.speedupScroll.setPos(0)
    getMod().set_speedup(0)
    ui.speedupScroll.OnScrollBarChange = speedup_adjusted(ui)

    # THE WINDOW THAT HOLDS ALL THE CONTROLS ABOVE
    ui.agentWindow = gui.create_window(guiMan, 'agentWindow', Pos2i(10, 10), Pos2i(window_width, 5*control_height+25), 'Agent')
    ui.agentWindow.addChild(ui.agentBoxLabel)
    ui.agentWindow.addChild(ui.agentComboBox)
    ui.agentWindow.addChild(ui.newMazeButton)
    ui.agentWindow.addChild(ui.startAgentButton)
    ui.agentWindow.addChild(ui.pauseAgentButton)
    ui.agentWindow.addChild(ui.snapshotAgentButton)
    ui.agentWindow.addChild(ui.helpButton)
    ui.agentWindow.addChild(ui.epsilonLabel)
    ui.agentWindow.addChild(ui.epsilonScroll)
    ui.agentWindow.addChild(ui.epsilonValue)
    ui.agentWindow.addChild(ui.speedupLabel)
    ui.agentWindow.addChild(ui.speedupScroll)
    ui.agentWindow.addChild(ui.speedupValue)

def epsilon_adjusted(ui):
    """ generate a closure that will be called whenever the epsilon slider is adjusted """
    ui.epsilonValue.text = str(ui.epsilonScroll.getPos())
    getMod().set_epsilon(float(ui.epsilonScroll.getPos())/100)
    def closure():
        """called whenever the epsilon slider is adjusted"""
        ui.epsilonValue.text = str(ui.epsilonScroll.getPos())
        getMod().set_epsilon(float(ui.epsilonScroll.getPos())/100)
    return closure

def speedup_adjusted(ui):
    """generate a closure that will be called whenever the speedup slider is adjusted"""
    ui.speedupValue.text = str(ui.speedupScroll.getPos())
    getMod().set_speedup(float(ui.speedupScroll.getPos())/100)
    def closure():
        """called whenever the speedup slider is adjusted"""
        ui.speedupValue.text = str(ui.speedupScroll.getPos())
        getMod().set_speedup(float(ui.speedupScroll.getPos())/100)
    return closure

def startAgent(ui):
    """ return a function that starts or stops the agent """
    def closure():
        """starts or stops the agent"""
        if ui.startAgentButton.text == 'Start':
            i = ui.agentComboBox.getSelected()
            (agent_name, agent_function, ee_enabled) = AGENTS[i]
            if ee_enabled:
                ui.epsilonScroll.enabled = True
                ui.epsilonValue.visible = True
                ui.epsilonLabel.visible = True
                ui.epsilonScroll.visible = True
            print 'Starting', agent_name
            agent_function()
            ui.pauseAgentButton.text = 'Pause'
            ui.pauseAgentButton.enabled = True
            ui.startAgentButton.text = 'Reset'
            ui.agentComboBox.enabled = False
        else:
            getMod().stop_maze()
            disable_ai()
            ui.epsilonScroll.enabled = False
            ui.epsilonValue.visible = False
            ui.epsilonLabel.visible = False
            ui.epsilonScroll.visible = False
            get_environment().cleanup()
            ui.startAgentButton.text = 'Start'
            ui.pauseAgentButton.text = 'Pause'
            ui.pauseAgentButton.enabled = False
            ui.agentComboBox.enabled = True
    return closure

def pauseAgent(ui):
    """ return a function that pauses and continues the agent """
    def closure():
        """pauses and continues the agent"""
        if ui.pauseAgentButton.text == 'Continue':
            ui.pauseAgentButton.text = 'Pause'
            enable_ai()
        else:
            ui.pauseAgentButton.text = 'Continue'
            disable_ai()
    return closure

def snapshot(ui):
    """ return a function that takes a snapshot of the screen """
    def closure():
        getSimContext().getActiveCamera().snapshot()
    return closure

def recenter(cam):
    """ return a function that recenters the camera """
    def closure():
        """recenters the camera"""
        cam.setPosition(Vector3f(-20, -20, 80))
        cam.setTarget(Vector3f(GRID_DX * ROWS / 2, GRID_DY * COLS / 2, 0))
    return closure

def ClientMain():
    # create fog effect
    getSimContext().setFog()

    # add a camera
    camRotateSpeed = 100
    camMoveSpeed   = 3000
    camZoomSpeed   = 500
    cam = getSimContext().addCamera(camRotateSpeed, camMoveSpeed, camZoomSpeed)
    cam.setFarPlane(5000)
    cam.setEdgeScroll(False)
    recenter_cam = recenter(cam) # create a closure to avoid having a global variable
    recenter_cam() # call the recenter function
    #snapshot_cam = snapshot(cam)

    # load the background
    addObject("data/terrain/Sea.xml", Vector3f(-3000 + NUDGE_X,-3000 + NUDGE_Y,-20))
    addObject("data/terrain/IslandTerrain.xml", Vector3f(-1100 + NUDGE_X, -2400 + NUDGE_Y, -17), Vector3f(0,0,-45))
    addSkyBox("data/sky/irrlicht2")

    # load the maze
    getSimContext().addLightSource(Vector3f(-500,-500,1000), 1500)
    getMod().add_maze()

    # load the GUI
    CreateGui(getGuiManager())

    # create the key binding
    ioMap = createInputMapping()
    ioMap.BindKey( "KEY_SPACE", "onPress", recenter_cam )
    #ioMap.BindKey( "KEY_P", "onPress", snapshot_cam )
    getSimContext().setInputMapping(ioMap)
