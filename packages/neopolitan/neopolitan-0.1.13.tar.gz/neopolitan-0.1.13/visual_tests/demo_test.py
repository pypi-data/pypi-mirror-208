"""Demo test"""
from neopolitan import main

def demo_test():
    """Test demo"""
    try:
        main.main()
    # pylint: disable=broad-except
    except Exception as err:
        assert False, str(err)
