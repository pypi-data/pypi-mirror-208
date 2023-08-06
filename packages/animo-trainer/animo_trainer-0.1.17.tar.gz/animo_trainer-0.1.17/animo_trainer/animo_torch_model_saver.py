import os, time, logging
from typing import Dict, OrderedDict, Tuple, List, cast

from mlagents.torch_utils import torch
from torch import Tensor
from torch.nn.modules import Module

from mlagents.trainers.settings import TrainerSettings
from mlagents.trainers.model_saver.torch_model_saver import TorchModelSaver
from mlagents.trainers.model_saver.torch_model_saver import DEFAULT_CHECKPOINT_NAME

from animo_trainer.animo_training_session import AnimoTrainingSession
from TransformsAI.Animo.Data import Serializer

SerializedModule = Dict[str, OrderedDict[str,Tensor]]

class AnimoTorchModelSaver(TorchModelSaver):
    def __init__(
        self,
        trainer_settings: TrainerSettings,
        model_path: str,
        session: AnimoTrainingSession,
        load: bool = False):

        super().__init__(trainer_settings, model_path, load)

        self.session = session

    def save_checkpoint(self, behavior_name: str, step: int) -> Tuple[str, List[str]]:
        timestamp = int(time.time_ns() / 1000)
        checkpoint_path = os.path.join(self.model_path, str(timestamp))

        modules = cast(Dict[str, Module], self.modules)  # type: ignore
        state_dict : SerializedModule = {
            name: module.state_dict() for name, module in modules.items()
        }

        onnx_path = self._save_checkpoint(behavior_name, checkpoint_path, state_dict)

        try:
            aux_paths = self._save_aux_files(behavior_name, checkpoint_path, timestamp, state_dict)
        except Exception as e:
            aux_paths = []
            logging.exception(e)

        return onnx_path, aux_paths

    def _save_checkpoint(self, behavior_name: str, checkpoint_path: str, state_dict: SerializedModule) -> str:
        os.makedirs(self.model_path, exist_ok=True)

        export_ckpt_path = f"{checkpoint_path}.onnx"
        pytorch_ckpt_path = f"{checkpoint_path}.pt"

        # Writing historical save files
        torch.save(state_dict, pytorch_ckpt_path)  # type: ignore
        self.export(checkpoint_path, behavior_name)

        return export_ckpt_path

    def _save_aux_files(self, behavior_name: str, checkpoint_path: str, timestamp: int, state_dict: SerializedModule) -> List[str]:
        accumulator = self.session.checkpoint_accumulators[behavior_name]
        agent_data = self.session.agent_datas[behavior_name]

        pytorch_ckpt_path = f"{checkpoint_path}.pt"

        default_pytorch_ckpt_path = os.path.join(self.model_path, DEFAULT_CHECKPOINT_NAME)
        default_export_ckpt_path = os.path.join(self.model_path, "model")  # File format not required by export function

        # Overwriting recent save files
        # Save `checkpoint.pt`, this is needed to resume training
        torch.save(state_dict, default_pytorch_ckpt_path)  # type: ignore
        self.export(default_export_ckpt_path, behavior_name)

        # Lock is needed as AnimoData and AnimoCheckpoint are accessed from different threads
        # (affinities and other shared state)

        with self.session.lock:
            # Writing AnimoData and AnimoCheckpoint
            new_checkpoint = accumulator.OnCheckpointCreated(timestamp, agent_data.Id, self.session.id,
                                                             agent_data.CurrentRewards)

            if new_checkpoint:
                agent_data.AddAndSelectCheckpoint(new_checkpoint)
                json_checkpoint = Serializer.ToJson(new_checkpoint)
                json_agent = Serializer.ToJson(agent_data)

                default_animo_agent_path = os.path.join(self.model_path, "AgentData.json")
                animo_ckpt_path = f"{checkpoint_path}.json"

                with open(default_animo_agent_path, 'w') as cp_file:
                    cp_file.write(json_agent)

                with open(animo_ckpt_path, 'w') as cp_file:
                    cp_file.write(json_checkpoint)
                print(f"Animo-Learn::Checkpoint::{self.session.id}::{checkpoint_path}")
                return [pytorch_ckpt_path, animo_ckpt_path]
            else:
                print(f"Animo-Learn::Error::Accumulator did not return new checkpoint")
                return [pytorch_ckpt_path]
