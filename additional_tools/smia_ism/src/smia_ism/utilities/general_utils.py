import smia

def print_smia_ism_banner():
    """
    This method prints the SMIA ISM banner as a string, based on the main SMIA banner. The banner has been created with
     Python 'art' library.
    """
    # The code for creating the banner with 'art' is commented to avoid installing it with SMIA ISM
    # ascii_art_smia = text2art("SMIA", font="varsity")
    # ascii_art_ism = text2art("ISM", font="varsity")
    # combined = []
    # smia_lines = ascii_art_smia.split('\n')
    # ism_lines = ascii_art_ism.split('\n')
    # combined.append("=" * 84)
    # for i in range(len(smia_lines)):
    #     combined.append(smia_lines[i] + "   " + "\033[34m" + ism_lines[i] + "\033[0m")
    # combined.append("=" * 84)
    # combined_banner = '\n'.join(combined)
    # print(combined_banner)

    # The banner for the SMIA is set as string, avoiding installing 'art' library (which has been used to create it)
    banner_str = f"""
====================================================================================
  ______    ____    ____   _____        _          [34m _____    ______    ____    ____  [0m
.' ____ \  |_   \  /   _| |_   _|      / \         [34m|_   _| .' ____ \  |_   \  /   _| [0m
| (___ \_|   |   \/   |     | |       / _ \        [34m  | |   | (___ \_|   |   \/   |   [0m
 _.____`.    | |\  /| |     | |      / ___ \       [34m  | |    _.____`.    | |\  /| |   [0m
| \____) |  _| |_\/_| |_   _| |_   _/ /   \ \_     [34m _| |_  | \____) |  _| |_\/_| |_  [0m
 \______.' |_____||_____| |_____| |____| |____|    [34m|_____|  \______.' |_____||_____| [0m
                                                   [34m                                  [0m
   [34m[0m
====================================================================================
                                                                            v{smia.__version__} 
====================================================================================
    """
    print(banner_str)