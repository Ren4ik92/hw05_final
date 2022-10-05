from django.core.paginator import Paginator

MESSAGE_N = 10


def paginator_posts(post_list, post_on_page, request):
    paginator = Paginator(post_list, post_on_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj
