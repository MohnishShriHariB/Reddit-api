from django.shortcuts import render
from .serializers import Postserializers,Voteserializer
from .models import Post,Vote
from rest_framework.exceptions import ValidationError
from rest_framework import generics,permissions,mixins,status
from rest_framework.response import Response
# Create your views here.

class Postlist(generics.ListCreateAPIView):
    queryset=Post.objects.all()
    serializer_class=Postserializers
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    def perform_create(self,serializers):
        serializers.save(poster=self.request.user)

class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=Postserializers
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    def delete(self,request,*args,**kwargs):
        post=Post.objects.filter(poster=self.request.user,pk=self.kwargs['pk'])
        if post.exists():
            return self.destroy(request,*args,**kwargs)
        else:
            raise ValidationError('This is not your post')


class Votelist(generics.CreateAPIView,mixins.DestroyModelMixin):
    serializer_class=Voteserializer
    permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self):
        user=self.request.user
        post=Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user,post=post)
    def perform_create(self,serializers):
        if self.get_queryset().exists():
            raise ValidationError('You have already voted for this post')
        serializers.save(voter=self.request.user,post=Post.objects.get(pk=self.kwargs['pk']))
    def delete(self,request,*args,**kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('You have not voted for this post')
