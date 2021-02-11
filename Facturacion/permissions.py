from rest_framework.permissions import BasePermission


class SoloCajeros(BasePermission):
    def has_permission(self, request, view):
        # print(request.user.usuarioTipo)
        print(request.auth)
        print(request.method)
        # if request.auth == None:
        # return False
        if(request.method == 'GET' and request.user.usuarioTipo == 3):
            return True
        if(request.method == 'POST' and request.user.usuarioTipo == 1):
            return True
        print(view)
        return False


class SoloMeseros(BasePermission):
    def has_permission(self, request, view):
        if(request.user.usuarioTipo == 3):
            return True
        return False
