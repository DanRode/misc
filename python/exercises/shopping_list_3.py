import os

shopping_list = []


def clear_screen():
    os.system("cls"
              if os.name == "nt"
              else "clear")


def show_help():
    clear_screen()


print("What should we pick up at the store?")
print(""
      "
      Enter 'DONE'
      to stop adding items.Enter 'HELP'
      for this help.Enter 'SHOW'
      to see your current list.
      ""
      ")


def add_to_list(item):
    shopping_list.append(new_item) print("Added! List has {} items.".format(len(shopping_list))) show_list()

    def show_list():
    clear_screen() print("Here's your list:") for item in shopping_list:
    print(item)

    show_help()

    while True:
    new_item = input("> ")

    if new_item.upper() == 'DONE'
    or new_item.upper() == 'QUIT':
    break elif new_item.upper == 'HELP':
    show_help() continue elif new_item.uppwer() == 'SHOW':
    show_list() continue
    else:
        add_to_list(new_item)

    show_list()
