# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# image_manager:
#    This module allow to manage images globaly. It
#    allow to make basic actions on images. It can 
#    manage all types of images.
#
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import basic modules
import os
import crypt
import yaml
import logging
import atexit
import inspect
import csv
import subprocess
import sys
from enum import Enum, auto

# Import diskless modules
from utils import *
from kernel_manager import KernelManager


class ImageManager:
    """Class to manage images of the diskless tool."""

    # Modules location
    MODULES_PATH = '/lib/python3.6/site-packages/diskless/modules'

    class ImageStatus(Enum):
        """Enumeration that represents the status of an image. An image can have three status. We don't care about enumaration members values."""
        # Value is auto because we don't care about it
        IN_CREATION = auto()
        CORRUPTED = auto()
        CREATED = auto()

    @staticmethod
    def get_class(class_name):
        """Get a diskless image class object by it's class name. The class must be in a diskless module.

        :param class_name: The class name
        :type class_name: str
        :raises ValueError: When there is no class corresponding to class_name to load in modules.
        :return: `_class` the class of the image
        :rtype: Class as object
        """
        # Get modules files names
        module_file_names = os.listdir(ImageManager.MODULES_PATH)

        # Get only module names
        module_names = [module_name.replace('.py', '') for module_name in module_file_names if not 'base' in module_name and 'module' in module_name]
    
        # Search for the class in all modules
        for module_name in module_names:

            # Import the module of the image
            module = __import__(module_name)

            # Get only classes of the module
            class_members = inspect.getmembers(module, inspect.isclass)
        
            for member in class_members:
                if class_name in member:
                    # Import the image class from the module
                    _class = getattr(module, class_name)
                    return _class

        raise ValueError('No class ' + class_name + ' fouded in modules.')

    @staticmethod
    def get_image_names():
        """Get the name of all existing images base directories inside the Image.IMAGES_DIRECTORY directory.

        :return: `image_list` if there is at least one image, `None` overwise
        :rtype: list of str
        """
        # Get images names
        image_list = [image for image in os.listdir(Image.IMAGES_DIRECTORY)]

        # If there are images
        if image_list:
            return image_list
        # If there are no images
        else:
            return None

    @staticmethod
    def get_image_data_path(image_name):
        """Get image image_data file path. This file is inside the image base direcrory in Image.IMAGES_DIRECTORY.

        :param image_name: The name of the image
        :type image_name: str
        :return: `image_data_path` if there is an image_data_file for this image, `None` overwise
        :rtype: str
        """
        # Set image path with the name
        image_path = Image.IMAGES_DIRECTORY + '/' + image_name
        # Get image data file to access image data
        image_data_path = image_path + '/image_data.yml'

        # If the image data file exists
        if os.path.isfile(image_data_path):
            # Return the image data file
            return image_data_path
        else:
            return None

    @staticmethod
    def get_created_image(image_name):
        """Get a created image object by it's name. Each image can be loaded using it's implicit image_data file.

        :param image_name: The name of a ImageManager.ImageStatus.CREATED image
        :type image_name: str
        :return: `image`
        :rtype: Image
        :raises ValueError: When image_name not corresponding to a ImageManager.ImageStatus.CREATED image
        :raises ValueError: When image class cannot be loaded
        :raises FileNotFoundError: When image_data file cannot be found
        """

        # Check if it is a created image
        if ImageManager.get_image_status(image_name) is not ImageManager.ImageStatus.CREATED:
            raise ValueError('Image ' + image_name + ' is not a created image.')
        
        # Get image image_data file, this file contain all attributs of the image
        image_data_file = ImageManager.get_image_data_path(image_name)
        
        # Check if the image_data file of the image exists
        if not image_data_file: 
            raise ValueError('No founded image_data file for image ' + image_name)

        try:
            # Get the image module and class to create image by its name with it's class constructor
            with open(image_data_file, 'r') as f:
                # Get image datas
                image_dict = yaml.safe_load(f)
                # Get image class
                image_class = image_dict['image_data']['image_class']

            # Import the image class from the image_class name
            image_class = ImageManager.get_class(image_class)

            # Use the constructor of the image class to create fresh image object by it's name
            image = image_class(image_name)

            # Return constructed image object
            return image

        except FileNotFoundError as err:
            raise FileNotFoundError('Error loading image_data file for image ' + image_name)
        except ValueError as err:
            raise ValueError ('Enable to load image class for image ' + image_name + 'from image data file ' + image_data_file)

    # Get all images objects
    @staticmethod
    def get_created_images():
        """Get a created image object by it's name. Each image can be loaded with it's implicit image_data file that's contains all it's attributs.

        :return: `created_images_list` if there are created images, `None` overwise.
        :rtype: list of Image
        """
        # Create empty images list
        created_images_list = []

        # Get all images names
        images_names = ImageManager.get_image_names()
        
        # If there are images
        if images_names:

            # Get only created images names
            created_images_names = [image_name for image_name in images_names if ImageManager.get_image_status(image_name) is ImageManager.ImageStatus.CREATED]
            
            # If there are created images
            if created_images_names:
                for image_name in created_images_names:

                    try:
                        # Load corresponding image to access the image display_info method
                        image = ImageManager.get_created_image(image_name)
                        created_images_list.append(image)

                    # ImageManager.get_created_image method can generate an exception
                    except Exception as e:
                        # Don't add the image to the list and display exception
                        logging.error(e)
                
                return created_images_list
        
        return None

    @staticmethod
    def remove_image(image):
        """Remove an existing image

        :param image: A created image object
        :type image: Image
        """
        # Use image object method to delete all related files
        image.remove_files()
        
    @staticmethod
    def is_image(image_name):
        """Check if an image_name correspond to an image 

        :param image_name: A created image object
        :type image_name: str
        :return: `True` if there is an image that correspond to the name, `False` overwise
        :rtype: bool
        """
        # If there is images
        if ImageManager.get_image_names():
            # If an image with the same name already exist
            if image_name in ImageManager.get_image_names():
                return True
        
        return False

    @classmethod
    def clean_intallations(cls):
        """Clean all corrupted images."""
        logging.debug("Start cleaning images.")

        # Get ongoing installations dictionary
        ongoing_intallations = cls.get_ongoing_installations()

        # For each image in the ongoing installation file
        for image_name in ongoing_intallations.keys():

            # If the image status is 'CORRUPTED', clean the image
            if cls.get_image_status(image_name) == cls.ImageStatus.CORRUPTED:

                logging.warning('Image \'' + image_name + '\' corrupted, trying to clean image')

                # Importing image class for cleaning
                image_class = cls.get_class(ongoing_intallations[image_name]['image_class'])

                # Use the image class clean static method to clean image
                image_class.clean(image_name)

                # Unregister image from ongoing installations
                cls.unregister_installation(image_name)

                logging.warning('Image \'' + image_name + '\' cleaned\n')

    @classmethod
    def clean_intallation(cls, image_name):
        """Clean an specific image.

        :param image_name: The name of the created or corrupted image object to clean
        :type image_name: str
        """

        # The cleaning method depends on the image status
 
        # Cannot clean an in creation image
        if cls.get_image_status(image_name) == ImageManager.ImageStatus.IN_CREATION:
            raise ValueError('Cannot remove an in creation image')

        # Cleaning a corrupted image
        elif cls.get_image_status(image_name) == ImageManager.ImageStatus.CORRUPTED:

            # Get ongoing installations dictionary
            ongoing_intallations = cls.get_ongoing_installations()

            # Importing image class from dictionary for cleaning
            image_class = cls.get_class(ongoing_intallations[image_name]['image_class'])

            # Use the image class clean static method to clean image
            image_class.clean(image_name)

            # Unregister image from ongoing installations
            cls.unregister_installation(image_name)

        # Cleaning a created image
        elif cls.get_image_status(image_name) == ImageManager.ImageStatus.CREATED:
            
            # Get the created image
            image = ImageManager.get_created_image(image_name)

            # Get the created image class
            image_class = cls.get_class(image.image_class)

            # Use class to clean the image
            image_class.clean(image_name)

        logging.info('Image ' + image_name + ' cleaned')

        
    @classmethod
    def get_image_status(cls, image_name):
        """Get the status of an image

        :param image_name: An image name
        :type image_name: str
        :return: 
        `ImageManager.ImageStatus.IN_CREATION` if the image is currently in creation by a process,
        `ImageManager.ImageStatus.CORRUPTED` if the image is in ongoing_installation dictionary but there is no process to finishing created it,
        `ImageManager.ImageStatus.CREATED` if the image has finished is creation successfully.
        :rtype: ImageManager.ImageStatus
        """
        # Get ongoing installations dictionary
        ongoing_intallations = cls.get_ongoing_installations()

        # If image_name is in the ongoing installations dictionary
        if image_name in ongoing_intallations:

            # Get the pid of the process that install image
            # In fact multiple instance of the diskless program can create image simultaneously.
            # So we need the pid of the program that has create the image
            image_pid = ongoing_intallations[image_name]['pid']
            
            try:
                # Try to get image creator instance pid
                subprocess.check_output("ps -A -o pid | grep -w " + str(image_pid), shell=True)
                # An image is in creation if there is in the ongoing_intallations dictionary 
                # and there is a process instance to finishing created it.
                return cls.ImageStatus.IN_CREATION

            # If there is not running process for image creator instance pid
            except subprocess.CalledProcessError:
                # An image is corrupted when it is in the ongoing_intallations dictionary 
                # but there is no process instance to finishing created it.
                return cls.ImageStatus.CORRUPTED

        # The not in ongoing installation
        else:
            # Try to create image 
            return cls.ImageStatus.CREATED

    @classmethod
    def get_installation_pid(cls, image_name):
        """Get the pid of the process that as started image creation.

        :param image_name: The image name
        :type image: str
        :return: `pid` If the image is present on the ongoing_intallations dictionary, `None` overwise
        :rtype: str
        """
        # Get ongoing_installations dictionary
        ongoing_intallations = cls.get_ongoing_installations()

        # if image_name is in the the ongoing_installations dictionary
        if image_name in ongoing_intallations.keys():
            # Return image creation process pid
            return ongoing_intallations[image_name]['pid']
        else:
            return None

    @classmethod
    def register_installation(cls, image_name, image_class):
        """Add the image to the ongoing_intallations dictionary

        :param image_name: The image name
        :type image_name: str
        :param image_class: The class of the image
        :type image_class: str
        """
        # Get ongoing_intallations dictionary
        ongoing_intallations = cls.get_ongoing_installations()
        # Add image to dictionary
        ongoing_intallations[image_name] = {'pid': os.getpid(), 'image_class': image_class}
        # Write ongoing_intallations dictionary
        cls.set_ongoin_installations(ongoing_intallations)

    @classmethod
    def unregister_installation(cls, image_name):
        """Remove the image from the ongoing_intallations dictionary

        :param image_name: The image name
        :type image_name: str
        """
        # Get ongoing_intallations dictionary
        ongoing_intallations = cls.get_ongoing_installations()
        # Delete image from dictionary
        del (ongoing_intallations[image_name])
        # Write ongoing_intallations dictionary
        cls.set_ongoin_installations(ongoing_intallations)

    @classmethod
    def get_ongoing_installations(cls):
        """Get ongoing_intallations dictionary content from the /diskless/installations.yml file

        :return: `ongoing_intallations`
        :rtype: dict
        :raises FileNotFoundError: If cannot load /diskless/installations.yml file
        """
        # Create fresh dictionary
        ongoing_intallations = {}

        try:
            # For installations.yml file instance
            with open('/var/lib/diskless/installations.yml', 'r') as f:
                # Get file content as dictionary
                ongoing_intallations = yaml.safe_load(f)

                # Replace ongoing_installations if None
                if ongoing_intallations == None:
                    ongoing_intallations = {}

            return ongoing_intallations

        except FileNotFoundError as e:
            raise FileNotFoundError('Enable to load /diskless/installations.yml file')

    # Set ongoing_intallations dictionary content
    @classmethod
    def set_ongoin_installations(cls, ongoing_intallations):
        """Set ongoing_intallations dictionary content

        :param ongoing_intallations: The dictionary to write inside /diskless/installations.yml file
        :type ongoing_intallations: dict
        :raises FileNotFoundError: If cannot load /diskless/installations.yml file
        """
        try:
            # For installations.yml file instance
            with open('/var/lib/diskless/installations.yml', 'w') as f:
                # Write ongoing_intallations dictionary in the installations.yml file
                yaml.dump(ongoing_intallations, f, default_flow_style=False)

        except FileNotFoundError as e:
            raise FileNotFoundError('File /diskless/installations.yml cannot be writen.')


    ######################
    ## CLI reserved part##
    ######################

    # Use a specific image module
    @staticmethod
    def cli_use_modules():
        """The method for using modules with cli interface"""

        # Get available modules
        modules = os.listdir(ImageManager.MODULES_PATH)

        # Get only module name to display
        # We have to modif name because module naming convention is:
        #   "<image_type>_module.py"
        module_names = [module.replace('_module.py', '') for module in modules if not 'base' in module and 'module' in module]
        
        # Select desired image type in the list
        printc('[+] Select the module you want to use:\n', CBLUE)
        selected_module_name = select_from_list(module_names)

        # Convert image type into it's corresponding module name
        selected_module =  selected_module_name + '_module'

        # Import the module
        module = __import__(selected_module)

        # Launch module menu
        module.cli_menu()

    @staticmethod
    def cli_select_created_image():
        """Select an image from the list of created images"""
        # Get created images 
        images_list = ImageManager.get_created_images()
        
        if images_list:
            # Get created images names
            images_names_list = [image.name for image in images_list]
            
            # If there are images
            if images_names_list:
                printc('[+] Select the image:\n', CBLUE)
                # Allow the user to select an image name from the list
                return select_from_list(images_names_list)

        raise UserWarning('No image to select.')

    @staticmethod
    def cli_display_images():
        """Display informations about all images"""
        # Get list of image names
        image_names = ImageManager.get_image_names()

        # If there are images
        if image_names:
            # For each image name
            for image_name in image_names:

                # Get the status of image
                image_status = ImageManager.get_image_status(image_name)

                if image_status == ImageManager.ImageStatus.CREATED:
                    printc('   [CREATED]', CGREEN)
                    image = ImageManager.get_created_image(image_name)
                    image.cli_display_info()

                elif image_status == ImageManager.ImageStatus.IN_CREATION:
                    printc('   [IN_CREATION]', CORANGE_BLINK)
                    pid = ImageManager.get_installation_pid(image_name)
                    print(' • Image name: ' + image_name + '\n   Installation pid: ' + str(pid))

                elif image_status == ImageManager.ImageStatus.CORRUPTED:
                    printc('   [CORRUPTED]', CRED)
                    print(' • Image name: ' + image_name)

                print('')

        else:
            raise UserWarning('No images.')


# Add the modules directory path to importation path 
sys.path.append(ImageManager.MODULES_PATH)
# When import module base_module at the end because we need to add first 
# ImageManager.MODULES_PATH ImageManager attribute to importation path 
from base_module import Image


                   

               
 
        
       

