from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import RefreshProfileProc, FindPublicNeeds, FindPublicNeedsByLocation, GetNewProductsProc


@require_login()
def home(context, request):
    profile = RefreshProfileProc(request, {'token': context.user.token})
    best_match = FindPublicNeeds(request, {'Search': {'tags': profile.display_skills}})
    location = FindPublicNeedsByLocation(request)
    return {'profile': profile, 'best_match':best_match, 'isMyProfile': True, 'location_needs':location}



@require_login()
def user(context, request):
    profile = RefreshProfileProc(request, {'token': request.matchdict['slug']})
    if not profile:
        return {'profile': None}
    else:
        best_match = FindPublicNeeds(request, {'Search': {'tags': profile.display_skills}})
        return {'profile': profile, 'best_match':best_match, 'isMyProfile': False, 'location_needs':location}
