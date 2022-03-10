# serializers.py
from rest_framework import serializers
from .models import File,Batch,Profile
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=32)
    first_name = serializers.CharField(max_length=32)
    last_name = serializers.CharField(max_length=32)
    is_active = serializers.BooleanField()

    def create(self, validated_data):
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user, first_name=first_name, last_name=last_name)
        return user


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone", "password"]


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=16)
    repeat_password = serializers.CharField(max_length=16)
    user = serializers.CharField(max_length=4)

    def create(self, validated_data):
        query_set = User.objects.all()
        new_password = validated_data.get("new_password")
        user_id = validated_data.get("user")
        user = get_object_or_404(query_set, pk=user_id)
        print(user)
        user.set_password(new_password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class GetUserSerilaizer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "password",
            "last_login",
            "is_admin",
            "phone",
            "email",
            "is_staff",
            "is_active",
            "created_date",
            "profile",
        ]
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = [
            "id",
            "last_login",
            "date_joined",
        ]

    def create(self, validated_data):
        user = super(GetUserSerilaizer, self).create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserUpdateSerilaizer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "is_active", "profile"]


class BatchSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField('get_user_name')
    class Meta:
        model = Batch
        fields = ["id","created_date","description","user","user_name"]

    #based on myuser profile under first_name
    
    def get_user_name(self,obj):
        return obj.user.profile.first_name



class FileSerializer(serializers.ModelSerializer):
    Description = serializers.SerializerMethodField('get_desc')
    created_date = serializers.SerializerMethodField('get_date')
    user_name = serializers.SerializerMethodField('get_username')
    user_id = serializers.SerializerMethodField('get_user_id')

    class Meta:
        model = File
        fields=['id','file_path','batch','Description','c_date','u_name','u_id']

    def get_desc(self,obj):
        return obj.batch.description
    
    def get_date(self,obj):
        return obj.batch.created_date

    def get_username(self,obj):
        return obj.batch.user.profile.first_name

    def get_user_id(self,obj):
        return obj.batch.user.profile.user_id



class BatchFileSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=200)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    files = serializers.ListField(
        child=serializers.FileField(
            max_length=100000, allow_empty_file=False, use_url=False
        )
    )   

    def create(self, validated_data):
        user_query_set = User.objects.all()
        images = validated_data.pop("files")
        batch = Batch.objects.create(**validated_data)
        for img in images:
            file = File.objects.create(file_path=img, batch=batch)
        return batch

    
    
