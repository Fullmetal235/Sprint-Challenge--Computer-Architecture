import sys

LDI = 130
PRN = 71
HLT = 1
MUL = 162
PUSH = 69
POP = 70
CMP = 167
# unconditional jump
JMP = 84
# jump if equal
JEQ = 85
# jump if condition is met
JNE = 86

class CPU:
	def __init__(self):
		"""Construct A New CPU"""
		self.ram = [0] * 256
		self.register = [0] * 8
		self.pc = 0
		self.register[7] = 0xF4
		self.sp = 7
		self.flags = {}
		# Construct a branch table
		self.branch_table = {}
		self.branch_table[LDI] = self.ldi
		self.branch_table[PRN] = self.prn
		self.branch_table[MUL] = self.mul
		self.branch_table[PUSH] = self.push
		self.branch_table[POP] = self.pop
		self.branch_table[CMP] = self.cmp
		self.branch_table[JMP] = self.jmp
		self.branch_table[JEQ] = self.jeq
		self.branch_table[JNE] = self.jne

	# takes file input
	def load(self):
		"""Load a program into memory."""
		address = 0

		with open(sys.argv[1]) as file:
			for instruction in file:
				cleaned_instruction = instruction.split("#")
				cleaned_valued = cleaned_instruction[0].strip()
				if cleaned_valued != "":
					self.ram[address] = int(cleaned_valued, 2) # keeping it in binary
					address += 1

	# ALU to perform arithmatic operations and also CMP operations
	def alu(self, op, reg_a, reg_b):
		"""ALU operations."""

		# vars to be used for flagging
		a = self.register[reg_a]
		b = self.register[reg_b]

		if op == "ADD":
			self.register[a] += self.register[b]
		elif op == "MUL":
			self.register[a] *= self.register[b]
		elif op == "CMP":
			if a == b:
				self.flags["E"] = 1
			else:
				self.flags["E"] = 0

			if a < b:
				self.flags["L"] = 1
			else:
				self.flags["L"] = 0

			if a > b:
				self.flags["G"] = 1
			else:
				self.flags["G"] = 0

		else:
			raise Exception("Unsupported ALU operation")

	def read_ram(self, MAR):
		return self.ram[MAR]

	def write_ram(self, MAR, MDR):
		self.ram[MAR] = MDR

	def ldi(self, operand_a, operand_b):
		self.register[operand_a] = operand_b

	def prn(self, operand_a, operand_b):
		print(self.register[operand_a])

	def mul(self, operand_a, operand_b):
		self.alu("MUL", operand_a, operand_b)

	def cmp(self, operand_a, operand_b):
		self.alu("CMP", operand_a, operand_b)

	def jmp(self, operand_a, operand_b):
		self.pc = self.register[operand_a]

	def jeq(self, operand_a, operand_b):
		if self.flags['E'] == 1:
			self.pc = self.register[operand_a]
		else:
			self.pc += 2

	def jne(self, operand_a, operand_b):
		if self.flags["E"] == 0:
			self.pc = self.register[operand_a]
		else:
			self.pc += 2

	def push(self, operand_a, operand_b):
		self.register[self.sp] -= 1
		val = self.register[operand_a]
		self.write_ram(self.register[self.sp], val)

	def pop(self, operand_a, operand_b):
		val = self.read_ram(self.register[self.sp])
		self.register[operand_a] = val
		self.register[self.sp] += 1

	def run(self):
		"""Run The CPU"""
		# end condition
		halted = False
		# add separate case in the instance of a jump related instruction
		jump = [JNE, JMP, JEQ]

		while not halted:
			IR = self.read_ram(self.pc)
			operand_a = self.read_ram(self.pc + 1)
			operand_b = self.read_ram(self.pc + 2)

			if IR == HLT:
				halted = True
			# need this extra block because the jump instructions increment the program pointer themselves
			elif IR in jump:
				self.branch_table[IR](operand_a, operand_b)
			elif IR in self.branch_table:
				self.branch_table[IR](operand_a, operand_b)
				self.pc += (IR >> 6) + 1
			else:
				print("Instruction not recognized")
				sys.exit(1)