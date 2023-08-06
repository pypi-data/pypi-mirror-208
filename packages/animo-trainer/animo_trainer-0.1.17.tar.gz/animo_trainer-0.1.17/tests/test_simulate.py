from pythonnet import load
load("coreclr")

import clr, os
import pathlib

CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
ANIMO_UNITY_DLL_DIR = os.path.realpath(os.path.join(CURRENT_DIR, "../lib"))
ANIMO_DB_PATH = "/Users/liam/Library/Application Support/Transitional Forms Inc/Little Learning Machines/Database"
# Load AnimoUnity DLLs
for f in os.listdir(ANIMO_UNITY_DLL_DIR):
    dll_path = os.path.join(ANIMO_UNITY_DLL_DIR, f)
    if os.path.isfile(dll_path) and dll_path.endswith(".dll"):
        print(f"Adding Reference to DLL: {dll_path}")
        clr.AddReference(dll_path)

from System.Collections.Generic import List
from TransformsAI.Animo.Grid import GridTransform, VoxelGrid, GridObject
from TransformsAI.Animo.Numerics import Vector3Int
from TransformsAI.Animo.Simulation import SimulationRunner
from TransformsAI.Animo.Objects import Character, CharacterActions, TypeIds
from TransformsAI.Animo.Learning.Rewards import NewReward, RewardAmounts, RewardSource
from TransformsAI.Animo.Objects.Items import CrystalItem, CrystalInteractions

def test_item_rewards():
    grid_size = Vector3Int(8, 8, 8)
    grid = VoxelGrid.CreateDefaultGrid(grid_size, 100)
    simRunner = SimulationRunner(grid)
    character = Character(0)
    characterPlaced = grid.PlaceOn(character, GridTransform(Vector3Int(0, 0, 0), Vector3Int(0, 0, 1)))
    assert characterPlaced

    item = CrystalItem()
    itemPlaced = grid.PlaceOn(item, GridTransform(Vector3Int(0, 0, 1), Vector3Int(0, 0, 1)))
    assert itemPlaced

    reward = NewReward()
    reward.RewardAmount = RewardAmounts.Plus1
    reward.Source = RewardSource.Item(TypeIds.Crystal)
    reward.InteractionId = int(CrystalInteractions.Collect)

    character.NextAction = CharacterActions.Forward
    simRunner.Simulate()
    didApply = reward.Evaluate(character)
    assert didApply

def test_load_cloud_from_json():
    cloud_json = os.path.join(ANIMO_DB_PATH, "Levels/cloud_0.json")
    with open(cloud_json) as file:
        cloud_json = file.read()
    grid = VoxelGrid.FromJson(cloud_json)
    grid_objects = List[GridObject]()
    grid.GetObjects(grid_objects)
    print(grid_objects.Count)


test_item_rewards()
# test_load_cloud_from_json()
# test_init_database()
