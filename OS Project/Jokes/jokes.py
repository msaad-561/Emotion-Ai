"""
Jokes Module
Helper module to provide programming jokes for the SAD emotion state.
"""

import pyjokes


def get_programming_joke():
    """
    Get a random programming joke.
    
    Returns:
        A string containing a funny programming joke
    """
    try:
        # pyjokes.get_joke() returns a random programming joke
        # category='neutral' ensures the jokes are appropriate
        joke = pyjokes.get_joke(language='en', category='neutral')
        return joke
    except Exception as e:
        # Fallback joke in case pyjokes fails
        print(f"Error getting joke: {e}")
        return "Why do programmers prefer dark mode? Because light attracts bugs! 🐛"


# For testing purposes
if __name__ == "__main__":
    print("Testing joke module:")
    print(get_programming_joke())
