from bing_image_downloader import downloader
import winsound

DATADIR = 'dataset'

clas = {'humans':["baby images","boy images","girl images","man images","woman images"],'animals':["aquatic mammals images","fish images","insects images","large omnivores and herbivores images","medium-sized mammals images","non-insect invertebrates images","reptiles images","small mammals images","large carnivores images","bird images","horse images","frog images","dog images","deer images","cat images"],'other':["flowers images","food containers images","fruit and vegetables images","household electrical devices images","household furniture images","large man-made outdoor things images","large natural outdoor scenes images","trees images","airplane images","vehicles images","ship images","truck images"]}

for i in clas.keys():
    for j in clas[i]:
        downloader.download(j, limit=130,  output_dir=f'{DATADIR}/{i}', adult_filter_off=True, force_replace=False, timeout=30)

winsound.Beep(2500,1000)
print("Download complete! Check your 'dataset' folder.")