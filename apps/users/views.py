from .serializers import UserSerializer
from .models import NewUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, \
    IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .pagination import AuthorsPagination
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .custom_permissions import UserAuthentication
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = NewUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action == 'list':
            return [IsAdminUser()]
        else:
            return [UserAuthentication()]

    @swagger_auto_schema(
        operation_description="Create a new user.",
        responses={
            status.HTTP_201_CREATED:
            openapi.Response(description="User created successfully"),
            status.HTTP_400_BAD_REQUEST:
            openapi.Response(description="Invalid data provided")
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new user"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a list of users.",
        responses={
            status.HTTP_200_OK:
            openapi.Response(description="List of users",
                             schema=UserSerializer(many=True)),
            status.HTTP_401_UNAUTHORIZED:
            openapi.Response(description="Unauthorized")
        }
    )
    def list(self, request, *args, **kwargs):
        """Retrieve list of users"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a user by ID.",
        responses={
            status.HTTP_200_OK:
            openapi.Response(description="User data", schema=UserSerializer),
            status.HTTP_404_NOT_FOUND:
            openapi.Response(description="User not found")
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a user by their ID"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a user's data.",
        responses={
            status.HTTP_200_OK:
            openapi.Response(description="User updated successfully"),
            status.HTTP_400_BAD_REQUEST:
            openapi.Response(description="Invalid data provided"),
            status.HTTP_404_NOT_FOUND:
            openapi.Response(description="User not found")
        }
    )
    def update(self, request, *args, **kwargs):
        """Update user data"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a user.",
        responses={
            status.HTTP_204_NO_CONTENT:
            openapi.Response(description="User deleted successfully"),
            status.HTTP_404_NOT_FOUND:
            openapi.Response(description="User not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a user"""
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['delete'], url_path='delete-photo')
    @swagger_auto_schema(
        operation_description="Delete the user's profile photo.",
        responses={
            status.HTTP_204_NO_CONTENT:
            openapi.Response(description="Photo deleted successfully"),
            status.HTTP_400_BAD_REQUEST:
            openapi.Response(
                description=(
                    "User has no photo or another error\
                                        occurred thatprevented the operation.")
            )
        }
    )
    def delete_photo(self, request, pk):
        user = self.get_object()
        if user.photo:
            user.photo.delete()
            user.photo = None
            user.save()
        return Response({'message': 'photo deleted successfully'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'put'], url_path='add-photo')
    @swagger_auto_schema(
        operation_description="Add a photo to the user's profile.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'photo': openapi.Schema(type=openapi.TYPE_FILE,
                                        description='The photo\
                                                    file to be added')
            },
        ),
        responses={
            status.HTTP_200_OK:
            openapi.Response(description="Photo added successfully"),
            status.HTTP_400_BAD_REQUEST:
            openapi.Response(description="No photo provided or invalid data")
        }
    )
    def add_photo(self, request, pk=None):
        user = self.get_object()
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'message': 'no photo added'},
                            status=status.HTTP_400_BAD_REQUEST)
        if user.photo:
            user.photo.delete()
        user.photo = photo
        user.save()
        return Response({'message': 'photo added successfully'},
                        status=status.HTTP_200_OK)


class BlackListTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Blacklist a refresh token to invalidate it.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token':
                openapi.Schema(type=openapi.TYPE_STRING,
                               description='The refresh\
                                            token to be\
                                            blacklisted')
            },
        ),
        responses={
            status.HTTP_200_OK:
            openapi.Response(description="Token blacklisted successfully"),
            status.HTTP_400_BAD_REQUEST:
            openapi.Response(description="Invalid refresh token")
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as ex:
            return Response({'error': f'{str(ex)}'},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    tags=["Authors"],
    operation_summary="Search for Authors",
    operation_description=(
        "This endpoint allows authenticated users to search for authors "
        "based on their first name or username."
    ),
    manual_parameters=[
        openapi.Parameter(
            'search_query',
            openapi.IN_QUERY,
            description="The search term to filter\
                        authors by first name or username",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of authors matching the search query",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
        ),
        404: openapi.Response(
            description="No authors found matching the query",
            examples={"application/json":
                      {"message": "No similar authors found"}},
        ),
        400: openapi.Response(
            description="Bad request due to an error",
            examples={"application/json": {"error": "An error occurred"}},
        ),
    },
)
def search_for_authors(request):
    search_query = request.query_params.get('search_query', '').strip()
    if not search_query:
        return Response({'error': 'search_query parameter is required'},
                        status=status.HTTP_400_BAD_REQUEST)

    authors = NewUser.objects.filter(
        Q(first_name__icontains=search_query) |
        Q(username__icontains=search_query)
    )
    paginator = AuthorsPagination()
    paginated_authors = paginator.paginate_queryset(authors, request)
    if not authors.exists():
        return Response({'message': 'No similar authors found'},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(paginated_authors, many=True)
    return paginator.get_paginated_response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([UserAuthentication])
@swagger_auto_schema(
    operation_summary="Change User Password",
    operation_description=(
        "Allows an authenticated user to change their password.\
        The user must provide "
        "their old password, a new password,\
        and a confirmation of the new password. "
        "The new password must be at least 8 characters long, \
        and the confirmation password must match the new password."
    ),
    tags=["User"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "old_password":
            openapi.Schema(type=openapi.TYPE_STRING,
                           description="The user's current password."),
            "new_password":
            openapi.Schema(type=openapi.TYPE_STRING,
                           description="The new password to set."),
            "confirm_password":
            openapi.Schema(type=openapi.TYPE_STRING,
                           description="Confirmation of the new password."),
        },
        required=["old_password", "new_password", "confirm_password"]
    ),
    responses={
        200: openapi.Response(
            description="Password changed successfully.",
            examples={"application/json":
                      {"message": "Your password changed successfully"}}
        ),
        400: openapi.Response(
            description="Bad request.",
            examples={
                "application/json": {
                    "message": "All fields are required",
                    "error": "Your old password is incorrect",
                    "note": "Password must be at least 8 characters",
                    "mismatch": "Confirm password does not match new password"
                }
            }
        ),
        403: openapi.Response(
            description="Permission denied.",
            examples={"application/json": {"detail": "You are not authorized\
                                          to perform this action."}}
        )
    }
)
def change_password(request, pk):
    user = get_object_or_404(NewUser, pk=pk)

    # Check if the user has the right permission
    if user != request.user:
        raise PermissionDenied('You are not authorized\
                               to perform this action.')

    data = request.data
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    # Validate input
    if not old_password or not new_password or not confirm_password:
        raise ValidationError({'error': 'All fields are required'})

    if not check_password(old_password, user.password):
        return Response({'error': 'Your old password is incorrect'},
                        status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 8:
        return Response({'error': 'Password must be at least 8 characters'},
                        status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({'error':
                        'Confirm password does not match new password'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Set the new password
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Your password changed successfully'},
                    status=status.HTTP_200_OK)
