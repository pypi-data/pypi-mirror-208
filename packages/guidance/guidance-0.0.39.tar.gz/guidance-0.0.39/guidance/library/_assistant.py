from ._role import role

async def assistant(block_content, partial_output, parser, prev_node, next_node, next_next_node, hidden=False):
    ''' A chat role block for the 'assistant' role.

    This is just a shorthand for {{#role 'assistant'}}...{{/role}}.
    '''
    return await role(name="assistant", block_content=block_content, partial_output=partial_output, parser=parser, prev_node=prev_node, next_node=next_node, next_next_node=next_next_node, hidden=hidden)
assistant.is_block = True