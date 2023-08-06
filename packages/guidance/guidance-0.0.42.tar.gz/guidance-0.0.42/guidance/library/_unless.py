from ._if import if_

async def unless(value, block_content, parser):
    return await if_(value, block_content, parser, invert=True)
unless.is_block = True