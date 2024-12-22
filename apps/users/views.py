from .serializers import UserSerializer,AllUsersData
from .models import NewUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,viewsets
from rest_framework.permissions import AllowAny,IsAdminUser,IsAuthenticated,BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework.decorators import api_view,permission_classes
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
# Create your views here.



class UserAuthentication(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return obj == request.user




class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        reg_serializer = UserSerializer(data=request.data)
        if reg_serializer.is_valid():
            reg_serializer.save()
            return Response(
            {
                "message": "User registered successfully.",
                "user": reg_serializer.data,
            },
            status=status.HTTP_201_CREATED,
            )
        return Response(reg_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        


class BlackListTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)




class UsersList(APIView):
    permission_classes = [IsAdminUser] 

    def get(self,request):
        try:
            users = NewUser.objects.all()
            serializer = AllUsersData(users,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
    


class UpdateUser(APIView):
    permission_classes = [UserAuthentication]

    def put(self,request,pk):
        try:
            user = NewUser.objects.get(id=pk)
            if request.user != user.id:
                raise PermissionDenied('You do not have permission to perform this action.')
            serializer = UserSerializer(data=request.data,instance=user,partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response({'message':'updated successfully'},status=status.HTTP_200_OK)
        except NewUser.DoesNotExist:
            return Response({'message':'no such user'},status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        
class DeleteUser(APIView):
    permission_classes = [UserAuthentication]

    def delete(self,request,pk):
        try:
            user = NewUser.objects.get(id=pk)
            if request.user != user:
                raise PermissionDenied("You do not have permission to access this user's data.")
            user.delete()
            return Response({'message':'user deleted successfully'},status=status.HTTP_204_NO_CONTENT)
        except NewUser.DoesNotExist:
            return Response({'message':'no such user'},status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        


class RetrieveUser(APIView):
    permission_classes = [UserAuthentication]
    def get(self,request,pk):
        try:
            user = NewUser.objects.get(id=pk)
            if request.user != user:
                raise PermissionDenied("You do not have permission to access this user's data.")
            serializer = UserSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        except NewUser.DoesNotExist:
            return Response({'message':'no such user'},status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def search_for_authors(request,search_query):
    try:
        authors = NewUser.objects.filter(
            Q(first_name__icontains=search_query) | Q(username__icontains=search_query)
        )
        serializer = UserSerializer(authors,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except NewUser.DoesNotExist:
        return Response({'message':'no similar authors'},status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
    

@permission_classes([UserAuthentication])
@api_view(['POST'])
def upload_photo(request,pk):
    user = get_object_or_404(NewUser,pk=pk)
    if user != request.user:
        raise PermissionDenied('You do not have permission to perform this action')
    if 'photo' not in request.FILES:
        return Response({'error':'no image found'})
    try:
        user.photo = request.FILES['photo']
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
    


@permission_classes([UserAuthentication])
@api_view(['DELETE'])
def delete_photo(request,pk):
    user = get_object_or_404(NewUser,pk=pk)
    if user != request.user:
        raise PermissionDenied('You do not have permission to perform this action')
    try:
        if user.photo:
            user.photo.delete(save=False)
            user.phot = None
            user.save()
            return Response({'message':'photo removed successfully'},status=status.HTTP_200_OK)
        else:
            return Response({'message':'no photo to remove'},status=status.HTTP_204_NO_CONTENT)
    except Exception as ex:
        return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
    

@permission_classes([UserAuthentication])
@api_view(['POST'])
def change_password(request,pk):
    user = get_object_or_404(NewUser,pk=pk)
    if user != request.user:
        raise PermissionDenied('You are not authorized to perform this action.')
    
    data = request.data

    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not old_password or not new_password or not confirm_password:
        return Response({'error':'all fields are required'},status=status.HTTP_400_BAD_REQUEST)
    
    if not check_password(old_password,user.password):
        return Response({'error':'Your old password is incorrect'},status=status.HTTP_400_BAD_REQUEST)
    
    
    if len(new_password) < 8:
        return Response({'error':'password must be at least 8 characters'},status=status.HTTP_400_BAD_REQUEST)
    
    if confirm_password != new_password:
        return Response({'error':'confirm password does not match new password'},status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    return Response({'message':'Your password changed successfully'},status=status.HTTP_200_OK)