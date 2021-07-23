from django.db import models
from django.shortcuts import render

from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel
from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet

from core.models import SEOPage

from user.forms import LoginForm
from user.models import Auth

from .forms import MemberForm

class RegistrationPage (SEOPage):
    template_credentials = models.CharField(max_length=125, default='memberships/credentials_page.html')
    template_memberships = models.CharField(max_length=125, default='memberships/memberships_page.html')
    template_test = models.CharField(max_length=125, default='memberships/memberships_page.html')

    promote_panels = SEOPage.promote_panels + [
        FieldPanel('template_credentials'),
        FieldPanel('template_memberships')
    ]

    class Meta:
        verbose_name = 'Memberships: Inscription'

    def get_data_for_step (self, step):
        if step == 2:
            return MemberForm, self.template_memberships

        else:
            return LoginForm, self.template_credentials
            

    def serve(self, request, *args, **kwargs):
        """
        Implements a simple multi-step form.

        Stores each step into a session.
        When the last step was submitted correctly, saves whole form into a DB.
        """

        session_key_data = 'form_data-%s' % self.pk
        is_last_step = False
        step_number = int(request.GET.get('p', 1))   
        is_last_step = True if step_number == 3 else False
        print (step_number)

        if request.method == 'POST':
            print ('d')
            prev_form_class, prev_template = self.get_data_for_step(step_number - 1)
            prev_form = prev_form_class(data=request.POST)

            if prev_form.is_valid():
                print ('a')
                form_data = request.session.get(session_key_data, {})
                form_data.update(prev_form.cleaned_data)
                request.session[session_key_data] = form_data

                if is_last_step:
                    print ('b')
                    pass

                else:
                    print ('c')
                    form_class, template = self.get_data_for_step(step_number)
                    form = form_class()
            
            else:
                print ('e')
                form = prev_form
                template = prev_template
                print (form.errors)

        else:
            print ('g')
            form_class, template = self.get_data_for_step(1) 
            form = form_class()

        context = self.get_context(request)
        context['form'] = form

        return render(
            request,
            template,
            context
        )

        paginator = Paginator(self.get_form_fields(), per_page=1)
        try:
            step = paginator.page(step_number)
        except PageNotAnInteger:
            step = paginator.page(1)
        except EmptyPage:
            step = paginator.page(paginator.num_pages)
            is_last_step = True

        if request.method == 'POST':
            # The first step will be submitted with step_number == 2,
            # so we need to get a form from previous step
            # Edge case - submission of the last step

            prev_step = step if is_last_step else paginator.page(step.previous_page_number())

            # Create a form only for submitted step
            prev_form_class = self.get_form_class_for_step(prev_step)
            prev_form = prev_form_class(request.POST, page=self, user=request.user)
            if prev_form.is_valid():
                # If data for step is valid, update the session
                form_data = request.session.get(session_key_data, {})
                form_data.update(prev_form.cleaned_data)
                request.session[session_key_data] = form_data

                if prev_step.has_next():
                    # Create a new form for a following step, if the following step is present
                    form_class = self.get_form_class_for_step(step)
                    form = form_class(page=self, user=request.user)
                else:
                    # If there is no next step, create form for all fields
                    form = self.get_form(
                        request.session[session_key_data],
                        page=self, user=request.user
                    )

                    if form.is_valid():
                        # Perform validation again for whole form.
                        # After successful validation, save data into DB,
                        # and remove from the session.
                        form_submission = self.process_form_submission(form)
                        del request.session[session_key_data]
                        # render the landing page
                        return self.render_landing_page(request, form_submission, *args, **kwargs)
            else:
                # If data for step is invalid
                # we will need to display form again with errors,
                # so restore previous state.
                form = prev_form
                step = prev_step
        else:
            # Create empty form for non-POST requests
            form_class = self.get_form_class_for_step(step)
            form = form_class(page=self, user=request.user)

        context = self.get_context(request)
        context['form'] = form
        context['fields_step'] = step
        return render(
            request,
            self.template,
            context
        )

        