from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class Container(ABC):

    def __init__(self, *args, children: list[Container] | list[str], indent: int=0, **kwargs):
        self.args = args
        self.children = children
        self.indent = indent
        self.kwargs = kwargs

    @abstractmethod
    def __str__(self) -> str:
        ...

@dataclass
class program(Container):

    def to_str(self):
        return f"""

        """
    
@dataclass
class If(Container):
    
    def __init__(self):
        self.initial_condition = self._join_if_logic(self.args)
        self.else_ifs = []
        self.else_logic = None

    def _join_if_logic(self, *args, is_initial: bool=True):
        if is_initial:
            return f"If {' '.join(args)} Then"
        return f"ElseIf {' '.join(args)} Then"
    
    def ElseIf(self, *args, logic):
        self.else_ifs.append(
            f"""
            {self._join_if_logic(*args, False)}
                {logic}
            """
        )
    
    def Else(self, logic):
        self.else_logic = f"Else\n    {logic}"
        return self
    
    def __str__(self):

        code = [self.initial_condition]
        code.append(f"    {self.logic}")

        for elseif in self.else_ifs:
            code.append(elseif)

        if self.else_logic:
            code.append(self.else_logic)

        code.append("EndIf")
        return "\n".join(code)
    
    def Else

