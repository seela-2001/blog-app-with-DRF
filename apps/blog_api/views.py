from blog.models import Post,Category,Comment
from django.shortcuts import get_object_or_404
from .serializers import PostSerializer,CategorySerializer,CommentSerializer
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS,BasePermission, IsAuthenticated,IsAdminUser,DjangoModelPermissions,AllowAny
from rest_framework import viewsets,status
from rest_framework.decorators import api_view,permission_classes
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import generics

class PostUserWritePermission(BasePermission):
    message = 'Editing is restricted to the author only.'
      
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True 
        return obj.author == request.user
    



class CommentUpdateOrDeletePermission(BasePermission):
    message = 'Editing is restricted to the author only.'
      
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True 
        return obj.user == request.user






class CategoryViewSet(viewsets.ViewSet):
    query_set = Category.objects.all()
    permission_classes = [IsAdminUser]

    def list(self,request):
        try:
            serializer = CategorySerializer(self.query_set,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)

    def create(self,request):
        serializer = CategorySerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST) 
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)

    def destroy(self,request,pk=None):
        category = get_object_or_404(self.query_set,pk=pk)
        try:
            category.delete()
            return Response({'message':'deleted successfully'},status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        



class PostViewSet(viewsets.ViewSet):
    query_set = Post.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [PostUserWritePermission()]
        

    def list(self,request):
        try:
            serializer= PostSerializer(self.query_set,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'})
        
    def create(self,request):
        try:
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        

    def retrieve(self,request,pk):
        post = get_object_or_404(self.query_set,pk=pk)
        print(f"Retrieved post: {post}")
        self.check_object_permissions(request,post)
        try:
            serializer = PostSerializer(post)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'})
        

    def update(self,request,pk):
        post = get_object_or_404(self.query_set,pk=pk)
        self.check_object_permissions(request,post)
        try:
            serializer = PostSerializer(data=request.data,instance=post,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self,request,pk):
        post = get_object_or_404(self.query_set,pk=pk)
        try:
            self.check_object_permissions(request,post)
            post.delete()
            return Response({'message':'deleted successfully'},status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        
    



class AuthorPostsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        post = Post.objects.filter(author=request.user)
        try:
            if post:
                serializer = PostSerializer(post,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({'message':'You do not have posts yet.'},status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)




@permission_classes([IsAuthenticated])
@api_view(['GET'])
def search_for_blog(request,search_query):
    try:
        posts = Post.objects.filter(
            Q(title__icontains=search_query) | Q(slug__icontains=search_query)
        )
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({'message':'no similar blogs'},status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return Response({'error':f'{str(ex)}'})



# ----------------------------------------------------------------------------

# comments endpoints

class CreateComment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,post_id):
        post = get_object_or_404(Post,id=post_id)
        serializer = CommentSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class RetrieveAllPostComments(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,post_id):
        post = get_object_or_404(Post,id=post_id)
        comments = post.posts.all()
        try:
            serializer = CommentSerializer(comments,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        


class DeletePostComment(APIView):
    permission_classes = [CommentUpdateOrDeletePermission]

    def delete(self,request,post_id,comment_id):
        comment = get_object_or_404(Comment,post_id=post_id,id=comment_id)
        self.check_object_permissions(request,comment)
        try:
            comment.delete()
            return Response({'message':'deleted successfully'},status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)
        

class UpdatePostComment(APIView):
    permission_classes = [CommentUpdateOrDeletePermission]

    def put(self,request,post_id,comment_id):
        comment = get_object_or_404(Comment,post_id=post_id,id=comment_id)
        self.check_object_permissions(request,comment)
        try:
            serializer = CommentSerializer(comment,data=request.data,partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'error':f'{str(ex)}'},status=status.HTTP_400_BAD_REQUEST)