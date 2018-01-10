from collections import deque
import sys


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
			"*":		self.mul,
			"+":		self.plus,
			"-":		self.minus,
			"/":		self.div,
			#"==":		self.eq,
			"cast_int": self.cast_int,
			#"cast_str": self.cast_str,
			"over":		self.over,
			"print":	self.print_,
			"println":	self.println,
			"read":		self.read,
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

	def mul(self):
		self.push(self.pop() * self.pop())

	def plus(self):
		self.push(self.pop() + self.pop())

	def minus(self):
		last = self.pop()
		self.push(self.pop() - last)

	def div(self):
		last = self.pop()
		self.push(self.pop() / last)

	def print_(self):
		sys.stdout.write(str(self.pop()))
		sys.stdout.flush()

	def println(self):
		sys.stdout.write("%s\n" % self.pop())
		sys.stdout.flush()

	def read(self):
		self.push(raw_input())

	def cast_int(self):
		self.push(int(self.pop()))

	def over(self):
		b = self.pop()
		a = self.pop()
		self.push(a)
		self.push(b)
		self.push(a)

#Machine([2, 3, "+", 4, "*", "println"]).run()

Machine([
	'"Enter a number: "', "print", "read", "cast_int",
	'"Enter another number: "', "print", "read", "cast_int",
	"over", "over",
	'"Their sum is: "', "print", "+", "println",
	'"Their product is: "', "print", "*", "println"
]).run()
