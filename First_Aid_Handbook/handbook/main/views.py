from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Help, Lesion, HelpLesion, CustomUser
from .serializers import HelpSerializer, LesionSerializer, HelpLesionSerializer
from .minio import upload_image

def fixed_user():
    return CustomUser.objects.get_or_create(username='fixed_user')[0]

class HelpView(APIView):
    def get(self, request):
        helps = Help.objects.filter(is_active=True)
        serializer = HelpSerializer(helps, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HelpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HelpDetailView(APIView):
    def get(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        serializer = HelpSerializer(help)
        return Response(serializer.data)

    def put(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        serializer = HelpSerializer(help, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        help.is_active = False
        help.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LesionView(APIView):
    def get(self, request):
        lesions = Lesion.objects.exclude(status__in=['deleted', 'draft'])
        serializer = LesionSerializer(lesions, many=True)
        return Response(serializer.data)

class LesionDetailView(APIView):
    def get(self, request, pk):
        lesion = get_object_or_404(Lesion, pk=pk)
        serializer = LesionSerializer(lesion)
        return Response(serializer.data)

    def put(self, request, pk):
        lesion = get_object_or_404(Lesion, pk=pk)
        serializer = LesionSerializer(lesion, data=request.data, partial=True)
        
        if serializer.is_valid():
            new_status = request.data.get('status')
            if new_status and not self.validate_status(lesion.status, new_status):
                return Response({"error": "Invalid status transition"}, status=400)
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def validate_status(self, old_status, new_status):
        transitions = {
            'draft': ['formed', 'deleted'],
            'formed': ['completed', 'rejected'],
            'completed': [],
            'rejected': [],
            'deleted': []
        }
        return new_status in transitions.get(old_status, [])

class LesionDraftView(APIView):
    def get(self, request):
        user = fixed_user()
        draft = Lesion.objects.filter(creator=user, status='draft').first()
        if not draft:
            draft = Lesion.objects.create(creator=user, status='draft')
        serializer = LesionSerializer(draft)
        return Response(serializer.data)

class HelpLesionView(APIView):
    def post(self, request, lesion_id):
        lesion = get_object_or_404(Lesion, pk=lesion_id)
        serializer = HelpLesionSerializer(data=request.data)
        
        if serializer.is_valid():
            if lesion.status != 'draft':
                return Response({"error": "Can only add to draft lesions"}, status=400)
            
            serializer.save(lesion=lesion)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, lesion_id, help_id):
        relation = get_object_or_404(HelpLesion, lesion_id=lesion_id, help_id=help_id)
        relation.delete()
        return Response(status=204)

class ImageUploadView(APIView):
    def post(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        image = request.FILES.get('image')
        
        if not image:
            return Response({"error": "No image provided"}, status=400)
        
        url = upload_image(help, image)
        help.image_url = url
        help.save()
        
        return Response({"image_url": url}, status=200)