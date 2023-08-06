import warnings

from pathlib import Path
from napari._qt.qthreading import GeneratorWorker
from napari.qt.threading import create_worker
from typing import Generator, Tuple

# from aicssegmentation.workflow import BatchWorkflow  # WorkflowEngine,
from infer_subc.workflow import WorkflowEngine, BatchWorkflow
from organelle_segmenter_plugin.core._interfaces import IApplication
from organelle_segmenter_plugin.core.controller import Controller
from organelle_segmenter_plugin.view.batch_processing_view import BatchProcessingView
from organelle_segmenter_plugin.widgets.batch_complete_dialog import BatchCompleteDialog
from ._interfaces import IBatchProcessingController

from typing import List


class BatchProcessingController(Controller, IBatchProcessingController):
    _worker: GeneratorWorker = None
    _batch_workflow: BatchWorkflow

    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine = workflow_engine
        self._view = BatchProcessingView(self)

        self._input_folder = None
        self._output_folder = None
        self._channel_index = None

        self._workflow_config = None
        self._workflow_config = None

        self._segmentation_names = None
        self._segmentation_name = None

        self._run_lock = False  # lock to avoid triggering multiple runs at the same time
        self._canceled = False

    @property
    def view(self):
        return self._view

    def index(self):
        self.load_view(self._view)

    def run_batch(self):
        if not self._run_lock:
            self._worker: GeneratorWorker = create_worker(self._run_batch_async)
            self._worker.yielded.connect(self._on_step_processed)
            self._worker.started.connect(self._on_run_batch_started)
            self._worker.aborted.connect(self._on_run_batch_aborted)
            self._worker.finished.connect(self._on_run_batch_finished)
            self._worker.start()

    def cancel_run_batch(self):
        if self._worker is not None:
            self._worker.quit()

    def update_batch_parameters(
        self,
        workflow_configs: List[Path],
        channel_index: int,
        input_dir: Path,
        output_dir: Path,
        segmentation_names: List[str],
    ):
        self._workflow_configs = workflow_configs
        self._workflow_config = workflow_configs[0]
        if segmentation_names is None:
            # segmentation_names = [wf.stem.split("_")[0] for wf in workflow_configs]
            segmentation_names = [wf.stem.split("-")[-1] for wf in workflow_configs]
            print(f"should never get here--> programmic segmentation_name = {segmentation_names}")

        self._segmentation_names = segmentation_names
        self._segmentation_name = segmentation_names[0]

        self._channel_index = channel_index
        self._input_folder = input_dir
        self._output_folder = output_dir

        ready = self._ready_to_process()
        # print(f" ch={channel_index}, inp={input_dir}, out={output_dir}   : ready={ready} ")
        self._view.update_button(ready)

    def _ready_to_process(self) -> bool:
        """
        Check to see if the batch processing is ready to start
        (user has provided all needed parameters to run a batch workflow)

        Outputs:
            (Bool): True if ready to start batch workflow, False if not
        """
        if self._workflow_config is None:
            return False
        if self._segmentation_name is None:
            return False
        if self._input_folder is None:
            return False
        if self._output_folder is None:
            return False
        if self._channel_index is None:
            return False
        # JAH: hack
        if self._workflow_configs is None:
            return False
        if self._segmentation_names is None:
            return False
        return True

    def _run_batch_async(self) -> Generator[Tuple[int, int], None, None]:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # JAH: refactor channel -> z_slice... what do i need to do for the workflow engine?
            # add segmentation name
            # batch_workflow = self._workflow_engine.get_executable_batch_workflow_from_config_file(
            #     self._workflow_config,
            #     self._input_folder,
            #     self._output_folder,
            #     segmentation_name=self._segmentation_name,
            #     channel_index=self._channel_index,
            # )
            batch_workflows = self._workflow_engine.get_executable_batch_workflows_from_config_file(
                self._workflow_configs,
                self._input_folder,
                self._output_folder,
                segmentation_names=self._segmentation_names,
                channel_index=self._channel_index,
            )

            while not batch_workflows.is_done():
                batch_workflows.execute_next()
                yield batch_workflows.processed_files, batch_workflows.total_files

            batch_workflows.write_log_file_summary()

    def _on_step_processed(self, processed_args: Tuple[int, int]):
        processed_files, total_files = processed_args
        # Update progress
        progress = 100 * processed_files // total_files
        self._view.set_progress(progress)

    def _on_run_batch_started(self):
        self._run_lock = True
        self._view.set_run_batch_in_progress()

    def _on_run_batch_finished(self):
        self._run_lock = False

        if not self._canceled:
            # Open completion dialog
            # TODO: this should be moved back to batch_processing_view, but testing QDialog.exec_()
            # is tricky
            completion_dlg = BatchCompleteDialog(self._output_folder)
            completion_dlg.exec_()

        self._view.reset_run_batch()
        self._canceled = False

    def _on_run_batch_aborted(self):
        self._canceled = True
