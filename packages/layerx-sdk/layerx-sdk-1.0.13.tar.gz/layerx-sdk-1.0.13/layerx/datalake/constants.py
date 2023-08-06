# System Label Type
from enum import Enum

LABEL_CLASS = 1
LABEL_CLASS_WITH_ATTRIBUTES = 2
FILE_UPLOAD_THREADS = 10
SUB_FILE_LENGTH = 100
# Annotation Geometric Type
LINE_ANNOTATION = 'line'
POLYGON_ANNOTATION = 'polygon'
BOX_ANNOTATION = 'rectangle'

# Operation Data Meta Updates
OPERATION_TYPE_ANNOTATION = 1
OPERATION_MODE_HUMAN = 1
OPERATION_MODE_AUTO = 2

# Request Batch Sizes
META_UPDATE_REQUEST_BATCH_SIZE = 1000


class MediaType(Enum):
    VIDEO = 4
    IMAGE = 5
    OTHER = 7

class ObjectType(Enum):
    VIDEO = 1
    IMAGE = 2
    DATASET = 3
    VIDEO_COLLECTION = 4
    IMAGE_COLLECTION = 5

class JobStatus(Enum):
    IN_PROGRESS = 1
    COMPLETED = 2
    QUEUED = 3
    FAILED = 4
