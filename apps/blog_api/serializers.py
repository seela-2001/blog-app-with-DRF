from rest_framework import serializers
from blog.models import Post, Comment, Category


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'post', 'user']


class PostSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField(read_only=True)

    def get_comment(self, obj):
        comment = Comment.objects.filter(post=obj)
        serializer = CommentSerializer(comment, many=True)
        return serializer.data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_autenticated:
            validated_data['author'] = request.user
        return super().create(validated_data)

    class Meta:
        model = Post
        fields = ['id',
                  'title',       # Title of the post
                  'excerpt',
                  'content',     # Main content
                  'category',    # Post category
                  'comment',]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
