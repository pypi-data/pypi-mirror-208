from antlr4 import *

from waveforms.qlisp._antlr.qLispLexer import qLispLexer
from waveforms.qlisp._antlr.qLispParser import qLispParser
from waveforms.qlisp._antlr.qLispParserVisitor import qLispParserVisitor
from ast import literal_eval


class Instruction():

    def __init__(self, name: str, args=(), label: str | None = None):
        self.name = name
        self.args = args
        self.label = label

    def __repr__(self):
        if self.label is None:
            return f"{self.name}(args={self.args})"
        else:
            return f"{self.name}(args={self.args}, label={self.label!r})"


class Symbol():

    def __init__(self, name: str, quantum: bool = False):
        self.name = name
        self.quantum = quantum

    def __repr__(self) -> str:
        return f"Symbol({self.name!r}, quantum={self.quantum})"


class Fragment():

    def __init__(self, code, scropes):
        self.code = code
        self.scropes = scropes

    def __repr__(self) -> str:
        return f"Fragment({self.code!r}, {self.scropes!r})"


class Ref():

    def __init__(self, label):
        self.label = label

    def __repr__(self) -> str:
        return f"Ref({self.label!r})"


class qlispVisitor(qLispParserVisitor):

    def __init__(self):
        self.stack = []
        self.code = []
        self.functions = {}
        self.constants = {}
        self.scropes = []
        self.exports = []
        self.fragments = {}
        self.__frag_count = 0

    def _create_expr(self, code, start_label=None, end_label=None):
        label = f"!frag_{self.__frag_count}"
        self.__frag_count += 1
        code = [
            Instruction('label', start_label), *code,
            Instruction('label', end_label)
        ]
        self.fragments[label] = Fragment(code, self.scropes.copy())
        return label

    # Visit a parse tree produced by qLispParser#program.
    def visitProgram(self, ctx: qLispParser.ProgramContext):
        return self.visit(ctx.expr())

    # Visit a parse tree produced by qLispParser#applyExpr.
    def visitApplyExpr(self, ctx: qLispParser.ApplyExprContext):
        head = self.visit(ctx.head)
        if ctx.binds is None:
            binds = []
        else:
            binds = self.visit(ctx.binds)
        return [*binds, *head, Instruction('call', len(binds))]

    # Visit a parse tree produced by qLispParser#notExpr.
    def visitNotExpr(self, ctx: qLispParser.NotExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by qLispParser#powerExpr.
    def visitPowerExpr(self, ctx: qLispParser.PowerExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by qLispParser#addSubExpr.
    def visitAddSubExpr(self, ctx: qLispParser.AddSubExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by qLispParser#lambdaExpr.
    def visitLambdaExpr(self, ctx: qLispParser.LambdaExprContext):
        label = self._create_expr(self.visit(ctx.body))
        if ctx.binds is None:
            self.functions[label] = [], label
        else:
            self.functions[label] = self.visit(ctx.binds), label
        return [Ref(label)]

    # Visit a parse tree produced by qLispParser#unaryExpr.
    def visitUnaryExpr(self, ctx: qLispParser.UnaryExprContext):
        if ctx.op.type == qLispLexer.MINUS:
            return [*self.visit(ctx.expr()), Instruction('neg')]
        elif ctx.op.type == qLispLexer.PLUS:
            return [*self.visit(ctx.expr())]

    # Visit a parse tree produced by qLispParser#atomExpr.
    def visitAtomExpr(self, ctx: qLispParser.AtomExprContext):
        return [self.visit(ctx.getChild(0))]

    # Visit a parse tree produced by qLispParser#orExpr.
    def visitOrExpr(self, ctx: qLispParser.OrExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by qLispParser#mulDivModExpr.
    def visitMulDivModExpr(self, ctx: qLispParser.MulDivModExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by qLispParser#parenExpr.
    def visitParenExpr(self, ctx: qLispParser.ParenExprContext):
        return [self.visit(ctx.expr())]

    # Visit a parse tree produced by qLispParser#compareExpr.
    def visitCompareExpr(self, ctx: qLispParser.CompareExprContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        if ctx.op.type == qLispLexer.EQ:
            return [left, right, Instruction('=')]
        elif ctx.op.type == qLispLexer.NEQ:
            return [left, right, Instruction('!=')]
        elif ctx.op.type == qLispLexer.LT:
            return [left, right, Instruction('<')]
        elif ctx.op.type == qLispLexer.LTE:
            return [left, right, Instruction('<=')]
        elif ctx.op.type == qLispLexer.GT:
            return [left, right, Instruction('>')]
        elif ctx.op.type == qLispLexer.GTE:
            return [left, right, Instruction('>=')]

        return self.visitChildren(ctx)

    # Visit a parse tree produced by qLispParser#andExpr.
    def visitAndExpr(self, ctx: qLispParser.AndExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by qLispParser#defineConstant.
    def visitDefineConstant(self, ctx: qLispParser.DefineConstantContext):
        name = ctx.getChild(0).getText()
        label = self._create_expr(self.visit(ctx.body))
        self.constants[name] = label
        return [Ref(label)]

    # Visit a parse tree produced by qLispParser#defineFunction.
    def visitDefineFunction(self, ctx: qLispParser.DefineFunctionContext):
        name = ctx.getChild(0).getText()
        label = self._create_expr(self.visit(ctx.body))
        if ctx.binds is None:
            binds = []
        else:
            binds = self.visit(ctx.binds)
        self.functions[name] = binds, label
        return [Ref(label)]

    # Visit a parse tree produced by qLispParser#assign.
    def visitAssign(self, ctx: qLispParser.AssignContext):
        name = ctx.getChild(0).getText()
        label = self._create_expr(self.visit(ctx.body))
        return [name, Ref(label), Instruction('set')]

    # Visit a parse tree produced by qLispParser#positionBind.
    def visitPositionBind(self, ctx: qLispParser.PositionBindContext):
        return self.visit(ctx.value)

    # Visit a parse tree produced by qLispParser#namedBind.
    def visitNamedBind(self, ctx: qLispParser.NamedBindContext):
        return [(Symbol(ctx.getChild(0).getText()), self.visit(ctx.value))]

    # Visit a parse tree produced by qLispParser#bind_list.
    def visitBind_list(self, ctx: qLispParser.Bind_listContext):
        if ctx.rest is None:
            return [*self.visit(ctx.first)]
        else:
            return [*self.visit(ctx.first), *self.visit(ctx.rest)]

    # Visit a parse tree produced by qLispParser#qubits.
    def visitQubits(self, ctx: qLispParser.QubitsContext):
        return Symbol(ctx.getText(), True)

    # Visit a parse tree produced by qLispParser#identifier.
    def visitIdentifier(self, ctx: qLispParser.IdentifierContext):
        return Symbol(ctx.getText())

    # Visit a parse tree produced by qLispParser#int.
    def visitInt(self, ctx: qLispParser.IntContext):
        return literal_eval(ctx.getText())

    # Visit a parse tree produced by qLispParser#hex.
    def visitHex(self, ctx: qLispParser.HexContext):
        return literal_eval(ctx.getText())

    # Visit a parse tree produced by qLispParser#oct.
    def visitOct(self, ctx: qLispParser.OctContext):
        return literal_eval(ctx.getText())

    # Visit a parse tree produced by qLispParser#bin.
    def visitBin(self, ctx: qLispParser.BinContext):
        return literal_eval(ctx.getText())

    # Visit a parse tree produced by qLispParser#float.
    def visitFloat(self, ctx: qLispParser.FloatContext):
        return literal_eval(ctx.getText())

    # Visit a parse tree produced by qLispParser#complex.
    def visitComplex(self, ctx: qLispParser.ComplexContext):
        return literal_eval(ctx.getText())

    # Visit a parse tree produced by qLispParser#string.
    def visitString(self, ctx: qLispParser.StringContext):
        return literal_eval(ctx.getText())


def parse(input: str):
    lexer = qLispLexer(InputStream(input))
    stream = CommonTokenStream(lexer)
    parser = qLispParser(stream)
    tree = parser.prog()
    visitor = qlispVisitor()
    code = visitor.visitProgram(tree)
    return code, visitor
