import re


class _Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self, values=()):
        self.top = None
        for value in reversed(list(values)):
            self.push(value)

    def push(self, data):
        node = _Node(data)
        node.next = self.top
        self.top = node

    def pop(self):
        if self.top is None:
            return None
        popped = self.top
        self.top = popped.next
        popped.next = None
        return popped.data

    def peek(self):
        if self.top:
            return self.top.data
        return None

    def to_list(self):
        values = []
        current = self.top
        while current:
            values.append(current.data)
            current = current.next
        return values


def infix_to_postfix(expression):
    token_pattern = re.compile(r'\d+(?:\.\d*)?|\.\d+|[A-Za-z_][A-Za-z0-9_]*|[()+\-*/^]')
    tokens = []
    position = 0
    for match in token_pattern.finditer(expression):
        if expression[position:match.start()].strip():
            raise ValueError('Use numbers, variables, parentheses, and the operators +, -, *, /, and ^.')
        tokens.append(match.group())
        position = match.end()
    if expression[position:].strip():
        raise ValueError('Use numbers, variables, parentheses, and the operators +, -, *, /, and ^.')
    if not tokens:
        raise ValueError('Enter an infix expression to convert.')

    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    right_associative = {'^'}
    operators = []
    output = []
    steps = []
    expect_operand = True

    for token in tokens:
        if re.fullmatch(r'\d+(?:\.\d*)?|\.\d+|[A-Za-z_][A-Za-z0-9_]*', token):
            if not expect_operand:
                raise ValueError('Add an operator between values.')
            output.append(token)
            expect_operand = False
        elif token == '(':
            if not expect_operand:
                raise ValueError('Add an operator before the opening parenthesis.')
            operators.append(token)
        elif token == ')':
            if expect_operand:
                raise ValueError('Check for an empty parenthesis or a missing value.')
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            if not operators:
                raise ValueError('There is a closing parenthesis without a matching opening parenthesis.')
            operators.pop()
            expect_operand = False
        else:
            if expect_operand:
                raise ValueError('An expression cannot start with an operator or have two operators in a row.')
            while operators and operators[-1] != '(':
                top = operators[-1]
                higher_precedence = precedence[top] > precedence[token]
                same_left_associative = (
                    precedence[top] == precedence[token]
                    and token not in right_associative
                )
                if not (higher_precedence or same_left_associative):
                    break
                output.append(operators.pop())
            operators.append(token)
            expect_operand = True

        steps.append({
            'token': token,
            'operators': ' '.join(operators) if operators else '—',
            'output': ' '.join(output) if output else '—',
        })

    if expect_operand:
        raise ValueError('The expression cannot end with an operator.')

    while operators:
        operator = operators.pop()
        if operator == '(':
            raise ValueError('There is an opening parenthesis without a matching closing parenthesis.')
        output.append(operator)
        steps.append({
            'token': 'END',
            'operators': ' '.join(operators) if operators else '—',
            'output': ' '.join(output),
        })

    return ' '.join(output), steps
