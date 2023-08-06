import os
import shutil
from . import utils


class Downloader():
    download_warning = '''You are trying to download an already downloaded dataset.
        This message may have happened to due interrupted download or extract.
        To force the download use the `force=True` keyword such as
        get_data(..., force=True) or download(..., force=True).
        '''
    download_mark_name = 'already_downloaded'
        
    def get_data(self, root, force=False, **kwargs):
        name = self.__class__.__name__
        
        already_downloaded = self.check_downloaded_mark(root)
        if already_downloaded and not force:
            print('DATASET %s: DOWNLOADING STARTED.' % name)
            print(self.download_warning)
        else:
            print('DATASET %s: DOWNLOADING STARTED.' % name)
            self.download(root, force=force, **kwargs)
            print('DATASET %s: EXTRACTING STARTED.' % name)
            self.extract(root,  **kwargs)
            print('DATASET %s: FINISHED.\n' % name)

    def download(self, root, force=False, **kwargs):
        name = self.__class__.__name__

        already_downloaded = self.check_downloaded_mark(root)
        if already_downloaded and not force:
            print('DATASET %s: DOWNLOADING STARTED.' % name)            
            print(self.download_warning)
        else:
            self.remove_download_mark(root)
            with utils.data_directory(root):
                self._download(**kwargs)
            self.add_downloaded_mark(root)
    
    def extract(self, root, **kwargs):
        with utils.data_directory(root):
            self._extract(**kwargs)

    def _download(self, *args, **kwargs):
        raise NotImplemented('Needs to be implemented by subclasses.')
    
    def _extract(self, *args, **kwargs):
        raise NotImplemented('Needs to be implemented by subclasses.')

    def check_downloaded_mark(self, root):
        file_name = os.path.join(root, self.download_mark_name)
        return os.path.exists(file_name)

    def add_downloaded_mark(self, root):
        if not os.path.exists(root):
            os.makedirs(root)
        file_name = os.path.join(root, self.download_mark_name)
        open(file_name, 'a').close()

    def remove_download_mark(self, root):
        file_name = os.path.join(root, self.download_mark_name)
        if os.path.exists(file_name):
            os.remove(file_name)

class AAUZebraFish(Downloader):
    archive = 'aau-zebrafish-reid.zip'

    def _download(self):
        command = f"datasets download -d 'aalborguniversity/aau-zebrafish-reid'"
        exception_text = '''Kaggle must be setup.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#aauzebrafish'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class AerialCattle2017(Downloader):
    url = 'https://data.bris.ac.uk/datasets/tar/3owflku95bxsx24643cybxu3qh.zip'
    archive = '3owflku95bxsx24643cybxu3qh.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class ATRW(Downloader):
    url = 'https://github.com/cvwc2019/ATRWEvalScript/archive/refs/heads/main.zip'
    archive = 'main.zip'
    downloads = [
        # Wild dataset (Detection)
        ('https://lilablobssc.blob.core.windows.net/cvwc2019/test/atrw_detection_test.tar.gz', 'atrw_detection_test.tar.gz'),

        # Re-ID dataset
        ('https://lilablobssc.blob.core.windows.net/cvwc2019/train/atrw_reid_train.tar.gz', 'atrw_reid_train.tar.gz'),
        ('https://lilablobssc.blob.core.windows.net/cvwc2019/train/atrw_anno_reid_train.tar.gz', 'atrw_anno_reid_train.tar.gz'),
        ('https://lilablobssc.blob.core.windows.net/cvwc2019/test/atrw_reid_test.tar.gz', 'atrw_reid_test.tar.gz'),
        ('https://lilablobssc.blob.core.windows.net/cvwc2019/test/atrw_anno_reid_test.tar.gz', 'atrw_anno_reid_test.tar.gz'),
    ]

    def _download(self):
        for url, archive in self.downloads:
            utils.download_url(url, archive)
        # Evaluation scripts
        utils.download_url(self.url, self.archive)

    def _extract(self):
        for url, archive in self.downloads:
            archive_name = archive.split('.')[0]
            utils.extract_archive(archive, archive_name, delete=True)
        # Evaluation scripts
        utils.extract_archive(self.archive, 'eval_script', delete=True)

class BelugaID(Downloader):
    url = 'https://lilablobssc.blob.core.windows.net/liladata/wild-me/beluga.coco.tar.gz'
    archive = 'beluga.coco.tar.gz'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class BirdIndividualID(Downloader):
    url = 'https://drive.google.com/uc?id=1YT4w8yF44D-y9kdzgF38z2uYbHfpiDOA'
    archive = 'ferreira_et_al_2020.zip'

    def _download(self):
        exception_text = '''Dataset must be downloaded manually.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#birdindividualid'''
        raise Exception(exception_text)
        # utils.gdown_download(self.url, self.archive, exception_text=exception_text)
            
    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

        # Create new folder for segmented images
        folder_new = os.getcwd() + 'Segmented'
        if not os.path.exists(folder_new):
            os.makedirs(folder_new)

        # Move segmented images to new folder
        folder_move = 'Cropped_pictures'
        shutil.move(folder_move, os.path.join(folder_new, folder_move))

class CTai(Downloader):
    url = 'https://github.com/cvjena/chimpanzee_faces/archive/refs/heads/master.zip'
    archive = 'master.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)
        shutil.rmtree('chimpanzee_faces-master/datasets_cropped_chimpanzee_faces/data_CZoo')

class CZoo(Downloader):
    url = 'https://github.com/cvjena/chimpanzee_faces/archive/refs/heads/master.zip'
    archive = 'master.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)
        shutil.rmtree('chimpanzee_faces-master/datasets_cropped_chimpanzee_faces/data_CTai')

class Cows2021(Downloader):
    url = 'https://data.bris.ac.uk/datasets/tar/4vnrca7qw1642qlwxjadp87h7.zip'
    archive = '4vnrca7qw1642qlwxjadp87h7.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class Drosophila(Downloader):
    downloads = [
        ('https://dataverse.scholarsportal.info/api/access/datafile/71066', 'week1_Day1_train_01to05.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71067', 'week1_Day1_train_06to10.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71068', 'week1_Day1_train_11to15.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71069', 'week1_Day1_train_16to20.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71065', 'week1_Day1_val.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71071', 'week1_Day2_train_01to05.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71072', 'week1_Day2_train_06to10.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71073', 'week1_Day2_train_11to15.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71075', 'week1_Day2_train_16to20.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71070', 'week1_Day2_val.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71077', 'week1_Day3_01to04.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71078', 'week1_Day3_05to08.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71079', 'week1_Day3_09to12.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71080', 'week1_Day3_13to16.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71081', 'week1_Day3_17to20.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71083', 'week2_Day1_train_01to05.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71084', 'week2_Day1_train_06to10.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71085', 'week2_Day1_train_11to15.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71086', 'week2_Day1_train_16to20.zip'),        
        ('https://dataverse.scholarsportal.info/api/access/datafile/71082', 'week2_Day1_val.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71094', 'week2_Day2_train_01to05.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71095', 'week2_Day2_train_06to10.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71109', 'week2_Day2_train_11to15.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71110', 'week2_Day2_train_16to20.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71093', 'week2_Day2_val.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71111', 'week2_Day3_01to04.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71112', 'week2_Day3_05to08.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71115', 'week2_Day3_09to12.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71117', 'week2_Day3_13to16.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71118', 'week2_Day3_17to20.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71119', 'week3_Day1_train_01to05.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71120', 'week3_Day1_train_06to10.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71121', 'week3_Day1_train_11to15.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71124', 'week3_Day1_train_16to20.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71097', 'week3_Day1_val.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71125', 'week3_Day2_train_01to05.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71126', 'week3_Day2_train_06to10.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71127', 'week3_Day2_train_11to15.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71128', 'week3_Day2_train_16to20.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71107', 'week3_Day2_val.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71129', 'week3_Day3_01to04.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71130', 'week3_Day3_05to08.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71131', 'week3_Day3_09to12.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71132', 'week3_Day3_13to16.zip'),
        ('https://dataverse.scholarsportal.info/api/access/datafile/71133', 'week3_Day3_17to20.zip'),
    ]

    def _download(self):
        for url, archive in self.downloads:
            utils.download_url(url, archive)

    def _extract(self):
        for url, archive in self.downloads:
            utils.extract_archive(archive, extract_path=os.path.splitext(archive)[0], delete=True)

class FriesianCattle2015(Downloader):
    url = 'https://data.bris.ac.uk/datasets/wurzq71kfm561ljahbwjhx9n3/wurzq71kfm561ljahbwjhx9n3.zip'
    archive = 'wurzq71kfm561ljahbwjhx9n3.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class FriesianCattle2017(Downloader):
    url = 'https://data.bris.ac.uk/datasets/2yizcfbkuv4352pzc32n54371r/2yizcfbkuv4352pzc32n54371r.zip'
    archive = '2yizcfbkuv4352pzc32n54371r.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class GiraffeZebraID(Downloader):
    url = 'https://lilablobssc.blob.core.windows.net/giraffe-zebra-id/gzgc.coco.tar.gz'
    archive = 'gzgc.coco.tar.gz'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class Giraffes(Downloader):
    def _download(self):
        url = 'ftp://pbil.univ-lyon1.fr/pub/datasets/miele2021/'
        command = f"wget -rpk -l 10 -np -c --random-wait -U Mozilla {url} -P '.' "
        exception_text = '''Download works only on Linux. Please download it manually.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#giraffes'''
        if os.name == 'posix':
            os.system(command)
        else:
            raise Exception(exception_text)

    def _extract(self):
        pass

class HappyWhale(Downloader):
    archive = 'happy-whale-and-dolphin.zip'

    def _download(self):
        command = f"competitions download -c happy-whale-and-dolphin --force"
        exception_text = '''Kaggle terms must be agreed with.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#happywhale'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=self.archive)

    def _extract(self):
        try:
            utils.extract_archive(self.archive, delete=True)
        except:
            exception_text = '''Extracting failed.
                Either the download was not completed or the Kaggle terms were not agreed with.
                Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#happywhale'''
            raise Exception(exception_text)

class HumpbackWhaleID(Downloader):
    archive = 'humpback-whale-identification.zip'

    def _download(self):
        command = f"competitions download -c humpback-whale-identification --force"
        exception_text = '''Kaggle terms must be agreed with.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#humpbackwhale'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=self.archive)

    def _extract(self):
        try:
            utils.extract_archive(self.archive, delete=True)
        except:
            exception_text = '''Extracting failed.
                Either the download was not completed or the Kaggle terms were not agreed with.
                Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#humpbackwhale'''
            raise Exception(exception_text)

class HyenaID2022(Downloader):
    url = 'https://lilablobssc.blob.core.windows.net/liladata/wild-me/hyena.coco.tar.gz'
    archive = 'hyena.coco.tar.gz'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class IPanda50(Downloader):
    downloads = [
        ('https://drive.google.com/uc?id=1nkh-g6a8JvWy-XsMaZqrN2AXoPlaXuFg', 'iPanda50-images.zip'),
        ('https://drive.google.com/uc?id=1gVREtFWkNec4xwqOyKkpuIQIyWU_Y_Ob', 'iPanda50-split.zip'),
        ('https://drive.google.com/uc?id=1jdACN98uOxedZDT-6X3rpbooLAAUEbNY', 'iPanda50-eyes-labels.zip'),
    ]

    def _download(self):
        for url, archive in self.downloads:
            utils.gdown_download(url, archive)

    def _extract(self):
        for url, archive in self.downloads:
            utils.extract_archive(archive, delete=True)

class LeopardID2022(Downloader):
    url = 'https://lilablobssc.blob.core.windows.net/liladata/wild-me/leopard.coco.tar.gz'
    archive = 'leopard.coco.tar.gz'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class LionData(Downloader):
    url = 'https://github.com/tvanzyl/wildlife_reidentification/archive/refs/heads/main.zip'
    archive = 'main.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)
        shutil.rmtree('wildlife_reidentification-main/Nyala_Data_Zero')

class MacaqueFaces(Downloader):
    def _download(self):
        downloads = [
            ('https://github.com/clwitham/MacaqueFaces/raw/master/ModelSet/MacaqueFaces.zip', 'MacaqueFaces.zip'),
            ('https://github.com/clwitham/MacaqueFaces/raw/master/ModelSet/MacaqueFaces_ImageInfo.csv', 'MacaqueFaces_ImageInfo.csv'),
        ]
        for url, file in downloads:
            utils.download_url(url, file)

    def _extract(self):
        utils.extract_archive('MacaqueFaces.zip', delete=True)

class NDD20(Downloader):
    url = 'https://data.ncl.ac.uk/ndownloader/files/22774175'
    archive = 'NDD20.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)    

class NOAARightWhale(Downloader):
    archive = 'noaa-right-whale-recognition.zip'

    def _download(self):
        command = f"competitions download -c noaa-right-whale-recognition --force"
        exception_text = '''Kaggle terms must be agreed with.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#noaarightwhale'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=self.archive)

    def _extract(self):
        try:
            utils.extract_archive(self.archive, delete=True)
            utils.extract_archive('imgs.zip', delete=True)
            # Move misplaced image
            shutil.move('w_7489.jpg', 'imgs')
            os.remove('w_7489.jpg.zip')
        except:
            exception_text = '''Extracting failed.
                Either the download was not completed or the Kaggle terms were not agreed with.
                Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#noaarightwhale'''
            raise Exception(exception_text)

class NyalaData(Downloader):
    url = 'https://github.com/tvanzyl/wildlife_reidentification/archive/refs/heads/main.zip'
    archive = 'main.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)
        shutil.rmtree('wildlife_reidentification-main/Lion_Data_Zero')

class OpenCows2020(Downloader):
    url = 'https://data.bris.ac.uk/datasets/tar/10m32xl88x2b61zlkkgz3fml17.zip'
    archive = '10m32xl88x2b61zlkkgz3fml17.zip'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class SeaTurtleIDHeads(Downloader):
    archive = 'seaturtleidheads.zip'

    def _download(self):
        command = f"datasets download -d 'wildlifedatasets/seaturtleidheads' --force"
        exception_text = '''Kaggle must be setup.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#seaturtleid'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class SeaTurtleID(Downloader):
    archive = 'seaturtleid.zip'

    def _download(self):
        command = f"datasets download -d 'wildlifedatasets/seaturtleid' --force"
        exception_text = '''Kaggle must be setup.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#seaturtleid'''
        utils.kaggle_download(command, exception_text=exception_text, required_file=self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class SealID(Downloader):
    archive = '22b5191e-f24b-4457-93d3-95797c900fc0_ui65zipk.zip'
    
    def _download(self, url=None):
        if url is None:
            raise(Exception('URL must be provided for SealID.\nCheck https://wildlifedatasets.github.io/wildlife-datasets/downloads/#sealid'))
        utils.download_url(url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)
        utils.extract_archive(os.path.join('SealID', 'full images.zip'), delete=True)
        utils.extract_archive(os.path.join('SealID', 'patches.zip'), delete=True)
        
        # Create new folder for segmented images
        folder_new = os.getcwd() + 'Segmented'
        if not os.path.exists(folder_new):
            os.makedirs(folder_new)
        
        # Move segmented images to new folder
        folder_move = os.path.join('patches', 'segmented')
        shutil.move(folder_move, os.path.join(folder_new, folder_move))
        folder_move = os.path.join('full images', 'segmented_database')
        shutil.move(folder_move, os.path.join(folder_new, folder_move))
        folder_move = os.path.join('full images', 'segmented_query')
        shutil.move(folder_move, os.path.join(folder_new, folder_move))
        file_copy = os.path.join('patches', 'annotation.csv')
        shutil.copy(file_copy, os.path.join(folder_new, file_copy))
        file_copy = os.path.join('full images', 'annotation.csv')
        shutil.copy(file_copy, os.path.join(folder_new, file_copy))            

class SMALST(Downloader):
    url = 'https://drive.google.com/uc?id=1yVy4--M4CNfE5x9wUr1QBmAXEcWb6PWF'
    archive = 'zebra_training_set.zip'

    def _download(self):
        exception_text = '''Download filed. GDown quota probably reached. Download dataset manually.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#smalst'''
        utils.gdown_download(self.url, self.archive, exception_text)

    def _extract(self):
        exception_text = '''Extracting works only on Linux. Please extract it manually.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#smalst'''
        if os.name == 'posix':
            os.system('jar xvf ' + self.archive)
            os.remove(self.archive)
            shutil.rmtree(os.path.join('zebra_training_set', 'annotations'))
            shutil.rmtree(os.path.join('zebra_training_set', 'texmap'))
            shutil.rmtree(os.path.join('zebra_training_set', 'uvflow'))

        else:
            raise Exception(exception_text)

class StripeSpotter(Downloader):
    def _download(self):
        urls = [
            'https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/stripespotter/data-20110718.zip',
            'https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/stripespotter/data-20110718.z02',
            'https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/stripespotter/data-20110718.z01',
            ]
        for url in urls:
            os.system(f"wget -P '.' {url}")

    def _extract(self):
        exception_text = '''Extracting works only on Linux. Please extract it manually.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#stripespotter'''
        if os.name == 'posix':
            os.system(f"zip -s- data-20110718.zip -O data-full.zip")
            os.system(f"unzip data-full.zip")
            os.remove('data-20110718.zip')
            os.remove('data-20110718.z01')
            os.remove('data-20110718.z02')
            os.remove('data-full.zip')
        else:
            raise Exception(exception_text)       

class WhaleSharkID(Downloader):
    url = 'https://lilablobssc.blob.core.windows.net/whale-shark-id/whaleshark.coco.tar.gz'
    archive = 'whaleshark.coco.tar.gz'

    def _download(self):
        utils.download_url(self.url, self.archive)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)

class WNIGiraffes(Downloader):
    url = "https://lilablobssc.blob.core.windows.net/wni-giraffes/wni_giraffes_train_images.zip"
    archive = 'wni_giraffes_train_images.zip'
    url2 = 'https://lilablobssc.blob.core.windows.net/wni-giraffes/wni_giraffes_train.zip'
    archive2 = 'wni_giraffes_train.zip'

    def _download(self):
        exception_text = '''Dataset must be downloaded manually.
            Check https://wildlifedatasets.github.io/wildlife-datasets/downloads#wnigiraffes'''
        raise Exception(exception_text)
        #os.system(f'azcopy cp {self.url} {self.archive}')
        #utils.download_url(self.url2, self.archive2)

    def _extract(self):
        utils.extract_archive(self.archive, delete=True)
        utils.extract_archive(self.archive2, delete=True)

class ZindiTurtleRecall(Downloader):
    def _download(self):
        downloads = [
            ('https://storage.googleapis.com/dm-turtle-recall/train.csv', 'train.csv'),
            ('https://storage.googleapis.com/dm-turtle-recall/extra_images.csv', 'extra_images.csv'),
            ('https://storage.googleapis.com/dm-turtle-recall/test.csv', 'test.csv'),
            ('https://storage.googleapis.com/dm-turtle-recall/images.tar', 'images.tar'),
        ]
        for url, file in downloads:
            utils.download_url(url, file)

    def _extract(self):
        utils.extract_archive('images.tar', 'images', delete=True)


class Segmented(Downloader):
    warning = '''You are trying to download or extract a segmented dataset.
        It is already included in its non-segmented version.
        Skipping.'''
    
    def get_data(self, root, name=None):
        print(self.warning)

    def _download(self):
        print(self.warning)

    def _extract(self):
        print(self.warning)
