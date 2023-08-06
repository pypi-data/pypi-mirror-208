# copyright (c) 2020 PaddlePaddle Authors. All Rights Reserve.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from ppocr.metrics.det_metric import DetMetric
import distance
from apted import APTED, Config
from apted.helpers import Tree
from lxml import etree, html
from collections import deque
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed


def parallel_process(array, function, n_jobs=16, use_kwargs=False, front_num=0):
    """
        A parallel version of the map function with a progress bar.

        Args:
            array (array-like): An array to iterate over.
            function (function): A python function to apply to the elements of array
            n_jobs (int, default=16): The number of cores to use
            use_kwargs (boolean, default=False): Whether to consider the elements of array as dictionaries of
                keyword arguments to function
            front_num (int, default=3): The number of iterations to run serially before kicking off the parallel job.
                Useful for catching bugs
        Returns:
            [function(array[0]), function(array[1]), ...]
    """
    # We run the first few iterations serially to catch bugs
    if front_num > 0:
        front = [function(**a) if use_kwargs else function(a) for a in array[:front_num]]
    else:
        front = []
    # If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs == 1:
        return front + [function(**a) if use_kwargs else function(a) for a in array[front_num:]]
    # Assemble the workers
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        # Pass the elements of array into function
        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array[front_num:]]
        else:
            futures = [pool.submit(function, a) for a in array[front_num:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        # Print out the progress as tasks complete
        for f in as_completed(futures):
            pass
    out = []
    # Get the results from the futures.
    for i, future in enumerate(futures):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return front + out


class TableTree(Tree):
    def __init__(self, tag, colspan=None, rowspan=None, content=None, *children):
        self.tag = tag
        self.colspan = colspan
        self.rowspan = rowspan
        self.content = content
        self.children = list(children)

    def bracket(self):
        """Show tree using brackets notation"""
        if self.tag == 'td':
            result = '"tag": %s, "colspan": %d, "rowspan": %d, "text": %s' % \
                     (self.tag, self.colspan, self.rowspan, self.content)
        else:
            result = '"tag": %s' % self.tag
        for child in self.children:
            result += child.bracket()
        return "{{{}}}".format(result)


class CustomConfig(Config):
    @staticmethod
    def maximum(*sequences):
        """Get maximum possible value
        """
        return max(map(len, sequences))

    def normalized_distance(self, *sequences):
        """Get distance from 0 to 1
        """
        return float(distance.levenshtein(*sequences)) / self.maximum(*sequences)

    def rename(self, node1, node2):
        """Compares attributes of trees"""
        if (node1.tag != node2.tag) or (node1.colspan != node2.colspan) or (node1.rowspan != node2.rowspan):
            return 1.
        if node1.tag == 'td':
            if node1.content or node2.content:
                return self.normalized_distance(node1.content, node2.content)
        return 0.


class TEDS(object):
    ''' Tree Edit Distance basead Similarity
    '''

    def __init__(self, structure_only=False, n_jobs=1, ignore_nodes=None):
        assert isinstance(n_jobs, int) and (n_jobs >= 1), 'n_jobs must be an integer greather than 1'
        self.structure_only = structure_only
        self.n_jobs = n_jobs
        self.ignore_nodes = ignore_nodes
        self.__tokens__ = []

    def tokenize(self, node):
        ''' Tokenizes table cells
        '''
        self.__tokens__.append('<%s>' % node.tag)
        if node.text is not None:
            self.__tokens__ += list(node.text)
        for n in node.getchildren():
            self.tokenize(n)
        if node.tag != 'unk':
            self.__tokens__.append('</%s>' % node.tag)
        if node.tag != 'td' and node.tail is not None:
            self.__tokens__ += list(node.tail)

    def load_html_tree(self, node, parent=None):
        ''' Converts HTML tree to the format required by apted
        '''
        global __tokens__
        if node.tag == 'td':
            if self.structure_only:
                cell = []
            else:
                self.__tokens__ = []
                self.tokenize(node)
                cell = self.__tokens__[1:-1].copy()
            new_node = TableTree(node.tag,
                                 int(node.attrib.get('colspan', '1')),
                                 int(node.attrib.get('rowspan', '1')),
                                 cell, *deque())
        else:
            new_node = TableTree(node.tag, None, None, None, *deque())
        if parent is not None:
            parent.children.append(new_node)
        if node.tag != 'td':
            for n in node.getchildren():
                self.load_html_tree(n, new_node)
        if parent is None:
            return new_node

    def evaluate(self, pred, true):
        ''' Computes TEDS score between the prediction and the ground truth of a
            given sample
        '''
        if (not pred) or (not true):
            return 0.0
        parser = html.HTMLParser(remove_comments=True, encoding='utf-8')
        pred = html.fromstring(pred, parser=parser)
        true = html.fromstring(true, parser=parser)
        if self.ignore_nodes:
            etree.strip_tags(pred, *self.ignore_nodes)
            etree.strip_tags(true, *self.ignore_nodes)
        n_nodes_pred = len(pred.xpath(".//*"))
        n_nodes_true = len(true.xpath(".//*"))
        n_nodes = max(n_nodes_pred, n_nodes_true)
        tree_pred = self.load_html_tree(pred)
        tree_true = self.load_html_tree(true)
        distance = APTED(tree_pred, tree_true, CustomConfig()).compute_edit_distance()
        return 1.0 - (float(distance) / n_nodes)

    def batch_evaluate(self, preds, trues):
        inputs = [{'pred': pred, 'true': true} for pred, true in zip(preds, trues)]
        scores = parallel_process(inputs, self.evaluate, use_kwargs=True, n_jobs=self.n_jobs, front_num=1)
        scores = np.sum(scores)
        return scores


class TableStructureMetric(object):
    def __init__(self,
                 main_indicator='acc',
                 eps=1e-6,
                 del_thead_tbody=False,
                 **kwargs):
        if main_indicator == "teds":
            self.teds = TEDS(n_jobs=16, ignore_nodes='b')
        self.main_indicator = main_indicator
        self.eps = eps
        self.del_thead_tbody = del_thead_tbody
        self.reset()

    def __call__(self, pred_label, batch=None, *args, **kwargs):
        preds, labels = pred_label
        pred_structure_batch_list = preds['structure_batch_list']
        gt_structure_batch_list = labels['structure_batch_list']
        if self.main_indicator == "teds":
            score = self.teds.batch_evaluate([''.join(data[0]) for data in pred_structure_batch_list],
                                             [''.join(data) for data in gt_structure_batch_list])
            all_num = len(gt_structure_batch_list)
        else:
            score = 0
            all_num = 0
            for (pred, pred_conf), target in zip(pred_structure_batch_list,
                                                 gt_structure_batch_list):
                pred_str = ''.join(pred)
                target_str = ''.join(target)
                if self.del_thead_tbody:
                    pred_str = pred_str.replace('<thead>', '').replace(
                        '</thead>', '').replace('<tbody>', '').replace('</tbody>',
                                                                       '')
                    target_str = target_str.replace('<thead>', '').replace(
                        '</thead>', '').replace('<tbody>', '').replace('</tbody>',
                                                                       '')
                if pred_str == target_str:
                    score += 1
                all_num += 1
        self.score += score
        self.all_num += all_num

    def get_metric(self):
        acc = 1.0 * self.score / (self.all_num + self.eps)
        self.reset()
        if self.main_indicator == "teds":
            return {'teds': acc}
        else:
            return {'acc': acc}

    def reset(self):
        self.score = 0
        self.all_num = 0
        self.len_acc_num = 0
        self.token_nums = 0
        self.anys_dict = dict()


class TableMetric(object):
    def __init__(self,
                 main_indicator='acc',
                 compute_bbox_metric=False,
                 box_format='xyxy',
                 del_thead_tbody=False,
                 **kwargs):
        """

        @param sub_metrics: configs of sub_metric
        @param main_matric: main_matric for save best_model
        @param kwargs:
        """
        self.structure_metric = TableStructureMetric(
            del_thead_tbody=del_thead_tbody)
        self.bbox_metric = DetMetric() if compute_bbox_metric else None
        self.main_indicator = main_indicator
        self.box_format = box_format
        self.reset()

    def __call__(self, pred_label, batch=None, *args, **kwargs):
        self.structure_metric(pred_label)
        if self.bbox_metric is not None:
            self.bbox_metric(*self.prepare_bbox_metric_input(pred_label))

    def prepare_bbox_metric_input(self, pred_label):
        pred_bbox_batch_list = []
        gt_ignore_tags_batch_list = []
        gt_bbox_batch_list = []
        preds, labels = pred_label

        batch_num = len(preds['bbox_batch_list'])
        for batch_idx in range(batch_num):
            # pred
            pred_bbox_list = [
                self.format_box(pred_box)
                for pred_box in preds['bbox_batch_list'][batch_idx]
            ]
            pred_bbox_batch_list.append({'points': pred_bbox_list})

            # gt
            gt_bbox_list = []
            gt_ignore_tags_list = []
            for gt_box in labels['bbox_batch_list'][batch_idx]:
                gt_bbox_list.append(self.format_box(gt_box))
                gt_ignore_tags_list.append(0)
            gt_bbox_batch_list.append(gt_bbox_list)
            gt_ignore_tags_batch_list.append(gt_ignore_tags_list)

        return [
            pred_bbox_batch_list,
            [0, 0, gt_bbox_batch_list, gt_ignore_tags_batch_list]
        ]

    def get_metric(self):
        structure_metric = self.structure_metric.get_metric()
        if self.bbox_metric is None:
            return structure_metric
        bbox_metric = self.bbox_metric.get_metric()
        if self.main_indicator == self.bbox_metric.main_indicator:
            output = bbox_metric
            for sub_key in structure_metric:
                output["structure_metric_{}".format(
                    sub_key)] = structure_metric[sub_key]
        else:
            output = structure_metric
            for sub_key in bbox_metric:
                output["bbox_metric_{}".format(sub_key)] = bbox_metric[sub_key]
        return output

    def reset(self):
        self.structure_metric.reset()
        if self.bbox_metric is not None:
            self.bbox_metric.reset()

    def format_box(self, box):
        if self.box_format == 'xyxy':
            x1, y1, x2, y2 = box
            box = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        elif self.box_format == 'xywh':
            x, y, w, h = box
            x1, y1, x2, y2 = x - w // 2, y - h // 2, x + w // 2, y + h // 2
            box = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        elif self.box_format == 'xyxyxyxy':
            x1, y1, x2, y2, x3, y3, x4, y4 = box
            box = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        return box
