from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple, MutableMapping


class SymbolScope(Enum):
    LOCAL = "LOCAL"
    BLOCK = "BLOCK"
    CYCLE = "CYCLE"
    COUNTER = "COUNTER"


class Symbol(NamedTuple):
    name: str
    scope: SymbolScope
    index: int


@dataclass
class Scope:
    store: MutableMapping[str, Symbol] = field(default_factory=dict)
    size: int = field(default=0)


class SymbolTable:
    def __init__(self, outer: SymbolTable = None):
        self.outer = outer

        self.locals = Scope()
        self.cycles = Scope()
        self.counters = Scope()

    def define(self, name: str) -> Symbol:
        if self.outer:
            scope = SymbolScope.BLOCK
        else:
            scope = SymbolScope.LOCAL

        symbol = Symbol(name=name, scope=scope, index=self.locals.size)

        self.locals.store[name] = symbol
        self.locals.size += 1
        return symbol

    def resolve(self, name: str) -> Symbol:
        try:
            obj = self.locals.store[name]
        except KeyError:
            if self.outer:
                return self.outer.resolve(name)
            raise
        return obj

    def define_counter(self, name: str) -> Symbol:
        if self.outer:
            return self.outer.define_counter(name)

        if name in self.counters.store:
            return self.counters.store[name]

        symbol = Symbol(name=name, scope=SymbolScope.COUNTER, index=self.counters.size)
        self.counters.store[name] = symbol
        self.counters.size += 1

        return symbol

    def define_cycle(self, group_name, args) -> Symbol:
        if self.outer:
            return self.outer.define_cycle(group_name, args)

        name = f"{group_name}:{''.join([str(arg) for arg in args])}"

        if name in self.cycles.store:
            return self.cycles.store[name]

        symbol = Symbol(name=name, scope=SymbolScope.CYCLE, index=self.cycles.size)
        self.cycles.store[name] = symbol
        self.cycles.size += 1

        return symbol