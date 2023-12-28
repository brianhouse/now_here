#!/Users/house/Studio/now_here/venv/bin/python

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import *
# from rmcl import Item, Document, Folder, register_device
# from rmapy.api import Client
# from rmapy.document import Document
# from rmapy.folder import Folder


"""
ok, so it appears that the api code is not working with the current remarkable release,
pretty much across the board. bummer. using the cloud service is much more attractive than having to 
plug in the device, but I guess I have to try that approach.

https://github.com/reHackable/awesome-reMarkable

https://remarkable.guide/guide/access/ssh.html


"""
 

# rmapy = Client()
# while not rmapy.is_auth():
#     code = input("https://my.remarkable.com/device/desktop/connect : ")
#     print(code)
#     rmapy.register_device(code)
#     print('complete')
#     rmapy.renew_token()
# rmapy.renew_token()    
# collection = rmapy.get_meta_items()
# print(len([f for f in collection if isinstance(f, Document)]))
# print(len([f for f in collection if isinstance(f, Folder)]))


# def get_pages():    
#     root = Item.get_by_id_s('')
#     for child in root.children:
#         if isinstance(child, Folder):
#             print(f"{child.name}: folder")
#         elif isinstance(child, Document):
#             print(f"{child.name}: {child.type_s()}")


# if __name__ == "__main__":
#     get_pages()
