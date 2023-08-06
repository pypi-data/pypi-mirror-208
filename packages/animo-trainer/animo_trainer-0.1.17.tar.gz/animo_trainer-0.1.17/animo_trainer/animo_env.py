from typing import Dict, List, Mapping, Tuple
import numpy as np
from numpy.typing import NDArray

from mlagents_envs.base_env import (
    ActionTuple,
    BaseEnv,
    BehaviorMapping,
    DecisionSteps,
    TerminalSteps,
    BehaviorSpec,
    ActionSpec,
    ObservationSpec,
    DimensionProperty,
    ObservationType,
    BehaviorName,
    AgentId,
)

from TransformsAI.Animo.Simulation import SimulationRunner
from TransformsAI.Animo.Objects import CharacterActions
from TransformsAI.Animo.Learning.Observations.Primitives import ObservationBuffer
from TransformsAI.Animo.Learning.Observations import AgentObservations

from animo_trainer.animo_training_session import AnimoTrainingSession
import animo_trainer.typed_numpy as tnp

ACTION_MASK = [tnp.zeros((1, 7), np.bool_)]
GROUP_ID = tnp.zeros((1,), dtype=np.int32)
GROUP_REWARD = tnp.zeros((1,), dtype=np.float32)


class AnimoEnv(BaseEnv):
    def __init__(self, training_session: AnimoTrainingSession):
        self.session = training_session
        self.step_index: int = 0
        self.episode_index: int = 0
        self.will_reset_next_step = False

        self.behavior_mapping: BehaviorMapping
        self.observation_dict: Dict[int, AgentObservations]

    def reset(self) -> None:
        # we copy the session's grid to avoid modifying the original
        self.voxel_grid = self.session.level_data.SavedGrid.Copy()
        self.simulation_runner = SimulationRunner(self.voxel_grid)
        self.observation_dict = {}

        behaviour_specs: Dict[BehaviorName, BehaviorSpec] = {}

        for behaviour_name, agent_data in self.session.agent_datas.items():
            observation = AgentObservations(
                behaviour_name, agent_data.AffinitySlots, agent_data.VisionMask
            )
            self.observation_dict[agent_data.Id] = observation
            obs_specs: List[ObservationSpec] = [
                ObservationSpec(
                    name=observation.Name,
                    shape=(observation.ObservationCount,),
                    dimension_property=(DimensionProperty.NONE,),
                    observation_type=ObservationType.DEFAULT,
                )
            ]
            action_spec = ActionSpec(continuous_size=0, discrete_branches=(7,))
            behavior_spec = BehaviorSpec(obs_specs, action_spec)
            behaviour_specs[behaviour_name] = behavior_spec

        self.behavior_mapping = BehaviorMapping(behaviour_specs)

    @property
    def behavior_specs(self) -> Mapping[BehaviorName, BehaviorSpec]:
        return self.behavior_mapping

    def get_steps(self, behavior_name: BehaviorName) -> Tuple[DecisionSteps, TerminalSteps]:
        (observations, reward, agent_id) = self.get_env_step_data(behavior_name)

        if self.will_reset_next_step:
            is_interrupted = tnp.zeros((1, 1), dtype=np.bool_)

            decision_steps = DecisionSteps.empty(self.behavior_mapping[behavior_name])
            terminal_steps = TerminalSteps(
                observations, reward, is_interrupted, agent_id, GROUP_ID, GROUP_REWARD
            )
        else:
            decision_steps = DecisionSteps(observations, reward, agent_id, ACTION_MASK, GROUP_ID, GROUP_REWARD)
            terminal_steps = TerminalSteps.empty(self.behavior_mapping[behavior_name])

        return (decision_steps, terminal_steps)

    def set_actions(self, behavior_name: BehaviorName, action: ActionTuple) -> None:
        if not self.will_reset_next_step:
            character = self.voxel_grid.GetCharacter(int(behavior_name))
            raw_action = int(action.discrete[0])  # type: ignore
            character.NextAction = CharacterActions(raw_action)

    def step(self) -> None:
        if self.will_reset_next_step:
            for accumulator in self.session.checkpoint_accumulators.values():
                accumulator.OnEpisodeEnded(self.step_index)
            self.reset()
            self.will_reset_next_step = False
            self.step_index = 0
            self.episode_index += 1
        else:
            self.simulation_runner.Simulate()
            self.step_index += 1
            if self.voxel_grid.EndConditions.IsMet(self.voxel_grid, self.step_index):
                self.will_reset_next_step = True

    def get_env_step_data(self, behavior_name: BehaviorName) -> Tuple[
        List[NDArray[np.float32]],  # Observations
        NDArray[np.float32],  # Reward
        NDArray[np.int32],  # Agent ID
    ]:
        agent_data = self.session.agent_datas[behavior_name]
        character = self.voxel_grid.GetCharacter(agent_data.Id)
        buffer = ObservationBuffer.Acquire()
        agent_observation = self.observation_dict[agent_data.Id]
        agent_observation.Perceive(character, buffer)
        observations = tnp.array(buffer.Observations, dtype=np.float32)
        observations = [tnp.expand_dims(observations, axis=0)]

        reward = 0
        for i, r in enumerate(agent_data.CurrentRewards):
            if r.Evaluate(character):
                reward = reward + r.Scale
                accumulator = self.session.checkpoint_accumulators[behavior_name]
                accumulator.AddReward(i, self.step_index)

        reward = tnp.multiply(tnp.ones((1,), dtype=np.float32), reward)

        agent_id = tnp.multiply(tnp.ones((1,), dtype=np.int32), self.episode_index)
        return (observations, reward, agent_id)

    def set_action_for_agent(self, behavior_name: BehaviorName, agent_id: AgentId, action: ActionTuple) -> None:
        # TODO: Explain why this isn't implemented
        pass

    def close(self) -> None:
        pass
