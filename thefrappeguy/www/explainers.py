from thefrappeguy.content import explainer_list


def get_context(context):
	context.page_title = "Explainers"
	context.page_description = "Every explainer on The Frappe Guy, in story order: twelve releases, each told in short parts."
	context.nav = "explainers"
	context.explainers = explainer_list()
