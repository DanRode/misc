#!/usr/bin/env python
shopping_list = []


def add_to_list(item):
    shopping_list.append(item)
    print("Added! List has {} items".format(len(shopping_list)))


def show_help():
    print("What should we pick up at the store?")
    print("""
Enter 'DONE to stop adding items
Enter 'HELP' to stop adding items
Enter 'SHOW' to print the list
""")


def show_list():
    print("Here's your list:")
    print("\n".join(shopping_list))


show_help()
while True:
    new_item = input("> ")

    if new_item == 'DONE':
        break
    elif new_item == 'HELP':
        show_help()
        continue
    elif new_item == 'SHOW':
        show_list()
        continue
    add_to_list(new_item)