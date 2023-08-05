import json

from django.http import Http404, HttpResponse, HttpResponseBadRequest

from ..models import Publication
from ..apps import get_app_label

APP_LABEL = get_app_label()

def update_markup_cache(request):

    caches = {}

    publications = Publication.objects.all()

    for publication in publications:
        publication.clear_markup_cache()
        publication.save()
        markup_cache = publication.markup_cache
        harvard_cache = markup_cache.get("harvard", {})
        html_cache = harvard_cache.get(APP_LABEL + ":html", {})
        html_content = html_cache.get("content", "")
        caches[publication.id] = html_content

    caches = json.dumps(caches)
    response = HttpResponse(content=caches.encode("utf-8"), content_type='application/json')
    return response


def import_dois(request):

    if request.method == "POST":
        dois = request.POST.get("doi", None)

        if dois is None:
            dois = request.FILES.get("doi", None)

            if dois is not None:
                dois.seek(0)
                dois = dois.read(0).decode('utf-8')
                dois = [doi.trim() for doi in dois.split('\n')]
    else:
        dois = request.GET.get("doi", None)

    if dois is None:
        raise HttpResponseBadRequest

    if isinstance(dois, str):
        dois = [dois]

    results = Publication.create_from_dois(dois)



    pass


ACTIONS_BY_TYPE = {
    "update_markup_cache": update_markup_cache
}


def action(request):

    if request.method == "POST":
        action_type = request.POST.get("type", None)
    else:
        action_type = request.GET.get("type", None)

    if not action_type:
        raise Http404

    action = ACTIONS_BY_TYPE.get(action_type, None)

    if not action:
        raise Http404

    return action(request)

