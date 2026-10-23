class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class SinglyLinkedList:
    def __init__(self, values=()):
        self.head = None
        self.tail = None
        for value in values:
            self.insert_at_end(value)

    def insert_at_beginning(self, data):
        node = Node(data)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node

    def insert_at_end(self, data):
        node = Node(data)
        if self.tail is None:
            self.head = node
            self.tail = node
            return
        self.tail.next = node
        self.tail = node

    def insert_after(self, nodedata, data):
        current = self.head
        while current:
            if current.data == nodedata:
                node = Node(data)
                node.next = current.next
                current.next = node
                if self.tail is current:
                    self.tail = node
                return node
            current = current.next
        return None

    def remove_beginning(self):
        if self.head is None:
            return None
        removed = self.head
        self.head = removed.next
        removed.next = None
        if self.head is None:
            self.tail = None
        return removed.data

    def remove_at_end(self):
        if self.head is None:
            return None
        if self.head is self.tail:
            return self.remove_beginning()

        current = self.head
        while current.next is not self.tail:
            current = current.next
        removed = self.tail
        current.next = None
        self.tail = current
        return removed.data

    def remove_at(self, data):
        if self.head is None:
            return None
        if self.head.data == data:
            return self.remove_beginning()

        previous = self.head
        current = self.head.next
        while current:
            if current.data == data:
                previous.next = current.next
                if self.tail is current:
                    self.tail = previous
                current.next = None
                return current.data
            previous, current = current, current.next
        return None

    def to_list(self):
        values = []
        current = self.head
        while current:
            values.append(current.data)
            current = current.next
        return values
