"""
Arnold Fitness CLI Colors System
Unified color management for consistent UI experience across all CLI modes
"""

from colorama import init, Fore, Back, Style

init()

class ArnoldColors:
    """Sistema colori unificato per Arnold Fitness CLI"""
    
    # Colori primari
    HEADER = Fore.CYAN + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    WARNING = Fore.YELLOW + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    INFO = Fore.BLUE + Style.BRIGHT
    
    # Arnold branding colors
    ARNOLD = Fore.GREEN + Style.BRIGHT
    ARNOLD_ACCENT = Fore.LIGHTGREEN_EX + Style.BRIGHT
    USER = Fore.CYAN + Style.BRIGHT
    PROMPT = Fore.MAGENTA + Style.BRIGHT
    
    # Stati visuali
    DIM = Style.DIM
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL
    
    # Checklist status colors
    CHECK_COMPLETED = Fore.GREEN + Style.BRIGHT
    CHECK_IN_PROGRESS = Fore.YELLOW + Style.BRIGHT + Back.BLUE
    CHECK_PENDING = Fore.WHITE + Style.DIM
    CHECK_CURRENT = Fore.MAGENTA + Style.BRIGHT
    
    # Progress colors
    PROGRESS_LOW = Fore.RED + Style.BRIGHT
    PROGRESS_MED = Fore.YELLOW + Style.BRIGHT  
    PROGRESS_HIGH = Fore.GREEN + Style.BRIGHT
    
    @staticmethod
    def print_logo():
        """Arnold Fitness ASCII logo"""
        logo = f"""
{ArnoldColors.ARNOLD}
    _                    _     _ 
   / \\   _ __ _ __   ___ | | __| |
  / _ \\ | '__| '_ \\ / _ \\| |/ _` |
 / ___ \\| |  | | | | (_) | | (_| |
/_/   \\_\\_|  |_| |_|\\___/|_|\\__,_|
                                 
{ArnoldColors.ARNOLD_ACCENT}FITNESS COACHING PLATFORM{ArnoldColors.RESET}
        """
        print(logo)
        
    @staticmethod
    def format_progress(percentage):
        """Format progress percentage with color"""
        if percentage < 30:
            return f"{ArnoldColors.PROGRESS_LOW}{percentage}%{ArnoldColors.RESET}"
        elif percentage < 70:
            return f"{ArnoldColors.PROGRESS_MED}{percentage}%{ArnoldColors.RESET}"
        else:
            return f"{ArnoldColors.PROGRESS_HIGH}{percentage}%{ArnoldColors.RESET}"