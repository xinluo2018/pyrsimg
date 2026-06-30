## author: xin luo
## create: 2021.10.27, modify: 2023.10.1


import numpy as np
import itertools
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix

class metrics_segm:
    def __init__(self, cla_map, truth_map, 
                 class_labels=None, mean_mode=False):
        """
        cla_map: predicted segmentation map, 2D numpy array of shape (H, W) or (B, H, W)
        truth_map: ground truth map, 2D numpy array of shape matching cla_map
        """     
        self.cla_map = cla_map
        self.truth_map = truth_map
        # Ensure input shapes match
        if cla_map.shape != truth_map.shape:
            raise ValueError("Shape of cla_map and truth_map must match.")        
        # Get unique class labels if not provided
        if class_labels is None:
            self.class_labels = np.unique(np.concatenate([cla_map.flatten(), 
                                                          truth_map.flatten()]))
        else:
            self.class_labels = np.array(class_labels)
        self.mean_mode = mean_mode
    def _get_intersection_union(self, class_label):
        """
        Helper function to compute intersection and union for a specific class
        """
        intersection = np.logical_and(self.cla_map == class_label, 
                                      self.truth_map == class_label).sum()
        union = np.logical_or(self.cla_map == class_label, 
                              self.truth_map == class_label).sum()
        return intersection, union

    @property
    def oa(self):
        """
        Overall Accuracy (OA) for binary segmentation
        """
        oa = np.mean(self.cla_map == self.truth_map)
        return oa

    @property
    def iou(self, target_class_labels=None):
        """Intersection over Union (IoU) for a specific class
        """        
        if target_class_labels is None:
            target_class_labels = self.class_labels    
        iou_scores = {}
        for c in target_class_labels:
            intersection, union = self._get_intersection_union(c)
            iou_scores[f'label_{c.item()}'] = intersection / (union + 1e-7)  # avoid division by zero
        if self.mean_mode:
            iou_scores[f'labels_mean'] = np.mean(list(iou_scores.values()))
        return iou_scores

    @property
    def dice(self, target_class_labels=None):
        """Dice Coefficient for a specific class
        """        
        if target_class_labels is None:
            target_class_labels = self.class_labels    
        dice_scores = {}
        for c in target_class_labels:
            intersection, union = self._get_intersection_union(c)
            dice_scores[f'label_{c.item()}'] = (2 * intersection) / (union + intersection + 1e-7)  # avoid division by zero
        if self.mean_mode:
            dice_scores['labels_mean'] = np.mean(list(dice_scores.values()))
        return dice_scores

    @property
    def precision(self, target_class_labels=None):
        """Precision for a specific class
        """        
        if target_class_labels is None:
            target_class_labels = self.class_labels    
        precision_scores = {}
        for c in target_class_labels:
            tp = np.logical_and(self.cla_map == c, self.truth_map == c).sum()
            fp = np.logical_and(self.cla_map == c, self.truth_map != c).sum()
            precision_scores[f'label_{c.item()}'] = tp / (tp + fp + 1e-7)  # avoid division by zero
        if self.mean_mode:
            precision_scores['labels_mean'] = np.mean(list(precision_scores.values()))
        return precision_scores

    @property
    def recall(self, target_class_labels=None):
        """Recall for a specific class
        """        
        if target_class_labels is None:
            target_class_labels = self.class_labels    
        recall_scores = {}
        for c in target_class_labels:
            tp = np.logical_and(self.cla_map == c, self.truth_map == c).sum()
            fn = np.logical_and(self.cla_map != c, self.truth_map == c).sum()
            recall_scores[f'label_{c.item()}'] = tp / (tp + fn + 1e-7)  # avoid division by zero
        if self.mean_mode:
            recall_scores['labels_mean'] = np.mean(list(recall_scores.values()))
        return recall_scores

    @property
    def f1_score(self, target_class_labels=None):
        """F1 Score for a specific class
        """        
        if target_class_labels is None:
            target_class_labels = self.class_labels    
        f1_scores = {}
        for c in target_class_labels:
            tp = np.logical_and(self.cla_map == c, self.truth_map == c).sum()
            fp = np.logical_and(self.cla_map == c, self.truth_map != c).sum()
            fn = np.logical_and(self.cla_map != c, self.truth_map == c).sum()
            precision = tp / (tp + fp + 1e-7)
            recall = tp / (tp + fn + 1e-7)
            f1_scores[f'label_{c.item()}'] = (2 * precision * recall) / (precision + recall + 1e-7)    
        if self.mean_mode:
            f1_scores['labels_mean'] = np.mean(list(f1_scores.values()))
        return f1_scores

## note: should separate the pixel-based accuracy matrix 
#         and the image-based accuracy matrix.
def acc_matrix(cla_map, truth_map=None, sam_pixel=None, id_label=None):
    ''' 
    des: calculate the accuracy matrix
    args: 
        cla_map: classification result of the full image.
        truth_map: truth image (either truth_map or sam_pixel should be given).
        sam_pixel: np.array, (num_samples,3), col 1,2,3 are the row,col and label.            
        id_label: 0/1/2/..., Calculating producer's or user's accuracy for target class.
    Note: Either one of the truth_map and sam_pixel should be determination. 
    Return: 
        acc_oa, confus_mat: the overall accuracy and confusion matrix
    '''
    if sam_pixel is not None:
        sam_result = []
        sam_label = sam_pixel[:,2]
        num_cla = sam_label.max()+1
        labels = list(range(num_cla))
        for i in range(sam_label.shape[0]):
            sam_result.append(cla_map[sam_pixel[i,0], sam_pixel[i,1]])            
        sam_result = np.array(sam_result)
    if truth_map is not None:
        sam_label = truth_map.flatten()  
        sam_result = cla_map.flatten()
        num_cla = sam_label.max()+1
        labels = list(range(num_cla))
    acc_oa = np.around(accuracy_score(sam_label, sam_result), 4)
    confus_mat = confusion_matrix(sam_label, sam_result, labels=labels)
    if id_label is not None:
        acc_prod=np.around(confus_mat[id_label, id_label]/confus_mat[id_label,:].sum(), 4)
        acc_user=np.around(confus_mat[id_label, id_label]/confus_mat[:,id_label].sum(), 4)
        return acc_oa, acc_prod, acc_user, confus_mat
    else:
        return acc_oa, confus_mat

## note: deprecated, use metrics_segm instead
def acc_miou(cla_map, truth_map, labels=None):
    '''
    des: calculate the mean IoU metric.
    args:
        cla_map: classification result of the full image
        truth_map: truth image (either truth_map or sam_pixel should be given)
        labels: a list, the class id for calculating. e.g., [0,1,2]
    return:
        MIoU score
    '''  
    iou = []
    if labels == None:
        labels = np.unique(truth_map)
    for label in labels:
        intersection = np.logical_and(cla_map==label, truth_map==label)
        union = np.logical_or(cla_map==label, truth_map==label)
        iou_score = np.sum(intersection)/np.sum(union)
        iou.append(iou_score)
    return np.mean(iou)

## --- accuracy matrix ploting ---
def plot_confusion_matrix(confus_matrix, classes, normalize=False, title='Confusion matrix', cmap=plt.cm.Blues):
    ''' 
    des: plot the accuracy matrix.
    args: 
        confus_matrix: np.array, confusion matrix derived by using sklearn.metrics.confusion_matrix
        classes: list, labels name.
        normalize: option, if True, the value of matrix should be normalized to 0~1.
    Return: 
        none
    '''

    if normalize:
        cm = cm.astype('float') / confus_matrix.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt), horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

