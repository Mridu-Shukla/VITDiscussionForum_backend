from django.utils.timezone import datetime
from django.contrib.auth import get_user_model
from django.conf import settings
import graphene
import pytz
from models.models import *
from .object_types import (
    TagsType,
    UserType,
    QuestionType,
    AnswerType,
    AnswerReplyType
)

class CreateTags(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
    
    tag = graphene.Field(TagsType, name="tag")
    errors = graphene.String()
    def mutate(self, info, name=None):
        user = info.context.user
        is_existing = (
            True if len(Tags.objects.filter(name=name)) > 0 else False 
        )
        if is_existing:
            return CreateTags(
                tag=None, 
                errors="Tag Already Exixts."
            )
        if user:
            try:
                tagInstance = Tags(name=name)
                tagInstance.save()
            
            except Exception as err:
                return CreateTags(
                    tag=None, errors=str(err)
                )
            return CreateTags(
                tag=tagInstance, errors=None
            )
        return CreateTags(
            tag=None, errors="Insufficient Privileges"
        )

class UpdateTag(graphene.Mutation):
    class Arguments:
        id=graphene.Int(required=True)
        name=graphene.String(required=True)
    
    tag = graphene.Field(TagsType, name="tag")
    errors = graphene.String()

    def mutate(self,info,name=None,id=None):
        user = info.context.user
        try:
            tagInstance = Tags.objects.get(pk=id)
        except Tags.DoesNotExist:
            return UpdateTag(
                tag=None,
                errors="Tags Not Found"
            )        
        try:
            tagInstance.name = name
            tagInstance.save()
        except Exception as err:
            return UpdateTag(
                tag=None,
                errors=str(err)
            )
        return UpdateTag(
                tag=tagInstance,
                errors=None
            )

class DeleteTags(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    tag = graphene.Field(TagsType, name="tag")
    errors = graphene.String()

    def mutate(self,info,id=None):
        try:
            tagInstance = Tags.objects.get(pk=id)
        except Tags.DoesNotExist:
            return UpdateTag(
                tag=None,
                errors="Tags Not Found"
            )        
        try:
            tagInstance.delete()
        except Exception as err:
            return UpdateTag(
                tag=None,
                errors=str(err)
            )
        return UpdateTag(
                tag=tagInstance,
                errors=None
            )

class CreateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        email = graphene.String(required=True)
        about = graphene.String()   

    user = graphene.Field(UserType)
    errors = graphene.String()     

    def mutate(self, info, username, password,last_name,first_name,confirm_password, email,about=None):
        if(User.objects.filter(email=email)):
            return CreateUser(user=None, errors="Email already taken")
        
        if(User.objects.filter(username=username)):
            return CreateUser(user=None, errors="Username already taken")

        if password != confirm_password:
            return CreateUser(user=None, errors="Paswords Do Not Match")
        user = User.objects.create_user(
            username=username,
            email=email,
            about=about,
            last_name=last_name,
            first_name=first_name
        )
        user.set_password(password)
        user.save()
        return CreateUser(user=user,errors=None)


class CreateQuestion(graphene.Mutation):
    class Arguments:
        question = graphene.String(required=True)
        tags = graphene.List(
            graphene.NonNull(graphene.Int) ,required=True
        )
    
    ques = graphene.Field(QuestionType) 
    errors = graphene.String()

    def mutate(self,info,tags,question=None):
        user = info.context.user
        tagsInstance = []
        for tag in tags:
            try:
                tagInstance = Tags.objects.get(id=tag)
                tagsInstance.append(tagInstance)
            except Tags.DoesNotExist:
                return CreateQuestion(
                    ques=None,
                    errors="Invalid Tag"
                )
        if user:
            try:                
                questionInstance = Question(
                    question=question,
                    author=user,
                    timestamp=datetime.now(pytz.timezone(settings.TIME_ZONE))
                )                
                questionInstance.full_clean()                
                questionInstance.save()
                questionInstance.tags.set(tagsInstance)
                questionInstance.save()
            except Exception as err:
                return CreateQuestion(
                    ques=None, errors=str(err)
                )
            return CreateQuestion(
                ques=questionInstance, errors=None
            )
        return CreateQuestion(
            ques=None, errors="Insufficient Privileges"
        )

class UpdateQuestion(graphene.Mutation):
    class Arguments:
        id=graphene.Int(required=True)
        question=graphene.String(required=True)
        tags = graphene.List(
            graphene.NonNull(graphene.Int) ,required=True
        )
    
    ques = graphene.Field(QuestionType) 
    errors = graphene.String()

    def mutate(self, info,tags, id, question):
        user = info.context.user
        try:
            questionInstance = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return UpdateQuestion(
                ques=None,
                errors="Question Not Found"
            )        
        if questionInstance.author != user:
            return UpdateQuestion(
                ques=None,
                errors="Not allowed to edit foreign question"
            )
        try:
            if question:
                questionInstance.question = question            
            if tags:
                tagsInstance = []
                for tag in tags:
                    try:
                        tagInstance = Tags.objects.get(id=tag)
                        tagsInstance.append(tagInstance)
                    except Tags.DoesNotExist:
                        return CreateQuestion(
                            ques=None,
                            errors="Invalid Tag"
                    )
                questionInstance.tags.set(tagsInstance)
            questionInstance.save()
        except Exception as err:
            return UpdateQuestion(
                ques=None, errors=str(err)
            )
        return UpdateQuestion(ques=questionInstance, errors=None)


class DeleteQuestion(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    ques = graphene.Field(QuestionType) 
    errors = graphene.String()

    def mutate(self, info, id=None):
        user = info.context.user
        try:
            questionInstance = Question.objects.get(id=id)
        except Question.DoesNotExist:
            return DeleteQuestion(
                ques=None, errors="No such question found"
            )        
        if questionInstance.author != user:
            return DeleteQuestion(
                ques=None, errors="Not delete question from foreign authors"
            )
        try:
            questionInstance.delete()
        except Exception as err:
            return DeleteQuestion(ques=None, errors=str(err))
        return DeleteQuestion(ques=questionInstance,errors=None)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_tags = CreateTags.Field()
    update_tag = UpdateTag.Field()
    delete_tags = DeleteTags.Field()
    create_question = CreateQuestion.Field()
    update_question = UpdateQuestion.Field()
    delete_question = DeleteQuestion.Field()