from blog.models import Post,Category,Comment
from .serializers import PostSerializer,CategorySerializer,CommentSerializer
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS,BasePermission, IsAuthenticated,IsAdminUser
from rest_framework import viewsets,status
from rest_framework.decorators import api_view,permission_classes
from django.db.models import Q
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Retrieve a specific category",
        operation_description="Retrieve details of a category by its unique ID.",
        responses={
            200: CategorySerializer,
            404: openapi.Response("Category not found.")
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List all categories",
        operation_description="Retrieve a list of all categories available in the system.",
        responses={
            200: CategorySerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new category",
        operation_description="Add a new category to the system. Admin permissions required.",
        request_body=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: openapi.Response("Invalid data provided.")
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a category",
        operation_description="Update an existing category by its unique ID. Admin permissions required.",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: openapi.Response("Invalid data provided."),
            404: openapi.Response("Category not found.")
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a category",
        operation_description="Partially update fields of an existing category by its unique ID. Admin permissions required.",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: openapi.Response("Invalid data provided."),
            404: openapi.Response("Category not found.")
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a category",
        operation_description="Remove a category from the system by its unique ID. Admin permissions required.",
        responses={
            204: openapi.Response("Category deleted."),
            404: openapi.Response("Category not found.")
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

        


class PostViewSet(viewsets.ModelViewSet):

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminUser()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        else:
            return [PostUserWritePermission()]

    
    @swagger_auto_schema(
        operation_description="Retrieve a list of all posts. Admin access is required.",
        responses={200: PostSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new post. Requires user authentication.",
        request_body=PostSerializer,
        responses={
            201: openapi.Response("Post created successfully", PostSerializer),
            400: "Invalid input",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific post by its ID.",
        responses={
            200: openapi.Response("Post retrieved successfully", PostSerializer),
            404: "Post not found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a specific post by its ID. Requires appropriate permissions.",
        request_body=PostSerializer,
        responses={
            200: openapi.Response("Post updated successfully", PostSerializer),
            400: "Invalid input",
            404: "Post not found",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a specific post by its ID. Requires appropriate permissions.",
        responses={
            204: "Post deleted successfully",
            404: "Post not found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
        
        

    
class AuthorPostsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        summary="Retrieve all posts by the logged-in author",
        description="Returns a list of posts authored by the authenticated user. If no posts are found, it returns a 404 message.",
        responses={
            200: PostSerializer(many=True),  # Response for successful retrieval
            404: dict,  # Message when no posts exist
            400: dict,  # Error response
        },
        tags=["Posts"], 
    )
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
@swagger_auto_schema(
    summary="Search for blogs by title or slug",
    description=(
        "This endpoint allows users to search for blogs by providing a query. "
        "It performs a case-insensitive search in the `title` or `slug` fields of posts."
    ),
    parameters=[
        {
            "name": "search_query",
            "required": True,
            "in": "query",
            "description": "The search term to look for in blog titles or slugs.",
            "schema": {"type": "string"},
        }
    ],
    responses={
        200: PostSerializer(many=True),  # Successful response with matching posts
        404: dict,  # No similar blogs message
        400: dict,  # Error details in case of unexpected issues
    },
    tags=["Blogs"],  # Optional grouping
)
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


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing comments on specific posts.
    """

    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id)
    
    @swagger_auto_schema(
        operation_description="Create a new comment for a specific post.",
        request_body=CommentSerializer,
        responses={
            201: openapi.Response("Comment created successfully", CommentSerializer),
            400: "Invalid input data",
        },
    )
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(user=self.request.user, post_id=post_id)

    def get_permissions(self):
        if self.action in ['list', 'create', 'retrieve']:
            return [IsAuthenticated()]
        else:
            return [CommentUpdateOrDeletePermission()]

    @swagger_auto_schema(
        operation_description="Retrieve a list of comments for a specific post.",
        responses={200: CommentSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific comment for a post.",
        responses={
            200: openapi.Response("Comment retrieved successfully", CommentSerializer),
            404: "Comment not found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a specific comment for a post. Requires appropriate permissions.",
        request_body=CommentSerializer,
        responses={
            200: openapi.Response("Comment updated successfully", CommentSerializer),
            400: "Invalid input data",
            404: "Comment not found",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a specific comment for a post. Requires appropriate permissions.",
        responses={
            204: "Comment deleted successfully",
            404: "Comment not found",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)