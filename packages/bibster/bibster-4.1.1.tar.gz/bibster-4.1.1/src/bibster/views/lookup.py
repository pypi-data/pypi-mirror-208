
import json
from django.http import Http404, HttpResponse

from wagtail.telepath import JSContext

from ..auto_fill import identify_reference
from ..blocks import ReferenceBlock


def lookup(request):

    query_string = request.GET.get("query", "")
    lookup_result = identify_reference(query_string)

    if lookup_result is None:
        result = {
            "status": "",
            "reference_type": "",
            "blockDef": None,
            "blockValue": None,
            "blockErrors": None
        }

        return result

    reference_type = None

    for key in lookup_result.keys():
        reference_type = key
        break

    result = {
        "status": "",
        "reference_type": reference_type,
    }

    block_data = create_frontend_block_data(REFERENCE_BLOCK_DEF, block_value=lookup_result, reference_type=reference_type)
    result.update(block_data)

    result = json.dumps(result)
    response = HttpResponse(content=result.encode("utf-8"), content_type='application/json')
    return response


REFERENCE_BLOCK_DEF = ReferenceBlock()


def create_frontend_block_data(block_def, errors=None, block_value=None, reference_type=None):

    js_context = JSContext()
    block_def_data = js_context.pack(block_def)

    if block_value and reference_type in block_def.child_blocks:
        block_value = dict(block_value)
        block_value["__type__"] = reference_type

    block_value = block_def.to_python(block_value)
    value_data = block_def.get_form_state(block_value)

    error_data = js_context.pack(errors)

    result = {
        'blockDef': block_def_data,
        'blockValue': value_data,
        'blockErrors': error_data
    }

    return result
