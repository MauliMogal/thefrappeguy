from thefrappeguy.content import series_with_counts


def get_context(context):
	context.page_title = "Roadmap"
	context.page_description = "The whole story, release by release: what each one covers and what you will be able to decide after reading it."
	context.nav = "roadmap"
	releases = []
	for i, s in enumerate(series_with_counts(), start=1):
		s.no = i
		s.section_list = [line.strip() for line in (s.sections or "").splitlines() if line.strip()]
		releases.append(s)
	context.releases = releases
	context.live = sum(1 for r in releases if r.count)
