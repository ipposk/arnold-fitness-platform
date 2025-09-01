#!/usr/bin/env python3
"""
Arnold CLI Checklist-Driven Enhanced - Visual Experience Upgrade
Implementazione della visione originale con presentazione visiva migliorata
Segue rigorosamente le checklist come binario per mantenere il contesto
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, Any, List, Tuple
import threading
import itertools

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from colorama import init, Fore, Style, Back
init(autoreset=True)

# Import componenti checklist-driven
from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
from src.checklist_manager import ChecklistProgressDisplay


class EnhancedColors:
    """Sistema colori avanzato per CLI premium"""
    # Colori primari con maggiore profondità
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
    
    # Stati visuali migliorati
    DIM = Style.DIM
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL
    
    # Checklist status colors
    CHECK_COMPLETED = Fore.GREEN + Style.BRIGHT
    CHECK_IN_PROGRESS = Fore.YELLOW + Style.BRIGHT + Back.BLUE
    CHECK_PENDING = Fore.WHITE + Style.DIM
    CHECK_CURRENT = Fore.MAGENTA + Style.BRIGHT
    
    # Gradient effects per progress bars
    PROGRESS_LOW = Fore.RED + Style.BRIGHT
    PROGRESS_MED = Fore.YELLOW + Style.BRIGHT  
    PROGRESS_HIGH = Fore.GREEN + Style.BRIGHT
    
    # Background highlights
    BG_SUCCESS = Back.GREEN + Fore.WHITE + Style.BRIGHT
    BG_INFO = Back.BLUE + Fore.WHITE + Style.BRIGHT
    BG_WARNING = Back.YELLOW + Fore.BLACK + Style.BRIGHT
    BG_ERROR = Back.RED + Fore.WHITE + Style.BRIGHT
    
    # Special effects
    GLOW = Fore.WHITE + Style.BRIGHT
    SHADOW = Fore.BLACK + Style.DIM


class VisualElements:
    """Elementi visivi avanzati per l'interfaccia"""
    
    # Box drawing characters per layout professionali
    BOX_TOP_LEFT = "╭"
    BOX_TOP_RIGHT = "╮"
    BOX_BOTTOM_LEFT = "╰"
    BOX_BOTTOM_RIGHT = "╯"
    BOX_HORIZONTAL = "─"
    BOX_VERTICAL = "│"
    BOX_CROSS = "┼"
    BOX_T_DOWN = "┬"
    BOX_T_UP = "┴"
    BOX_T_LEFT = "┤"
    BOX_T_RIGHT = "├"
    
    # Progress indicators avanzati
    PROGRESS_FULL = "█"
    PROGRESS_SEVEN_EIGHTHS = "▉"
    PROGRESS_THREE_QUARTERS = "▊"
    PROGRESS_FIVE_EIGHTHS = "▋"
    PROGRESS_HALF = "▌"
    PROGRESS_THREE_EIGHTHS = "▍"
    PROGRESS_QUARTER = "▎"
    PROGRESS_EIGHTH = "▏"
    PROGRESS_EMPTY = "░"
    
    # Icone migliorate
    ICON_SUCCESS = "✓"
    ICON_ERROR = "✗"
    ICON_WARNING = "⚠"
    ICON_INFO = "ℹ"
    ICON_ARROW_RIGHT = "→"
    ICON_ARROW_DOWN = "↓"
    ICON_DIAMOND = "◆"
    ICON_STAR = "★"
    ICON_CHECK_COMPLETED = "✅"
    ICON_CHECK_IN_PROGRESS = "🔄"
    ICON_CHECK_PENDING = "⏸️"
    ICON_CHECK_CURRENT = "👉"
    
    # Separatori decorativi
    SEPARATOR_HEAVY = "━"
    SEPARATOR_LIGHT = "─"
    SEPARATOR_DOUBLE = "═"
    SEPARATOR_DOT = "·"


class AnimationManager:
    """Gestore animazioni per feedback visivo"""
    
    def __init__(self):
        self.spinning = False
        self.spinner_thread = None
    
    def start_spinner(self, message: str = "Elaborando..."):
        """Avvia spinner di caricamento"""
        self.spinning = True
        self.spinner_thread = threading.Thread(
            target=self._spin_animation,
            args=(message,)
        )
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
    
    def stop_spinner(self):
        """Ferma spinner"""
        self.spinning = False
        if self.spinner_thread:
            self.spinner_thread.join(timeout=0.1)
        # Clear the spinner line
        print("\r" + " " * 50 + "\r", end="", flush=True)
    
    def _spin_animation(self, message: str):
        """Loop di animazione spinner"""
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        for char in itertools.cycle(spinner_chars):
            if not self.spinning:
                break
            print(f"\r{EnhancedColors.INFO}{char} {message}{EnhancedColors.RESET}", 
                  end="", flush=True)
            time.sleep(0.1)
    
    def typewriter_effect(self, text: str, delay: float = 0.03):
        """Effetto macchina da scrivere per testo"""
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
        print()  # Newline finale


class EnhancedProgressBar:
    """Barra di progresso avanzata con gradienti e animazioni"""
    
    @staticmethod
    def create_progress_bar(progress: float, width: int = 40, 
                          style: str = "gradient") -> str:
        """Crea barra di progresso avanzata"""
        if style == "gradient":
            return EnhancedProgressBar._create_gradient_bar(progress, width)
        elif style == "blocks":
            return EnhancedProgressBar._create_block_bar(progress, width)
        else:
            return EnhancedProgressBar._create_smooth_bar(progress, width)
    
    @staticmethod
    def _create_gradient_bar(progress: float, width: int) -> str:
        """Barra con gradiente di colore"""
        filled = int(width * progress / 100)
        
        # Scegli colore in base al progresso
        if progress < 33:
            color = EnhancedColors.PROGRESS_LOW
        elif progress < 66:
            color = EnhancedColors.PROGRESS_MED
        else:
            color = EnhancedColors.PROGRESS_HIGH
        
        filled_str = color + VisualElements.PROGRESS_FULL * filled
        empty_str = EnhancedColors.DIM + VisualElements.PROGRESS_EMPTY * (width - filled)
        
        return f"[{filled_str}{empty_str}{EnhancedColors.RESET}]"
    
    @staticmethod
    def _create_smooth_bar(progress: float, width: int) -> str:
        """Barra smooth con caratteri frazionari"""
        progress_chars = [
            VisualElements.PROGRESS_EMPTY,
            VisualElements.PROGRESS_EIGHTH,
            VisualElements.PROGRESS_QUARTER,
            VisualElements.PROGRESS_THREE_EIGHTHS,
            VisualElements.PROGRESS_HALF,
            VisualElements.PROGRESS_FIVE_EIGHTHS,
            VisualElements.PROGRESS_THREE_QUARTERS,
            VisualElements.PROGRESS_SEVEN_EIGHTHS,
            VisualElements.PROGRESS_FULL
        ]
        
        exact_progress = width * progress / 100
        full_blocks = int(exact_progress)
        fraction = exact_progress - full_blocks
        
        # Carattere frazionario
        fraction_index = int(fraction * 8)
        fraction_char = progress_chars[min(fraction_index, 7)]
        
        # Costruisci barra
        full_part = VisualElements.PROGRESS_FULL * full_blocks
        empty_part = VisualElements.PROGRESS_EMPTY * (width - full_blocks - 1)
        
        color = EnhancedColors.PROGRESS_HIGH if progress > 70 else EnhancedColors.PROGRESS_MED
        
        return f"[{color}{full_part}{fraction_char}{EnhancedColors.DIM}{empty_part}{EnhancedColors.RESET}]"


class EnhancedLayout:
    """Gestore layout avanzato per interfaccia"""
    
    def __init__(self, terminal_width: int):
        self.width = terminal_width
        self.content_width = terminal_width - 4  # Margins
    
    def create_box(self, title: str, content: List[str], 
                   box_style: str = "rounded") -> List[str]:
        """Crea box decorativo con contenuto"""
        if box_style == "rounded":
            return self._create_rounded_box(title, content)
        elif box_style == "double":
            return self._create_double_box(title, content)
        else:
            return self._create_simple_box(title, content)
    
    def _create_rounded_box(self, title: str, content: List[str]) -> List[str]:
        """Box con angoli arrotondati"""
        box_lines = []
        
        # Top border con titolo
        title_line = f"{VisualElements.BOX_TOP_LEFT}"
        title_line += f" {title} "
        title_line += VisualElements.BOX_HORIZONTAL * (self.width - len(title) - 4)
        title_line += VisualElements.BOX_TOP_RIGHT
        box_lines.append(title_line)
        
        # Content lines
        for line in content:
            content_line = f"{VisualElements.BOX_VERTICAL} {line:<{self.width-4}} {VisualElements.BOX_VERTICAL}"
            box_lines.append(content_line)
        
        # Bottom border
        bottom_line = (VisualElements.BOX_BOTTOM_LEFT + 
                      VisualElements.BOX_HORIZONTAL * (self.width - 2) + 
                      VisualElements.BOX_BOTTOM_RIGHT)
        box_lines.append(bottom_line)
        
        return box_lines
    
    def create_section_header(self, title: str, subtitle: str = None) -> str:
        """Crea header di sezione stilizzato"""
        lines = []
        
        # Main title
        title_line = f"{EnhancedColors.HEADER}{'═' * self.width}{EnhancedColors.RESET}"
        lines.append(title_line)
        
        centered_title = f"{title:^{self.width}}"
        title_formatted = f"{EnhancedColors.HEADER}{centered_title}{EnhancedColors.RESET}"
        lines.append(title_formatted)
        
        if subtitle:
            centered_subtitle = f"{subtitle:^{self.width}}"
            subtitle_formatted = f"{EnhancedColors.DIM}{centered_subtitle}{EnhancedColors.RESET}"
            lines.append(subtitle_formatted)
        
        bottom_line = f"{EnhancedColors.HEADER}{'═' * self.width}{EnhancedColors.RESET}"
        lines.append(bottom_line)
        
        return "\n".join(lines)


class ArnoldEnhancedCLI:
    """
    Arnold CLI Enhanced - Sistema checklist-driven con esperienza visiva premium
    Mantiene tutta la funzionalità originale con presentazione migliorata
    """
    
    def __init__(self):
        # Configurazione terminale avanzata
        try:
            terminal_size = shutil.get_terminal_size()
            self.terminal_width = min(120, terminal_size.columns - 2)
            self.terminal_height = terminal_size.lines
        except OSError:
            self.terminal_width = 100
            self.terminal_height = 30
        
        # Componenti sistema originali
        self.orchestrator = None
        self.progress_display = ChecklistProgressDisplay()
        self.session_id = None
        
        # Componenti visuali avanzati
        self.layout = EnhancedLayout(self.terminal_width)
        self.animation = AnimationManager()
        
        # Context simulato per demo (mantenuto uguale all'originale)
        self.user_context = {
            'sessions_count': 0,
            'days_since_last_session': 0
        }
        
        # Configurazione esperienza utente
        self.typing_effect_enabled = True
        self.animation_enabled = True
        
    def run(self):
        """Avvia il CLI checklist-driven con esperienza premium"""
        try:
            self.show_enhanced_welcome()
            self.initialize_session_with_style()
            self.enhanced_main_loop()
        except KeyboardInterrupt:
            self.show_graceful_exit()
        except Exception as e:
            self.show_error_with_style(f"Errore fatale: {e}")
    
    def show_enhanced_welcome(self):
        """Schermata di benvenuto con design premium"""
        self.clear_screen()
        
        # Arnold ASCII Art Header
        arnold_header = f"""
{EnhancedColors.ARNOLD}╔══════════════════════════════════════════════════════════════════════════════════════╗
║    █████╗ ██████╗ ███╗   ██╗ ██████╗ ██╗     ██████╗                                ║
║   ██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║     ██╔══██╗                               ║
║   ███████║██████╔╝██╔██╗ ██║██║   ██║██║     ██║  ██║                               ║
║   ██╔══██║██╔══██╗██║╚██╗██║██║   ██║██║     ██║  ██║                               ║
║   ██║  ██║██║  ██║██║ ╚████║╚██████╔╝███████╗██████╔╝                               ║
║   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═════╝                                ║
║                                                                                    ║
║            🏋️ AI NUTRITIONIST & FITNESS COACH - Sistema Professionale              ║
╚══════════════════════════════════════════════════════════════════════════════════════╝{EnhancedColors.RESET}
"""
        print(arnold_header)
        
        # Informazioni sistema con layout migliorato
        info_box = self.layout.create_box(
            "🎯 APPROCCIO PROFESSIONALE GUIDATO",
            [
                "",
                "Arnold segue un approccio sistematico basato su checklist professionali.",
                "Ogni domanda ha uno scopo preciso per costruire il tuo profilo completo.",
                "",
                f"{EnhancedColors.SUCCESS}✅ COSA ASPETTARTI:{EnhancedColors.RESET}",
                f"  {VisualElements.ICON_DIAMOND} Domande strutturate e sequenziali",
                f"  {VisualElements.ICON_DIAMOND} Progress visibile per ogni step",
                f"  {VisualElements.ICON_DIAMOND} Assessment completo prima dei consigli",
                f"  {VisualElements.ICON_DIAMOND} Personalizzazione basata sul tuo stile",
                "",
                f"{EnhancedColors.INFO}📊 VISUALIZZAZIONE PROGRESS:{EnhancedColors.RESET}",
                f"  {VisualElements.ICON_CHECK_COMPLETED} = Completato",
                f"  {VisualElements.ICON_CHECK_IN_PROGRESS} = In corso",
                f"  {VisualElements.ICON_CHECK_PENDING} = In attesa",
                f"  {VisualElements.ICON_CHECK_CURRENT} = Step corrente",
                ""
            ]
        )
        
        for line in info_box:
            print(f"{EnhancedColors.INFO}{line}{EnhancedColors.RESET}")
        
        # Footer con animazione
        footer_text = "Arnold ti guiderà passo dopo passo attraverso l'assessment iniziale..."
        print(f"\n{EnhancedColors.DIM}{'━' * self.terminal_width}{EnhancedColors.RESET}")
        
        if self.typing_effect_enabled:
            print(f"{EnhancedColors.DIM}", end="")
            self.animation.typewriter_effect(f"    {footer_text}")
            print(f"{EnhancedColors.RESET}", end="")
        else:
            print(f"{EnhancedColors.DIM}    {footer_text}{EnhancedColors.RESET}")
        
        print(f"{EnhancedColors.DIM}{'━' * self.terminal_width}{EnhancedColors.RESET}\n")
        
        # Pausa per effetto drammatico
        time.sleep(1.5)
    
    def initialize_session_with_style(self):
        """Inizializzazione sessione con feedback visivo avanzato"""
        if self.animation_enabled:
            self.animation.start_spinner("Inizializzando sistema checklist-driven...")
            time.sleep(2)  # Simula caricamento
            self.animation.stop_spinner()
        
        # Genera session ID (stesso sistema originale)
        import uuid
        self.session_id = f"CHECKLIST-{uuid.uuid4().hex[:8]}"
        
        # Inizializza orchestrator (funzionalità originale mantenuta)
        self.orchestrator = ChecklistDrivenOrchestrator(
            session_id=self.session_id,
            user_context=self.user_context
        )
        
        # Status report stilizzato
        print(f"{EnhancedColors.BG_SUCCESS} ✓ SISTEMA ATTIVO {EnhancedColors.RESET}")
        print()
        
        # Session info box
        session_info = self.layout.create_box(
            f"🚀 SESSIONE ATTIVA - ID: {self.session_id}",
            [
                f"Orario: {datetime.now().strftime('%H:%M:%S, %d/%m/%Y')}",
                f"Modalità: Checklist-Driven Assessment",
                f"Terminale: {self.terminal_width}x{self.terminal_height}",
                f"Stato: Sistema pronto per assessment completo"
            ]
        )
        
        for line in session_info:
            print(f"{EnhancedColors.INFO}{line}{EnhancedColors.RESET}")
        
        print()
    
    def enhanced_main_loop(self):
        """Loop principale con esperienza utente migliorata"""
        # Messaggio di benvenuto stilizzato
        welcome_msg = "🚀 Arnold è pronto per il tuo assessment professionale!"
        
        print(f"{EnhancedColors.BG_SUCCESS} {welcome_msg} {EnhancedColors.RESET}")
        print(f"{EnhancedColors.DIM}    (Digita /help per i comandi avanzati disponibili){EnhancedColors.RESET}")
        print()
        
        # Mostra stato iniziale (funzionalità originale)
        self.show_enhanced_initial_state()
        
        while True:
            try:
                # Input utente con prompt migliorato
                user_input = self.get_enhanced_user_input()
                
                if not user_input.strip():
                    continue
                    
                # Gestisci comandi speciali (funzionalità originale mantenuta)
                if user_input.startswith('/'):
                    if not self.handle_enhanced_command(user_input):
                        break
                    continue
                
                # Processa input (stesso sistema originale)
                self.process_user_message_enhanced(user_input)
                
            except KeyboardInterrupt:
                self.show_graceful_exit()
                break
            except Exception as e:
                self.show_error_with_style(str(e))
    
    def show_enhanced_initial_state(self):
        """Mostra stato iniziale con stile migliorato"""
        # Ottieni contesto checklist (stesso sistema originale)
        checklist_context = self.orchestrator.get_checklist_context()
        
        if checklist_context.get('checklist'):
            print(f"{EnhancedColors.INFO}📋 CHECKLIST INIZIALE CARICATA{EnhancedColors.RESET}")
            
            # Mostra progress con stile migliorato
            self.progress_display.display_checklist_status(
                checklist_context['checklist'], 
                terminal_width=self.terminal_width
            )
            
            # Context window se disponibile
            if checklist_context.get('current_check'):
                self.progress_display.display_context_window(
                    checklist_context['current_check'],
                    checklist_context.get('previous_check'),
                    checklist_context.get('next_check'),
                    terminal_width=self.terminal_width
                )
        
        # Prima domanda con stile
        print(f"\n{EnhancedColors.ARNOLD}💬 Arnold Nutritionist:{EnhancedColors.RESET}")
        print(f"{EnhancedColors.DIM}{'─' * self.terminal_width}{EnhancedColors.RESET}")
        
        first_question = "   Ciao! Iniziamo il tuo assessment personalizzato.\n   Dimmi, come ti chiami?"
        
        if self.typing_effect_enabled:
            self.animation.typewriter_effect(first_question, delay=0.04)
        else:
            print(first_question)
        
        print(f"{EnhancedColors.DIM}{'─' * self.terminal_width}{EnhancedColors.RESET}")
        print()
    
    def process_user_message_enhanced(self, user_input: str):
        """Processa messaggio utente con feedback visivo migliorato"""
        # Animazione processing
        if self.animation_enabled:
            self.animation.start_spinner("Analizzando risposta e aggiornando checklist...")
            time.sleep(1)  # Simula processing
        
        # Processa attraverso orchestrator (funzionalità originale)
        result = self.orchestrator.process_user_input(user_input)
        
        if self.animation_enabled:
            self.animation.stop_spinner()
        
        # Feedback completamento check se necessario
        if result.get('status') == 'advancing' and result.get('checklist_state', {}).get('just_completed'):
            self.show_enhanced_check_completion()
        
        # Progress aggiornato con stile
        self.show_enhanced_progress(result)
        
        # Risposta Arnold con presentazione migliorata
        self.show_enhanced_arnold_response(result['response'])
        
        # Context window aggiornato
        checklist_context = self.orchestrator.get_checklist_context()
        if checklist_context.get('current_check'):
            self.progress_display.display_context_window(
                checklist_context['current_check'],
                checklist_context.get('previous_check'),
                checklist_context.get('next_check'),
                terminal_width=self.terminal_width
            )
    
    def show_enhanced_check_completion(self):
        """Celebrazione completamento check con animazione"""
        print()
        
        # Animazione celebrazione
        celebration_frames = [
            f"{EnhancedColors.SUCCESS}🎉 ✅ CHECK COMPLETATO! ✅ 🎉{EnhancedColors.RESET}",
            f"{EnhancedColors.ARNOLD}🌟 ✅ CHECK COMPLETATO! ✅ 🌟{EnhancedColors.RESET}",
            f"{EnhancedColors.SUCCESS}🎊 ✅ CHECK COMPLETATO! ✅ 🎊{EnhancedColors.RESET}"
        ]
        
        for frame in celebration_frames:
            print(f"\r{frame:^{self.terminal_width}}", end="", flush=True)
            time.sleep(0.3)
        
        print(f"\n{EnhancedColors.SUCCESS}{'🎉' * (self.terminal_width // 4)}{EnhancedColors.RESET}")
        time.sleep(0.5)
    
    def show_enhanced_progress(self, result: Dict):
        """Progress aggiornato con barra avanzata"""
        checklist_state = result.get('checklist_state', {})
        progress = checklist_state.get('progress', 0)
        
        if progress > 0:
            print()
            print(f"{EnhancedColors.INFO}📊 PROGRESS AGGIORNATO{EnhancedColors.RESET}")
            
            # Barra di progresso avanzata
            progress_bar = EnhancedProgressBar.create_progress_bar(
                progress, 
                width=self.terminal_width - 20,
                style="smooth"
            )
            
            print(f"  {progress_bar} {progress:.1f}%")
            
            # Status testuale
            if progress < 25:
                status = f"{EnhancedColors.PROGRESS_LOW}Iniziale{EnhancedColors.RESET}"
            elif progress < 50:
                status = f"{EnhancedColors.PROGRESS_MED}In corso{EnhancedColors.RESET}"
            elif progress < 75:
                status = f"{EnhancedColors.PROGRESS_MED}Avanzato{EnhancedColors.RESET}"
            else:
                status = f"{EnhancedColors.PROGRESS_HIGH}Quasi completo{EnhancedColors.RESET}"
            
            print(f"  Status: {status}")
            print()
    
    def show_enhanced_arnold_response(self, response: str):
        """Risposta Arnold con presentazione premium"""
        # Header stilizzato
        header = self.layout.create_section_header(
            "💬 ARNOLD NUTRITIONIST",
            "Risposta personalizzata basata su assessment"
        )
        print(header)
        print()
        
        # Contenuto con word wrap intelligente
        self._display_formatted_text(response, prefix="  ")
        
        # Footer
        print(f"\n{EnhancedColors.DIM}{'━' * self.terminal_width}{EnhancedColors.RESET}")
        print()
    
    def _display_formatted_text(self, text: str, prefix: str = ""):
        """Mostra testo formattato con word wrap intelligente"""
        words = text.split()
        line = ""
        max_width = self.terminal_width - len(prefix) - 2
        
        for word in words:
            if len(line + " " + word) <= max_width:
                line += (" " if line else "") + word
            else:
                if line:
                    if self.typing_effect_enabled and len(line) > 50:
                        print(f"{prefix}", end="")
                        self.animation.typewriter_effect(line, delay=0.02)
                    else:
                        print(f"{prefix}{line}")
                line = word
        
        if line:
            if self.typing_effect_enabled and len(line) > 20:
                print(f"{prefix}", end="")
                self.animation.typewriter_effect(line, delay=0.02)
            else:
                print(f"{prefix}{line}")
    
    def get_enhanced_user_input(self) -> str:
        """Input utente con prompt avanzato"""
        print(f"{EnhancedColors.DIM}{'─' * self.terminal_width}{EnhancedColors.RESET}")
        
        # Prompt avanzato con icone
        prompt = f"{EnhancedColors.PROMPT}➤ Rispondi {EnhancedColors.DIM}(o /help per comandi):{EnhancedColors.RESET} "
        
        try:
            return input(prompt)
        except EOFError:
            return "/exit"
    
    def handle_enhanced_command(self, command: str) -> bool:
        """Gestisce comandi speciali con feedback migliorato"""
        cmd = command.lower().strip()
        
        # Feedback comando riconosciuto
        print(f"{EnhancedColors.INFO}⚡ Eseguendo comando: {cmd}{EnhancedColors.RESET}")
        
        if cmd == "/help":
            self.show_enhanced_help()
        elif cmd == "/progress":
            self.show_enhanced_full_progress()
        elif cmd == "/context":
            self.show_enhanced_context_details()
        elif cmd == "/checklist":
            self.show_enhanced_full_checklist()
        elif cmd == "/clear":
            self.clear_screen()
            self.show_enhanced_welcome()
        elif cmd == "/settings":
            self.show_settings_menu()
        elif cmd == "/stats":
            self.show_session_stats()
        elif cmd == "/exit":
            return False
        else:
            print(f"{EnhancedColors.WARNING}⚠ Comando non riconosciuto: {command}{EnhancedColors.RESET}")
            print(f"{EnhancedColors.DIM}  Usa /help per vedere tutti i comandi disponibili{EnhancedColors.RESET}")
        
        return True
    
    def show_enhanced_help(self):
        """Help system con design migliorato"""
        help_header = self.layout.create_section_header(
            "🆘 SISTEMA AIUTO ARNOLD",
            "Comandi disponibili e guida utilizzo"
        )
        print(help_header)
        
        # Comandi base
        base_commands = [
            "",
            f"{EnhancedColors.SUCCESS}📋 COMANDI PRINCIPALE:{EnhancedColors.RESET}",
            f"  {EnhancedColors.SUCCESS}/progress{EnhancedColors.RESET}   - Mostra progress completo checklist",
            f"  {EnhancedColors.SUCCESS}/checklist{EnhancedColors.RESET}  - Visualizza intera checklist con stati",
            f"  {EnhancedColors.SUCCESS}/context{EnhancedColors.RESET}    - Mostra context JSON corrente",
            f"  {EnhancedColors.SUCCESS}/clear{EnhancedColors.RESET}      - Pulisce schermo e ricarica welcome",
            "",
            f"{EnhancedColors.INFO}⚙️ COMANDI AVANZATI:{EnhancedColors.RESET}",
            f"  {EnhancedColors.INFO}/settings{EnhancedColors.RESET}   - Menu impostazioni interfaccia",
            f"  {EnhancedColors.INFO}/stats{EnhancedColors.RESET}      - Statistiche sessione corrente",
            f"  {EnhancedColors.INFO}/help{EnhancedColors.RESET}       - Mostra questo aiuto",
            f"  {EnhancedColors.ERROR}/exit{EnhancedColors.RESET}       - Termina sessione",
            "",
            f"{EnhancedColors.ARNOLD}🏋️ SISTEMA CHECKLIST-DRIVEN:{EnhancedColors.RESET}",
            f"  {VisualElements.ICON_DIAMOND} Ogni domanda segue checklist professionale",
            f"  {VisualElements.ICON_DIAMOND} Dati raccolti sistematicamente",
            f"  {VisualElements.ICON_DIAMOND} Progress sempre visibile",
            f"  {VisualElements.ICON_DIAMOND} Personalizzazione stile comunicativo",
            ""
        ]
        
        help_box = self.layout.create_box("💡 GUIDA COMANDI", base_commands)
        for line in help_box:
            print(f"{EnhancedColors.INFO}{line}{EnhancedColors.RESET}")
        
        print(f"\n{EnhancedColors.DIM}Continua a rispondere per completare l'assessment!{EnhancedColors.RESET}\n")
    
    def show_enhanced_full_progress(self):
        """Progress completo con visualizzazione migliorata"""
        print(self.layout.create_section_header("📊 PROGRESS COMPLETO"))
        
        checklist_context = self.orchestrator.get_checklist_context()
        if checklist_context.get('checklist'):
            self.progress_display.display_checklist_status(
                checklist_context['checklist'],
                checklist_context.get('current_check', {}).get('check_id'),
                terminal_width=self.terminal_width
            )
        
        print()
    
    def show_enhanced_context_details(self):
        """Context JSON con presentazione migliorata"""
        print(self.layout.create_section_header("📄 CONTEXT JSON", "Stato interno sistema"))
        
        context_box = self.layout.create_box(
            "🔧 CONTEXT CORRENTE",
            [json.dumps(self.orchestrator.context, indent=2, ensure_ascii=False)]
        )
        
        for line in context_box:
            print(f"{EnhancedColors.DIM}{line}{EnhancedColors.RESET}")
        
        print()
    
    def show_enhanced_full_checklist(self):
        """Checklist completa con stile migliorato"""
        checklist_context = self.orchestrator.get_checklist_context()
        
        if checklist_context.get('checklist'):
            print(self.layout.create_section_header("📋 CHECKLIST COMPLETA"))
            
            # Info checklist
            info_lines = [
                f"Titolo: {checklist_context['checklist'].get('title', 'N/A')}",
                f"Phase ID: {checklist_context['checklist'].get('phase_id', 'N/A')}",
                f"Tipo: Assessment Professionale Strutturato"
            ]
            
            info_box = self.layout.create_box("ℹ️ INFORMAZIONI CHECKLIST", info_lines)
            for line in info_box:
                print(f"{EnhancedColors.INFO}{line}{EnhancedColors.RESET}")
            
            print()
            
            # Status checklist
            self.progress_display.display_checklist_status(
                checklist_context['checklist'],
                checklist_context.get('current_check', {}).get('check_id'),
                terminal_width=self.terminal_width
            )
        
        print()
    
    def show_settings_menu(self):
        """Menu impostazioni interfaccia (nuovo)"""
        print(self.layout.create_section_header("⚙️ IMPOSTAZIONI INTERFACCIA"))
        
        settings_info = [
            "",
            f"Effetto typing: {'🟢 ATTIVO' if self.typing_effect_enabled else '🔴 DISATTIVO'}",
            f"Animazioni: {'🟢 ATTIVO' if self.animation_enabled else '🔴 DISATTIVO'}",
            f"Larghezza terminale: {self.terminal_width}",
            f"Altezza terminale: {self.terminal_height}",
            "",
            f"{EnhancedColors.DIM}Le impostazioni sono configurabili nel codice{EnhancedColors.RESET}",
            ""
        ]
        
        settings_box = self.layout.create_box("🎛️ CONFIGURAZIONE CORRENTE", settings_info)
        for line in settings_box:
            print(f"{EnhancedColors.INFO}{line}{EnhancedColors.RESET}")
        
        print()
    
    def show_session_stats(self):
        """Statistiche sessione (nuovo)"""
        print(self.layout.create_section_header("📈 STATISTICHE SESSIONE"))
        
        # Calcola statistiche
        uptime = datetime.now().strftime('%H:%M:%S')
        
        stats_info = [
            "",
            f"Session ID: {self.session_id}",
            f"Uptime: {uptime}",
            f"Modalità: Checklist-Driven Assessment",
            f"Stato sistema: 🟢 ATTIVO",
            f"Context size: {len(str(self.orchestrator.context))} caratteri",
            ""
        ]
        
        stats_box = self.layout.create_box("📊 METRICHE CORRENTI", stats_info)
        for line in stats_box:
            print(f"{EnhancedColors.INFO}{line}{EnhancedColors.RESET}")
        
        print()
    
    def show_graceful_exit(self):
        """Uscita elegante con stile"""
        print(f"\n\n{EnhancedColors.SUCCESS}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    👋 ARRIVEDERCI!                          ║")
        print("║                                                            ║")
        print("║    Grazie per aver usato Arnold AI Nutritionist!          ║")
        print("║    La tua sessione è stata salvata automaticamente.       ║")
        print("║                                                            ║")
        print("║           🏋️ Continua il tuo percorso fitness! 🏋️          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{EnhancedColors.RESET}")
    
    def show_error_with_style(self, error_msg: str):
        """Mostra errori con stile visivo"""
        print(f"\n{EnhancedColors.BG_ERROR} ⚠ ERRORE SISTEMA {EnhancedColors.RESET}")
        
        error_box = self.layout.create_box(
            "🚨 DETTAGLI ERRORE",
            [
                "",
                f"Messaggio: {error_msg}",
                f"Timestamp: {datetime.now().strftime('%H:%M:%S')}",
                f"Session ID: {self.session_id or 'N/A'}",
                "",
                "Il sistema continuerà a funzionare normalmente.",
                ""
            ]
        )
        
        for line in error_box:
            print(f"{EnhancedColors.ERROR}{line}{EnhancedColors.RESET}")
        
        print()
    
    def clear_screen(self):
        """Pulisce schermo con supporto multi-platform"""
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Punto di ingresso principale con presentazione migliorata"""
    print(f"{EnhancedColors.HEADER}🚀 Starting Arnold Enhanced CLI System...{EnhancedColors.RESET}")
    time.sleep(1)
    
    cli = ArnoldEnhancedCLI()
    cli.run()


if __name__ == "__main__":
    main()