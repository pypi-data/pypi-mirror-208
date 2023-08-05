from maintenance_mode.http import need_maintenance_response


def need_maintenance_response_context_processor(request):
    return {"need_maintenance_response": need_maintenance_response(request)}
