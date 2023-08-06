# import aiofiles
# import os
# from aiofiles.os import scandir
#
#
# class AsyncDirIterator(object):
#     def __init__(self, *args, **kwargs):
#         self.path = args[0]
#
#     async def load_data_info(self):
#         files = []
#
#         async for entry in aiofiles.os.scandir(self.path):
#             if entry.is_file():
#                 files.append(os.path.abspath(entry.path))
#             # elif entry.is_dir():
#             #     subfiles = await list_files(entry.path)
#             #     files.extend(subfiles)
#         return files
#
#     # async def __aiter__(self):
#     #     async with aiofiles.os.scandir(self.path) as scan_dir:
#     #         async for entry in scan_dir:
#     #             if entry.is_file():
#     #                 yield entry.name
#     #
#     # async def __anext__(self):
#     #     raise StopAsyncIteration
