from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsPostOwnerOrReadOnly
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer


class PostView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        return serializer.save(posted_by=self.request.user)

    def get_queryset(self):
        return Post.objects.filter(access="public")


class PostDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPostOwnerOrReadOnly]

    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CommentView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return serializer.save(post=post, commented_by=self.request.user)


class LikeView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        like = Like.objects.filter(liked_by_id=self.request.user.id, posted_in=post)

        if like.exists():
            return Response(
                {"detail": "This post was already liked"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(liked_by=self.request.user, posted_in=post)
