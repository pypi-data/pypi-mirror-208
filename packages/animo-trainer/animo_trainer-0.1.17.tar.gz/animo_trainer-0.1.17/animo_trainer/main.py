import os, argparse, logging
from pathlib import Path
from typing import Optional

from animo_trainer import __version__

ASCII_LOGO = f"""
---------------------
Transitional Forms Inc.
---------------------
"""

parser = argparse.ArgumentParser(prog="animo-learn")
parser.add_argument(
    "training_session_full_path", nargs="?", default=None
)
parser.add_argument(
    "--daemon",
    type=int,
    default=None,
    help="Process id. If process dead at check the training will be interrupted",
)

parser.add_argument(
    "-v",
    "--version",
    action='version', version=f"%(prog)s {__version__}"
)

def main():
    parsed_args = parser.parse_args()
    print(ASCII_LOGO)

    # TODO: Move to docs (-h)
    # This is the path to the native library that contains mono
    # ANIMO_PYTHONNET_LIBMONO=/Users/dante/Desktop/Builds/LLM.app/Contents/Frameworks/libmonobdwgc-2.0.dylib

    # This is a Colon Separated (I think it might be semicolons in windows) list of folders where managed DLL paths are loaded from
    # This path should contain mscorlib.dll
    # MONO_PATH="/Users/dante/Desktop/Builds/LLM.app/Contents/Resources/Data/Managed"

    # This is where the config file for mono is stored
    # MONO_CONFIG="/Users/dante/Desktop/Builds/LLM.app/Contents/MonoBleedingEdge/etc/mono/config"

    # If this is set, and MONO_CONFIG is set, Mono will be initialized with an updated config that
    # expands the $mono_libdir macro inside the config to the given path. This path should contain MonoPosixHelper
    # ANIMO_MONO_LIBRARY="/Users/dante/Desktop/Builds/LLM.app/Contents/Frameworks"

    runtime = None
    libmono = os.getenv("ANIMO_PYTHONNET_LIBMONO")

    if libmono:
        mono_path = os.getenv("MONO_PATH")
        if not mono_path:
            print("Setting ANIMO_PYTHONNET_LIBMONO without setting MONO_PATH is likely an Error.")
        config_path = os.getenv("MONO_CONFIG")
        lib_path = os.getenv("ANIMO_MONO_LIBRARY")
        if lib_path and config_path:
            with open(config_path, mode='r', encoding='utf-8') as file:
                config_str = file.read()
            config_path = str(Path("./llm_mono_config").resolve())

            config_str = config_str.replace("$mono_libdir", lib_path)

            with open(config_path, mode='w', encoding='utf-8') as file:
                file.write(config_str)

            os.environ["MONO_CONFIG"] = config_path

        import clr_loader
        runtime = clr_loader.get_mono(libmono=libmono, debug=False)  # type: ignore

    import pythonnet

    pythonnet.load(runtime)
    import clr, pathlib

    def load_dll(base_path: str, override_path: Optional[str], dll_name: str):
        base_dll = os.path.join(base_path, dll_name)

        if not override_path:
            clr.AddReference(base_dll)
            return

        override_dll = os.path.join(override_path, dll_name)

        if os.path.isfile(override_dll):
            clr.AddReference(override_dll)
            return

        if os.path.isfile(base_dll):
            clr.AddReference(base_dll)
            return

        raise ValueError(f"Missing important dll: {dll_name}")

    current_dir = pathlib.Path(__file__).parent.resolve()
    animo_unity_dll_dir = os.path.realpath(os.path.join(current_dir, "lib"))

    os.environ["PATH"] += os.pathsep + animo_unity_dll_dir
    dll_dir_override = os.getenv("ANIMO_DLL_DIRECTORY")

    if dll_dir_override:
        print("DLL OVERRIDE PATH {}".format(dll_dir_override))

    load_dll(animo_unity_dll_dir, dll_dir_override, "System.Numerics.Vectors.dll")
    load_dll(animo_unity_dll_dir, dll_dir_override, "Newtonsoft.Json.dll")
    load_dll(animo_unity_dll_dir, dll_dir_override, "AnimoSimulation.dll")
    load_dll(animo_unity_dll_dir, dll_dir_override, "AnimoData.dll")

    from TransformsAI.Animo.Tools import AnimoLogger
    AnimoLogger.RegisterLogger(AnimoLogger.StandardLogger)

    from animo_trainer.animo_training_session import AnimoTrainingSession
    from animo_trainer.animo_trainer_controller import AnimoTrainingController
    from animo_trainer.animo_stats_writers import register_animo_stats_writers
    from mlagents.plugins.trainer_type import register_trainer_plugins
    register_trainer_plugins()

    training_session_folder_path = parsed_args.training_session_full_path
    if training_session_folder_path is None:
        raise ValueError("Training session full path must be provided")

    training_session_data = AnimoTrainingSession(training_session_folder_path, parsed_args.daemon)

    register_animo_stats_writers(training_session_data.run_options)

    animo_trainer_controller = AnimoTrainingController(training_session_data)
    print(f"Animo-Learn::Started")
    animo_trainer_controller.train()
    try:
        pythonnet.unload()
    except Exception as e:
        logging.exception(e)
    print(f"Animo-Learn::Stopped")


if __name__ == "__main__":
    main()
