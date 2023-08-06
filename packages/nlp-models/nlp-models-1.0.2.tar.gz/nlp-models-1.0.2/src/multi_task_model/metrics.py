from typing import Optional, Literal
from torchmetrics.classification import (
    MultilabelHammingDistance,
    BinaryHammingDistance,
    MultilabelAccuracy,
    BinaryAccuracy
)


def hamming_distance(
    outputs, 
    targets, 
    multi_label: bool = False, 
    num_labels: Optional[int] = None, 
    average:Literal['micro', 'macro', 'weighted', 'none']='macro'
    ):
    if multi_label:
        if not num_labels:
            raise ValueError('num_labels is required for multi_label is True')
        else:
            hamming_distance = MultilabelHammingDistance(num_labels, average=average)
    else:
        hamming_distance = BinaryHammingDistance()
    return hamming_distance(outputs, targets)


def accuracy(
    outputs, 
    targets, 
    multi_label: bool = False, 
    num_labels: Optional[int] = None,
    average: Literal['micro', 'macro', 'weighted', 'none'] = 'macro'
    ):
    if multi_label:
        if not num_labels:
            raise ValueError('num_labels is required for multi_label is True')
        else:
            accuracy = MultilabelAccuracy(num_labels, average=average)
    else:
        accuracy = BinaryAccuracy()
    return accuracy(outputs, targets)
