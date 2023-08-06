def mentor_prompt(code):
    return f"""The following code may have a bug. If it exists, tell me exactly where to look. In your response only tell me concisely exactly where to look. Be as concise as possible. Respond like, You may want to look at _____ where there's an issue with ____ and you can fix it by _____. Be specific with your suggested fix. Show a minimal representation of the fixed code.
                                              
    If there is no obvious bug simply reply, "no bug".
    
    Next you'll play the role of a software architect. You'll take a second look at our architecture decisions and recommend alternatives if there's something better.
    
    If there is no obvious recommendation, simply reply, "no rec"
    
    Below I will paste the contents from a bunch of my files. If I show you errors pay special attention to the errors and help me fix them.
{code}"""


def architect_prompt(code):
    return f"""I'm going to copy/paste a bunch of code. You will act as a fullstack software architect. You will use systems thinking to analyze the current architecture decisions and you will make any suggestions you see fit. Be very precise and concise with your words. If it makes sense, draw sequence diagrams in markdown to show off systems thinking.
                                              
    If there is no obvious improvement to make say, "No architecture advice".
    
    Below I will paste the contents from a bunch of my files. If I show you errors pay special attention to the errors and help me fix them.
{code}"""
