from djangoldp_community.permissions import CommunityPermissions
from django.urls import resolve
from djangoldp.utils import is_authenticated_user


class TzcldCommunityProfilePermissions(CommunityPermissions):
    filter_backends = []

    def get_container_permissions(self, request, view, obj=None):
        perms = set({'view'})
        if obj is None:
            from djangoldp_community.models import Community
            resolved = resolve(request.path_info)
            if 'slug' in resolved.kwargs and (resolved.url_name == "tzcldcommunity-list" or
                                              resolved.url_name == "tzcldcommunity-detail"):
                community = Community.objects.get(slug=resolved.kwargs['slug'])
                if is_authenticated_user(request.user) and community.members.filter(user=request.user).exists():
                    if community.members.get(user=request.user).is_admin:
                        perms = perms.union({'add', 'change'})
        else:
            return self.get_object_permissions(request, view, obj)
        return perms
