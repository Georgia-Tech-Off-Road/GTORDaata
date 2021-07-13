# Code taken and modified from https://www.tutorialspoint.com/python_data_structure/python_linked_lists.htm

class GridNode:
    def __init__(self, data):
        self.data = data
        self.row = None
        self.col = None
        self.next = None

class GridLinkedList:
    def __init__(self):
        self.head = None

    def insertHead(self, data):
        new_node = GridNode(data)
        new_node.next = self.head
        self.head = new_node

    def insertTail(self, data):
        node = self.head
        new_node = GridNode(data)

        if self.head == None:
            self.head = new_node
            return

        while node.next != None:
            node = node.next

        node.next = new_node

    def insertAfterNode(self, newdata, node_to_insert_after):
        node_to_insert_after = self.getNode(node_to_insert_after)
        if node_to_insert_after is None:
            print("The mentioned node is absent")
            return

        new_node = GridNode(newdata)
        new_node.next = node_to_insert_after.next
        node_to_insert_after.next = new_node

    def insertBeforeNode(self, newdata, node_to_insert_before):
        node_to_insert_after = self.head
        while node_to_insert_after.next.data != node_to_insert_before:
            node_to_insert_after = node_to_insert_after.next

        self.insertAfterNode(node_to_insert_after, newdata)


    def getNode(self, key):
        node = self.head
        while node.data != key:
            node = node.next
        return node

    def setRowCol(self, node, row, col):
        self.node.row = row
        self.node.col = col

    # Function to remove node
    def removeNode(self, node):

        head_val = self.head

        if (head_val is not None):
            if (head_val.data == node):
                self.head = head_val.next
                head_val = None
                return

        while (head_val is not None):
            if head_val.key == node:
                break
            prev = head_val
            head_val = head_val.next

        if (head_val == None):
            return

        prev.next = head_val.next

        head_val = None

    def printList(self):
        print_val = self.head
        while (print_val):
            print(print_val.data),
            print_val = print_val.next

dict = {}
dict["0"] = "0"
dict["1"] = "1"
dict["2"] = "2"
dict["3"] = "3"
dict["4"] = "4"

llist = GridLinkedList()

llist.insertHead(dict["1"])
llist.insertTail(dict["2"])
llist.insertTail(dict["4"])
llist.insertHead(dict["0"])
llist.insertBeforeNode(dict["3"], dict["4"])
llist.printList()
