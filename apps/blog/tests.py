from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post,Category



class TestCreatePost(TestCase):
   @classmethod
   def setUpTestData(cls):
      test_category = Category.objects.create(name='django')
      testuser1 = User.objects.create_user(username='test_user1',password='123456789')
      testpost = Post.objects.create(category_id=4,title='Post Title',excerpt='Post Excerpt',content='Post Content',author_id=1,status='published')

   def test_blog_content(self):
       post = Post.objects.get(id=1)
       cat = Category.objects.get(id=1)
       author = f'{post.author}'
       excerpt = f'{post.excerpt}'
       title = f'{post.title}'
       content = f'{post.content}'
       status = f'{post.status}'
       self.assertEqual(author,'test_user1')
       self.assertEqual(title,'Post Title')
       self.assertEqual(content,'Post Content')
       self.assertEqual(status,'published')
       self.assertEqual(str(post),'Post Title')
   
