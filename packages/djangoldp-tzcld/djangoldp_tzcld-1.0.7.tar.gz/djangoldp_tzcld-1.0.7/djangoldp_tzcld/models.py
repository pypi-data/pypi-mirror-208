from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from djangoldp.models import Model
from djangoldp_community.models import Community, CommunityMember
from djangoldp_tzcld.permissions import TzcldCommunityProfilePermissions

#############################
# Extend user model
#############################


class TzcldTerritoryDepartment(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Department')
        verbose_name_plural = _("TZCLD Departments")
        anonymous_perms = ['view']
        container_path = "tzcld-departments/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:departments"

class TzcldTerritoryRegion(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Région')
        verbose_name_plural = _("TZCLD Régions")
        anonymous_perms = ['view']
        container_path = "tzcld-regions/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:regions"

class TzcldProfilesMembership(Model):
    name = models.CharField(max_length=255, blank=False, null=True, default='')


    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Memebership type')
        verbose_name_plural = _("TZCLD Memebership types")
        anonymous_perms = ['view']
        authenticated_perms = ['view']
        superuser_perms = ['inherit', 'change']
        container_path = "tzcld-profile-membership/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:profileMembership"

# DjangoLDP User Extension

class TzcldProfile(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tzcld_profile")
    #description = models.CharField(max_length=255, blank=True, null=True, default='')
    #postal_code = models.CharField(max_length=255, blank=True, null=True, default='')
    #address = models.CharField(max_length=255, blank=True, null=True, default='')
    #phone = models.CharField(max_length=255, blank=True, null=True, default='')
    #position = models.CharField(max_length=255, blank=True, null=True, default='')
    last_contribution_year = models.CharField(max_length=255, blank=True, null=True, default='')
    regions = models.ManyToManyField(TzcldTerritoryRegion, related_name='profile_regions', blank=True)
    departments = models.ManyToManyField(TzcldTerritoryDepartment, related_name='profile_department', blank=True)
    is_member = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} ({})'.format(self.user.get_full_name(), self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Profile')
        verbose_name_plural = _("TZCLD Profiles")
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['inherit', 'change']
        ordering = ['user']
        #serializer_fields = ['@id', 'description', 'regions', 'postal_code', 'address', 'events', 'phone', 'orgs', 'position', 'membership', 'last_contribution_year', 'jobs']
        serializer_fields = ['@id', 'last_contribution_year', 'jobs', 'regions', 'departments', 'is_member']
        rdf_type = "tzcld:profile"
        auto_author = 'user'
        depth = 3

class TzcldProfileJob(Model):
    position = models.CharField(max_length=255, blank=True, null=True, default='')
    organisation = models.CharField(max_length=255, blank=True, null=True, default='')
    address = models.CharField(max_length=255, blank=True, null=True, default='')
    postal_code = models.CharField(max_length=255, blank=True, null=True, default='')
    city = models.CharField(max_length=255, blank=True, null=True, default='')
    department = models.ForeignKey(TzcldTerritoryDepartment, on_delete=models.DO_NOTHING,related_name='job_department', blank=True, null=True)
    #address_public = models.BooleanField(default=False)
    profile = models.ForeignKey(TzcldProfile, on_delete=models.CASCADE,related_name='jobs', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True, default='')
    
    phone = models.CharField(max_length=255, blank=True, null=True, default='')
    phone_public = models.BooleanField(default=False)
    mobile_phone = models.CharField(max_length=255, blank=True, null=True, default='')
    mobile_phone_public = models.BooleanField(default=False)
    email = models.CharField(max_length=255, blank=True, null=True, default='')
    email_public = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} ({})'.format(self.position, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD profile job')
        verbose_name_plural = _("TZCLD profiile jobs")
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'view', 'add', 'change']
        superuser_perms = ['inherit', 'change']
        container_path = "tzcld-profile-job/"
        serializer_fields = ['@id', 'position', 'organisation', 'address', 'postal_code', 'city', 'department','profile', 'link','phone' ,'phone_public' ,'mobile_phone' ,'mobile_phone_public' ,'email' ,'email_public' ]
        nested_fields = []
        rdf_type = "tzcld:profileJob"

#############################
# Old models version
#############################
"""

class TzcldProfileEvent(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    tzcldprofile = models.ManyToManyField(TzcldProfile, related_name='events', blank=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Event')
        verbose_name_plural = _("TZCLD Events")
        anonymous_perms = ['view']
        container_path = "tzcld-events/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:event"


class TzcldProfileOrganisation(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    tzcldprofile = models.ManyToManyField(TzcldProfile, related_name='orgs', blank=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Organisation or Territory')
        verbose_name_plural = _("TZCLD Organisations or Territories")
        anonymous_perms = ['view']
        container_path = "tzcld-orgs/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:org"


class TzcldProfileRegion(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')
    tzcldprofile = models.ManyToManyField(TzcldProfile, related_name='regions', blank=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Region or departement')
        verbose_name_plural = _("TZCLD Regions or departements")
        anonymous_perms = ['view']
        container_path = "tzcld-regions/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:regions"
"""

#############################
# DjangoLDP Community Extension
#############################

class TzcldTerritoriesStepState(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory step state')
        verbose_name_plural = _("TZCLD Territories step states")
        anonymous_perms = ['view']
        container_path = "tzcld-territories-step-states/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:territoryStepState"

class TzcldTerritoriesKind(Model):
    name = models.CharField(max_length=254, blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory Kind')
        verbose_name_plural = _("TZCLD Territories Kind")
        anonymous_perms = ['view']
        container_path = "tzcld-kinds/"
        serializer_fields = ['@id', 'name']
        nested_fields = []
        rdf_type = "tzcld:territoryKind"

class TzcldCommunity(Model):
    community = models.OneToOneField(Community, on_delete=models.CASCADE, related_name='tzcld_profile', null=True, blank=True)
    kind = models.ForeignKey(TzcldTerritoriesKind, on_delete=models.DO_NOTHING,related_name='kind', blank=True, null=True)
    step_state = models.ForeignKey(TzcldTerritoriesStepState, on_delete=models.DO_NOTHING,related_name='step_state', blank=False, null=True)
    regions = models.ManyToManyField(TzcldTerritoryRegion, related_name='community_regions', blank=True)
    departments = models.ManyToManyField(TzcldTerritoryDepartment, related_name='community_departments', blank=True)
    membership = models.ForeignKey(TzcldProfilesMembership, on_delete=models.DO_NOTHING,related_name='membership', blank=False, null=True)
    membership_organisation_name = models.CharField(max_length=254, blank=True, null=True, default='')
    """
    features = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_mail_1 = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_mail_2 = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_mail_3 = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_last_name = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_first_name = models.CharField(max_length=255, blank=True, null=True, default='')
    contact_job = models.CharField(max_length=255, blank=True, null=True, default='')
    membership = models.BooleanField(default=False)
    last_contribution_year = models.CharField(max_length=255, blank=True, null=True, default='')
    """

    def __str__(self):
        try:
            return '{} ({})'.format(self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Community Profile')
        verbose_name_plural = _("TZCLD Communities Profiles")
        permission_classes = [TzcldCommunityProfilePermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        superuser_perms = ['view']
        ordering = ['community']
        container_path = "/tzcld-communities/"
        #serializer_fields = ['@id', 'contact_first_name', 'contact_last_name', 'contact_job', 'kind', 'features', 'region', 'contact_mail_1', 'contact_mail_2', 'contact_mail_3', 'membership', 'last_contribution_year']
        serializer_fields = ['@id', 'community', 'kind', 'step_state', 'kind', 'departments', 'regions', 'locations', 'tzcld_community_contacts', 'membership', 'membership_organisation_name']
        rdf_type = "tzcld:communityProfile"
        depth = 3


class TzcldTerritoryLocation(Model):
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    address = models.CharField(max_length=255, blank=True, null=True, default='')
    postal_code = models.CharField(max_length=255, blank=True, null=True, default='')
    city = models.CharField(max_length=255, blank=True, null=True, default='')
    department = models.ForeignKey(TzcldTerritoryDepartment, on_delete=models.DO_NOTHING,related_name='location_department', blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True, default='')
    twitter_link = models.CharField(max_length=255, blank=True, null=True, default='')
    linkedin_link = models.CharField(max_length=255, blank=True, null=True, default='')
    community = models.ForeignKey(TzcldCommunity, on_delete=models.CASCADE,related_name='locations', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Territory location')
        verbose_name_plural = _("TZCLD Territories locations")
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'view', 'add', 'change']
        superuser_perms = ['inherit', 'view', 'add', 'change']
        container_path = "tzcld-territories-location/"
        serializer_fields = ['@id', 'name', 'address', 'postal_code', 'city', 'department', 'link', 'twitter_link', 'linkedin_link', 'phones', 'emails', 'community']
        nested_fields = []
        rdf_type = "tzcld:territoryLocation"


#############################
# Shared models for user and community
#############################

class TzcldContactPhone(Model):
    phone = models.CharField(max_length=255, blank=True, null=True, default='')
    phone_type = models.CharField(max_length=255, blank=True, null=True, default='')
    phone_public = models.BooleanField(default=False)
    job = models.ForeignKey(TzcldProfileJob, on_delete=models.CASCADE, related_name='phones', blank=True, null=True)
    location = models.ForeignKey(TzcldTerritoryLocation, on_delete=models.CASCADE, related_name='phones', blank=True, null=True)


    def __str__(self):
        try:
            return '{} ({})'.format(self.position, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD phone')
        verbose_name_plural = _("TZCLD phones")
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['inherit', 'change']
        container_path = "tzcld-contact-phone/"
        serializer_fields = ['@id', 'phone', 'phone_type', 'phone_public', 'job', 'location']
        nested_fields = []
        rdf_type = "tzcld:phone"

class TzcldContactEmail(Model):
    email = models.CharField(max_length=255, blank=True, null=True, default='')
    email_type = models.CharField(max_length=255, blank=True, null=True, default='')
    email_public = models.BooleanField(default=False)
    job = models.ForeignKey(TzcldProfileJob, on_delete=models.CASCADE,related_name='emails', blank=True, null=True)
    location = models.ForeignKey(TzcldTerritoryLocation, on_delete=models.CASCADE,related_name='emails', blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.position, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD email')
        verbose_name_plural = _("TZCLD emails")
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['inherit', 'change']
        container_path = "tzcld-contact-email/"
        serializer_fields = ['@id', 'email', 'email_type', 'email_public', 'job', 'location']
        nested_fields = []
        rdf_type = "tzcld:email"


class TzcldContactMember(Model):
    member = models.OneToOneField(CommunityMember, on_delete=models.CASCADE, related_name="tzcld_contact_member")
    tzcldCommunity = models.ForeignKey(TzcldCommunity, on_delete=models.CASCADE, related_name='tzcld_community_contacts', null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('TZCLD Contact Member')
        verbose_name_plural = _("TZCLD Contact Members")
        anonymous_perms = ['view']
        authenticated_perms = ['view']
        superuser_perms = ['inherit', 'change']
        container_path = "tzcld-contact-member/"
        serializer_fields = ['@id', 'member', 'is_primary']
        nested_fields = []
        rdf_type = "tzcld:contactMember"


# Create tzcld user profile, job instance and contact email/phone when user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_tzcld_profile(sender, instance, created, **kwargs):
    if not Model.is_external(instance) and created:
        tzcld_profile = TzcldProfile.objects.create(user=instance)
        profile_job = TzcldProfileJob.objects.create(profile=tzcld_profile)
        TzcldContactEmail.objects.create(job=profile_job)
        TzcldContactPhone.objects.create(job=profile_job)

        # add the user to the first (tzcld) community
        community = Community.objects.order_by('id').first()
        if community:
            community.members.create(user=instance)

# Create tzcld community profile, job instance and contact email/phone when community is created
@receiver(post_save, sender=Community)
def create_tzcld_community(instance, created, **kwargs):
    if not Model.is_external(instance) and created:
        tzCommunity = TzcldCommunity.objects.create(community=instance)
        territory_location = TzcldTerritoryLocation.objects.create(name=instance.name + " Location", community=tzCommunity)
        TzcldContactEmail.objects.create(email="brad@example.com", location=territory_location)
        TzcldContactPhone.objects.create(phone="0606060606", location=territory_location)

