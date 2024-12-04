
def get_slide_index(presentation, list_keys):
    '''
    Function to get index slide based on a keyword found in a specific slide in pptx

    - presentation: ppt file sotred in memory
    - list_keys: List of keys to search into the pptx to identify the indexes. Ex.(['team', 'usecase'])

    Return: List of indexes
    '''

    # Ensure the key_name is stripped of any zero-width space characters
    keywords = [kw.replace("\u200b", "").strip() for kw in list_keys]

    # Track slides to remove
    slides_to_remove = []

    # Iterate over slides with zero-based indexing (default)
    for slide_num, slide in enumerate(presentation.slides):
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    # Check if any keyword in thew list is in the title
                    if any(kw in paragraph.text.strip() for kw in keywords):
                        slides_to_remove.append(slide_num)
                        break

    return slides_to_remove


def delete_slide_by_tittle(presentation,  list_keys):
    '''
    Function to delete selected slides by passing a key name

    Entry: Lists of key names to delete to

    Return: File in Memory that will contain the general changes
    '''

    slides_to_remove = get_slide_index(presentation, list_keys)

    # Sort indices in reverse order to avoid issues when deleting
    slides_to_remove.sort(reverse=True)

    # Delete the slides
    for slide_num in slides_to_remove:
        try:
            xml_slides = presentation.slides._sldIdLst
            slides = list(xml_slides)
            xml_slides.remove(slides[slide_num])

            print(f"Slide removed successfully: {slide_num + 1}")

        except Exception as e:
            raise Exception(f"Failed to delete slide at index {slide_num}: {e}")

