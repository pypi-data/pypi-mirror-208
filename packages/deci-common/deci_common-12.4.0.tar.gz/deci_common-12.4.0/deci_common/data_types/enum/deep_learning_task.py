from enum import Enum


class DeepLearningTask(str, Enum):
    CLASSIFICATION = "classification"
    SEMANTIC_SEGMENTATION = "semantic_segmentation"
    OBJECT_DETECTION = "object_detection"
    NLP = "nlp"
    TEXT_RECOGNITION = "text_recognition"
    OTHER = "other"


class DeepLearningTaskLabel(str, Enum):
    CLASSIFICATION = "Classification"
    SEMANTIC_SEGMENTATION = "Semantic Segmentation"
    OBJECT_DETECTION = "Object Detection"
    NLP = "NLP"
    TEXT_RECOGNITION = "Text Recognition"
    OTHER = "Other"
