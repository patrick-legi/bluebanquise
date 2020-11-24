# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# demo module:
#   A module to demonstate how to create customized diskless images classes.
#
# 1.2.0: Role update. David Pieters <davidpieters22@gmail.com>
# 1.1.0: Role update. Benoit Leveugle <benoit.leveugle@gmail.com>, Bruno Travouillon <devel@travouillon.fr>
# 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
#
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import base modules
import os
import shutil

# Import diskless modules
from diskless.base_module import Image
from diskless.utils import Color, printc


class DemoImage(Image):
    """This module will allow you to understand how to create your own image class.\
       Images created with this class are not real diskless images."""

    # Class constructor
    # You can see that only name is a mandatory argument. To create an already existing image, call the constructor whith only the image name.
    # To create a new image you must enter all arguments.
    #                                ↴                       ↴
    def __init__(self, name, my_message=None, useless_argument=None):
        super().__init__(name, my_message, useless_argument)

    #                               V             V  <- You can see the arguments relation
    # Create demo image             V             V
    def create_new_image(self, my_message, useless_argument):
        # Create the 'my_message attribute'
        self.my_message = my_message
        self.generate_files()
        printc("Image created ! Check images list to look at it.", Color.RED)

    def generate_files(self):
        self.create_image_folders()
        self.generate_file_system()
        # The 'my_message attribute' will be saved in image_data file when registering.
        # You will see it when listing images after demo image creation.
        self.register_image()

    def create_image_folders(self):
        # Create a folder just for the exemple.
        os.makedirs('/diskless/demo_directory_' + self.name)

    # This function will help us to understand the difference between clean and remove methods
    def generate_file_system(self):
        # Create a file to remove
        f = open('/diskless/demo_file_to_remove_' + self.name + '.txt', 'a')
        f.write("This file will be removed throughout normal image generation !")
        f.close()

        print('Would you like to corrupt this image generation?(yes/no)')
        choice = input('-->: ')
        if choice == 'yes':
            exit()  # <- Fake a program crash
        # Exiting without removed file_to_remove.txt file.
        # Therefore, the file will be removed by the clean method.
        elif choice != 'no':
            raise UserWarning('Not a valid input.')

        # Else, continue normal process...

        # Remove the file_to_remove file is the normal image creation process
        os.remove('/diskless/demo_file_to_remove_' + self.name + '.txt')

    def remove_files(self):
        # Remove the image files when the image was properly created
        super().remove_files()
        shutil.rmtree('/diskless/demo_directory_' + self.name)

    # Clean all image files without image object when an image is corrupted
    @staticmethod
    def clean(image_name):
        # Cleaning image base directory
        if os.path.isdir(Image.IMAGES_DIRECTORY + image_name):
            shutil.rmtree(Image.IMAGES_DIRECTORY + image_name)

        # Cleaning all other related files and directories...

        if os.path.isdir('/diskless/demo_directory_' + image_name):
            shutil.rmtree('/diskless/demo_directory_' + image_name)

        # We need to try to delete the demo_file.txt file in the clean method.
        # In fact the generation of the demo image can be halted before that the
        # normal process of DemoImage image creation removed demo_file.txt.
        if os.path.isfile('/diskless/demo_file_to_remove_' + image_name + '.txt'):
            os.remove('/diskless/demo_file_to_remove_' + image_name + '.txt')

    @staticmethod
    def get_boot_file_template():
        """Get the class boot file template.
        This method must be redefined in all Image subclasses."""
        return 'Useless bootfie content'


def cli_menu():
    """This method is needed for all diskless module to be available by cli interface."""

    printc('\n == Welcome to demo image module == \n', Color.GREEN)

    print('1 - Create my demo image')

    print('\n Select an action')
    main_action = input('-->: ')
    print('')

    if main_action == '1':

        printc('Give a name to your demo image:', Color.GREEN)
        demo_name = input('-->: ').replace(' ', '')

        printc('Give a message for your demo image:', Color.GREEN)
        demo_message = input('-->: ')

        # Create a DemoImage image
        DemoImage(demo_name, demo_message)

    # Bad entry
    else:
        raise UserWarning('\'' + main_action + '\' is not a valid entry. Please enter another value.')