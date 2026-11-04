from thefrappeguy.content import explainer_list


def get_context(context):
	context.page_title = "Explainers"
	context.page_description = "Every explainer: one question, one honest answer, one takeaway."
	context.nav = "explainers"
	context.explainers = explainer_list()
