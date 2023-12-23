# anki-images

This script adds images to an Anki deck.

## Usage
1. Export the deck from Anki as a txt file.
2. Run the script: `python add_images <exported_anki_filename>`
3. Copy the images in the `images` directory to the `collection.media` folder
   for your device and OS.
   [Find out where this folder is](https://docs.ankiweb.net/files.html#file-locations).
4. Import the generated `*_with_images.tsv` file into Anki. If you select
   `Update existing notes when first field matches`, you will be able to update
   the imported notes without creating duplicates. Note that the note type must
   be updated to accept an image field.
