import base64, logging
from hnc.apiclient.backend import DBNotification, DBException
from ufostart.website.apps.models.auth import RefreshAccessTokenProc, SocialConnectProc, SOCIAL_NETWORK_TYPES_REVERSE

log = logging.getLogger(__name__)


class InvalidSignatureException(Exception):pass


def fb_accept_requests(context, request):
    # this needs to be client initiated, as we cant decide serverside if user has accepted facebook login, only javascript really knows
    request.session.pop_flash("fb_requests")
    return {'success': True}



def fb_token_refresh(context, request):
    json_body = request.json_body
    isLogin = request.user.facebookId != json_body.get("facebookId")
    request.user.accessToken = json_body.get('accessToken')
    if not request.user.isAnon():
        try:
            RefreshAccessTokenProc(request, {'token':request.user.token, 'accessToken':json_body.get('accessToken')})
        except (DBNotification, DBException), e:
            pass
    return {"success":True, "isLogin": isLogin}


def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

def social_login(context, request):
    result = {'success': False}
    profile = request.json_body['profile']
    network = profile.pop('type')
    networkSettings = context.settings.networks.get(network)
    if networkSettings and networkSettings.requiresAction():
        try:
            profile = networkSettings.action(request, profile)
        except InvalidSignatureException, e:
            return {'success':False, 'message':"Invalid Signature!"}

    if not profile: return result
    profile['type'] = SOCIAL_NETWORK_TYPES_REVERSE[network]
    try:
        user = SocialConnectProc(request, {'Profile': [profile]})
    except DBNotification, e:
        log.error("UNHANDLED DB MESSAGE: %s", e.message)
        return {'success':False, 'message': e.message}
    result['success'] = True
    result['user'] = user.toJSON()
    return result

