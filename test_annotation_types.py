#!/usr/bin/env python
"""
Script to test the annotation type creation and deletion functionality
"""
import os
import sys
import django
import json

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyProject.settings')
django.setup()

from django.contrib.auth.models import User
from rawdocs.models import AnnotationType, Annotation
from expert.views import create_annotation_type_ajax, delete_annotation_type_ajax
from django.test import RequestFactory
from django.http import JsonResponse

def test_create_annotation_type():
    """Test creating a new annotation type"""
    print("\n=== Testing Annotation Type Creation ===")
    
    # Get an expert user
    try:
        expert_user = User.objects.filter(groups__name="Expert").first()
        if not expert_user:
            print("❌ No expert user found. Creating one...")
            from django.contrib.auth.models import Group
            expert_user = User.objects.create_user(username='test_expert', password='test123')
            expert_group, created = Group.objects.get_or_create(name='Expert')
            expert_user.groups.add(expert_group)
            print(f"✅ Created expert user: {expert_user.username}")
        else:
            print(f"✅ Found expert user: {expert_user.username}")
    except Exception as e:
        print(f"❌ Error finding/creating expert user: {e}")
        return False

    # Create a mock request
    factory = RequestFactory()
    request_data = {
        'display_name': 'Test Annotation Type',
        'name': 'test_annotation_type'
    }
    
    request = factory.post(
        '/expert/api/create-annotation-type/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = expert_user
    
    # Call the function
    try:
        response = create_annotation_type_ajax(request)
        response_data = json.loads(response.content)
        
        if response_data.get('success'):
            print(f"✅ Successfully created annotation type: {response_data.get('message')}")
            return response_data.get('annotation_type', {}).get('id')
        else:
            print(f"❌ Failed to create annotation type: {response_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during creation: {e}")
        return False

def test_delete_annotation_type(annotation_type_name):
    """Test deleting an annotation type"""
    print(f"\n=== Testing Annotation Type Deletion: {annotation_type_name} ===")
    
    # Get an expert user
    expert_user = User.objects.filter(groups__name="Expert").first()
    
    # Create a mock request
    factory = RequestFactory()
    request_data = {
        'annotation_type_name': annotation_type_name
    }
    
    request = factory.post(
        '/expert/api/delete-annotation-type/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = expert_user
    
    # Call the function
    try:
        response = delete_annotation_type_ajax(request)
        response_data = json.loads(response.content)
        
        if response_data.get('success'):
            print(f"✅ Successfully deleted annotation type: {response_data.get('message')}")
            return True
        else:
            print(f"❌ Failed to delete annotation type: {response_data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during deletion: {e}")
        return False

def show_existing_annotation_types():
    """Show all existing annotation types"""
    print("\n=== Existing Annotation Types ===")
    annotation_types = AnnotationType.objects.all()
    
    if annotation_types.exists():
        for ann_type in annotation_types:
            annotations_count = Annotation.objects.filter(annotation_type=ann_type).count()
            print(f"- {ann_type.display_name} (name: {ann_type.name}, id: {ann_type.id}) - Used by {annotations_count} annotations")
    else:
        print("No annotation types found.")
    
    return annotation_types.count()

if __name__ == "__main__":
    print("🧪 Testing Annotation Type Management Functions")
    
    # Show existing types
    initial_count = show_existing_annotation_types()
    
    # Test creation
    created_id = test_create_annotation_type()
    
    if created_id:
        # Show types after creation
        print(f"\nAfter creation (should be {initial_count + 1} types):")
        show_existing_annotation_types()
        
        # Test deletion
        test_delete_annotation_type('test_annotation_type')
        
        # Show types after deletion
        print(f"\nAfter deletion (should be {initial_count} types):")
        final_count = show_existing_annotation_types()
        
        if final_count == initial_count:
            print("\n✅ All tests passed! Create and delete functions work correctly.")
        else:
            print(f"\n❌ Test failed. Expected {initial_count} types, got {final_count}")
    else:
        print("\n❌ Creation test failed, skipping deletion test.")