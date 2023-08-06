import os
import hyped
import datasets
import transformers
import pydantic
import dataclasses
from datetime import datetime
from typing_extensions import Annotated
from typing import Optional, Any


import warnings
# ignore warning of _n_gpu field of TrainingArguments
# dataclass when converted to pydantic model
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="fields may not start with an underscore, ignoring \"_n_gpu\""
)

class DataConfig(pydantic.BaseModel):
    """Data Configuration Model"""
    dataset:str
    splits:dict[str, str] = {
        datasets.Split.TRAIN: datasets.Split.TRAIN,
        datasets.Split.VALIDATION: datasets.Split.VALIDATION,
        datasets.Split.TEST: datasets.Split.TEST
    }
    kwargs:dict = {}

    @pydantic.validator('dataset')
    def _check_dataset(cls, v):
        if v is None:
            raise ValueError("No Dataset provided by configuration!")
        try:
            # try to load dataset builder
            builder = datasets.load_dataset_builder(v)
            return v
        except FileNotFoundError as e:
            # raise exception if dataset builder cannot be found
            raise ValueError("Dataset not found: %s" % v) from e

    @pydantic.validator('kwargs')
    def _prepare_kwargs(cls, v):
        if 'data_files' in v:
            data_files = v['data_files']
            # make data files absolut paths
            if isinstance(data_files, str):
                data_files = os.path.abspath(data_files)
            elif isinstance(data_files, (tuple, list)):
                data_files = [os.path.abspath(f) for f in data_files]
            elif isinstance(data_files, dict):
                data_files = {k: os.path.abspath(f) for k,f in data_files.items()}
            # update data files
            v['data_files'] = data_files
        return v

class PrepareConfig(pydantic.BaseModel):
    """Data Configuration Model"""
    # dataset config
    data:DataConfig
    # preprocessing pipeline
    pipeline:list[
        Annotated[
            hyped.pipeline.AnyProcessorConfig,
            pydantic.Field(..., discriminator='processor_type')
        ]
    ]
    filters:list[hyped.pipeline.AnyFilterConfig]
    # columns to keep
    columns:dict[str, str]

    # data filters
    #filters:list[
    #    Annotated[
    #        hyped.AnyFilterConfig,
    #        pydantic.Field(..., discriminator='filter_type')
    #    ]
    #]

class ModelConfig(pydantic.BaseModel):
    """Model Configuration Model"""
    # base model
    pretrained_ckpt:str
    kwargs:dict ={}
    # adapters and heads

    heads:dict[
        str,
        Annotated[
            hyped.modeling.heads.AnyHypedHeadConfig,
            pydantic.Field(..., discriminator='head_type')
        ]
    ]

    def check_and_prepare(self, features:datasets.Features) -> None:
        [hconfig.check_and_prepare(features) for hconfig in self.heads.values()]

    @property
    def pretrained_config(self) -> transformers.PretrainedConfig:
        config = transformers.AutoConfig.from_pretrained(self.pretrained_ckpt)
        config.prediction_heads = {hname: dataclasses.asdict(hconfig) for hname, hconfig in self.heads.items()}
        return config

    @pydantic.validator('pretrained_ckpt')
    def _check_pretrained_ckpt(cls, value):
        try:
            # check if model is valid by loading config
            transformers.AutoConfig.from_pretrained(value)
        except OSError as e:
            # handle model invalid
            raise ValueError("Unkown pretrained checkpoint: %s" % value) from e

        return value

@pydantic.dataclasses.dataclass
@dataclasses.dataclass
class TrainerConfig(transformers.TrainingArguments):
    """ Trainer Configuration """
    # passed fromi run config and needed for output directory
    name:str =None
    # create default for output directory
    run_name:str ="{name}-{timestamp}"
    output_dir:str ="output/{name}-{timestamp}"
    overwrite_output_dir:bool =True
    # early stopping setup
    early_stopping_patience:Optional[int] =1
    early_stopping_threshold:Optional[float] =0.0
    # checkpointing
    load_best_model_at_end:bool =True
    metric_for_best_model:str ='eval_loss'
    greater_is_better:bool =False
    # overwrite some default values
    do_train:bool =True
    do_eval:bool =True
    evaluation_strategy:transformers.trainer_utils.IntervalStrategy ="epoch"
    save_strategy:transformers.trainer_utils.IntervalStrategy ="epoch"
    eval_accumulation_steps:Optional[int] =1
    save_total_limit:Optional[int] =3
    label_names:list[str] =dataclasses.field(default_factory=lambda: ['labels'])
    report_to:Optional[list[str]] =dataclasses.field(default_factory=list)
    log_level:Optional[str] ='warning'
    # fields with incomplete types in Training Arguments
    # set type to avoid error in pydantic validation
    debug:str|list[transformers.debug_utils.DebugOption]               =""
    sharded_ddp:str|list[transformers.trainer_utils.ShardedDDPOption]  =""
    fsdp:str|list[transformers.trainer_utils.FSDPOption]               =""
    fsdp_config:Optional[str|dict]                                     =None
    # don't do that because we use args and kwargs in the
    # model's forward function which confuses the trainer
    remove_unused_columns:bool =False

    # use pytorch implementation of AdamW optimizer
    # to avoid deprecation warning
    optim="adamw_torch"

    @pydantic.root_validator()
    def _format_output_directory(cls, values):
        # get timestamp
        timestamp=datetime.now().isoformat()
        # format all values depending on output directory
        return values | {
            'output_dir': values.get('output_dir').format(
                name=values.get('name'),
                timestamp=datetime.now().isoformat()
            ),
            'logging_dir': values.get('logging_dir').format(
                name=values.get('name'),
                timestamp=datetime.now().isoformat()
            ),
            'run_name': values.get('run_name').format(
                name=values.get('name'),
                timestamp=datetime.now().isoformat()
            ),
        }

class RunConfig(pydantic.BaseModel):
    """Run Configuration Model"""
    # run name
    name:str
    # model and trainer configuration
    model:ModelConfig
    trainer:TrainerConfig
    metrics:dict[str,dict[str,Any]]

    @pydantic.validator('trainer', pre=True)
    def _pass_name_to_trainer_config(cls, v, values):
        assert 'name' in values
        if isinstance(v, pydantic.BaseModel):
            return v.copy(update={'name': values.get('name')})
        elif isinstance(v, dict):
            return v | {'name': values.get('name')}
