import graphene
from .models import *
from .object_types import (
    TagsType,
    UserType,
    AnswerType,
    QuestionType,
    AnswerReplyType
)

class Query(object):
    tags = graphene.List(
        TagsType,
        ids=graphene.List(
            graphene.NonNull(graphene.Int),
        ),
        name_iexact=graphene.String(),
        name_icontains=graphene.String()
    )

    def resolve_tags(self,info, **kwargs):
        if not info.context.user.is_anonymous:
            queryset = Tags.objects.all()
            if kwargs.get("ids"):
                queryset = queryset.filter(id__in=kwargs.get("ids"))
            if kwargs.get("name_iexact"):
                queryset = queryset.filter(name__iexact=kwargs.get("name_iexact"))
            if kwargs.get("name_icontains"):
                queryset = queryset.filter(name__icontains=kwargs.get("name_icontains"))
            return queryset
        return None

    all_user = graphene.List(
        UserType,
        username=graphene.String(),
    )
    
    def resolve_all_user(self, info, **kwargs):
        username  = kwargs.get("username")
        userInstance = User.objects.all()
        if username:
            userInstance = userInstance.filter(username__iexact=username)
        return userInstance
    
    questions = graphene.List(
        QuestionType,
        ids=graphene.List(
            graphene.NonNull(graphene.Int)
        ),
        question_iexact=graphene.String(),
        question_icontains=graphene.String(),
        author=graphene.String()
    )

    def resolve_questions(self,info,**kwargs):       
        user=info.context.user        
        queryset = Question.objects.all()
        if kwargs.get("ids"):
            queryset = queryset.filter(id__in=kwargs.get("ids"))        
        if kwargs.get("question_iexact"):
            queryset = queryset.filter(question__iexact=kwargs.get("question_iexact"))
        if kwargs.get("question_icontains"):
            queryset = queryset.filter(question__icontains=kwargs.get("question_icontains"))
        if kwargs.get("author"):
            queryset = queryset.filter(author=kwargs.get("author"))        
        return queryset