import pathlib, os, shutil, time, yaml, threading
import numpy as np
from typing import Dict, Optional

from mlagents.trainers.cli_utils import parser as ml_agents_parser
from mlagents.trainers.settings import RunOptions, TrainerSettings

from TransformsAI.Animo.Data import AgentData, LevelData
from TransformsAI.Animo.Data import AgentCheckpointAccumulator, Serializer

INPUT_FOLDER_NAME = "Input"
OUTPUT_FOLDER_NAME = "Output"
AGENTS_FOLDER_NAME = "Agents"
CONFIG_FILE_NAME = "config.yaml"
LEVEL_FILE_NAME = "level.json"
AGENT_DATA_FILE_NAME = "AgentData.json"
AGENT_CHECKPOINT_FILE_NAME = "checkpoint.pt"

BehaviorName = str


class AnimoTrainingSession:
    def __init__(self, folder_path: str, daemon_pid: Optional[int] = None) -> None:
        self.id: str
        self.run_options: RunOptions
        self.level_data: LevelData
        self.agent_datas: Dict[BehaviorName, AgentData] = {}
        self.checkpoint_accumulators: Dict[BehaviorName, AgentCheckpointAccumulator] = {}
        self.agent_output_paths: Dict[BehaviorName, str] = {}
        self.lock = threading.Lock()

        if daemon_pid is not None:
            self.should_check_daemon = True
            self.daemon_pid: int = daemon_pid
        else:
            self.should_check_daemon = False

        # Input folders
        training_session_full_folder_path = pathlib.Path(folder_path)
        if not os.path.isdir(training_session_full_folder_path):
            raise ValueError("Training session folder not found")

        input_folder_full_path = os.path.join(training_session_full_folder_path, INPUT_FOLDER_NAME)
        if not os.path.isdir(input_folder_full_path):
            raise ValueError("Input folder not found")

        input_agents_full_path = os.path.join(input_folder_full_path, AGENTS_FOLDER_NAME)
        if not os.path.isdir(input_agents_full_path):
            raise ValueError("Input agents folder not found")

        # Config
        input_config_full_path = os.path.join(input_folder_full_path, CONFIG_FILE_NAME)
        if not os.path.isfile(input_config_full_path):
            raise ValueError("Config.yaml not found")

        args = ml_agents_parser.parse_args([input_config_full_path])
        self.run_options = RunOptions.from_argparse(args)

        if self.run_options.env_settings.seed == -1:
            self.run_options.env_settings.seed = np.random.randint(0, 10000)  # type:ignore

        self.id = training_session_full_folder_path.name
        self.run_options.checkpoint_settings.run_id = self.id
        self.run_options.checkpoint_settings.results_dir = str(
            os.path.join(training_session_full_folder_path, OUTPUT_FOLDER_NAME, AGENTS_FOLDER_NAME))

        # Level
        input_level_full_path = os.path.join(input_folder_full_path, LEVEL_FILE_NAME)
        if not os.path.isfile(input_level_full_path):
            raise ValueError("Level.json not found")

        json_level = None
        with open(input_level_full_path, mode='r') as file:
            json_level = file.read()
        level_data: LevelData = Serializer.FromJson[LevelData](json_level)
        self.level_data = level_data

        # Agents
        characters = level_data.SavedGrid.Characters

        if characters.Count < 1:
            raise ValueError("Level.json does not contain any characters")

        for character in characters:
            character_id: str = str(character.CharacterId)

            agent_full_path = os.path.join(input_agents_full_path, character_id)
            if not os.path.isdir(agent_full_path):
                raise ValueError(f"Agent {character_id} folder not found")

            agent_data_full_path = os.path.join(agent_full_path, AGENT_DATA_FILE_NAME)
            if not os.path.isfile(agent_data_full_path):
                raise ValueError(f"Agent {character_id} AgentData.json not found")

            json_agent_data = None
            with open(agent_data_full_path, mode='r') as file:
                json_agent_data = file.read()

            agent_data = Serializer.FromJson[AgentData](json_agent_data)
            self.agent_datas[character_id] = agent_data
            self.checkpoint_accumulators[character_id] = AgentCheckpointAccumulator()

            agent_checkpoint_full_path = os.path.join(agent_full_path, AGENT_CHECKPOINT_FILE_NAME)
            if os.path.isfile(agent_checkpoint_full_path):
                trainer_settings: TrainerSettings = self.run_options.behaviors.get(character_id)  # type: ignore
                trainer_settings.init_path = agent_checkpoint_full_path

            self.agent_output_paths[character_id] = os.path.join(training_session_full_folder_path, OUTPUT_FOLDER_NAME,
                                                                 AGENTS_FOLDER_NAME, character_id)

        # Output folders and files
        output_folder_full_path = os.path.join(training_session_full_folder_path, OUTPUT_FOLDER_NAME)
        if os.path.isdir(output_folder_full_path):
            timestamp = int(time.time_ns() / 1000)
            new_folder_name = OUTPUT_FOLDER_NAME + "_" + str(timestamp)
            new_folder_full_path = os.path.join(training_session_full_folder_path, new_folder_name)
            print(f"Found existing output folder. Renaming it to {new_folder_name}")
            os.rename(output_folder_full_path, new_folder_full_path)

        os.mkdir(output_folder_full_path)

        output_config_full_path = os.path.join(output_folder_full_path, CONFIG_FILE_NAME)
        with open(output_config_full_path, 'x') as f:
            yaml.dump(self.run_options.as_dict(), f, sort_keys=False)

        output_level_full_path = os.path.join(output_folder_full_path, LEVEL_FILE_NAME)
        shutil.copy(input_level_full_path, output_level_full_path)
