import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from django.conf import settings
from .models import Plugin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.core.files.storage import FileSystemStorage
# from .utils import update_plugins


# VIEWS ############################################################################################
def plugin_list(request: HttpRequest) -> HttpResponse:
    # Update plugins before rendering the plugin list
    update_plugins()

    plugins = Plugin.objects.all()
    return render(request, 'plugin_list.html', {'plugins': plugins})

def download_plugin(request: HttpRequest, plugin_id: int) -> HttpResponse:
    plugin = get_object_or_404(Plugin, pk=plugin_id)
    # Increment the download count if DOWNLOAD_COUNTER is enabled
    if settings.DOWNLOAD_COUNTER:
        plugin.downloads += 1
        plugin.save()
    # Redirect to the download URL
    return redirect(plugin.download_url)

# Add view function to handle plugin upload
def upload_plugin(request):
    if request.method == 'POST' and request.FILES['plugin_zip']:
        plugin_zip = request.FILES['plugin_zip']
        # Save the uploaded plugin zip file to the designated directory
        fs = FileSystemStorage(location=settings.PLUGIN_ZIP_UPLOAD_DIR)
        filename = fs.save(plugin_zip.name, plugin_zip)
        # Optionally, update the database with the file path or other relevant information
        # For example:
        # Plugin.objects.create(zip_path=filename, ...)
        return redirect('plugin_list')
    return render(request, 'upload_plugin.html')


# HELPERS ##########################################################################################
def update_plugins():
    plugins_dir = os.path.join(settings.BASE_DIR, 'qgs_plugins', 'plugins')
    # print(plugins_dir)

    if len(os.listdir(plugins_dir)) == 0:
        return
    
    for plugin_file in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, plugin_file)
        # print(plugin_path)

        if os.path.isfile(plugin_path) and plugin_file.endswith('.zip'):
            metadata = parse_metadata(plugin_path)
            print(metadata)
            
            if metadata:
                existing_plugin = Plugin.objects.filter(name=metadata['name']).first()
                
                if existing_plugin:
                    existing_version = existing_plugin.version
                    new_version = metadata['version']
                    
                    if compare_versions(new_version, existing_version) > 0:
                        update_existing_plugin(existing_plugin, metadata)
                else:
                    create_new_plugin(metadata)


def parse_metadata(zip_file):
    # metadata_file = 'metadata.txt'
    # extract plugin name from zip file (last element of the path)
    plugin_name = os.path.basename(zip_file).split('\\')[-1].split('.')[0]
    metadata_file = plugin_name + '/metadata.txt' 
    # print(metadata_file)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:

        # print(zip_ref.namelist())
        if metadata_file in zip_ref.namelist():

            with zip_ref.open(metadata_file) as file:
                # print(file)
                data = file.read().decode('utf-8')
                # print(data)
                metadata = {}
                
                for line in data.splitlines():
                    try:
                        key, value = line.split('=', 1)
                        metadata[key.strip()] = value.strip()
                    except ValueError:
                        # not a key-value pair
                        pass
                return metadata
    return None


def update_existing_plugin(existing_plugin, metadata):
    existing_plugin.version = metadata.get('version', existing_plugin.version)
    existing_plugin.description = metadata.get('description', existing_plugin.description)
    existing_plugin.about = metadata.get('about', existing_plugin.about)
    existing_plugin.qgis_minimum_version = metadata.get('qgisMinimumVersion', existing_plugin.qgis_minimum_version)
    existing_plugin.qgis_maximum_version = metadata.get('qgisMaximumVersion', existing_plugin.qgis_maximum_version)
    existing_plugin.homepage = metadata.get('homepage', existing_plugin.homepage)
    existing_plugin.file_name = os.path.basename(existing_plugin.zip_path)
    existing_plugin.download_url = metadata.get('downloadUrl', existing_plugin.download_url)
    existing_plugin.uploaded_by = metadata.get('author', existing_plugin.uploaded_by)
    existing_plugin.create_date = datetime.now()
    existing_plugin.update_date = datetime.now()
    existing_plugin.experimental = metadata.get('experimental', False)
    existing_plugin.deprecated = metadata.get('deprecated', False)
    existing_plugin.tracker = metadata.get('tracker', '')
    existing_plugin.repository = metadata.get('repository', '')
    existing_plugin.tags = metadata.get('tags', '')
    existing_plugin.external_dependencies = metadata.get('externalDependencies', '')
    existing_plugin.server = metadata.get('server', False)
    existing_plugin.downloads = metadata.get('downloads', 0)
    existing_plugin.save()


def create_new_plugin(metadata):
    Plugin.objects.create(
        name=metadata.get('name', 'ExamplePlugin'),
        version=metadata.get('version', '2.0.3'),
        description=metadata.get('description', 'An example plugin shipped with phpQGISrepository'),
        about=metadata.get('about', 'This simple plugin is created as an example for phpQGISrepository.'),
        qgis_minimum_version=metadata.get('qgisMinimumVersion', '2.14'),
        qgis_maximum_version=metadata.get('qgisMaximumVersion', '3.98'),
        homepage=metadata.get('homepage', 'https://gitlab.com/GIS-projects/phpQGISrepository'),
        file_name=metadata.get('file_name', 'ExamplePlugin.zip'),
        download_url=metadata.get('download_url', ''),
        uploaded_by=metadata.get('uploaded_by', ''),
        create_date=datetime.now(),
        update_date=datetime.now(),
        experimental=metadata.get('experimental', False),
        deprecated=metadata.get('deprecated', False),
        tracker=metadata.get('tracker', ''),
        repository=metadata.get('repository', ''),
        tags=metadata.get('tags', ''),
        external_dependencies=metadata.get('external_dependencies', ''),
        server=metadata.get('server', False),
        downloads=metadata.get('downloads', 0)
    )


def compare_versions(version1, version2):
    # Implement your version comparison logic here
    # For simplicity, assume version strings are in x.y.z format
    v1 = [int(x) for x in version1.split('.')]
    v2 = [int(x) for x in version2.split('.')]
    
    if v1 > v2:
        return 1
    elif v1 < v2:
        return -1
    else:
        return 0
