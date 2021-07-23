from rest_framework import serializers

from .models import Place, PlaceGalleryImage, Employee, School


class EmployeeSerializer (serializers.ModelSerializer):
    type = serializers.ReadOnlyField(source='get_type')

    class Meta:
        model = Employee
        fields = '__all__'


class PlaceGalleryImageSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = PlaceGalleryImage
        fields = ['id', 'sort_order', 'caption', 'place', 'image', 'url']
        # fields = '__all__'


class PlaceSerializer (serializers.ModelSerializer):
    gallery_images = PlaceGalleryImageSerializer(many=True, read_only=True) 
    # images_formated = PlaceGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Place
        fields = '__all__'
        # fields = ('id', 'gallery_images', 'images_formated',)


class SchoolSerializer (serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    anim_director = EmployeeSerializer(read_only=True)
    program_project_url = serializers.ReadOnlyField()

    class Meta:
        model = School
        fields = '__all__'
        # fields += ['program_project_url']

