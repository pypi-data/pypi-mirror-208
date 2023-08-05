import math
from dataclasses import dataclass
from typing import Union, Callable, Type, Dict, Literal, Tuple, Any

from aislib.misc_utils import get_logger
from torch import nn
from transformers import PreTrainedModel, AutoModel, AutoConfig

from eir.models.models_base import get_output_dimensions_for_input
from eir.models.sequence.transformer_models import (
    TransformerFeatureExtractor,
    PerceiverIOFeatureExtractor,
    SequenceModelConfig,
    TransformerWrapperModel,
    BasicTransformerFeatureExtractorModelConfig,
    PerceiverIOModelConfig,
    get_embedding_dim_for_sequence_model,
)
from eir.setup.setup_utils import get_unsupported_hf_models

logger = get_logger(name=__name__)


@dataclass
class SequenceModelObjectsForWrapperModel:
    feature_extractor: Union[
        TransformerFeatureExtractor, PerceiverIOFeatureExtractor, nn.Module
    ]
    embeddings: Union[None, nn.Module]
    embedding_dim: int
    external: bool
    known_out_features: Union[None, int]


def get_sequence_model(
    sequence_model_config: SequenceModelConfig,
    model_registry_lookup: Callable[[str], Type[nn.Module]],
    num_tokens: int,
    max_length: int,
    embedding_dim: int,
    device: str,
) -> TransformerWrapperModel:
    feature_extractor_max_length = max_length
    num_chunks = 1
    if sequence_model_config.window_size:
        logger.info(
            "Using sliding model for sequence input as window size was set to %d.",
            sequence_model_config.window_size,
        )
        feature_extractor_max_length = sequence_model_config.window_size
        num_chunks = math.ceil(max_length / sequence_model_config.window_size)

    objects_for_wrapper = _get_sequence_feature_extractor_objects_for_wrapper_model(
        model_type=sequence_model_config.model_type,
        model_registry_lookup=model_registry_lookup,
        pretrained=sequence_model_config.pretrained_model,
        pretrained_frozen=sequence_model_config.freeze_pretrained_model,
        model_config=sequence_model_config.model_init_config,
        num_tokens=num_tokens,
        embedding_dim=embedding_dim,
        feature_extractor_max_length=feature_extractor_max_length,
        num_chunks=num_chunks,
        pool=sequence_model_config.pool,
    )

    wrapper_model_class = model_registry_lookup(model_type="sequence-wrapper-default")
    sequence_model = wrapper_model_class(
        feature_extractor=objects_for_wrapper.feature_extractor,
        external_feature_extractor=objects_for_wrapper.external,
        model_config=sequence_model_config,
        embedding_dim=objects_for_wrapper.embedding_dim,
        num_tokens=num_tokens,
        max_length=max_length,
        embeddings=objects_for_wrapper.embeddings,
        device=device,
        pre_computed_num_out_features=objects_for_wrapper.known_out_features,
    ).to(device=device)

    return sequence_model


def _get_sequence_feature_extractor_objects_for_wrapper_model(
    model_type: str,
    model_registry_lookup: Callable[[str], Type[nn.Module]],
    pretrained: bool,
    pretrained_frozen: bool,
    model_config: Union[
        BasicTransformerFeatureExtractorModelConfig, PerceiverIOModelConfig, Dict
    ],
    num_tokens: int,
    embedding_dim: int,
    feature_extractor_max_length: int,
    num_chunks: int,
    pool: Union[Literal["max"], Literal["avg"], None],
) -> SequenceModelObjectsForWrapperModel:
    if "sequence-default" in model_type or model_type.startswith("eir-"):
        model_class = model_registry_lookup(model_type=model_type)
        objects_for_wrapper = _get_basic_sequence_feature_extractor_objects(
            model_config=model_config,
            num_tokens=num_tokens,
            feature_extractor_max_length=feature_extractor_max_length,
            embedding_dim=embedding_dim,
            feature_extractor_class=model_class,
        )
    elif model_type == "perceiver":
        objects_for_wrapper = _get_perceiver_sequence_feature_extractor_objects(
            model_config=model_config,
            max_length=feature_extractor_max_length,
            num_chunks=num_chunks,
        )
    elif pretrained:
        objects_for_wrapper = _get_pretrained_hf_sequence_feature_extractor_objects(
            model_name=model_type,
            frozen=pretrained_frozen,
            feature_extractor_max_length=feature_extractor_max_length,
            num_chunks=num_chunks,
            num_tokens=num_tokens,
            pool=pool,
        )
    else:
        objects_for_wrapper = _get_hf_sequence_feature_extractor_objects(
            model_name=model_type,
            model_config=model_config,
            feature_extractor_max_length=feature_extractor_max_length,
            num_chunks=num_chunks,
            pool=pool,
        )

    return objects_for_wrapper


def _get_manual_out_features_for_external_feature_extractor(
    input_length: int,
    embedding_dim: int,
    num_chunks: int,
    feature_extractor: nn.Module,
    pool: Union[Literal["max"], Literal["avg"], None],
) -> int:
    input_shape = _get_sequence_input_dim(
        input_length=input_length,
        embedding_dim=embedding_dim,
    )
    out_feature_shape = get_output_dimensions_for_input(
        module=feature_extractor,
        input_shape=input_shape,
        hf_model=True,
        pool=pool,
    )
    manual_out_features = out_feature_shape.numel() * num_chunks

    return manual_out_features


def _get_sequence_input_dim(
    input_length: int, embedding_dim: int
) -> Tuple[int, int, int]:
    return 1, input_length, embedding_dim


def _get_pretrained_hf_sequence_feature_extractor_objects(
    model_name: str,
    num_tokens: int,
    frozen: bool,
    feature_extractor_max_length: int,
    num_chunks: int,
    pool: Union[Literal["max"], Literal["avg"], None],
) -> SequenceModelObjectsForWrapperModel:
    _warn_about_unsupported_hf_model(model_name=model_name)

    pretrained_model = _get_hf_pretrained_model(model_name=model_name)
    pretrained_model.resize_token_embeddings(new_num_tokens=num_tokens)
    pretrained_model_embeddings = pretrained_model.get_input_embeddings()
    feature_extractor = pretrained_model

    if frozen:
        logger.info("Freezing weights and embeddings of model '%s'.", model_name)
        for param in feature_extractor.parameters():
            param.requires_grad = False
        for param in pretrained_model_embeddings.parameters():
            param.requires_grad = False

    pretrained_embedding_dim = _pretrained_hf_model_embedding_dim(
        embeddings=pretrained_model_embeddings,
        model_name=model_name,
    )
    known_out_features = _get_manual_out_features_for_external_feature_extractor(
        input_length=feature_extractor_max_length,
        embedding_dim=pretrained_embedding_dim,
        num_chunks=num_chunks,
        feature_extractor=feature_extractor,
        pool=pool,
    )
    objects_for_wrapper = SequenceModelObjectsForWrapperModel(
        feature_extractor=pretrained_model,
        embeddings=pretrained_model_embeddings,
        embedding_dim=pretrained_embedding_dim,
        external=True,
        known_out_features=known_out_features,
    )

    return objects_for_wrapper


def _get_hf_pretrained_model(model_name: str) -> PreTrainedModel:
    pretrained_model = AutoModel.from_pretrained(
        pretrained_model_name_or_path=model_name
    )
    logger.info(
        "Loaded external pre-trained model '%s'. Note that this means that "
        "many configurations that might be set in input_type_info and model_config"
        "(e.g. 'embedding_dim') have no effect, as the default settings for "
        "the pre-trained model are used.",
        model_name,
    )
    return pretrained_model


def _get_hf_sequence_feature_extractor_objects(
    model_name: str,
    model_config: Dict[str, Any],
    feature_extractor_max_length: int,
    num_chunks: int,
    pool: Union[Literal["max"], Literal["avg"], None],
) -> SequenceModelObjectsForWrapperModel:
    _warn_about_unsupported_hf_model(model_name=model_name)

    feature_extractor = _get_hf_model(model_name=model_name, model_config=model_config)
    pretrained_model_embeddings = feature_extractor.get_input_embeddings()

    pretrained_embedding_dim = _pretrained_hf_model_embedding_dim(
        embeddings=pretrained_model_embeddings,
        model_name=model_name,
    )
    known_out_features = _get_manual_out_features_for_external_feature_extractor(
        input_length=feature_extractor_max_length,
        embedding_dim=pretrained_embedding_dim,
        num_chunks=num_chunks,
        feature_extractor=feature_extractor,
        pool=pool,
    )
    objects_for_wrapper = SequenceModelObjectsForWrapperModel(
        feature_extractor=feature_extractor,
        embeddings=None,
        embedding_dim=pretrained_embedding_dim,
        external=True,
        known_out_features=known_out_features,
    )

    return objects_for_wrapper


def _pretrained_hf_model_embedding_dim(
    embeddings: nn.Module, model_name: str = ""
) -> int:
    if hasattr(embeddings, "embedding_dim"):
        return embeddings.embedding_dim
    elif hasattr(embeddings, "dim"):
        return embeddings.dim
    elif hasattr(embeddings, "emb_layers"):
        return embeddings.emb_layers[0].embedding_dim

    raise ValueError(f"Could not find embedding dimension for model {model_name}.")


def _get_hf_model(model_name: str, model_config: Dict[str, Any]) -> nn.Module:
    config = AutoConfig.for_model(model_type=model_name, **model_config)
    model = AutoModel.from_config(config=config)
    logger.info(
        "Set up external (not using pre-trained weights) model '%s'. "
        "With configuration %s. Note that setting up external models ignores values "
        "for fields 'embedding_dim' and 'max_length' from input_type_info "
        "configuration. To configure these models, set the relevant values in the "
        "model_config field of the input configuration.",
        model_name,
        config,
    )
    return model


def _get_basic_sequence_feature_extractor_objects(
    model_config: BasicTransformerFeatureExtractorModelConfig,
    num_tokens: int,
    feature_extractor_max_length: int,
    embedding_dim: int,
    feature_extractor_class: Callable = TransformerFeatureExtractor,
) -> SequenceModelObjectsForWrapperModel:
    parsed_embedding_dim = get_embedding_dim_for_sequence_model(
        embedding_dim=embedding_dim,
        num_tokens=num_tokens,
        num_heads=model_config.num_heads,
    )

    feature_extractor = feature_extractor_class(
        model_config=model_config,
        num_tokens=num_tokens,
        max_length=feature_extractor_max_length,
        embedding_dim=parsed_embedding_dim,
    )

    objects_for_wrapper = SequenceModelObjectsForWrapperModel(
        feature_extractor=feature_extractor,
        embeddings=None,
        embedding_dim=parsed_embedding_dim,
        external=False,
        known_out_features=0,
    )

    return objects_for_wrapper


def _get_perceiver_sequence_feature_extractor_objects(
    model_config: PerceiverIOModelConfig,
    max_length: int,
    num_chunks: int,
):
    feature_extractor = PerceiverIOFeatureExtractor(
        model_config=model_config,
        max_length=max_length,
    )

    known_out_features = feature_extractor.num_out_features * num_chunks

    objects_for_wrapper = SequenceModelObjectsForWrapperModel(
        feature_extractor=feature_extractor,
        embeddings=None,
        embedding_dim=model_config.dim,
        external=False,
        known_out_features=known_out_features,
    )

    return objects_for_wrapper


def _sequence_model_registry(model_type: str) -> Type[nn.Module]:
    if model_type == "sequence-default":
        return TransformerFeatureExtractor
    elif model_type == "sequence-wrapper-default":
        return TransformerWrapperModel
    else:
        raise ValueError()


def _warn_about_unsupported_hf_model(model_name: str) -> None:
    unsupported_models = get_unsupported_hf_models()
    if model_name in unsupported_models.keys():
        reason = unsupported_models[model_name]
        logger.warning(
            "Model '%s' has not been tested for compatibility with EIR due to "
            "reason: '%s'. It is very likely that it will not work straight out of "
            "the box with EIR.",
            model_name,
            reason,
        )
