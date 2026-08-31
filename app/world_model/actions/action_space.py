from enum import IntEnum


class BiasAction(IntEnum):

    REDUCE_LANGUAGE_BIAS = 0

    DIVERSIFY_SOURCES = 1

    ADD_BALANCED_VIEWPOINT = 2

    IMPROVE_VISUAL_REPRESENTATION = 3


ACTION_NAMES = {

    BiasAction.REDUCE_LANGUAGE_BIAS:
        "reduce_language_bias",

    BiasAction.DIVERSIFY_SOURCES:
        "diversify_sources",

    BiasAction.ADD_BALANCED_VIEWPOINT:
        "add_balanced_viewpoint",

    BiasAction.IMPROVE_VISUAL_REPRESENTATION:
        "improve_visual_representation",
}


ACTION_DESCRIPTIONS = {

    BiasAction.REDUCE_LANGUAGE_BIAS:
        "Reduce biased or emotionally loaded language.",

    BiasAction.DIVERSIFY_SOURCES:
        "Increase diversity and variety of information sources.",

    BiasAction.ADD_BALANCED_VIEWPOINT:
        "Add alternative or underrepresented viewpoints.",

    BiasAction.IMPROVE_VISUAL_REPRESENTATION:
        "Improve balance in visual representation.",
}