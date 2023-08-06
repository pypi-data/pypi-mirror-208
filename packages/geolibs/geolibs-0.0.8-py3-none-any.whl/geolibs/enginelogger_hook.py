import os
import glob

from mmengine.registry import HOOKS
from mmengine.dist import master_only
from mmengine.hooks.logger_hook import LoggerHook

from typing import Dict, Optional, Union


@HOOKS.register_module()
class EngineLoggerHook(LoggerHook):
    """Class to log metrics with engine.
    It requires `granular-engine`_ to be installed.
    Args:
        init_kwargs (dict): A dict contains the initialization keys. Check
            https://pypi.org/project/granular-engine/ for more init arguments.
        interval (int): Logging interval (every k iterations).
            Default 10.
        ignore_last (bool): Ignore the log of last iterations in each epoch
            if less than `interval`.
            Default: True.
        reset_flag (bool): Whether to clear the output buffer after logging.
            Default: False.
        commit (bool): Save the metrics dict to the engine server and increment
            the step. If false ``engine.log`` just updates the current metrics
            dict with the row argument and metrics won't be saved until
            ``engine.log`` is called with ``commit=True``.
            Default: True.
        by_epoch (bool): Whether EpochBasedRunner is used.
            Default: True.
        log_artifact (bool): If True, artifacts in {work_dir} will be uploaded
            to engine after training ends.
            Default: True
            `New in version 1.4.3.`
        out_suffix (str or tuple[str], optional): Those filenames ending with
            ``out_suffix`` will be uploaded to engine.
            Default: ('.log.json', '.log', '.py').
            `New in version 1.4.3.`
    """

    def __init__(self,
                 init_kwargs: Optional[Dict] = None,
                 interval: int = 10,
                 ignore_last: bool = True,
                 reset_flag: bool = False,
                 commit: bool = True,
                 by_epoch: bool = True,
                 log_artifact: bool = True,
                 out_suffix: Union[str, tuple] = ('.log.json', '.log', '.py')
                 ):
        super().__init__(interval=interval, 
                         ignore_last=ignore_last, 
                         keep_local=reset_flag, 
                         log_metric_by_epoch=by_epoch)
        self.init_kwargs = init_kwargs
        self.commit = commit
        self.log_artifact = log_artifact
        self.out_suffix = out_suffix
        self.by_epoch = by_epoch
        
    def import_engine(self) -> None:
        try:
            from engine import Engine
        except ImportError:
            raise ImportError(
                'Please run "pip install granular-engine" to install engine')
        self.engine = Engine(**self.init_kwargs)

    @master_only
    def before_run(self, runner) -> None:
        super().before_run(runner)
        if self.init_kwargs:
            self.import_engine()

    @master_only
    def after_train_iter(self,
                         runner,
                         batch_idx: int,
                         data_batch: Optional[Union[dict, tuple, list]] = None,
                         outputs: Optional[dict] = None) -> None:
        """All subclasses should override this method, if they need any
        operations after each validation epoch.
        Args:
            runner (Runner): The runner of the validation process.
            metrics (Dict[str, float], optional): Evaluation results of all
                metrics on validation dataset. The keys are the names of the
                metrics, and the values are corresponding results.
        """
        if self.every_n_inner_iters(batch_idx, self.interval):
            if self.log_artifact:
                tag, log_str = runner.log_processor.get_log_after_iter(
                        runner, batch_idx, 'train')
                out = {}
                for k in tag.keys():
                    out[f"train/{k}"] = tag[k]

                self.engine.log(step=runner.iter + 1, **out)

            
    @master_only
    def after_val_epoch(self, 
                        runner, 
                        metrics: Optional[Dict[str, float]] = None) -> None:
        if self.log_artifact:
            dst_path = self.engine.meta['experimentUrl']
            os.system(f"gsutil -m cp -r {runner.work_dir}/*.py {dst_path}/ 2> /dev/null")
            os.system(f"gsutil -m cp -r {runner.work_dir}/*log* {dst_path}/ 2> /dev/null")

            best_ckpt_path = glob.glob(f"{runner.work_dir}/best*")
            if len(best_ckpt_path):
                best_ckpt_path = best_ckpt_path[0]
            else:
                best_ckpt_path = None

            out = {}
            for k in metrics.keys():
                out[f"val/{k}"] = metrics[k]

            self.engine.log(step=runner.iter + 1,
                            best=True,
                            checkpoint_path=best_ckpt_path, 
                            **out)

    @master_only
    def after_run(self, runner) -> None:
        self.engine.done()