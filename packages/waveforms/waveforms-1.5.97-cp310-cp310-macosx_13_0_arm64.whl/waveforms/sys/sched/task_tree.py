from __future__ import annotations

from dataclasses import dataclass

from treelib import Node, Tree


@dataclass
class TaskNode():
    task_id: int = 0
    source: int = 0
    status: int = 0
    lazy: bool = True


class TaskTree(Tree):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_node(Node('root', 0, data=TaskNode(0, 0, 0, False)))
        self._remove_cache = set()

    @property
    def status(self):
        return self.get_node(self.root).data.status

    def _update_status(self, p, key):
        for i in self.rsearch(p):
            self.get_node(i).data.status ^= key

    def add_task(self, task_id, task_source, parent=0) -> bool:
        #print('~~~~~~~~ add_task', task_id, task_source, parent, file=out)
        if not self.contains(parent):
            return False
            # raise ValueError(f'Parent {parent} is not in the tree')
        parent_node, parent_source = self.get_node(parent), 0
        if parent_node.is_leaf():
            parent_source = parent_node.data.source
        if (self.status ^ parent_source) & task_source:
            return False
        self.add_node(Node(tag=task_id,
                           identifier=task_id,
                           data=TaskNode(task_id, task_source, task_source)),
                      parent=parent)
        self._update_status(parent, parent_source ^ task_source)
        self._clear_cache()
        return True

    def _delete_node(self, p):
        node, parent = self.get_node(p), self.parent(p).identifier
        self.remove_node(p)
        parent_node = self.get_node(parent)
        if not parent_node.identifier or parent_node.data.status or not parent_node.is_leaf(
        ):
            return False
        elif self.status & (parent_node.data.source):
            self.add_node(Node(tag=p,
                               identifier=p,
                               data=TaskNode(p, 0, 0, False)),
                          parent=parent)
            return True
        else:
            self._update_status(parent, parent_node.data.source)
            return False

    def _clear_cache(self):
        tmp = set()
        for p in self._remove_cache:
            if self.contains(p) and self._delete_node(p):
                tmp.add(p)
        self._remove_cache = tmp

    def remove_task(self, task_id, mode: int = 0):
        #print('~~~~~~~~ remove_task', task_id, file=out)
        if not task_id or not self.contains(task_id):
            raise ValueError(f'Task_id {task_id} is not in the tree')
        if mode == 2:
            ancestor = list(self.rsearch(task_id))
            #print(ancestor, file=out)
            for i in range(1, len(ancestor) - 1):
                for ps in self.is_branch(ancestor[i]):
                    if ps != ancestor[i - 1]:
                        self.move_node(ps, 0)
        if mode > 0:
            while self.parent(task_id).identifier:
                task_id = self.parent(task_id).identifier
        cur_node = self.get_node(task_id)
        self._update_status(task_id, cur_node.data.status)
        self._remove_cache.add(task_id)
        self._clear_cache()

    def ask_task(self) -> list[int]:
        #print('~~~~~~~~ ask_task', file=out)
        ret = []
        for node in self.leaves():
            if node.data.lazy:
                ret.append(node.identifier)
        #print('        ret', ret, file=out)
        return ret
