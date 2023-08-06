from PIL import Image
import logging

class Myra:
    """Overall class to manage image scans."""

    def __init__(self):
        """
        Initalize the Sola image scan class.
        """

    def scan(image_path:str) -> dict[tuple,int]:
      """
      Scans every pixel and counts the occurance of each color in the image.

      image_path: Absolute or relaitve filepath to the image.

      Returns a dictionary with count data. 
      """

      logging.info(f"Starting scan for image: {image_path}")

      if not isinstance(image_path, str):
            
            logging.error(f"The file path has an invalid type: {type(image_path)}. Please provide a {str}.")

            return

      elif len(image_path) == 0:

            logging.error(f"The file path has an length: {len(image_path)}. Please provide a string filepath with alength > 1.")

            return

      try:
            colors:dict[tuple,int] = {}

            # Load the image and grab pixel data.
            image = Image.open(image_path)

            pixels = image.load()
            
            logging.info(f"Image size: {image.size}")
            # Loop through the pixels, store the rgb values, and increment a count
            for x in range(image.size[0]):
                  for y in range(image.size[1]):
                        
                        rgba:tuple[int] = pixels[x,y]

                        colors[rgba[:3]] = 1 + colors.get(rgba[:3], 0)

      except FileNotFoundError:
            print(f"No such file or directory: {image_path}. Is the file in the correct directory?")

            logging.info("Scan complete.")

      return colors

    

    


    


