import os, threading, json, queue, sys, psutil
import numpy as np

from typing import Dict, Set, List
from collections import defaultdict

from mlagents_envs import logging_util
from mlagents_envs.side_channel.environment_parameters_channel import EnvironmentParametersChannel
from mlagents_envs.exception import (
    UnityEnvironmentException,
    UnityCommunicationException,
    UnityCommunicatorStoppedException,
)
from mlagents_envs.timers import (
    hierarchical_timer,
    timed,
    get_timer_stack_for_thread,
    merge_gauges,
)

from mlagents import torch_utils
from mlagents.torch_utils.globals import get_rank

from mlagents.trainers.env_manager import EnvManager, EnvironmentStep
from mlagents.trainers.simple_env_manager import SimpleEnvManager
from mlagents.trainers.behavior_id_utils import BehaviorIdentifiers
from mlagents.trainers.agent_processor import AgentManager
from mlagents.trainers.trainer import Trainer
from mlagents.trainers.trainer import TrainerFactory
from mlagents.trainers.trainer.rl_trainer import RLTrainer
from mlagents.trainers.environment_parameter_manager import EnvironmentParameterManager

from animo_trainer.animo_torch_model_saver import AnimoTorchModelSaver
from animo_trainer.animo_training_session import AnimoTrainingSession
from animo_trainer.animo_env import AnimoEnv

COMMAND_CHAR = ">"
INTERRUPTION_COMMAND = COMMAND_CHAR + "INTERRUPT"

DAEMON_CHECK_PERIOD = 25

stdin_queue: queue.Queue[str] = queue.Queue()


def read_stdin():
    # Do not access C# objects from separate threads
    while True:
        line = sys.stdin.readline().strip()
        if line.startswith(COMMAND_CHAR):
            stdin_queue.put(line)


# Create a new thread for reading from stdin
t = threading.Thread(target=read_stdin, daemon=True)
t.start()


class AnimoTrainingController:
    def __init__(self, session: AnimoTrainingSession):
        self.session = session
        run_options = session.run_options
        self.env_manager = SimpleEnvManager(AnimoEnv(session), EnvironmentParametersChannel())

        self.trainer_factory = TrainerFactory(
            trainer_config=run_options.behaviors,
            output_path=run_options.checkpoint_settings.write_path,
            train_model=not run_options.checkpoint_settings.inference,
            load_model=run_options.checkpoint_settings.resume,
            seed=run_options.env_settings.seed,
            param_manager=EnvironmentParameterManager(),  # Not used
            init_path=run_options.checkpoint_settings.maybe_init_path,  # type:ignore
            multi_gpu=False,
        )

        self.trainers: Dict[str, RLTrainer] = {}
        self.brain_name_to_identifier: Dict[str, Set] = defaultdict(set)  # type:ignore
        self.output_path = run_options.checkpoint_settings.write_path
        self.run_id = run_options.checkpoint_settings.run_id
        self.train_model = not run_options.checkpoint_settings.inference
        self.ghost_controller = self.trainer_factory.ghost_controller
        self.registered_behavior_ids: Set[str] = set()
        self.trainer_threads: List[threading.Thread] = []
        self.kill_trainers = False
        self.step = 0

        self.logger = logging_util.get_logger(__name__)
        torch_utils.set_torch_config(run_options.torch_settings)
        if run_options.debug:
            logging_util.set_log_level(logging_util.DEBUG)
            self.logger.debug(f"Configuration for this run: \n{json.dumps(run_options.as_dict(), indent=4)}")
        else:
            logging_util.set_log_level(logging_util.INFO)
        np.random.seed(run_options.env_settings.seed)
        torch_utils.torch.manual_seed(run_options.env_settings.seed)  # type: ignore
        self.rank = get_rank()

    @timed
    def _save_models(self):
        """
        Saves current model to checkpoint folder.
        """
        if self.rank is not None and self.rank != 0:
            return

        for brain_name in self.trainers.keys():
            trainer = self.trainers[brain_name]
            trainer.model_saver.save_checkpoint(brain_name, trainer.get_step)

        self.logger.debug("Saved Model")

    @staticmethod
    def _create_output_path(output_path):  # type: ignore
        try:
            if not os.path.exists(output_path):  # type: ignore
                os.makedirs(output_path)  # type: ignore
        except Exception:
            raise UnityEnvironmentException(
                f"The folder {output_path} containing the "
                "generated model could not be "
                "accessed. Please make sure the "
                "permissions are set correctly."
            )

    @timed
    def _reset_env(self, env_manager: EnvManager) -> None:
        """Resets the environment.

        Returns:
            A Data structure corresponding to the initial reset state of the
            environment.
        """
        env_manager.reset()  # type: ignore
        # Register any new behavior ids that were generated on the reset.
        self._register_new_behaviors(env_manager, env_manager.first_step_infos)

    def _not_done_training(self) -> bool:
        return (
            any(t.should_still_train for t in self.trainers.values())
            or not self.train_model
        ) or len(self.trainers) == 0

    def _create_trainer_and_manager(
        self, env_manager: EnvManager, name_behavior_id: str
    ) -> None:

        parsed_behavior_id = BehaviorIdentifiers.from_name_behavior_id(name_behavior_id)
        brain_name = parsed_behavior_id.brain_name
        trainerthread = None
        if brain_name in self.trainers:
            trainer = self.trainers[brain_name]
        else:
            trainer = self.trainer_factory.generate(brain_name)
            # Changing model saver to the one capable of saving into database
            if isinstance(trainer, RLTrainer):
                trainer.model_saver = AnimoTorchModelSaver(
                    trainer.trainer_settings,
                    self.session.agent_output_paths[brain_name],
                    session=self.session,
                    load=trainer.load)
            else:
                raise Exception("Trainer factory produced not RLTrainer, thats not right")
            self.trainers[brain_name] = trainer
            if trainer.threaded:
                # Only create trainer thread for new trainers
                trainerthread = threading.Thread(
                    target=self.trainer_update_func, args=(trainer,), daemon=True
                )
                self.trainer_threads.append(trainerthread)
            env_manager.on_training_started(
                brain_name, self.trainer_factory.trainer_config[brain_name]
            )

        policy = trainer.create_policy(
            parsed_behavior_id,
            env_manager.training_behaviors[name_behavior_id],
        )
        trainer.add_policy(parsed_behavior_id, policy)

        agent_manager = AgentManager(
            policy,
            name_behavior_id,
            trainer.stats_reporter,
            trainer.parameters.time_horizon,
            threaded=trainer.threaded,
        )
        env_manager.set_agent_manager(name_behavior_id, agent_manager)
        env_manager.set_policy(name_behavior_id, policy)
        self.brain_name_to_identifier[brain_name].add(name_behavior_id)  # type: ignore

        trainer.publish_policy_queue(agent_manager.policy_queue)
        trainer.subscribe_trajectory_queue(agent_manager.trajectory_queue)

        # Only start new trainers
        if trainerthread is not None:
            trainerthread.start()

    def _create_trainers_and_managers(
        self, env_manager: EnvManager, behavior_ids: Set[str]
    ) -> None:
        for behavior_id in behavior_ids:
            self._create_trainer_and_manager(env_manager, behavior_id)

    @timed
    def train(self) -> None:
        self._create_output_path(self.output_path)  # type: ignore
        try:
            # Initial reset
            self._reset_env(self.env_manager)
            while self._not_done_training():
                with self.session.lock:
                    self.advance(self.env_manager)
            # Stop advancing trainers
            self.join_threads()
        except (
            KeyboardInterrupt,
            UnityCommunicationException,
            UnityEnvironmentException,
            UnityCommunicatorStoppedException,
        ) as ex:
            self.join_threads()
            self.logger.info(
                "Learning was interrupted. Please wait while the graph is generated."
            )
            if isinstance(ex, KeyboardInterrupt) or isinstance(ex, UnityCommunicatorStoppedException):
                pass
            else:
                # If the environment failed, we want to make sure to raise
                # the exception, so we exit the process with a return code of 1
                raise ex
        finally:
            if self.train_model:
                self._save_models()

    @timed
    def advance(self, env_manager: EnvManager) -> int:
        # Check if interrupt training was passed through stdin
        while not stdin_queue.empty():
            if stdin_queue.get() == INTERRUPTION_COMMAND:
                raise KeyboardInterrupt

        # Check if daemon process is dead
        self.step += 1
        if self.session.should_check_daemon and self.step % DAEMON_CHECK_PERIOD == 0 and not psutil.pid_exists(
            self.session.daemon_pid):
            raise KeyboardInterrupt

        # Get steps
        with hierarchical_timer("env_step"):
            new_step_infos = env_manager.get_steps()
            self._register_new_behaviors(env_manager, new_step_infos)
            num_steps = env_manager.process_steps(new_step_infos)

        for trainer in self.trainers.values():
            if not trainer.threaded:
                with hierarchical_timer("trainer_advance"):
                    trainer.advance()

        return num_steps

    def _register_new_behaviors(
        self, env_manager: EnvManager, step_infos: List[EnvironmentStep]
    ) -> None:
        """
        Handle registration (adding trainers and managers) of new behaviors ids.
        :param env_manager:
        :param step_infos:
        :return:
        """
        step_behavior_ids: Set[str] = set()
        for s in step_infos:
            step_behavior_ids |= set(s.name_behavior_ids)
        new_behavior_ids = step_behavior_ids - self.registered_behavior_ids
        self._create_trainers_and_managers(env_manager, new_behavior_ids)
        self.registered_behavior_ids |= step_behavior_ids

    def join_threads(self, timeout_seconds: float = 1.0) -> None:
        """
        Wait for threads to finish, and merge their timer information into the main thread.
        :param timeout_seconds:
        :return:
        """
        self.kill_trainers = True
        for t in self.trainer_threads:
            try:
                t.join(timeout_seconds)
            except Exception:
                pass

        with hierarchical_timer("trainer_threads") as main_timer_node:  # type: ignore
            for trainer_thread in self.trainer_threads:
                thread_timer_stack = get_timer_stack_for_thread(trainer_thread)
                if thread_timer_stack:
                    main_timer_node.merge(  # type: ignore
                        thread_timer_stack.root,
                        root_name="thread_root",
                        is_parallel=True,
                    )
                    merge_gauges(thread_timer_stack.gauges)

    def trainer_update_func(self, trainer: Trainer) -> None:
        # Do not access C# objects from separate threads
        while not self.kill_trainers:
            with hierarchical_timer("trainer_advance"):
                trainer.advance()
