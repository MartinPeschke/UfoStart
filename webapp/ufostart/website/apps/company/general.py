from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, REQUIRED, TextareaField, MultipleFormField, EmailField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from pyramid.renderers import render_to_response
from ufostart.website.apps.models.procs import CreateCompanyProc, CreateRoundProc, InviteToCompanyProc


def index(context, request):
    company = context.company
    if company.getCurrentRound():
        return render_to_response("ufostart:website/templates/company/index.html", {'company': company, 'currentRound':company.getCurrentRound()}, request)
    else:
        return render_to_response("ufostart:website/templates/company/index_empty.html", {}, request)

def create_round(context, request):
    company = context.company
    if not company.getCurrentRound():
        round = CreateRoundProc(request, {'slug': company.slug})
    request.fwd("website_company", **context.urlArgs)




class SetupCompanyForm(BaseForm):
    id="SetupCompany"
    label = ""
    fields=[
        StringField("name", "Name", REQUIRED)
        , TextareaField("description", "Description", input_classes="x-high")
    ]
    @classmethod
    def on_success(cls, request, values):
        data = {
                "token": request.root.user.token,
                "Company": values
            }
        try:
            user = CreateCompanyProc(request,  data)
            company = user.Company
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': "Already used, please choose another name!"}}
            else:
                raise e

        return {'success':True, 'redirect': request.fwd_url("website_company_invite", slug = company.slug)}

class SetupCompanyHandler(FormHandler):
    form = SetupCompanyForm



class InviteeForm(MultipleFormField):
    template = 'ufostart:website/templates/company/controls/invitee.html'
    add_more_link_label = "Add Invitee"
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "email address", REQUIRED)
    ]


class InviteCompanyForm(BaseForm):
    id="InviteCompany"
    label = ""
    fields=[
        InviteeForm('Invitees')
    ]
    @classmethod
    def on_success(cls, request, values):
        data = []
        user = request.root.user
        company = request.root.company
        for inv in values.get('Invitees'):
            inv['invitorToken'] = user.token
            inv['invitorName'] = user.name
            inv['companySlug'] = company.slug
            data.append(inv)
        InviteToCompanyProc(request, data)
        request.session.flash(GenericSuccessMessage("You successfully invited{} users to your company!".format(len(data))), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_company", slug = request.matchdict['slug'], _query = [('s', '1')])}

class InviteCompanyHandler(FormHandler):
    form = InviteCompanyForm