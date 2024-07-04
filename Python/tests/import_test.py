from test import *


def test():
	log(title("Import Test"))
	log.expr("import utils.collection.ordered_dict")
	log.expr("glbls = globals()")
	log.expr_and_val("'OrderedDict' in glbls")
	log.expr_and_val("'utils.collection.ordered_dict.OrderedDict' in glbls")
	log(title("End of Import Test"))

run()