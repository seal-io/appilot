FIND_TEMPLATE_PROMPT = """
Templates are predefined configuration to create a particular type of service.

You will be provided existing templates and a user query describing a deployment task. 
Find a template that most likely can be used to accomplish the user query.
If you don't find any, say why.

Output the matched template name in quoted string.

TEMPLATES:
{templates}

User query: {query}
Output:"""
