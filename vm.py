import io
import sys
import tokenize
from collections import deque

class Stack(deque):
	push = deque.append

	def top(self):
		return self[-1]

class Machine(object):
	def __init__(self, code):
		self.data_stack = Stack()
		self.return_addr_stack = Stack()
		self.instruction_pointer = 0
		self.code = code
		self.dispatch_map = {
			"%":		self.mod,
			"*":		self.mul,
			"+":		self.plus,
			"-":		self.minus,
			"/":		self.div,
			"==":		self.equal,
			"cast_int": self.cast_int,
			#"cast_str":self.cast_str,
			#"drop":	self.drop,
			"dup":		self.dup,
			"if":		self.if_stmt,
			#"jmp":		self.jmp,
			"over":		self.over,
			"print":	self.print_,
			"println":	self.println,
			"read":		self.read,
			"stack":	self.dump_stack,
			#"swap":	self.swap,
			"exit":		self.exit,
		}

	def pop(self):
		return self.data_stack.pop()

	def push(self, value):
		self.data_stack.push(value)

	def top(self):
		return self.data_stack.top()

	def run(self):
		while self.instruction_pointer < len(self.code):
			opcode = self.code[self.instruction_pointer]
			self.instruction_pointer += 1
			self.dispatch(opcode)

	def dispatch(self, op):
		if op in self.dispatch_map:
			self.dispatch_map[op]()
		elif isinstance(op, int):
			# push numbers on the data stack
			self.push(op)
		elif isinstance(op, str) and op[0] == op[-1] == '"':
			# push quoted strings on the data stack
			self.push(op[1:-1])
		else:
			raise RuntimeError("Unknown opcode: '%s'" % op)

	def dump_stack(self):
		print("<Top>")
		for v in reversed(self.data_stack):
			print(" - type %s, value '%s'" % (type(v), v))

	def dup(self):
		self.push(self.top())

	def mod(self):
		last = self.pop()
		self.push(self.pop() % last)

	def plus(self):
		self.push(self.pop() + self.pop())

	def minus(self):
		last = self.pop()
		self.push(self.pop() - last)

	def mul(self):
		self.push(self.pop() * self.pop())

	def div(self):
		last = self.pop()
		self.push(self.pop() / last)

	def equal(self):
		self.push(self.pop() == self.pop())

	def print_(self):
		sys.stdout.write(str(self.pop()))
		sys.stdout.flush()

	def println(self):
		sys.stdout.write("%s\n" % self.pop())
		sys.stdout.flush()

	def read(self):
		self.push(input())

	def cast_int(self):
		self.push(int(self.pop()))

	def over(self):
		b = self.pop()
		a = self.pop()
		self.push(a)
		self.push(b)
		self.push(a)

	def if_stmt(self):
		false_clause = self.pop()
		true_clause = self.pop()
		test = self.pop()
		self.push(true_clause if test else false_clause)

	def exit(self):
		sys.exit(0)

def parse(text):
	tokens = tokenize.generate_tokens(io.StringIO(text).readline)
	for toknum, tokval, _, _, _ in tokens:
		if toknum == tokenize.NUMBER:
			yield int(tokval)
		elif toknum in [tokenize.OP, tokenize.STRING, tokenize.NAME]:
			yield tokval
		elif toknum == tokenize.ENDMARKER:
			break
		else:
			raise RuntimeError("Unknown token %s: '%s'" %
					(tokenize.tok_name[toknum], tokval))

def constant_fold(code):
	"""Constant-folds simple mathematical expressions like 2 3 + to 5."""
	while True:
		# Find two consecutive numbers and an arithmetic operator
		for i, (a, b, op) in enumerate(zip(code, code[1:], code[2:])):
			if isinstance(a, int) and isinstance(b, int) \
					and op in {"+", "-", "*", "/", "%"}:
				m = Machine((a, b, op))
				m.run()
				code[i:i+3] = [m.top()]
				print("Constant-folded %s%s%s to %s" % (a,op,b,m.top()))
				break
		else:
			break
	return code

def repl():
	print('Hit CTRL+D or type "exit" to quit.')

	while True:
		try:
			source = input("> ")
			code = list(parse(source))
			code = constant_fold(code)
			Machine(code).run()
		except (RuntimeError, IndexError) as e:
			print("IndexError: %s" % e)
		except KeyboardInterrupt:
			print("\nKeyboardInterrupt")

#Machine([2, 3, "+", 4, "*", "println"]).run()
'''
Machine([
	'"Enter a number: "', "print", "read", "cast_int",
	'"Enter another number: "', "print", "read", "cast_int",
	"over", "over",
	'"Their sum is: "', "print", "+", "println",
	'"Their product is: "', "print", "*", "println"
]).run()
'''
repl()
