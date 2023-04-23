import sys

def call_locals_with_args( external_locals ):
    if len(sys.argv) > 2:
        arr = []
        for i, a in enumerate(sys.argv):
            if (i > 1):
                arr.append(a)
        external_locals[sys.argv[1]](*arr)
    elif len(sys.argv) == 2:
        external_locals[sys.argv[1]]()