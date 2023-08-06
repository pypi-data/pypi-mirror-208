from mlagents.trainers.stats import StatsReporter, TensorboardWriter, GaugeWriter, ConsoleWriter
from mlagents.trainers.settings import RunOptions

def register_animo_stats_writers(run_options: RunOptions) -> None:
    stats_writers = [
        TensorboardWriter(
            run_options.checkpoint_settings.results_dir,
            clear_past_data = True,
            hidden_keys = ["Is Training", "Step"],
        ),
        GaugeWriter(),
        ConsoleWriter(),
    ]

    for sw in stats_writers:
            StatsReporter.add_writer(sw)