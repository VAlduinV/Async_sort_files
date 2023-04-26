import os
import shutil
import string
import unicodedata
from concurrent.futures import ThreadPoolExecutor
import logging

# Встановлюємо рівень логування на рівень DEBUG
logging.basicConfig(level=logging.DEBUG)

# Define the allowed extensions for each file category
IMAGE_EXTENSIONS = ('JPEG', 'PNG', 'JPG', 'SVG')
VIDEO_EXTENSIONS = ('AVI', 'MP4', 'MOV', 'MKV')
DOCUMENT_EXTENSIONS = ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
MUSIC_EXTENSIONS = ('MP3', 'OGG', 'WAV', 'AMR')
ARCHIVE_EXTENSIONS = ('ZIP', 'GZ', 'TAR')
PROGRAMMER_EXTENSIONS = ('py', 'cpp', 'm')


class FileSorter:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.known_extensions = set()
        self.unknown_extensions = set()
        self.images = []
        self.videos = []
        self.documents = []
        self.programmers = []
        self.music = []
        self.archives = []
        self.root = None
        self.logger = logging.getLogger(__name__) # Створюємо об'єкт логування

    def normalize(self, filename):
        # Transliterate Cyrillic characters to Latin and replace invalid characters with '_'
        valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
        filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
        return ''.join(c for c in filename if c in valid_chars)

    def sort_files(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for root, dirs, files in os.walk(self.folder_path):
                # Ignore certain folders
                dirs[:] = [d for d in dirs if
                           d not in ['images', 'video', 'audio', 'programmers', 'documents', 'archives']]

                # Process files in parallel using threads
                results = []
                for file in files:
                    file_path = os.path.join(root, file)
                    results.append(executor.submit(self.process_file, file_path))

                # Wait for all threads to complete
                for future in results:
                    future.result()

        # Unpack and sort the files in the archives folder
        self.sort_archives()
        self.logger.info("Files have been sorted.")
        self.logger.info(f"Known extensions: {self.known_extensions}")
        self.logger.info(f"Unknown extensions: {self.unknown_extensions}")
        self.logger.info(f"Images: {self.images}")
        self.logger.info(f"Videos: {self.videos}")
        self.logger.info(f"Documents: {self.documents}")
        self.logger.info(f"Programmers: {self.programmers}")
        self.logger.info(f"Music: {self.music}")
        self.logger.info(f"Archives: {self.archives}")

    def process_file(self, file_path):
        extension = file_path.split('.')[-1].upper()

        # Add the extension to the known_extensions list
        self.known_extensions.add(extension)

        # Determine the category of the file
        if extension in IMAGE_EXTENSIONS:
            self.images.append(file_path)
            dest_folder = 'images'
        elif extension in VIDEO_EXTENSIONS:
            self.videos.append(file_path)
            dest_folder = 'video'
        elif extension in DOCUMENT_EXTENSIONS:
            self.documents.append(file_path)
            dest_folder = 'documents'
        elif extension in PROGRAMMER_EXTENSIONS:
            self.programmers.append(file_path)
            dest_folder = 'programmers'
        elif extension in MUSIC_EXTENSIONS:
            self.music.append(file_path)
            dest_folder = 'audio'
        elif extension in ARCHIVE_EXTENSIONS:
            self.archives.append(file_path)
            dest_folder = 'archives'
        else:
            self.unknown_extensions.add(extension)
            dest_folder = 'unknown'

        # Normalize the filename
        normalized_filename = self.normalize(os.path.basename(file_path))

        # Create the destination folder if it doesn't exist
        dest_folder_path = os.path.join(self.folder_path, dest_folder)
        os.makedirs(dest_folder_path, exist_ok=True)

        # Move the file to the destination folder
        dest_file_path = os.path.join(dest_folder_path, normalized_filename)
        shutil.move(file_path, dest_file_path)
        self.logger.info(f"Moved {file_path} to {dest_file_path}")

    def sort_archives(self):
        # Sort and extract files from archives
        for archive_path in self.archives:
            dest_folder_path = os.path.join(self.folder_path, 'archives')
            with shutil.unpack_archive(archive_path, dest_folder_path) as extracted_files:
                for extracted_file in extracted_files:
                    self.process_file(extracted_file)
            os.remove(archive_path)
            self.logger.info(f"Removed {archive_path} after extraction")

    def sort(self):
        self.root = self.folder_path  # Save the root value in the FileSorter object
        self.sort_files()


if __name__ == '__main__':
    folder_path = input(f'Enter the folder path: ')
    sorter = FileSorter(folder_path)
    sorter.sort()
