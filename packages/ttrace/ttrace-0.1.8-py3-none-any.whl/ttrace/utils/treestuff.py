#!/usr/bin/env python3

"""Provides stuff we repeatedly need
"""

import os
import sys
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from itertools import chain
from typing import Any

from treelib import Tree

__all__ = ["attributed_tree", "traverse", "insert", "colored"]


def colored(text: str, color: str) -> str:
    """Returns @color formatted @text"""
    return (
        text
        if False  # color is None or not sys.stdout.isatty() or "COLORTERM" not in os.environ
        else {
            "none": "%s",
            "green": "\033[0;32m%s\033[0m",
            "green_bold": "\033[1;32m%s\033[0m",
            "red": "\033[0;31m%s\033[0m",
            "red_bold": "\033[1;31m%s\033[0m",
            "black": "\033[0;30m%s\033[0m",
            "black_bold": "\033[1;30m%s\033[0m",
            "blue": "\033[0;34m%s\033[0m",
            "blue_bold": "\033[1;34m%s\033[0m",
            "yellow": "\033[0;33m%s\033[0m",
            "yellow_bold": "\033[1;33m%s\033[0m",
        }.get(color, "%s")
        % text
    )


def display_name(name: str | int, attrs: Mapping[str, Any]) -> str:
    """Creates a display name (tag) for a treelib node"""
    tag_string = ", ".join(attrs.get("tags", []))
    return (
        f"{colored(str(name), attrs.get('color', ''))}{f' - [{tag_string}]' if tag_string else ''}"
    )


def populate_tree(
    tree: Tree, subtree: Mapping[str | int, Any], parent: str | int | None = None
) -> Tree:
    """Recursively builds a treelib tree from a nested dict"""
    if subtree is None:
        return tree

    if isinstance(subtree, str):
        return populate_tree(tree, {subtree: None}, parent)

    if not isinstance(subtree, Mapping):
        raise RuntimeError(f"Need Mapping, got {type(subtree)}")

    if parent is None and len(subtree) > 1:
        tree.create_node(".", "root")

    for name, subtree_data in subtree.items():
        if name in ("__data__", "__attrs__"):
            continue
        attrs = (subtree_data if isinstance(subtree_data, Mapping) else {}).get("__attrs__") or {}
        populate_tree(
            tree,
            subtree_data,
            tree.create_node(
                tag=display_name(name, attrs),
                identifier=f"{parent or tree.root}.{name}",
                parent=(parent and str(parent)) or tree.root,
            ).identifier,
        )

    return tree


def attributed_tree(tree_data: Mapping[str | int, Any]) -> str:
    """Creates a nice coloured tree with attributes
    >>> print(attributed_tree({
    ...     "A": {
    ...         "__attrs__": {},
    ...         "B": None,
    ...         "C": {},
    ...         "D": {
    ...         },
    ...     }
    ... }))
    A
    ├── B
    ├── C
    └── D
    <BLANKLINE>
    """
    return populate_tree(Tree(), tree_data).show(stdout=False)


def traverse(
    tree: Mapping[str, Any], must_have_data: bool = False
) -> Iterable[tuple[Sequence[str], Mapping[str, Any] | None, Mapping[str, Any] | None]]:
    """DF-traverses a nested dict and yields name, full path data and attrs elements"""

    def _traverse(
        tree: Mapping[str, Any], parent: Sequence[str]
    ) -> Iterable[tuple[Sequence[str], Mapping[str, Any] | None, Mapping[str, Any] | None]]:
        for key, value in tree.items():
            if key in ("__data__", "__attrs__"):
                continue
            assert isinstance(value, Mapping)
            assert isinstance(key, str)
            # https://stackoverflow.com/questions/65361188
            path = list(chain(parent, [key]))
            if "__data__" in value or not must_have_data:
                yield path, value.get("__data__"), value.get("__attrs__")
            yield from _traverse(value, path)

    yield from _traverse(tree, [])


def insert(
    tree: MutableMapping[str | int, Any],
    path: Sequence[str | int],
    *,
    name: str | int | None = None,
    display_name: str | None = None,
    data: Mapping[str, Any] | None = None,
    attrs: Mapping[str, Any] | None = None,
    insert_missing: bool = False,
) -> Mapping[str, Any]:
    """Inserts a new element with provided @data and @attrs at position @path
    into @tree"""
    iterator = tree
    *directory, name = path if name is None else list(chain(path, [name]))
    for folder in directory:
        iterator = iterator.setdefault(folder, {}) if insert_missing else iterator[folder]
    new_element = iterator.setdefault(name, {})
    assert isinstance(new_element, MutableMapping)
    if data is not None:
        new_element["__data__"] = data
    if attrs is not None:
        new_element["__attrs__"] = attrs
    return new_element


def get_node(
    tree: MutableMapping[str | int, Any],
    path: Sequence[str | int],
) -> MutableMapping[str | int, Any]:
    """Looks up a node from @tree with the given @path"""
    element = tree
    for key in path:
        element = element[key]
    return element
