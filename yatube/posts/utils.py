from django.core.paginator import Paginator


def pagination_pages(request, post, post_per_page):
    paginator = Paginator(post, post_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


POSTS_PER_PAGE = 10
SAVE_VALUE_IN_CACHE = 20
