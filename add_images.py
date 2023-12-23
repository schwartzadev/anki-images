# take argument anki_export_csv_file
# add images to anki media folder

import sys
import os
import glob
import shutil
import pandas as pd
from bing_image_downloader import downloader
import tqdm
import backoff

SOURCE_COLUMN_INDEX = 1

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 add_images.py anki_export_csv_file")
        return

    anki_export_csv_file = sys.argv[1]
    if not os.path.exists(anki_export_csv_file):
        print("File not found: " + anki_export_csv_file)
        return
    
    # name without extension
    anki_export_file_name = os.path.splitext(anki_export_csv_file)[0]
    
    # read tsv
    df = pd.read_csv(anki_export_csv_file, sep='\t', header=None)

    # mkdir images unless it exists
    if not os.path.exists("images"):
        os.mkdir("images")
    
    # add an empty column for the image
    df['image'] = None
    
    # iterate over rows with tqdm
    for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
        # get image
        try:
            file_name = _get_and_save_image_for_row(row, anki_export_file_name)
        except IndexError:
            # no image found
            continue

        # update row
        _update_row_with_image(df, index, file_name)
    
    _clean_up()

    _save_df_to_csv(df, anki_export_file_name)
    import pdb; pdb.set_trace()

@backoff.on_exception(backoff.expo, IndexError, max_tries=5)
def _get_and_save_image_for_row(row, anki_export_file_name):
    search_term = row[SOURCE_COLUMN_INDEX]
    # replace anything that is not a letter or number with _
    clean_search_term = ''.join(e for e in search_term if e.isalnum())

    # skip if image already exists with any extension using glob
    # if os.path.exists("images/" + anki_export_file_name + '_' + clean_search_term + ".*"):
    if glob.glob("images/" + anki_export_file_name + '_' + clean_search_term + ".*"):
        print("Skipping " + search_term + " because image already exists")
        return anki_export_file_name + '_' + clean_search_term + ".jpg"

    downloader.download(
        clean_search_term,
        limit=1,
        output_dir='_temp_images',
        adult_filter_off=True,
        force_replace=False,
        timeout=60,
        verbose=False
    )

    # get the files in the temp images folder
    dowloaded_dir = os.path.join("_temp_images", clean_search_term)
    files = os.listdir(dowloaded_dir)
    file_name = files[0] # this will be Image_1.XXX
    # get the extension
    extension = os.path.splitext(file_name)[1]
    new_file_name = anki_export_file_name + '_' + clean_search_term + extension

    old_image_path = os.path.join(dowloaded_dir, file_name)
    new_image_path = os.path.join("images", new_file_name)

    os.rename(old_image_path, new_image_path)
    return new_file_name

def _update_row_with_image(df, index, image_path):
    # <img src="image.jpg">
    df.at[index, 'image'] = '<img src="{0}" width="280px">'.format(image_path)

def _clean_up():
    # delete _temp_images even if it's not empty
    shutil.rmtree("_temp_images")

def _save_df_to_csv(df, anki_export_file_name):
    df.to_csv(anki_export_file_name + '_with_images.tsv', sep='\t', header=False, index=False)

if __name__ == "__main__":
    main()
