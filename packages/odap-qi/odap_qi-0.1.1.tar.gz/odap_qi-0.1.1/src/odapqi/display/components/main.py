from typing import List
from ipywidgets import (
    Layout,
    Box,
)


class Main:
    def __init__(self, *, body, graphics):
        self.bck = body
        self.body = body
        self.graphics = graphics

    def display_output(self):
        if self.graphics:
            return Box(
                children=[self.graphics, self.body], layout=Layout(display="block")
            )
        return self.body

    def add_child(self, *, child):
        self.body.children = tuple(list(self.body.children) + child)

    def remove_child(self, *, obj):
        self.body.children = [x for x in self.body.children if x != obj]

    def remove_grand_child(self, *, index, obj):
        self.body.children[index].children = [
            x for x in self.body.children[index].children if x != obj
        ]

    def remove_child_index(self, *, indexes: List[int]):
        self.body.children = tuple(
            list(
                [
                    self.body.children[x]
                    for x in range(len(self.body.children))
                    if x not in indexes
                ]
            )
        )
