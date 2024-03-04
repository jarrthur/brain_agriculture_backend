# TODO: Implementar Http Only Cookie
from rest_framework import exceptions as rest_exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    http_method_names = ["post"]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            raise rest_exceptions.ParseError({"detail": "Invalid token"})
