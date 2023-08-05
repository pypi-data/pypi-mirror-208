import collections

_Instruction = collections.namedtuple(
    "_Instruction",
    "opname opcode arg argval argrepr offset starts_line is_jump_target")

_Instruction.opname.__doc__ = "Human readable name for operation"
_Instruction.opcode.__doc__ = "Numeric code for operation"
_Instruction.arg.__doc__ = "Numeric argument to operation (if any), otherwise None"
_Instruction.argval.__doc__ = "Resolved arg value (if known), otherwise same as arg"
_Instruction.argrepr.__doc__ = "Human readable description of operation argument"
_Instruction.offset.__doc__ = "Start index of operation within bytecode sequence"
_Instruction.starts_line.__doc__ = "Line started by this opcode (if any), otherwise None"
_Instruction.is_jump_target.__doc__ = "True if other code jumps to here, otherwise False"

_OPNAME_WIDTH = 20
_OPARG_WIDTH = 5


class Instruction(_Instruction):
    """Details for a bytecode operation

       Defined fields:
         opname - human readable name for operation
         opcode - numeric code for operation
         arg - numeric argument to operation (if any), otherwise None
         argval - resolved arg value (if known), otherwise same as arg
         argrepr - human readable description of operation argument
         offset - start index of operation within bytecode sequence
         starts_line - line started by this opcode (if any), otherwise None
         is_jump_target - True if other code jumps to here, otherwise False
    """

    def _disassemble(self,
                     lineno_width=3,
                     mark_as_current=False,
                     offset_width=4):
        """Format instruction details for inclusion in disassembly output

        *lineno_width* sets the width of the line number field (0 omits it)
        *mark_as_current* inserts a '-->' marker arrow as part of the line
        *offset_width* sets the width of the instruction offset field
        """
        fields = []
        # Column: Source code line number
        if lineno_width:
            if self.starts_line is not None:
                lineno_fmt = "%%%dd" % lineno_width
                fields.append(lineno_fmt % self.starts_line)
            else:
                fields.append(' ' * lineno_width)
        # Column: Current instruction indicator
        if mark_as_current:
            fields.append('-->')
        else:
            fields.append('   ')
        # Column: Jump target marker
        if self.is_jump_target:
            fields.append('>>')
        else:
            fields.append('  ')
        # Column: Instruction offset from start of code sequence
        fields.append(repr(self.offset).rjust(offset_width))
        # Column: Opcode name
        fields.append(self.opname.ljust(_OPNAME_WIDTH))
        # Column: Opcode argument
        if self.arg is not None:
            fields.append(repr(self.arg).rjust(_OPARG_WIDTH))
            # Column: Opcode argument details
            if self.argrepr:
                fields.append('(' + self.argrepr + ')')
        return ' '.join(fields).rstrip()


class MetaInstruction(type):
    """Metaclass for Instruction

    This metaclass is used to create a subclass of Instruction that
    has a custom __new__ method that allows the fields of the class
    to be specified as positional arguments to the constructor.
    """
    def __new__(cls, name, bases, namespace):
        def __new__(cls, *args):
            if len(args) != len(cls._fields):
                raise TypeError("Expected %d arguments, got %d" %
                                (len(cls._fields), len(args)))
            return super().__new__(cls, *args)
        namespace['__new__'] = __new__
        return super().__new__(cls, name, bases, namespace)

class InstructionWithArg(Instruction, metaclass=MetaInstruction):
    """Instruction with a single numeric argument

    This is a convenience class for instructions that have a single
    numeric argument.  It is used to create a subclass of Instruction
    that has a custom __new__ method that allows the fields of the
    class to be specified as positional arguments to the constructor.
    """
